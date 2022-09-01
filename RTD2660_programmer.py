#!/usr/bin/env python

import time
import os
import stat
import crc
import sys
import array
import getopt

from smbus import SMBus
from config import i2c_bus, i2c_memaddr, FlashDevices, version
from config import _logger
from spi_cmd import spi_commands


bus = -1
progname = ""
sc = None

E_CC_NOOP = 0
E_CC_WRITE = 1
E_CC_READ = 2
E_CC_WRITE_AFTER_WREN = 3
E_CC_WRITE_AFTER_EWSR = 4
E_CC_ERASE = 5


def SaveFlash(output_file_name, chip_size):

    # FILE *dump = fopen(output_file_name, "wb");
    dump = open(output_file_name, "wb")
    # uint32_t addr = 0;
    addr = 0
    crc.InitCRC();
    while (addr < chip_size):
        # uint8_t buffer[1024];
        # buffer = 1024 * [None]
        buffer = bytearray()
        # print("Reading addr %x\r", addr);
        _logger.debug('Reading addr {0} [{0:02X}]\r'.format(addr))
        # SPIRead(addr, buffer, sizeof(buffer));
        sc.SPIRead(addr, buffer, 1024);
        # buffer = i2c.readList(addr, 32) # returns bytearray

        _logger.debug("Got data ({0} bytes):\r\n".format(len(buffer)))
        # print buffer
        # print "\r\n"

        # fwrite(buffer, 1, sizeof(buffer), dump);
        dump.write(buffer);

        # addr += sizeof(buffer);
        addr += len(buffer)


        # ProcessCRC(buffer, sizeof(buffer));

        # temporarily disabling CRC
        crc.ProcessCRC(buffer, len(buffer))
        # 

        _logger.debug("New address: {0}\r\n".format(addr))
    
    _logger.debug("done.\n")
    # fclose(dump);
    dump.close()
    # uint8_t data_crc = GetCRC();
    data_crc = crc.GetCRC()
    # uint8_t chip_crc = SPIComputeCRC(0, chip_size - 1);

    # Temporarily disabling CRC
    chip_crc = sc.SPIComputeCRC(0, chip_size - 1)
    # chip_crc = 0
    # 

    _logger.debug("Received data CRC {0:02X}\n".format(data_crc))
    _logger.debug("Chip CRC {0:02X}\n".format(chip_crc))
    return data_crc == chip_crc


def ShouldProgramPage(buffer, size):
    # for (uint32_t idx = 0; idx < size; ++idx) {
    idx = 0
    while idx < size:
        if (buffer[idx] != 0xff):
            return True
        ++idx
    return False


def ProgramFlash(fname, chip_size):
    masiv = open(fname, "rb")

    _logger.debug("Erasing...")
    sc.SPICommonCommand(E_CC_WRITE_AFTER_EWSR, 1, 0, 1, 0)  # // Unprotect the Status Register
    sc.SPICommonCommand(E_CC_WRITE_AFTER_WREN, 1, 0, 1, 0)  # // Unprotect the flash
    sc.SPICommonCommand(E_CC_ERASE, 0xc7, 0, 0, 0)          # // Chip Erase
    _logger.debug("Done")

    b = 0
    addr = 0
    buffer = bytearray()
    # res = array.array('c')
    crc.InitCRC()
    # RTD266x can program only 256 bytes at a time.
    _logger.debug("chip size %x" % chip_size)
    while addr < chip_size:
        while b & 0x40:
            # b = bus.read_i2c_block_data(0x4a, 0x6f, 1)[0]
            b = sc.readProgramByte()

        _logger.debug("Writing addr %x\r" % addr)
        buffer = masiv.read(256)
        data = []
        for i in buffer:
            data.append(ord(i))
        # print type(buffer)
        # res.fromfile(masiv, 256)
        # print buffer
        if True:
            sc.writeDataBlock(self, addr, 256, data)
        crc.ProcessCRC(list(data), len(buffer))
        addr += 256;
    _logger.debug("done")
    masiv.close()

    # Wait for programming cycle to finish
    while b & 0x40:
        # b = bus.read_i2c_block_data(0x4a, 0x6f, 1)[0]
        b = sc.readProgramByte()
  
    sc.SPICommonCommand(E_CC_WRITE_AFTER_EWSR, 1, 0, 1, 0x1c)  # // Unprotect the Status Register
    sc.SPICommonCommand(E_CC_WRITE_AFTER_WREN, 1, 0, 1, 0x1c)  # // Protect the flash

    # uint8_t data_crc = GetCRC();
    data_crc = crc.GetCRC()
    # uint8_t chip_crc = SPIComputeCRC(0, chip_size - 1);

    # Temporarily disabling CRC
    chip_crc = sc.SPIComputeCRC(0, chip_size - 1)
    # chip_crc = 0
    # 

    _logger.debug("Received data CRC {0:02X}\n".format(data_crc))
    _logger.debug("Chip CRC {0:02X}\n".format(chip_crc))
    return data_crc == chip_crc;


