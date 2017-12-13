import numpy as np
# constants
g = 9.81
Rair = 287.
Rwater = Rair/0.622


def make_tgrid(zgrid, gamma, Tsurf, Tstrat):
    """make temperature grid given lapse rate (gamma) and surface and
    isothermal stratosphere temperatures"""
    tlist = list()
    for i, z in enumerate(zgrid):
        if i == 0:
            tlist.append(Tsurf)
        else:
            tnext = tlist[i-1] - gamma*(zgrid[i] - zgrid[i-1])/1000.
            if tnext < Tstrat:
                tlist.append(Tstrat)
            else:
                tlist.append(tnext)
    return np.array(tlist)


def make_hydrostatic(zgrid, tabs, Psurf):
    """make hydrostatically-balanced pressure profile given a
    temperature profile,  and surface pressure. Could be extended to
     include water vapor"""
    plist = list()
    for i, t in enumerate(tabs):
        if i == 0:
            plist.append(Psurf)
        else:
            R = Rair
            plist.append(plist[i-1] + -g/(R*t)*plist[i-1]*(zgrid[i] - zgrid[i-1]))
    return np.array(plist)


if __name__=='__main__':
  import netcdf_helper
  import sys
  #  do this in a configuration yaml instead
  ncout = sys.argv[1] # output file
  Psurf = 1.e5
  Tsurf = 300.
  Tstrat = 180.

  CO2s = [100, 110, 200, 220,  400, 440, 800, 1600]
  gammas = [3, 6, 12]

  zgrid = np.linspace(0. ,50000., 501)  # dz = 100

  for gamma in gammas:
    for CO2_ppm in CO2s:
      ncout_name = ncout + '_' + str(CO2_ppm) + 'ppm_' +  str(gamma) + '.nc'
      ncZ = netcdf_helper.ncdim('z')
      ncZ.units = 'm'
      ncZ.data = zgrid
      ncdims = {'z': ncZ}

      # variables: p, tabs, CO2_ppm
      ncP = netcdf_helper.ncvar('p')
      ncTABS = netcdf_helper.ncvar('tabs')
      ncCO2 = netcdf_helper.ncvar('CO2_ppm')
      ncH2O = netcdf_helper.ncvar('H2O_ppm')

      ncP.units = 'Pa'
      ncTABS.units = 'K'
      ncCO2.units = 'CO2 parts per million by volume'
      ncH2O.units = 'H2O parts per million by volume'


      ncP.add_dims('z')
      ncTABS.add_dims('z')
      ncCO2.add_dims('z')
      ncH2O.add_dims('z')


      ncCO2.data = np.full(len(zgrid), CO2_ppm)
      ncH2O.data = np.zeros(len(zgrid))
      ncTABS.data = make_tgrid(zgrid, gamma, Tsurf, Tstrat)
      ncP.data = make_hydrostatic(zgrid, make_tgrid(zgrid, gamma, Tsurf, Tstrat), Psurf)

      ncvars ={ncP.name: ncP, ncTABS.name: ncTABS, ncCO2.name: ncCO2, ncH2O.name: ncH2O}
      netcdf_helper.create_netcdf(ncout_name, ncvars, ncdims)
