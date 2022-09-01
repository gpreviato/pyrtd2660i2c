# RTD2660_programmer.py
Realtek RTD2660/2662 programmer for Linux through I2C bus.
Based on: 			ghent360/RTD-2660-Programmer
					juancgarcia/RTD-2660-Programmer-Python.
					mushketer888/pyrtd2660i2c


This is a generic RTD2660 programmer.
Just needs a standard smbus module and an i2c available on your pc.
As an example, you can use i2c-tiny-usb or any board with an i2c available (i.e.: Raspberry, Olimex, etc)


It can be buggy and it is quite slow! (>10 min to flash)
Anyway it works fine!

The original software has been adapted to python3 and somehow restyled.
Works fine with python 3.7.
Requires smbus module installed

How to use:
there is and help:
./RTD2660_programmer.py with following options:
	-b <i2c_bus id>: defined as number 0... as per /dev/i2c-<i2c_bus_id>
	-h             : This help
	-v             : print version and exit
	-i             : print info on flash memory and exit
	-r <file_bin>  : read flash memory and save content in <file_bin>
	-w <file_bin>  : write flash memory with content of <file_bin>


The debug level is configurable in the file config.py
Supported flash are also defined in the config file

This project also contains firmwares for video adapter/lcd controller with this chip in binary format!
Feel free to help this project!
