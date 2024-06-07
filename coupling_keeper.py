
from pylablib.devices import Attocube
import numpy as np
import time
from pyvisa import ResourceManager, constants
import pandas as pd


##############################################################################################
########################## define some useful functions ######################################
##############################################################################################


def read_scopemin(rm : ResourceManager):

    try:    

        with rm.open_resource('USB0::0x0957::0x179A::MY52491615::INSTR') as scope:
                
            scope.write(f':MEASure:VMIN?')
            time.sleep(11)
            min = float(scope.read())
            print(f'min: {min}')

        return min
    
    except Exception as e:
        print(e)
        scope.close()


def read_scopemax(rm : ResourceManager):
    try:    
        with rm.open_resource('USB0::0x0957::0x179A::MY52491615::INSTR') as scope:
                
            scope.write(f':MEASure:VMAX?')
            time.sleep(11)
            max = float(scope.read())
            print(f'max: {max}')

        return max 
    
    except Exception as e:
        print(e)
        scope.close()


def read_scopeavg(rm : ResourceManager):

    try:    
        with rm.open_resource('USB0::0x0957::0x179A::MY52491615::INSTR') as scope:    
            scope.write(f':MEASure:VAV?')
            time.sleep(11)
            avg = float(scope.read())
            print(f'avg: {avg}')

        return avg
    
    except Exception as e:
        print(e)
        scope.close()


def save_scope_data(rm : ResourceManager,
                    filename : str,
                    channel : int = 1):

    with rm.open_resource('USB0::0x0957::0x179A::MY52491615::INSTR') as scope:
        
        scope.write(f'waveform:source channel{channel}') #Establish format of data from oscilloscope
        scope.write('waveform:format ASCii')
        scope.write('waveform:points 2500')
        scope.write('digitize')

        scope.write('waveform:data?')
        time.sleep(11)
        data = scope.read()

        volt_array = np.array(data.split(','))

        xIncrement = float(scope.query('waveform:xincrement?')) 
        xOrigin = float(scope.query('waveform:xorigin?'))
        time_array = np.array([(t* xIncrement) +xOrigin for t in range(len(volt_array))])

        data = np.vstack( ([time_array], [volt_array]) )
        
    df = pd.DataFrame(data[:, 5:-5].T, columns=['time', f'channel {channel}'])
    df.to_csv(filename)  


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
        
def drive_sample_up(rm : ResourceManager,
                    fftmin : float,
                    steps : int = 10):
    
    assert steps > 0, 'steps must be > 0'

    print('driving sample up')

    min = read_scopemin(rm)
    i = 0
    while min > fftmin: # uncoupled drive to coupled
        atc.move_by(1, steps=steps)
        min = read_scopemin(rm)
        i += 1

    return i * steps
    

def drive_fiber_to_res(steps : int = 5):

    assert steps > 0, 'steps must be > 0'

    print('driving sample to res')
    atc.move_by(2, steps=steps)
    return steps


def drive_fiber_to_edge(steps : int = -5):
    
    assert steps < 0, 'steps must be < 0'

    print('driving sample to edge')
    atc.move_by(2, steps=steps)
    return steps

##############################################################################################
######################################### locking logic ######################################
##############################################################################################
rm = ResourceManager()
print(rm.list_resources())

#for resource in rm.list_resources():
#    print(resource)
#    try:
#        instr = rm.open_resource(resource)
#        print(instr.query('*IDN?'))
#    except Exception as e:
#        print(e)

#for i in range(15):
#    print(i)
#    try:
#        atc = Attocube.ANC300(f'COM{i}')
#    except Exception as e:
#        print(e)

atc = Attocube.ANC300('COM5')
atc.update_available_axes()
atc.enable_axis(1) 
atc.enable_axis(2)

rm = ResourceManager()
print(rm.list_resources())

dark_voltage = 25.57e-3
norm_factor = 882e-3 - dark_voltage
norm_factor_threshold = 800e-3 - dark_voltage
gctmax = 1.0 * norm_factor + dark_voltage     #good coupling threshhold for max on sweep|
fftmin_down = .8 * norm_factor + dark_voltage       #free fiber threshold for min
fftmin_up = .8 * norm_factor + dark_voltage
nolightavg = 0.1 * norm_factor + dark_voltage 

x_steps = 10
z_steps = 5

spectrum_metrics = pd.DataFrame({'time':[], 'min':[], 'avg':[], 'max':[], 'norm_factor':[]})

atc_moves = pd.DataFrame({'time':[], 'x':[], 'z':[]})

i=0
read_scopemin(rm)
read_scopeavg(rm)
read_scopemax(rm)
print(fftmin_down)
print(fftmin_up)
print(gctmax)
#drive_sample_down(rm, fftmin, steps=-2*z_steps)
#atc.move_by(1, steps=-5000)
#atc.get_frequency(1)
#atc.get_voltage(1)
#atc.set_frequency(1,2500)
##atc.move_by(1, steps=-5000)
#atc.stop(1)
#atc.set_frequency(1,413)#

