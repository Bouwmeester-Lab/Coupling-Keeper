import time
import pyvisa
import logging
import matplotlib.pyplot as plt

# Configure the logger
log_format = '[FUNC GEN] %(asctime)s [%(levelname)s]: %(message)s'
log_time_format = '%Y-%m-%d %H:%M:%S'

# Set the log level (e.g., INFO, DEBUG, WARNING, ERROR)
log_level = logging.DEBUG

# Create a logger
logger = logging.getLogger('func_gen_logger')
logger.setLevel(log_level)

# Create a formatter with the custom time format
formatter = logging.Formatter(log_format, log_time_format)

# Create a StreamHandler to display log messages on the console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)

class AgilentFuncGen:
    def __init__(self, resource_name: str, DEBUG: bool = True) -> None:
        self.resource_name = resource_name
        self.DEBUG = DEBUG
        self.opened = False

    def open(self,) -> None:
        try:
            self.rm = pyvisa.ResourceManager()
            resources = self.rm.list_resources()
            for resource in resources:
                print(resource)

            assert self.resource_name in resources, f"WARNING: {resource_name} not found!"

            self.gen = self.rm.open_resource(self.resource_name)
        except Exception as e:
            logger.error(f"Error opening resource {self.resource_name}. {e}")

        
        self.gen.timeout = 10000 # ms
        self.gen.encoding = 'latin_1'
        self.gen.read_termination = '\n'
        self.gen.write_termination = None

        self.opened = True

    def set_channel_state(self, channel: int, state: str) -> None:
        assert channel in [1, 2], "channel must be 1 or 2"
        assert state.upper() in ["ON", "OFF"], "state must be in ON or OFF"
        
        self.write(f"C{channel}:OUTP {state.upper()}")

    def write_func(self, channel: int, _type: str, freq: int, ampl: float, offset: float, phase: float = 0.0, symmetry: float = 50) -> None:
        """
        freq: Hz
        ampl: V
        offset: V
        phase: degrees
        """
        assert ampl < 3.1, "VOLTAGE TOO HIGH, CHECK INPUTS"
        assert offset < 3.1-ampl, "VOLTAGE OFFSET TOO HIGH< CHECK INPUTS"

        self.write(f"SOUR{channel}:FUNC {_type}")
        self.write(f"SOUR{channel}:FREQ {freq}")
        self.write(f"SOUR{channel}:VOLT {ampl}")
        self.write(f"SOUR{channel}:VOLT:OFFS {offset}")
        self.write(f"SOUR{channel}:PHAS {phase}")
        if _type == 'RAMP':
            self.write(f'SOUR{channel}:FUNC:RAMP:SYMM 100')

        return
    
    def write_DC(self, channel : int, offset : float) -> None:
        """
        offset: V
        """

        assert offset < 3.1, "VOLTAGE TOO HIGH, CHECK INPUTS"

        self.write(f"SOUR{channel}:FUNC DC")
        self.write(f"SOUR{channel}:VOLT:OFFS {offset}")

        return


    # This function self.writes command codes to the instrument. 
    def write(self, command_code: str) -> None:
        try:
            if self.gen == None:
                self.gen = self.rm.open_resource(self.resource_name)
            if self.DEBUG:
                logger.info("self.write: " + command_code)
            
            self.gen.write(command_code)
        
        except Exception as e:
            logger.info("ERROR: Unable to open the USB communication link to the "\
            "Tektronix TDS2024B, make sure it is plugged in.")

    # This function self.reads the data stream returned by the instrument. 
    def read(self,):
        try:
            if self.gen == None:
                self.gen = self.rm.open_resource(self.resource_name)
            
            data = self.gen.read()
            
            if self.DEBUG:
                logger.info("self.read: " + data)
            
            return data
        except Exception as e:
            logger.info("ERROR: Unable to open the USB communication link to the "\
            "scope, make sure it is plugged in.")
            logger.error(e)

    # This function self.writes a command and self.reads the instrument's response.
    def query(self, command: str):
        self.write(command)
        return self.read()

if __name__ == "__main__":
    resource_name = 'USB0::0x0957::0x1607::MY50000804::INSTR'
 
    func_gen = AgilentFuncGen(resource_name, DEBUG = True)
    func_gen.open()

    channel = 1
    offset = .4 #V


    while offset < 3.0:
        func_gen.write_DC(channel, offset)

        offset += 0.1

        time.sleep(1)

    