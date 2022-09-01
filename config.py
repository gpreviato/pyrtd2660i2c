
import logging

version = "xtend ver 0.1a - Sept 1st, 2022"

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(__name__)


i2c_bus = 1
i2c_memaddr = 0x4a


class FlashDesc:
    def __init__(self, device_name, jedec_id, size_kb, page_size, block_size_kb, supported):
        self.device_name = device_name
        self.jedec_id = jedec_id
        self.size_kb = size_kb
        self.page_size = page_size
        self.block_size_kb = block_size_kb
        self.supported = supported


FlashDevices = [
    #          name,         Jedec ID,    sizeK, page size, block sizeK
    FlashDesc("AT25DF041A", 0x1F4401,      512,       256, 64, "N"),
    FlashDesc("AT25DF161",  0x1F4602, 2 * 1024,       256, 64, "N"),
    FlashDesc("AT26DF081A", 0x1F4501, 1 * 1024,       256, 64, "N"),
    FlashDesc("AT26DF0161", 0x1F4600, 2 * 1024,       256, 64, "N"),
    FlashDesc("AT26DF161A", 0x1F4601, 2 * 1024,       256, 64, "N"),
    FlashDesc("AT25DF321",  0x1F4701, 4 * 1024,       256, 64, "N"),
    FlashDesc("AT25DF512B", 0x1F6501,       64,       256, 32, "N"),
    FlashDesc("AT25DF512B", 0x1F6500,       64,       256, 32, "N"),
    FlashDesc("AT25DF021" , 0x1F3200,      256,       256, 64, "N"),
    FlashDesc("AT26DF641",  0x1F4800, 8 * 1024,       256, 64, "N"),
    # Manufacturer: ST                                       , "N"  
    FlashDesc("M25P05"    , 0x202010,       64,       256, 32, "N"),
    FlashDesc("M25P10"    , 0x202011,      128,       256, 32, "N"),
    FlashDesc("M25P20"    , 0x202012,      256,       256, 64, "N"),
    FlashDesc("M25P40"    , 0x202013,      512,       256, 64, "N"),
    FlashDesc("M25P80"    , 0x202014, 1 * 1024,       256, 64, "N"),
    FlashDesc("M25P16"    , 0x202015, 2 * 1024,       256, 64, "N"),
    FlashDesc("M25P32"    , 0x202016, 4 * 1024,       256, 64, "N"),
    FlashDesc("M25P64"    , 0x202017, 8 * 1024,       256, 64, "N"),
    # Manufacturer: Zbit                                     , "N"  
    FlashDesc("ZB25VQ40"  , 0x5E6013,      512,       256, 64, "Y"),
    # Manufacturer: Windbond                                 , "N"        
    FlashDesc("W25X10",     0xEF3011,      128,       256, 64, "Y"),
    FlashDesc("W25X20",     0xEF3012,      256,       256, 64, "Y"),
    FlashDesc("W25X40",     0xEF3013,      512,       256, 64, "Y"),
    FlashDesc("W25X80",     0xEF3014, 1 * 1024,       256, 64, "N"),
    # Manufacturer: Macronix                                 , "N"  
    FlashDesc("MX25L512",   0xC22010,       64,       256, 64, "N"),
    FlashDesc("MX25L3205",  0xC22016, 4 * 1024,       256, 64, "N"),
    FlashDesc("MX25L6405",  0xC22017, 8 * 1024,       256, 64, "N"),
    FlashDesc("MX25L8005",  0xC22014,     1024,       256, 64, "N"),
    # Microchip                                              , "N"   
    FlashDesc("SST25VF512", 0xBF4800,       64,       256, 32, "N"),
    FlashDesc("SST25VF032", 0xBF4A00, 4 * 1024,       256, 32, "N"),
]