#stpdwn=-8
#stpup=0
#stpedge=0
#stpdwn=stpdwn+drive_sample_down(rm, fftmin_down, steps=-z_steps)
#stpedge=stpedge+drive_fiber_to_edge(steps=-2*x_steps)
#print(stpedge)
#stpup=stpup+drive_sample_up(rm, fftmin_up, steps=z_steps)
#print(stpup)
#print(stpdwn)
#atc.move_by(1, steps=-100)

while True:
    
    i+=1
    gctmax = 1.0 * norm_factor + dark_voltage     #good coupling threshhold for max on sweep
    fftmin_down = .9 * norm_factor + dark_voltage       #free fiber threshold for min
    fftmin_up = .8 * norm_factor + dark_voltage
    nolightavg = 0.1 * norm_factor + dark_voltage 

    print(f'___{i}______________________________________________________________')
    print(f'fftmin_down: {fftmin_down}')
    print(f'fftmin_up: {fftmin_up}')
    print(f'gctmax: {gctmax}')
    if np.mod(i,5)==1:
        print(f'Sleeping for 60 minutes')
        time.sleep(10)
    min = read_scopemin(rm)
    avg = read_scopeavg(rm)
    max = read_scopemax(rm)

    spectrum_metrics = spectrum_metrics._append(pd.DataFrame({'time':[time.time()], 'min':[min], 'avg':[avg], 'max':[max], 'norm_factor':[norm_factor]}), ignore_index=True)

    spectrum_metrics.to_csv('data_cooldown_4/spectrum_metrics.csv')
    
    if max >= gctmax: # coupled
        stepsdown = drive_sample_down(rm, fftmin_down, steps=-1*z_steps)
        atc_moves = atc_moves._append(pd.DataFrame({'time':[time.time()], 'x':[0], 'z':[stepsdown]}), ignore_index=True)

        norm_factor = np.max([norm_factor_threshold, read_scopeavg(rm)-dark_voltage])

        stepstores = drive_fiber_to_res(steps=x_steps)
        atc_moves = atc_moves._append(pd.DataFrame({'time':[time.time()], 'x':[stepstores], 'z':[0]}), ignore_index=True)

        stepsup = drive_sample_up(rm, fftmin_up, steps=z_steps)
        atc_moves = atc_moves._append(pd.DataFrame({'time':[time.time()], 'x':[0], 'z':[stepsup]}), ignore_index=True)

        atc_moves.to_csv('data_cooldown_4/atc_moves.csv')
        time.sleep(1)

    elif max < gctmax: # bad coupling / on resonator
        stepsdown = drive_sample_down(rm, fftmin_down, steps=-1*z_steps)
        atc_moves = atc_moves._append(pd.DataFrame({'time':[time.time()], 'x':[0], 'z':[stepsdown]}), ignore_index=True)

        norm_factor = np.max([norm_factor_threshold, read_scopeavg(rm)-dark_voltage])

        stepstoedge = drive_fiber_to_edge(steps=-1*x_steps)
        atc_moves = atc_moves._append(pd.DataFrame({'time':[time.time()], 'x':[stepstoedge], 'z':[0]}), ignore_index=True)

        stepsup = drive_sample_up(rm, fftmin_up, steps=z_steps)
        atc_moves = atc_moves._append(pd.DataFrame({'time':[time.time()], 'x':[0], 'z':[stepsup]}), ignore_index=True)

        atc_moves.to_csv('data_cooldown_4/atc_moves.csv')
        time.sleep(1)
    
    elif avg < nolightavg:
        print("No light in transmission!")
        break

    elif KeyboardInterrupt():
        spectrum_metrics.to_csv('data_cooldown_4/spectrum_metrics.csv')
        break
        
atc.move_by(1, steps=-5000)
atc.get_frequency(1)
atc.get_voltage(1)
atc.set_frequency(2,3900)
atc.move_by(1, steps=5000)
atc.stop(1)
atc.set_frequency(1,413)

drive_sample_up(rm, fftmin, steps=100)
drive_sample_down(rm, fftmin, steps=-100)
atc.move_by(1, steps=5000)



atc.get_voltage(2)
atc.set_voltage(1,30)
drive_sample_up(rm, fftmin_up, steps=z_steps)


atc.set_frequency(1,4000)
atc.move_by(1, steps=100)

atc.set_frequency(1,4700)
atc.move_by(1, steps=-100)
atc.stop()

atc.set_frequency(2,50)
atc.set_voltage(2,70)

up_pattern = atc.get_voltage_pattern(1, "up")
print(up_pattern)



drive_fiber_to_res(steps=50)
drive_fiber_to_edge(steps=-50)

rm = ResourceManager()
print(rm.list_resources())
ANC150 = rm.open_resource('ASRL5::INSTR', write_termination='\n', read_termination='\n', baud_rate=38400, data_bits=8, parity=constants.Parity.none, stop_bits=constants.StopBits.one, flow_control=constants.VI_ASRL_FLOW_NONE)
print(ANC150.write_termination)
ANC150.write('ver')
print(ANC150.write('getf1'))
print(ANC150.read())