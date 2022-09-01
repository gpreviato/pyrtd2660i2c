# RTD2660_programmer.py

<p>
Realtek RTD2660/2662 programmer for Linux through I2C bus.<br>
	Based on: ghent360/RTD-2660-Programmer  <br>
								juancgarcia/RTD-2660-Programmer-Python.  <br>
								mushketer888/pyrtd2660i2c  <br>
</p>
<p>
This is a generic RTD2660 programmer.  <br>
Just needs a standard smbus module and an i2c available on your pc. <br> 
As an example, you can use i2c-tiny-usb or any board with an i2c <br>available (i.e.: Raspberry, Olimex, etc)  <br>
</p>


It can be buggy and it is quite slow! (>10 min to flash)  <br>
Anyway it works fine!  <br>

The original software has been adapted to python3 and somehow restyled.<br>  
Works fine with python 3.7. <br> 
Requires smbus module installed  <br>

<p>
## How to use:  <br>
there is and help:  <br>
./RTD2660_programmer.py can be used with the following options:  <br>
		-b <i2c_bus id>: defined as number 0... as per /dev/i2c-<i2c_bus_id>  <br>
		-h             : This help  <br>
		-v             : print version and exit   <br>
		-i             : print info on flash memory and exit <br> 
		-r <file_bin>  : read flash memory and save content in <file_bin>  <br>
		-w <file_bin>  : write flash memory with content of <file_bin>  <br>
</p>

<p>
The debug level is configurable in the file config.py  <br>
Supported flash are also defined in the config file  <br>
</p>
<p>
This project also contains firmwares for video adapter/lcd controller with this chip in <br>binary format!  <br>
Feel free to help this project!  <br>
</p>