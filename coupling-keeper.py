from pylablib.devices import Attocube
import numpy as np
import time
from pyvisa import ResourceManager, constants
import pandas as pd
from typing import Literal


class AgilentScope():
    def __init__(self, id : str):
        pass


class AttocubeController():
    def __init__(self):
        pass



class CouplingKeeper():
    def __init__(self, init_norm_factor : float,
                 dark_voltage : float,
                 norm_factor_threshold : float,
                 gct_max : float = 1.0,
                 fftmin_up : float = 0.8,
                 fftmin_down : float = 0.8,
                 no_light_avg : float = 0.1,
                 x_steps : int = 10,
                 z_steps : int = 10,
                 scope_id : str = '',
                 attocube_id : str = 'COM5',
                 x_channel : int = 2,
                 z_channel : int = 1):

        scope = AgilentScope(id = scope_id)

        atc = Attocube.ANC300(attocube_id)
        atc.update_available_axes()
        try: 
            atc.enable_axis(1) 
            atc.enable_axis(2)
        except:
            pass
        
        self.norm_factor_threshold = norm_factor_threshold
        self.gct_max = gct_max
        self.fftmin_up = fftmin_up
        self.fftmin_down = fftmin_down
        self.no_light_avg = no_light_avg
        self.dark_voltage = dark_voltage

        self.set_thresholds(init_norm_factor)

    def set_thresholds(self, norm_factor):
        norm_factor = norm_factor - self.dark_voltage
        norm_factor_threshold = norm_factor_threshold * norm_factor - self.dark_voltage
        gctmax = 1.0 * norm_factor + self.dark_voltage
        fftmin_down = .8 * norm_factor + self.dark_voltage
        fftmin_up = .8 * norm_factor + self.dark_voltage
        nolightavg = 0.1 * norm_factor + self.dark_voltage
        



    def drive_sample_down(rm : ResourceManager,
                      fftmin : float,
                      steps : int = -10):
    
        assert steps < 0, 'steps must be < 0'

        print('driving sample down')

        min = read_scopemin(rm)
        i = 0
        while min < fftmin: # coupled drive to uncoupled
            atc.move_by(1, steps=steps)
            min = read_scopemin(rm)
            i += 1

        return i * steps 