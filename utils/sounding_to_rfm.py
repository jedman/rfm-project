import netCDF4 as nc
import numpy as np
import sys


def ncvar_to_str(data, variable_name, unit_factor=1., separator=','):
  """convert netcdf variable to string for rfm input"""
  return np.array2string(unit_factor*data[variable_name][:],
                         separator=separator, precision=3,
                         max_line_width=80)[1:-1] + '\n'

def netcdf_atm_to_rfm(data, gases=None, filename='std.atm'):
  """convert netcdf data to rfm input atmosphere"""
  if gases is None:
      gases = ['H2O', 'CO2']
  nlev = len(data['z'][:])

  lines = []
  # required sections
  lines.append(str(nlev) +'\n' )
  lines.append('*HGT [km]\n')
  lines.append(ncvar_to_str(data, 'z', unit_factor=0.001))
  lines.append('*PRE [mb]\n')
  lines.append(ncvar_to_str(data, 'p', unit_factor=0.01))
  lines.append('*TEM [K]\n')
  lines.append(ncvar_to_str(data, 'tabs'))

  # optional gases
  for gas in gases:
      lines.append('*' + gas+ ' [ppmv] \n')
      lines.append(ncvar_to_str(data, gas + '_ppm'))
  lines.append('*END')
  with open(filename, 'w') as f:
      f.writelines(lines)
  return

if __name__=='__main__':
  try:
    input_sounding = sys.argv[1]
    output_atm = sys.argv[2]
    output_lev = sys.argv[3]
  except IndexError:
    print('Usage: input sounding, output atm file, output level file')
    exit()

  data = nc.Dataset(input_sounding)
  netcdf_atm_to_rfm(data, filename=output_atm)
  outlevs = data['z'][:]/1000. # convert to km
  outlevs.tofile(open(output_lev, 'w'), sep='\n')