def GetFileSize(file):
    return os.stat.st_size(file)


def usage():
    print("%s with following options:" % progname)
    print("\t-b <i2c_bus id>: defined as number 0... as per /dev/i2c-<i2c_bus_id>")
    print("\t-h             : This help")
    print("\t-v             : print version and exit")
    print("\t-i             : print info on flash memory and exit")
    print("\t-r <file_bin>  : read flash memory and save content in <file_bin>")
    print("\t-w <file_bin>  : write flash memory with content of <file_bin>")
    return


def check_i2cBus(bus_id):
    try:
        path = "/dev/i2c-%d" % int(bus_id)
    except:
        return False
    return os.path.exists(path) and stat.S_ISCHR(os.stat(path).st_mode)


def main():
    # manage options
    global progname
    global bus
    global sc 

    progname = sys.argv[0]
    printInfo = False
    fileBinName = ""
    command = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "b:hir:w:v", ["i2c_bus", "help", "info", "read", "write", "version"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("-v", "--version"):
            print("%s: %s" % (progname, version))
            sys.exit(0)
        elif o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-i", "--info"):
            printInfo = True
        elif o in ("-b", "--i2c_bus"):
            i2c_bus = int(a.strip())
            # check if bus exists
        elif o in ("-r", "--read"):
            fileBinName = a.strip()
            command = "read"
        elif o in ("-w", "--write"):
            fileBinName = a.strip()
            command = "write"
        else:
            assert False, "unhandled option"

    if check_i2cBus(i2c_bus) is False:
        print("error checking bus: /dev/i2c-%s" % i2c_bus)
        sys.exit(1)

    bus = SMBus(i2c_bus) # choose your bus 7 for usb tiny i2c
    sc = spi_commands(i2c_memaddr, bus)

#    print("Enter ISP?")
#    bus.write_i2c_block_data(0x4a, 0x6f, [0x80])
#        # uint32_t jedec_id = SPICommonCommand(E_CC_READ, 0x9f, 3, 0, 0);
#    print("Send SPI command")
#    jedec_id = sc.SPICommonCommand(E_CC_READ, 0x9f, 3, 0, 0)
#    print(jedec_id)
    # jedec_id=jedec_id[0]
        # print("JEDEC ID: 0x%02x\n", jedec_id);
    jedec_id = sc.getJedecId()
    # print("JEDEC ID: 0x{:02X}\n".format(jedec_id))
    chip = sc.FindChip()

    # 0xef3013
    if chip.supported == "Y":
        print("Flash supported!\n")
    else:
        print("Unsuported Flash memory")
        exit(0)

    sc.printChipInfo()
    if printInfo is True:
        sys.exit(0)

    #   // Setup flash command codes
    sc.SetupChipCommands(jedec_id)

    b = sc.SPICommonCommand(E_CC_READ, 0x5, 1, 0, 0)
    _logger.debug("Flash status register: 0x{:02X}\n".format(b))

    if command == "read" or command == "write":
        ticks = time.time()
        if fileBinName is None or len(fileBinName) == 0:
            print("Command: %s requires a file parameter!" % fileBinName)
            usage()
            sys.exit(1)
        filenam = fileBinName
    else:
        sys.exit(0)

    ticks = time.time()


    # uncomment here to read firmware to file (dump)
    if command == "read":
        print("Saving controller flash to \"{0}\"".format(os.path.abspath(filenam)))
        SaveFlash(filenam, chip.size_kb * 1024) # 4tenie
    # uncomment here to program chip
    elif command == "write":
        print("Flashing \"{0}\" to controller".format(os.path.abspath(filenam)))
        ProgramFlash(filenam, 256 * 1024) # zapisj
    else:
        print("Error with command: %s" % command)
        sys.exit(1)

    duration = time.time() - ticks

    remainder = duration % (60 * 60)
    hour_secs = duration - remainder
    hours = hour_secs/(60 * 60)

    duration -= hour_secs

    remainder = duration % (60)
    min_secs = duration - remainder
    mins = min_secs/(60)

    duration -= min_secs

    secs = duration

    _logger.debug("run time: {0}:{1}:{2}".format(hours, mins, secs))
    #  /cygdrive/z/Workspaces/RTD2660H\ LCD\ TFT\ Controller\ I2C

    exit()


if __name__ == '__main__':
    main()
