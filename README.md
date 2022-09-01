# pyrtd2660i2c
Realtek RTD2660/2662 programmer for Linux through I2C bus.
Based on: ghent360/RTD-2660-Programmer
					juancgarcia/RTD-2660-Programmer-Python.
					mushketer888/pyrtd2660i2c

This python script uses Linux SMBus I2C bus. 
You can program this chip for example with i2c-tiny-usb or any board with an i2c available (i.e.: Raspberry, Olimex, etc)


It can be buggy and it is quite slow! (>10 min to flash)
Anyway it works fine!

The original software has been adapted to python3 and somehow restyled.
working fine with python 3.7.
Requires smbus module installed


This project also contains firmwares for video adapter/lcd controller with this chip in binary format!
Feel free to help this project!
