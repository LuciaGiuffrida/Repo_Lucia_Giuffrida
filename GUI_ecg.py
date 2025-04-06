import os
import sys
import threading
import struct
import time
from datetime import datetime
import platform
import serial
import serial.tools.list_ports

from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QComboBox
)
from PyQt5.QtGui import QFont, QRegExpValidator

import pyqtgraph as pg
from pyqtgraph import PlotWidget

import numpy as np
from scipy.signal import (
    welch,
    butter,
    iirnotch,
    detrend,
    lfilter,
    filtfilt,
    find_peaks,
)

__BAUDRATE__ = 115200
__SAMPLE_RATE__ = 1000  # Hz
__SAMPLE_RATE_PLOT__ = 10  # Hz
__PLOT_INTERVAL__ = int(1/(__SAMPLE_RATE_PLOT__/__SAMPLE_RATE__))  # ms
__PLOT_SEC__ = 10
__PAD_SEC__ = 2.0
__PAD_SAMPLE__ = int(__PAD_SEC__ * __SAMPLE_RATE__)
# utilities ###


def pan_tompkins_detector(unfiltered_ecg, sampling_rate):
    """
    Jiapu Pan and Willis J. Tompkins.
    A Real-Time QRS Detection Algorithm.
    In: IEEE Transactions on Biomedical Engineering
    BME-32.3 (1985), pp. 230-236.
    """

    # Imposta la durata massima prevista di un complesso QRS in secondi
    maxQRSduration = 0.250

    # Calcola le frequenze di taglio per il filtro passa-banda
    f1 = 5 / (sampling_rate / 2)
    f2 = 15 / (sampling_rate / 2)

    # Crea il filtro passa-banda del primo ordine
    b, a = butter(1, [f1, f2], btype='bandpass')

    # Filtra il segnale ECG non filtrato
    filtered_ecg = filtfilt(b, a, unfiltered_ecg, padlen=__PAD_SAMPLE__)

    # Calcola la derivata del segnale filtrato
    diff = np.diff(filtered_ecg)

    # Calcola il quadrato della differenza
    squared = diff * diff

    # Calcola il numero di punti per la finestra mobile (MWA)
    N = int(maxQRSduration * sampling_rate)

    # Applica la media mobile cumulativa (MWA) ai valori quadrati
    mwa = MWA_cumulative(squared, N)

    # Azzeramento delle prime porzioni della MWA corrispondenti alla durata massima del complesso QRS
    mwa[:int(maxQRSduration * sampling_rate)] = 0

    # Applica la funzione di rilevamento dei picchi di Pan-Tompkins
    mwa_peaks = panPeakDetect(mwa, sampling_rate)

    # Restituisce gli indici dei picchi individuati
    return mwa_peaks



# Definizione della funzione per la media mobile cumulativa utilizzata nella precedente funzione
def MWA_cumulative(input_array, window_size):
    # Fast implementation of moving window average with numpy's cumsum function

    ret = np.cumsum(input_array, dtype=float)
    ret[window_size:] = ret[window_size:] - ret[:-window_size]

    for i in range(1, window_size):
        ret[i-1] = ret[i-1] / i
    ret[window_size - 1:] = ret[window_size - 1:] / window_size

    return ret


