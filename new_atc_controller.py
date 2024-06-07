from pyvisa import ResourceManager, constants

rm = ResourceManager()
print(rm.list_resources())
ANC150 = rm.open_resource('ASRL5::INSTR', write_termination='\r\n', read_termination='\r\n', baud_rate=38400, data_bits=8, parity=constants.Parity.none, stop_bits=constants.StopBits.one, flow_control=constants.VI_ASRL_FLOW_NONE)
print(ANC150.write_termination)
ANC150.write('ver')
print(ANC150.read(encoding='utf-8'))
print(ANC150.write('setpu 1 4'))
print(ANC150.write('getpu 1'))
print(ANC150.read(encoding='ASCII'))

print(ANC150.write('setpd 1 3'))
print(ANC150.write('getpd 1'))
print(ANC150.read(encoding='ASCII'))