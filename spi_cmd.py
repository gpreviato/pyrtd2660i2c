import time
import os
import stat
import crc
import sys
import array
import getopt
import inspect

from smbus import SMBus
from config import FlashDevices
from config import _logger


Instructions = """
1. Set common instruction type.
2. Set common instruction OP code.
3. Set write number ( 0 ~ 3 ).
4. Set read number if common instruction type is read.
5. Write data to Flash_prog_write_dum_readCRC_ISP if write number > 0 .
6. Execution common instruction enable.
7. Polling common instruction enable in ISP mode‡If it is finished and the instruction is read, read the Data in common_inst_read_port .
8. It would auto clear in normal mode. Then read the Data in common_inst_read_port if the instruction type is read.
"""

# RTD2660 - Common instruction field comm_inst - bits 7:5, page 311 Datasheet
E_CC_NOOP = 0
E_CC_WRITE = 1
E_CC_READ = 2
E_CC_WRITE_AFTER_WREN = 3
E_CC_WRITE_AFTER_EWSR = 4
E_CC_ERASE = 5

# RTD2660 registers
REG_COMMON_INST_ENABLE = 0x60
REG_COMMON_OP_CODE = 0x61
REG_WREN_OP_CODE = 0x62
REG_EWSR_OP_CODE = 0x63
REG_FLASH_PROG_ISP0 = 0x64
REG_FLASH_PROG_ISP1 = 0x65
REG_FLASH_PROG_ISP2 = 0x66
REG_COMM_INST_READ_PORT0 = 0x67
REG_COMM_INST_READ_PORT1 = 0x68
REG_COMM_INST_READ_PORT2 = 0x69

REG_READ_OP_CODE = 0x6a
REG_FAST_READ_OP_CODE = 0x6b
REG_READ_INSTRUCTION = 0x6c
REG_PROG_OP_CODE = 0x6d
REG_READ_STATUS_REG_OP_CODE = 0x6e
REG_PROGRAM_INSTRUCTION = 0x6f
REG_PROGRAM_DATA_PORT = 0x70
REG_PROGRAM_LENGTH = 0x71
REG_CRC0_END_ADDR0 = 0x72
REG_CRC0_END_ADDR1 = 0x73
REG_CRC0_END_ADDR2 = 0x74
REG_CRC_RESULT = 0x75
# Flash timing register
REG_CEN_CTRL = 0x76



def __fname__(): 
    return inspect.stack()[1].function