def panPeakDetect(detection, fs):
    """
    Implementazione dell'algoritmo di rilevamento dei picchi di Pan-Tompkins.

    :param detection: Lista dei valori usata per rilevare i picchi.
    :param fs: Frequenza di campionamento del segnale.
    :return: Lista degli indici dei picchi individuati.
    """

    # Imposta la distanza minima tra i picchi
    min_distance = int(0.35 * fs)

    # Inizializza le liste per i picchi del segnale e i picchi di rumore
    signal_peaks = [0]
    noise_peaks = []

    # Inizializza variabili per SPKI e NPKI (adattamento ai picchi del segnale e di rumore)
    SPKI = 0.0
    NPKI = 0.0

    # Inizializza soglie di rilevamento I1 e I2
    threshold_I1 = 0.0
    threshold_I2 = 0.0

    # Inizializza variabili per il rilevamento dei picchi mancanti
    RR_missed = 0
    index = 0
    indexes = []
    missed_peaks = []
    peaks = []

    # Loop attraverso i valori di rilevamento
    for i in range(1, len(detection)-1):
        if detection[i-1] < detection[i] and detection[i+1] < detection[i]:
            # Se il valore è un picco
            peak = i
            peaks.append(i)

            if detection[peak] > threshold_I1 and (peak - signal_peaks[-1]) > 0.3 * fs:
                # Se il picco supera la soglia I1 e la distanza dal picco precedente è sufficiente
                signal_peaks.append(peak)
                indexes.append(index)
                SPKI = 0.125 * detection[signal_peaks[-1]] + 0.875 * SPKI

                if RR_missed != 0:
                    if signal_peaks[-1] - signal_peaks[-2] > RR_missed:
                        # Se ci sono picchi mancanti, cerca di correggerli
                        missed_section_peaks = peaks[indexes[-2]+1:indexes[-1]]
                        missed_section_peaks2 = []

                        for missed_peak in missed_section_peaks:
                            # Filtra i picchi mancanti in base a determinati criteri
                            if (missed_peak - signal_peaks[-2] > min_distance and
                                    signal_peaks[-1] - missed_peak > min_distance and
                                    detection[missed_peak] > threshold_I2):
                                missed_section_peaks2.append(missed_peak)

                        if len(missed_section_peaks2) > 0:
                            # Se ci sono picchi mancanti che superano i criteri, correggi
                            signal_missed = [detection[i] for i in missed_section_peaks2]
                            index_max = np.argmax(signal_missed)
                            missed_peak = missed_section_peaks2[index_max]
                            missed_peaks.append(missed_peak)
                            signal_peaks.append(signal_peaks[-1])
                            signal_peaks[-2] = missed_peak

            else:
                # Se il picco non supera la soglia I1, trattalo come rumore
                noise_peaks.append(peak)
                NPKI = 0.125 * detection[noise_peaks[-1]] + 0.875 * NPKI

            # Aggiorna le soglie I1 e I2
            threshold_I1 = NPKI + 0.25 * (SPKI - NPKI)
            threshold_I2 = 0.5 * threshold_I1

            if len(signal_peaks) > 8:
                # Calcola la media delle differenze tra i picchi e calcola RR_missed
                RR = np.diff(signal_peaks[-9:])
                RR_ave = int(np.mean(RR))
                RR_missed = int(1.66 * RR_ave)

            index += 1

    # Rimuovi il valore iniziale utilizzato per inizializzare la lista
    signal_peaks.pop(0)

    # Restituisci la lista degli indici dei picchi individuati
    return signal_peaks

### end utilities ###

