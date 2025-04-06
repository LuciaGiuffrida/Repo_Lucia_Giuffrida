from smbus2 import SMBus

I2C_BUS = 1  # Di solito 1 su Raspberry Pi
DEVICE_ADDR = 0x19  # Es. indirizzo di un LIS3DH (accelerometro MEMS)
OUT_X_L = 0x28      # Registro LSB
OUT_X_H = 0x29      # Registro MSB

def read_sensor_register(msb_addr, lsb_addr):
    with SMBus(I2C_BUS) as bus:
        lsb = bus.read_byte_data(DEVICE_ADDR, lsb_addr)
        msb = bus.read_byte_data(DEVICE_ADDR, msb_addr)
        return msb, lsb

def bytes_to_signed_int(msb, lsb):
    raw = (msb << 8) | lsb
    if raw >= 0x8000:
        raw -= 0x10000
    return raw

def convert_to_g(raw_value):
    return raw_value * (2.0 / 32768)

def read_acceleration_x():
    msb, lsb = read_sensor_register(OUT_X_H, OUT_X_L)
    raw = bytes_to_signed_int(msb, lsb)
    return convert_to_g(raw)

# Test
if __name__ == "__main__":
    g = read_acceleration_x()
    print(f"Accelerazione X: {g:.6f} g")
