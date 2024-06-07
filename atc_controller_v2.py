from AgilentFuncGen import AgilentFuncGen
from pyvisa import ResourceManager
from datetime import datetime
import time

func_gen = AgilentFuncGen('USB0::0x0957::0x1607::MY50000804::INSTR')
func_gen.open()

def move(func_gen : AgilentFuncGen,
         freq : float,
         amp : float,
         steps : int):
    
    start = datetime.now()
    func_gen.write_func(1, 'RAMP', freq, amp, amp/2, 180, symmetry=1)
    time.sleep(steps/freq + start - datetime.now())

    func_gen.write_DC(1, 0)

    return

freq = 20
amp = 1
steps = 5

move(func_gen, freq, amp, steps)