class spi_commands:
    chipManId = 0x0

    def __init__(self, i2c_address, bus, mem_id=None):
        self.i2c_address = i2c_address
        self.mem_id = mem_id
        self.bus = bus
        # detect flash chip
        self.jedec_id = self.detectFlash()
        # check if flash is supported
        self.chip = self.FindChip()
        # save manufaturer id 
        self.chipManId = self.GetManufacturerId()
        self.ManufacturerName = self.getManufacturerName()

    def FindChip(self):
        for chip in FlashDevices:
            if (chip.jedec_id == self.jedec_id):
                return chip
        return None        

    def detectFlash(self):
        self.bus.write_i2c_block_data(self.i2c_address, REG_PROGRAM_INSTRUCTION, [0x80])
        # uint32_t jedec_id = SPICommonCommand(E_CC_READ, 0x9f, 3, 0, 0);
        _logger.debug("%s: Send SPI command" % (__fname__()))
        jedec_id = self.SPICommonCommand(E_CC_READ, 0x9f, 3, 0, 0)
        _logger.debug("%s: 0x%x" % (__fname__(), jedec_id))
        return jedec_id

    def getJedecId(self):
        return self.jedec_id

    # void PrintManufacturer(uint32_t id) {
    def getManufacturerName(self):
        if self.chipManId == 0x20:
            return("ST")
        elif self.chipManId == 0x5e:
            return("Zbit")
        elif self.chipManId == 0xef:
            return("Winbond")
        elif self.chipManId == 0x1f:
            return("Atmel")
        elif self.chipManId == 0xc2:
            return("Macronix")
        elif self.chipManId == 0xbf:
            return("Microchip")
        else:
            return("Unknown")

    # uint8_t GetManufacturerId(uint32_t jedec_id)
    def GetManufacturerId(self):
        self.chipManId = self.jedec_id >> 16
        return self.chipManId

    def printChipInfo(self):
        print("Manufacturer: %s" % self.ManufacturerName)
        print("\tChip Id: 0x%x" % self.jedec_id)
        print("\tChip: {}".format(self.chip.device_name))
        print("\tSize: {}KB".format(self.chip.size_kb))

    def readProgramByte(self):
        return self.bus.read_i2c_block_data(self.i2c_address, REG_PROGRAM_INSTRUCTION, 1)[0]

    def writeDataBlock(self, address, size, data):
        # Set program size-1
        bus.write_i2c_block_data(self.i2c_address, REG_PROGRAM_LENGTH, [size - 1])

          # Set the programming address
        bus.write_i2c_block_data(self.i2c_address, REG_FLASH_PROG_ISP0, [address >> 16])
        bus.write_i2c_block_data(self.i2c_address, REG_FLASH_PROG_ISP1, [address >> 8])
        bus.write_i2c_block_data(self.i2c_address, REG_FLASH_PROG_ISP2, [address])

        for byte in data:
            bus.write_i2c_block_data(self.i2c_address, REG_PROGRAM_DATA_PORT, [byte]) 
              
        bus.write_i2c_block_data(self.i2c_address, REG_PROGRAM_INSTRUCTION, [0xa0])
        return

    def SPICommonCommand(self, cmd_type, cmd_code, read_length, write_length, write_value):
        """ Write to the flash using the intenal chip MCU
            check RTD2660 datasheet, page 311
        """
        read_length &= 3
        write_length &= 3
        write_value &= 0xFFFFFF
        # uint8_t
        reg_value = (cmd_type << 5) | (write_length << 3) | (read_length << 1)

        self.bus.write_i2c_block_data(self.i2c_address, REG_COMMON_INST_ENABLE, [reg_value])
        self.bus.write_i2c_block_data(self.i2c_address, REG_COMMON_OP_CODE, [cmd_code])

        if write_length == 3:
            self.bus.write_i2c_block_data(self.i2c_address, REG_FLASH_PROG_ISP0, [write_value >> 16])
            self.bus.write_i2c_block_data(self.i2c_address, REG_FLASH_PROG_ISP1, [write_value >> 8])
            self.bus.write_i2c_block_data(self.i2c_address, REG_FLASH_PROG_ISP1, [write_value])
        elif write_length == 2:
            self.bus.write_i2c_block_data(self.i2c_address, REG_FLASH_PROG_ISP0, [write_value >> 8])
            self.bus.write_i2c_block_data(self.i2c_address, REG_FLASH_PROG_ISP1, [write_value])
        elif write_length == 3:
            self.bus.write_i2c_block_data(self.i2c_address, REG_FLASH_PROG_ISP0, [write_value])

        self.bus.write_i2c_block_data(self.i2c_address, REG_COMMON_INST_ENABLE, [reg_value | 1]) # Execute the command
        # uint8_t b;
        b = self.bus.read_i2c_block_data(self.i2c_address, REG_COMMON_INST_ENABLE, 1)
        _logger.debug("%s: %s" % (__fname__(), b))
        b = b[0]
        while (b & 1):
            b = self.bus.read_i2c_block_data(self.i2c_address, REG_COMMON_INST_ENABLE, 1)
            b = b[0]
        if read_length == 0:
            return 0
        elif read_length == 1:
            return self.bus.read_i2c_block_data(self.i2c_address, REG_COMM_INST_READ_PORT0, 1)[0]
        elif read_length == 2:
            return (self.bus.read_i2c_block_data(self.i2c_address, REG_COMM_INST_READ_PORT0, 1)[0] << 8) | self.bus.read_i2c_block_data(self.i2c_address, REG_COMM_INST_READ_PORT1, 1)[0]
        elif read_length == 3:
            return (self.bus.read_i2c_block_data(self.i2c_address, REG_COMM_INST_READ_PORT0, 1)[0] << 16) | (self.bus.read_i2c_block_data(self.i2c_address, REG_COMM_INST_READ_PORT1, 1)[0] << 8) | self.bus.read_i2c_block_data(self.i2c_address,REG_COMM_INST_READ_PORT2,1)[0]

    def SPIRead(self, address, data, len):
        self.bus.write_i2c_block_data(self.i2c_address, REG_COMMON_INST_ENABLE, [0x46])
        self.bus.write_i2c_block_data(self.i2c_address, REG_COMMON_OP_CODE, [0x3])
        self.bus.write_i2c_block_data(self.i2c_address, REG_FLASH_PROG_ISP0, [address >> 16])
        self.bus.write_i2c_block_data(self.i2c_address, REG_FLASH_PROG_ISP1, [address >> 8])
        self.bus.write_i2c_block_data(self.i2c_address, REG_FLASH_PROG_ISP1, [address])
        self.bus.write_i2c_block_data(self.i2c_address, REG_COMMON_INST_ENABLE, [0x47])  # Execute the command
        # uint8_t b;
        b = self.bus.read_i2c_block_data(self.i2c_address, REG_COMMON_INST_ENABLE, 1)[0]

        while(b & 1):
            b = self.bus.read_i2c_block_data(self.i2c_address, REG_COMMON_INST_ENABLE, 1)[0]
            # TODO: add timeout and reset the controller

        while (len > 0):
            read_len = len  # int32_t
            if (read_len > 64):
                read_len = 64

            # Original
            # ReadBytesFromAddr(REG_PROGRAM_DATA_PORT, data, read_len)

            # Adafruit library
            # keeps failing with an ACK error
            # bytedata = i2c.readList(REG_PROGRAM_DATA_PORT, read_len) # returns bytearray
            
            # fell back to reading ONE BYTE AT A TIME! (this took around 8-10 mins)
            bytedata = bytearray()
            itr = read_len
            while(itr > 0):
                bytedata += bytearray([self.bus.read_i2c_block_data(self.i2c_address, REG_PROGRAM_DATA_PORT, 1)[0]])
                itr -= 1
            
            # data += read_len

            data += bytedata
            len -= read_len

    def SetupChipCommands(self, jedec_id):
        # uint8_t manufacturer_id = GetManufacturerId(jedec_id);
        manufacturer_id = self.GetManufacturerId()
        if manufacturer_id == 0xEF:
            # These are the codes for Winbond
            self.bus.write_i2c_block_data(self.i2c_address, REG_WREN_OP_CODE, [0x6])  # Flash Write enable op code
            self.bus.write_i2c_block_data(self.i2c_address, REG_EWSR_OP_CODE, [0x50]) # Flash Write register op code
            self.bus.write_i2c_block_data(self.i2c_address, REG_READ_OP_CODE, [0x3])  # Flash Read op code.
            self.bus.write_i2c_block_data(self.i2c_address, REG_FAST_READ_OP_CODE, [0xb])  # Flash Fast read op code.
            self.bus.write_i2c_block_data(self.i2c_address, REG_PROG_OP_CODE, [0x2])  # Flash program op code.
            self.bus.write_i2c_block_data(self.i2c_address, REG_READ_STATUS_REG_OP_CODE, [0x5])  # Flash read status op code.
        else:
            print("Can not handle manufacturer code %02x" % manufacturer_id)

    def SPIComputeCRC(self, start, end):
        self.bus.write_i2c_block_data(self.i2c_address, REG_FLASH_PROG_ISP0, [start >> 16])
        self.bus.write_i2c_block_data(self.i2c_address, REG_FLASH_PROG_ISP1, [start >> 8])
        self.bus.write_i2c_block_data(self.i2c_address, REG_FLASH_PROG_ISP1, [start])

        self.bus.write_i2c_block_data(self.i2c_address, REG_CRC0_END_ADDR0, [end >> 16])
        self.bus.write_i2c_block_data(self.i2c_address, REG_CRC0_END_ADDR1, [end >> 8])
        self.bus.write_i2c_block_data(self.i2c_address, REG_CRC0_END_ADDR2, [end])

        self.bus.write_i2c_block_data(self.i2c_address, REG_PROGRAM_INSTRUCTION, [0x84])
        
        # uint8_t b;
        b = self.bus.read_i2c_block_data(self.i2c_address, REG_PROGRAM_INSTRUCTION, 1)[0]
        while (not (b & 0x2)):
            b = self.bus.read_i2c_block_data(self.i2c_address, REG_PROGRAM_INSTRUCTION, 1)[0]
        # TODO: add timeout and reset the controller

        return self.bus.read_i2c_block_data(self.i2c_address, REG_CRC_RESULT, 1)[0]