# Questa classe rappresenta un thread per la lettura asincrona dei dati da una porta seriale.
# Durante l'esecuzione del thread, vengono letti i dati seriali, e i pacchetti validi vengono aggiunti alle
# liste samples_plot e samples_save. I metodi pause, resume e stop consentono di controllare il comportamento
# del thread in modo asincrono.
class SerialReader(threading.Thread):
    def __init__(self, port, baudrate=115200):
        """
        Classe per la lettura asincrona di dati seriali da una porta seriale.

        :param port: Porta seriale da cui leggere i dati.
        :param baudrate: Velocità di trasmissione della porta seriale.
        """
        super().__init__()
        self.serial_port = port
        self.baudrate = baudrate
        self.stop_event = threading.Event()  # Evento per fermare il thread
        self.pause_event = threading.Event()  # Evento per mettere in pausa il thread
        self.daemon = True  # Consente al main di terminare anche se è ancora in esecuzione.

        self.samples_plot = []  # Lista per il plotting
        self.samples_save = []  # Lista per il salvataggio
        self.data_updated = False  # Flag per indicare che i dati sono stati aggiornati
        self.ser = None  # Oggetto per la comunicazione seriale

    def run(self):
        """
        Metodo eseguito quando il thread viene avviato. Legge i dati seriali e aggiorna le strutture dati.
        """
        self.ser = serial.Serial(self.serial_port, self.baudrate, timeout=1)
        self.ser.write(b"b")  # Invia il byte "b" per iniziare la trasmissione
        try:
            while not self.stop_event.is_set():
                if not self.pause_event.is_set():  # Controlla se il thread è in pausa
                    start_byte = self.ser.read(1)
                    if start_byte == b'\xA0':
                        data_bytes = self.ser.read(2)
                        if len(data_bytes) == 2:
                            data_value = struct.unpack('>H', data_bytes)[0]
                            end_byte = self.ser.read(1)
                            if end_byte == b'\xC0':
                                print(f"Received packet: {data_value}")
                                self.samples_plot.append(data_value)
                                self.samples_save.extend([data_value])
                                self.data_updated = True
                            else:
                                print("Invalid packet (missing end byte)")
                        else:
                            print("Invalid packet (missing data bytes)")
        except serial.SerialException:
            pass
        finally:
            self.ser.close()  # Chiude la porta seriale alla fine dell'esecuzione del thread

    def pause(self):
        """Mette in pausa la lettura dei dati."""
        self.ser.write(b"s")  # Invia il carattere "s" per mettere in pausa
        self.pause_event.set()  # Imposta l'evento di pausa

    def resume(self):
        """Riprende la lettura dei dati."""
        self.ser.write(b"b")  # Invia il carattere "b" per riprendere
        self.pause_event.clear()  # Cancella l'evento di pausa

    def stop(self):
        """Interrompe la lettura dei dati e chiude la porta seriale."""
        self.ser.write(b"s")  # Invia il carattere "s" per fermare la trasmissione
        self.stop_event.set()  # Imposta l'evento di stop
        self.ser.close()  # Chiude la porta seriale



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # title and geometry
        self.setWindowTitle("ECG Frontend GUI")
        self.width = 1200
        self.height = 800
        self.setMinimumSize(self.width, self.height)

        # Subject info
        self.subject_name = None
        self.filepathname = None

        # Flags
        self.bool_acq_data = False
        self.bool_save_data = False
        self.indexsample = 0

        # Visualization
        self.timer = QtCore.QTimer()
        self.timer.setInterval(__PLOT_INTERVAL__)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
        # self.n_seconds = __PLOT_SEC__

        # Aggiungi un timer per l'aggiornamento dell'etichetta dell'heart rate ogni 10 secondi
        self.heart_rate_label_timer = QtCore.QTimer()
        self.heart_rate_label_timer.setInterval(1000)  # Intervallo di 10 secondi
        self.heart_rate_label_timer.timeout.connect(self.update_heart_rate_label)
        self.heart_rate_label_timer.start()

        # Connection
        self.ser = None

        # Aggiunta del menu a tendina per le porte COM
        self.serial_ports_combobox = QComboBox(self)
        self.serial_ports_combobox.setToolTip("Select COM Port")
        self.serial_ports_combobox.currentIndexChanged.connect(self.on_serial_port_selected)
        self.update_serial_ports()  # Aggiorna l'elenco delle porte COM iniziale

        self.initUI()

    def set_subject_name(self):
        subject_name = self.input_sub_name.text()
        str_date = datetime.today().strftime('%Y-%m-%d_%H-%M')
        self.subject_name = f"{subject_name}_{str_date}.txt"
        print(self.subject_name)

        self.filepath_btn.setEnabled(True)

    def get_save_folder(self):
        folderpath = QFileDialog.getExistingDirectory(self,
                                                      'Select Folder')
        print(folderpath)
        self.filepathname = os.path.join(folderpath, self.subject_name)
        # self.start_btn.setEnabled(True)
        self.filepath_label.setText(self.filepathname)
        print(self.filepathname)

    def startAcquisition(self):
        try:
            self.ser.start()
        except:
            self.ser.resume()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.save_btn.setEnabled(False)
        self.bool_acq_data = True

    def stopAcquisition(self):
        self.bool_acq_data = False
        # self.ser.stop()
        self.ser.pause()
        self.stop_btn.setEnabled(False)
        self.start_btn.setEnabled(True)
        self.save_btn.setEnabled(True)

    def save_acquisition(self):
        if not self.bool_save_data:
            self.bool_save_data = True

        if self.filepathname is not None and self.bool_save_data:
            print("Saving")
            if len(self.ser.samples_save) > 0:
                print(len(self.ser.samples_save))
                # Save data file
                with open(self.filepathname, "w", encoding="utf-8") as f:
                    for data in self.ser.samples_save:
                        val1 = data
                        f.writelines(f"{val1:.10f}\n")

        else:
            print("Saved nothing")

    @staticmethod
    def define_time_axes():
        """!
        @brief Define the x axis (and init y to 0) according to sample rate.

        The dependency on the sample rate is needed to adjust from sample per
        seconds to seconds (which is the units displayed on the x axis)
        """
        n_points = __PLOT_SEC__ * __SAMPLE_RATE__  # Number of points to plot
        x_axis = np.linspace(-__PLOT_SEC__, 0, n_points).tolist()
        y_axis = np.zeros_like(x_axis).tolist()
        return x_axis, y_axis

    @staticmethod
    def test_com_port(port_name):
        try:
            print(f"provo porta {port_name}")
            ser = serial.Serial(port_name, baudrate=__BAUDRATE__, timeout=1)
            ser.write(b"$")
            time.sleep(10)  # Wait for a moment to receive the response
            response = ser.read(1)

            if response == b"$":
                print(f"conesso a porta {port_name}")
                return True,
        except serial.SerialException as e:
            print(e)

        return False

    def start_connection(self):

        myport = self.serial_ports_combobox.currentText()
        if self.test_com_port(myport):
            print(f"  {myport} - Connection successful")
            self.ser = SerialReader(myport,
                                        baudrate=__BAUDRATE__)
            self.connect_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            self.connect_btn.setText(myport)
        else:
                print(f" {myport} - Connection failed")

    def initUI(self):
        # First row UI element
        self.heart_rate_label = QLabel("Heart Rate: N/A", self)
        self.heart_rate_label.setFont(QFont("Arial", 18))
        self.sub_id_label = QLabel("Insert subject identifier")
        self.input_sub_name = QLineEdit(editingFinished=self.set_subject_name)
        # Create a regular expression which only allows alphanumeric characters
        reg_exp = QtCore.QRegExp("[a-zA-Z0-9-]*")
        # Create a validator with the regular expression
        validator = QRegExpValidator(reg_exp)
        # Set the validator for the QLineEdit
        self.input_sub_name.setValidator(validator)

        self.filepath_btn = QPushButton(
            text="Select file path",
            clicked=self.get_save_folder
        )
        self.connect_btn = QPushButton(
            text="Connect",
            clicked=self.start_connection
        )

        # Second row UI element
        self.start_btn = QPushButton(
            text="Start",
            clicked=self.startAcquisition
        )
        self.stop_btn = QPushButton(
            text="Stop",
            clicked=self.stopAcquisition
        )
        self.save_btn = QPushButton(
            text="Save",
            clicked=self.save_acquisition
        )

        # Third row UI element
        self.graph_widget_sgn = PlotWidget()
        self.graph_widget_peak = pg.ScatterPlotItem(
            size=15, symbol='x', pen='r')
        self.graph_widget_sgn.addItem(self.graph_widget_peak)

        # Last row UI element
        self.filepath_label = QLabel()
        self.filepath_label.setText("")


        # Set layout
        label_hlay = QHBoxLayout()
        label_hlay.addWidget(self.sub_id_label)
        label_hlay.addWidget(self.input_sub_name)
        label_hlay.addWidget(self.filepath_btn)
        label_hlay.addWidget(self.connect_btn)
        label_hlay.addWidget(self.heart_rate_label)  # Aggiunta dell'etichetta per l'heart rate

        button_hlay = QHBoxLayout()
        button_hlay.addWidget(self.start_btn)
        button_hlay.addWidget(self.stop_btn)
        button_hlay.addWidget(self.save_btn)

        vlay = QVBoxLayout()
        vlay.addLayout(label_hlay)
        vlay.addLayout(button_hlay)
        vlay.addWidget(self.graph_widget_sgn)
        vlay.addWidget(self.filepath_label)

        widget = QWidget()
        widget.setLayout(vlay)
        self.setCentralWidget(widget)

        # Disabled button at starting
        self.filepath_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.save_btn.setEnabled(False)

        # Set font size at 14
        fontbuttonsize = 14
        fontButtons = QFont()
        fontButtons.setPointSize(fontbuttonsize)

        self.input_sub_name.setFont(fontButtons)
        self.sub_id_label.setFont(fontButtons)
        self.filepath_label.setFont(fontButtons)
        self.filepath_btn.setFont(fontButtons)
        self.start_btn.setFont(fontButtons)
        self.stop_btn.setFont(fontButtons)
        self.save_btn.setFont(fontButtons)
        self.connect_btn.setFont(fontButtons)

        # Plot settings
        # Add grid
        self.graph_widget_sgn.showGrid(x=True, y=True)
        # Set background color
        self.graph_widget_sgn.setBackground('w')

        # Add plot labels
        styles = {'color': 'k', 'font-size': '18px'}

        self.graph_widget_sgn.setLabel('left', 'processed ECG [mV]', **styles)
        self.graph_widget_sgn.setLabel('bottom', 'Time [s]', **styles)

        self.graph_widget_sgn.addLegend()

        # Aggiunta del menu a tendina alle etichette e ai pulsanti
        label_hlay.addWidget(self.sub_id_label)
        label_hlay.addWidget(self.input_sub_name)
        label_hlay.addWidget(self.filepath_btn)
        label_hlay.addWidget(self.serial_ports_combobox)  # Aggiunta del menu a tendina per le porte COM
        label_hlay.addWidget(self.heart_rate_label)

        self.draw()

    def update_serial_ports(self):
        # Aggiorna l'elenco delle porte COM disponibili nel menu a tendina
        available_ports = [port.device for port in serial.tools.list_ports.comports()]
        self.serial_ports_combobox.clear()
        self.serial_ports_combobox.addItems(available_ports)

    def on_serial_port_selected(self):
        # Gestisce l'evento quando viene selezionata una porta COM nel menu a tendina
        selected_port = self.serial_ports_combobox.currentText()

    def draw(self):
        self.x_axis_raw_sgn, self.y_axis_raw_sgn = self.define_time_axes()

        self.line_raw_sgn = self.plot(self.graph_widget_sgn,
                                      self.x_axis_raw_sgn,
                                      self.y_axis_raw_sgn,
                                      'ECG',
                                      'r')

    def plot(self,
             graph,
             x,
             y,
             curve_name,
             color):
        """!
        @brief Draw graph.
        """
        pen = pg.mkPen(color=color)
        line = graph.plot(x, y, name=curve_name, pen=pen)
        return line

    def update_plot_data(self):
        if self.bool_acq_data:
            if len(self.ser.samples_plot) > 0:
                if self.ser.data_updated:
                    for _ in self.ser.samples_plot:
                        self.y_axis_raw_sgn.append(self.y_axis_raw_sgn.pop(0))
                        self.y_axis_raw_sgn[-1] = self.ser.samples_plot.pop(0)

                    self.line_raw_sgn.setData(self.x_axis_raw_sgn, self.y_axis_raw_sgn)
                    self.graph_widget_peak.setData(
                        pos=[(self.x_axis_raw_sgn[i], self.y_axis_raw_sgn[i]) for i in peaks])

                    self.ser.data_updated = False
        else:
            pass

    def update_heart_rate_label(self):
        if self.bool_acq_data:
            if len(self.ser.samples_plot) > 0:
                if self.ser.data_updated:
                    peaks = pan_tompkins_detector(self.y_axis_raw_sgn, sampling_rate=__SAMPLE_RATE__)
                    # Calcola il tasso di battito cardiaco
                    heart_rate = calculate_heart_rate(peaks, sampling_rate=__SAMPLE_RATE__)
                    # Forza l'heart rate ad essere compreso tra 70 e 90
                    #heart_rate = max(50, min(90, heart_rate))

                    # Aggiorna l'etichetta dell'heart rate nella tua GUI
                    self.heart_rate_label.setText(f"Heart Rate: {heart_rate:.0f} BPM")

                    self.ser.data_updated = False
        else:
            pass


    def closeEvent(self, event):
        if self.ser is not None:
            # self.stopAcquisition()
            self.ser.stop()

def calculate_heart_rate(peaks, sampling_rate, window_size=5):
    if len(peaks) < 2:
        return 0.0

    # Calcola la differenza tra gli indici dei picchi adiacenti
    rr_intervals = np.diff(peaks) / sampling_rate

    # Applica una media mobile ai dati dei picchi
    smoothed_rr_intervals = np.convolve(rr_intervals, np.ones(window_size) / window_size, mode='valid')

    # Calcola la frequenza cardiaca media in battiti al minuto (bpm)
    heart_rate_bpm = 60.0 / np.mean(smoothed_rr_intervals)

    return heart_rate_bpm

    # Calcola la media delle differenze tra i picchi
    RR_intervals = np.diff(peaks) / sampling_rate
    heart_rate = 60 / np.mean(RR_intervals)
    return heart_rate

if __name__ == '__main__':
    # Fix a pyqtgraph bug on windows when using a secondary screen
    if platform.system() == 'Windows' and int(platform.release()) >= 8:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(True)

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
