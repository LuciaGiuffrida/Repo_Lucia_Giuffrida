
parola = 'ciao'
for i in range(len(parola)):
    print(parola[i])
    print(len(parola))

if len(parola) < 5:
    print(parola)

x = list()
print(type(x))

for i in range(len(parola)):
    x.extend(parola[i])

print(x)


z = x + x
print(z)
y = tuple(x)
print(type(y))

#struttura del ciclo for


#struttura del ciclo while 

x = [0, 10, 20, 3, 6, 6, 7, 10, 11]
y = []
counter = 0
count = 0
length = len(x)
for i in range(1,len(x)):
    if counter==0:
        y.append(x[0])
        counter += 1
    if x[i] != x[i-1]:
        y.append(x[i])

print(y)

#dictionary
dict = {
    "nome": "Lucia",
    "cognome" : "Giuffrida"
    #abbiamo coppia chiave (univoca)-valore
}

#list 
lista = []
#tuple
t = (1, 2, 3)
#set 
s = set()
s = {1, 2, 3}

#CLASSI E OGGETTI
class Persona:
    #sono attributi 
    def __init__(self, nome, cognome ):
        self.nome = nome
        self.cognome = cognome
    #metodo --> la persona fa delle azioni 
    def saluta (self):
        print("ciao sono "+ self.nome)

persona1 = Persona("Lucia","Giuffrida") #sto passando delle stringhe quindi " "
print(persona1)
persona1.saluta()

#ereditarietà --> proprietà (metodi) che una classe eredita da un altro classe (abbiamo classe figlia e una classe madre)

class Insegnante(Persona):
    def __init__(self, nome, cognome, materia): #costruttore
        super().__init__(nome,cognome)
        self.materia = materia
    def saluta(self): #qui sto facendo overwrite, il metodo saluta viene sovrascritto dal figlio
        print ("Buongiorno sono " + self.nome + " " + self.cognome)

    def daivoto(selfself):
        print("voto 10")
        # questo è un metodo proprio del figlio, che il padre non ha


insegnante1 = Insegnante("Lucia", "Giuffrida", "Storia")
print(insegnante1)
insegnante1.saluta()

#overwriting: la classe figlia sovrascrive rispetto alla classe madre se non voglio che venga ereditato un metodo e quindi lo elimino

#SCOPE --> indica quella porzione di codice dove una variabile è disponibile
#LOCALE --> variabile disponibile solo all'interno di una funziona
#GLOBALE --> variabile che esiste anche fuori, la porto fuori dalla funziona con il RETURN
# se in una funziona voglio usare una variabile globale e riferirmi a quella devo mettere davanti: global

#MODULI
#è un file contenente funzioni o variabili che voglio includere nel mio codice, lo includo nel mio file con: import

#import modulo as md --> definisco un alias e cosi poi mi ci riferisco
#sono dei file .py con dentro funzioni che poi richiamo nel codice come alias.funzioneconsiderata

#DATE
#devo importare la libreria datetime per poter lavorare con le date

import datetime
x = datetime.datetime(2025, 4, 1)
print(x)

#import camelcase
#pip --> package manager: gestore di pacchetti

#TRY and EXPECT 

#INPUT 

persona = {
    nome : "Lucia",
    cognome: "Giuffrida",
    eta: 25
}

operazioni = ("aggiungere", "eliminare", "modificare" )

def start():
    operazione = input ("Cosa vuoi fare")
    if operazione == operazioni[0]: 
        x = input ("aggiungi chiave:valore separati da una virgola")
        aggiungi(x.split(",")) #splitta 
    if operazione == operazioni[1]: 
        x = input("inserire la chiave che si vuole eliminare")
    if operazione == operazioni[2]: 
        pass

def aggiungi(param): #gli sto passando un array
    chiave = param[0]
    valore = param[1]
    persona[chiave]=valore
    print(persona)

def delete(param):
    chiave = param
    delete.persona[chiave]
    print(persona)


while True:
    start()