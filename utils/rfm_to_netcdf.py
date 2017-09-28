import numpy as np
import netCDF4 as nc
import os, sys

def parse_rfm_line(line, sep='  ', **kwargs):
  """return a numpy array from a line in an rfm file"""
  return np.fromstring(line,dtype=np.float, sep=sep)

def get_rfm_data(outdir, prefix='rad', filename=None):
  """:param outdir: directory with rfm files
     :param prefix: output file prefix (rad for radiances)
     :param filename: if not none, gets data from a single ile
     returns wavenumber range, levels, and upward and downward data as
     numpy arrays"""

  downvals = []
  upvals = []
  othervals = []
  levels = set()

  if filename is not None:
      filenames = [filename]
  else:
      filenames = [file for file in os.listdir(outdir) if file.startswith(prefix)]

  for file in filenames:
      with open(outdir + file, 'r') as f:
          lines = [i.rstrip('\n') for i in f.readlines()]
          lev = float(file[-9:-4]) # trim .asc off the end
          levels.add(lev)
      if [_ for _ in file.split('_') if _.startswith('down')]:
          downvals.append(parse_rfm_line(lines[4]))
      elif [_ for _ in file.split('_') if _.startswith('up')]:
          upvals.append(parse_rfm_line(lines[4]))
      else:
          range_info = lines[3].split(' ')
          blah = list(filter(None, range_info)) # remove empty strings
          ndv, vmin, dv, vmax = list(filter(lambda x: x[0].isdigit(), blah))
          dvs = np.linspace(float(vmin), float(vmax), int(ndv))
          othervals.append(parse_rfm_line(lines[4]))

  return dvs, np.array(sorted(list(levels))), np.array(upvals), np.array(downvals)

def get_cooling_rate(uprad, downrad, levels):
    """computes spectral cooling rate from upward radiance, downward radiance,
     and levels"""
    net = uprad - downrad
    levels_mesh = np.tile(levels, (uprad.shape[1],1))
    # use numpy centered differences
    return np.gradient(net, axis = 0)/np.gradient(levels_mesh.transpose(), axis = 0)

if __name__=='__main__':
  import netcdf_helper

  try:
    outdir = sys.argv[1] # where to find the rfm output
    prefix = sys.argv[2] # prefix for rfm files
    ncout = sys.argv[3] #
  except IndexError:
    print('Usage: rfm out directory, file prefix, nc out directory')
    exit()

  print('making netCDF file from {}{}* at {}'.format(outdir, prefix, ncout))

  dvs, levels, uprad, downrad = get_rfm_data(outdir, prefix=prefix)
  cooling_rate = get_cooling_rate(uprad, downrad, levels)

  # define netCDF dimensions
  ncWAV = netcdf_helper.ncdim('wavenumber')
  ncWAV.units = '1/cm'
  ncZ = netcdf_helper.ncdim('z')
  ncZ.units = 'm'
  ncWAV.data = dvs
  ncZ.data = levels
  ncdims = {'wavenumber': ncWAV, 'z': ncZ}

  # define netCDF variables
  ncUP = netcdf_helper.ncvar('uprad')
  ncUP.units = 'W/m^2 cm'
  ncUP.data = uprad
  ncUP.add_dims([ 'z', 'wavenumber'])
  ncDOWN = netcdf_helper.ncvar('downrad')
  ncDOWN.units = 'W/m^2 cm'
  ncDOWN.data = downrad
  ncDOWN.add_dims(['z','wavenumber'])
  ncCOOL = netcdf_helper.ncvar('cooling rate')
  ncCOOL.units = 'W/m^3 cm'
  ncCOOL.data = cooling_rate
  ncCOOL.add_dims(['z','wavenumber'])
  ncvars = {ncUP.name: ncUP, ncDOWN.name: ncDOWN, ncCOOL.name: ncCOOL}

  # write netcdf file
  netcdf_helper.create_netcdf(ncout, ncvars, ncdims)
