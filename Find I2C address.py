import machine
sda = machine.Pin(12)
scl = machine.Pin(13)
i2c = machine.I2C(0, sda=sda, scl=scl, freq=400000)
print(i2c.scan())