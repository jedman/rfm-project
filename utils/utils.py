import netCDF4 as nc

def optical_depth_height(path_to_netcdf, opt_variable='upopt', tau=1.):
  """path_to_netcdf, containing optical depth variable 'opt_variable'
  returns the height at a given optical depth tau"""
  data = nc.Dataset(path_to_netcdf)
  tau = data[opt_variable][:]
  z = data['z'][:]
  t1height = []
  decreasing = True
  # check if optical depth is increasing or decreasing
  if tau.transpose()[0][1] - tau.transpose()[0][0] > 0.:
    decreasing = False
  for i, t in enumerate(tau.transpose()):
      for j, opt in enumerate(t):
        if decreasing:
          # record first tau <= 1
          if opt <= 1.:
              t1height.append(z[j])
              t1index.append(j)
              break
        else:
          # increasing, so record first tau >= 1
          if opt >= 1.:
              t1height.append(z[j])
              t1index.append(j)
              break
  return t1height
