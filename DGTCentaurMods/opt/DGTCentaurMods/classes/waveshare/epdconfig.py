# /*****************************************************************************
# * | File        :	  epdconfig.py
# * | Author      :   Waveshare team
# * | Function    :   Hardware underlying interface
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2019-06-21
# * | Info        :   
# ******************************************************************************
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
import logging
import sys
import time


class RaspberryPi:
    # Pin definition
    RST_PIN         = 12 
    DC_PIN          = 16
    CS_PIN          = 18
    BUSY_PIN        = 13

    def __init__(self):
        import spidev
        self.SPI = spidev.SpiDev()
        self.GPIO = None
        self.lgpio = None
        self.chip = None
        
        # Try RPi.GPIO first
        try:
            import RPi.GPIO
            self.GPIO = RPi.GPIO
            self.GPIO.setwarnings(False)
        except ImportError:
            pass
            
        # Try lgpio as fallback or for direct usage
        try:
            import lgpio
            self.lgpio = lgpio
        except ImportError:
            pass

    def digital_write(self, pin, value):
        if self.chip is not None and self.lgpio:
            self.lgpio.gpio_write(self.chip, pin, value)
        elif self.GPIO:
            self.GPIO.output(pin, value)

    def digital_read(self, pin):
        if self.chip is not None and self.lgpio:
            return self.lgpio.gpio_read(self.chip, pin)
        elif self.GPIO:
            return self.GPIO.input(pin)

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.SPI.writebytes(data)

    def spi_writebyte2(self, data):
        self.SPI.writebytes2(data)

    def module_init(self):
        
        success = False
        if self.GPIO:
            try:
                self.GPIO.setmode(self.GPIO.BCM)
                self.GPIO.setwarnings(False)
                self.GPIO.setup(self.RST_PIN, self.GPIO.OUT)
                self.GPIO.setup(self.DC_PIN, self.GPIO.OUT)
                self.GPIO.setup(self.CS_PIN, self.GPIO.OUT)
                self.GPIO.setup(self.BUSY_PIN, self.GPIO.IN)
                success = True
            except Exception as e:
                logging.warning(f"RPi.GPIO initialization failed: {e}. Trying lgpio fallback...")
                # We don't return here, we try lgpio if success is False

        if not success and self.lgpio:
            try:
                # Open gpiochip 0 (default for Pi 3/4/0) or 4 (Pi 5)
                for chip_idx in [0, 4]:
                    try:
                        self.chip = self.lgpio.gpiochip_open(chip_idx)
                        break
                    except:
                        continue
                
                if self.chip is None:
                    raise RuntimeError("Could not open any lgpio chip")
                
                self.lgpio.gpio_claim_output(self.chip, self.RST_PIN)
                self.lgpio.gpio_claim_output(self.chip, self.DC_PIN)
                self.lgpio.gpio_claim_output(self.chip, self.CS_PIN)
                self.lgpio.gpio_claim_input(self.chip, self.BUSY_PIN)
                success = True
                logging.info(f"lgpio initialized on chip {self.chip}")
            except Exception as e:
                logging.error(f"lgpio initialization failed: {e}")
                return -1

        if not success:
            logging.error("No GPIO backend could be initialized!")
            return -1

        # SPI device, bus = 1, device = 0
        try:
            self.SPI.open(1, 0)
            self.SPI.max_speed_hz = 4000000
            self.SPI.mode = 0b00
        except Exception as e:
            logging.error(f"SPI initialization failed: {e}")
            return -1
            
        return 0

    def module_exit(self):
        logging.debug("spi end")
        self.SPI.close()

        logging.debug("close 5V, Module enters 0 power consumption ...")
        try:
            self.digital_write(self.RST_PIN, 0)
            self.digital_write(self.DC_PIN, 0)
        except:
            pass

        if self.chip is not None and self.lgpio:
            self.lgpio.gpiochip_close(self.chip)
            self.chip = None
        elif self.GPIO:
            self.GPIO.cleanup()


class JetsonNano:
    # Pin definition
    RST_PIN         = 17
    DC_PIN          = 25
    CS_PIN          = 8
    BUSY_PIN        = 24

    def __init__(self):
        import ctypes
        find_dirs = [
            os.path.dirname(os.path.realpath(__file__)),
            '/usr/local/lib',
            '/usr/lib',
        ]
        self.SPI = None
        for find_dir in find_dirs:
            so_filename = os.path.join(find_dir, 'sysfs_software_spi.so')
            if os.path.exists(so_filename):
                self.SPI = ctypes.cdll.LoadLibrary(so_filename)
                break
        if self.SPI is None:
            raise RuntimeError('Cannot find sysfs_software_spi.so')

        import Jetson.GPIO
        self.GPIO = Jetson.GPIO

    def digital_write(self, pin, value):
        self.GPIO.output(pin, value)

    def digital_read(self, pin):
        return self.GPIO.input(self.BUSY_PIN)

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.SPI.SYSFS_software_spi_transfer(data[0])

    def module_init(self):
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setwarnings(False)
        self.GPIO.setup(self.RST_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.DC_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.CS_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.BUSY_PIN, self.GPIO.IN)
        self.SPI.SYSFS_software_spi_begin()
        return 0

    def module_exit(self):
        logging.debug("spi end")
        self.SPI.SYSFS_software_spi_end()

        logging.debug("close 5V, Module enters 0 power consumption ...")
        self.GPIO.output(self.RST_PIN, 0)
        self.GPIO.output(self.DC_PIN, 0)

        self.GPIO.cleanup()


def _is_raspberry_pi():
    # Newer kernels/images may not expose the legacy gpiomem-bcm2835 path.
    if os.path.exists("/sys/bus/platform/drivers/gpiomem-bcm2835"):
        return True
    if os.path.exists("/dev/gpiomem"):
        return True
    model_path = "/proc/device-tree/model"
    if os.path.exists(model_path):
        try:
            with open(model_path, "rb") as model_file:
                model = model_file.read().decode("utf-8", errors="ignore").lower()
            return "raspberry pi" in model
        except Exception:
            pass
    return False


if _is_raspberry_pi():
    try:
        implementation = RaspberryPi()
    except Exception:
        # Fallback to Jetson backend only when Pi backend cannot be initialized.
        implementation = JetsonNano()
else:
    implementation = JetsonNano()

for func in [x for x in dir(implementation) if not x.startswith('_')]:
    setattr(sys.modules[__name__], func, getattr(implementation, func))


### END OF FILE ###
