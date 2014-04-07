from netCDF4 import Dataset, datetime, timedelta
from netcdftime import utime
import numpy as np
import interp2D
import interpolation as interp
import IOwrite
from mpl_toolkits.basemap import addcyclic

import date
import grd
import barotropic
import IOinitial
import IOsubset

__author__ = 'Trond Kristiansen'
__email__ = 'trond.kristiansen@imr.no'
__created__ = datetime(2008, 8, 15)
__modified__ = datetime(2010, 1, 7)
__version__ = "1.5"
__status__ = "Development, modified on 15.08.2008,01.10.2009,07.01.2010"


def VerticalInterpolation(myvar, array1, array2, grdROMS, grdMODEL):
    outINDEX_ST = (grdROMS.Nlevels, grdROMS.eta_rho, grdROMS.xi_rho)
    outINDEX_U = (grdROMS.Nlevels, grdROMS.eta_u, grdROMS.xi_u)
    outINDEX_UBAR = (grdROMS.eta_u, grdROMS.xi_u)
    outINDEX_V = (grdROMS.Nlevels, grdROMS.eta_v, grdROMS.xi_v)
    outINDEX_VBAR = (grdROMS.eta_v, grdROMS.xi_v)

    if myvar in ['salinity', 'temperature']:
        print 'Start vertical interpolation for %s (dimensions=%s x %s)' % (myvar, grdROMS.xi_rho, grdROMS.eta_rho)
        outdata = np.zeros((outINDEX_ST), dtype=np.float64, order='Fortran')

        outdata = interp.interpolation.dovertinter(np.asarray(outdata, order='Fortran'),
                                                   np.asarray(array1, order='Fortran'),
                                                   np.asarray(grdROMS.depth, order='Fortran'),
                                                   np.asarray(grdROMS.z_r, order='Fortran'),
                                                   np.asarray(grdMODEL.z_r, order='Fortran'),
                                                   int(grdROMS.Nlevels),
                                                   int(grdMODEL.Nlevels),
                                                   int(grdROMS.xi_rho),
                                                   int(grdROMS.eta_rho),
                                                   int(grdROMS.xi_rho),
                                                   int(grdROMS.eta_rho))

        outdata = np.ma.masked_where(abs(outdata) > 1000, outdata)


        #import plotData
        #for k in range(grdROMS.Nlevels):
        #plotData.contourMap(grdROMS, grdROMS.lon_rho, grdROMS.lat_rho, np.squeeze(outdata[34,:,:]),34, myvar)


        return outdata

    if myvar == 'vvel':
        print 'Start vertical interpolation for uvel (dimensions=%s x %s)' % (grdROMS.xi_u, grdROMS.eta_u)
        outdataU = np.zeros((outINDEX_U), dtype=np.float64)
        outdataUBAR = np.zeros((outINDEX_UBAR), dtype=np.float64)

        outdataU = interp.interpolation.dovertinter(np.asarray(outdataU, order='Fortran'),
                                                    np.asarray(array1, order='Fortran'),
                                                    np.asarray(grdROMS.depth, order='Fortran'),
                                                    np.asarray(grdROMS.z_r, order='Fortran'),
                                                    np.asarray(grdMODEL.z_r, order='Fortran'),
                                                    int(grdROMS.Nlevels),
                                                    int(grdMODEL.Nlevels),
                                                    int(grdROMS.xi_u),
                                                    int(grdROMS.eta_u),
                                                    int(grdROMS.xi_rho),
                                                    int(grdROMS.eta_rho))

        outdataU = np.ma.masked_where(abs(outdataU) > 1000, outdataU)

        print 'Start vertical interpolation for vvel (dimensions=%s x %s)' % (grdROMS.xi_v, grdROMS.eta_v)
        outdataV = np.zeros((outINDEX_V), dtype=np.float64)
        outdataVBAR = np.zeros((outINDEX_VBAR), dtype=np.float64)

        outdataV = interp.interpolation.dovertinter(np.asarray(outdataV, order='Fortran'),
                                                    np.asarray(array2, order='Fortran'),
                                                    np.asarray(grdROMS.depth, order='Fortran'),
                                                    np.asarray(grdROMS.z_r, order='Fortran'),
                                                    np.asarray(grdMODEL.z_r, order='Fortran'),
                                                    int(grdROMS.Nlevels),
                                                    int(grdMODEL.Nlevels),
                                                    int(grdROMS.xi_v),
                                                    int(grdROMS.eta_v),
                                                    int(grdROMS.xi_rho),
                                                    int(grdROMS.eta_rho))

        outdataV = np.ma.masked_where(abs(outdataV) > 1000, outdataV)

        z_wu = np.zeros((grdROMS.Nlevels + 1, grdROMS.eta_u, grdROMS.xi_u), dtype=np.float64)
        z_wv = np.zeros((grdROMS.Nlevels + 1, grdROMS.eta_v, grdROMS.xi_v), dtype=np.float64)

        outdataUBAR = barotropic.velocity.ubar(np.asarray(outdataU, order='Fortran'),
                                               np.asarray(outdataUBAR, order='Fortran'),
                                               np.asarray(grdROMS.z_w, order='Fortran'),
                                               np.asarray(z_wu, order='Fortran'),
                                               grdROMS.Nlevels,
                                               grdROMS.xi_u,
                                               grdROMS.eta_u,
                                               grdROMS.xi_rho,
                                               grdROMS.eta_rho)
        outdataUBAR = np.ma.masked_where(abs(outdataUBAR) > 1000, outdataUBAR)

        #plotData.contourMap(grdROMS, grdROMS.lon_rho, grdROMS.lat_rho, outdataUBAR,1, "ubar")



        outdataVBAR = barotropic.velocity.vbar(np.asarray(outdataV, order='Fortran'),
                                               np.asarray(outdataVBAR, order='Fortran'),
                                               np.asarray(grdROMS.z_w, order='Fortran'),
                                               np.asarray(z_wv, order='Fortran'),
                                               grdROMS.Nlevels,
                                               grdROMS.xi_v,
                                               grdROMS.eta_v,
                                               grdROMS.xi_rho,
                                               grdROMS.eta_rho)

        #plotData.contourMap(grdROMS, grdROMS.lon_rho, grdROMS.lat_rho, outdataVBAR,1, "vbar")
        outdataVBAR = np.ma.masked_where(abs(outdataVBAR) > 1000, outdataVBAR)

        return outdataU, outdataV, outdataUBAR, outdataVBAR


def HorizontalInterpolation(myvar, grdROMS, grdMODEL, data, show_progress):
    print 'Start %s horizontal interpolation for %s' % (grdMODEL.grdType, myvar)

    if grdMODEL.grdType == 'regular':
        if myvar in ['temperature', 'salinity']:
            array1 = interp2D.doHorInterpolationRegularGrid(myvar, grdROMS, grdMODEL, data, show_progress)
        if myvar in ['ssh', 'ageice', 'uice', 'sim', 'sim2', 'vice', 'iceconcentration', 'icethickness', 'snowdepth']:
            array1 = interp2D.doHorInterpolationSSHRegularGrid(myvar, grdROMS, grdMODEL, data)
        if myvar in ['uvel', 'vvel']:
            array1 = interp2D.doHorInterpolationRegularGrid(myvar, grdROMS, grdMODEL, data, show_progress)

    if grdMODEL.grdType == 'irregular':
        if myvar == 'temperature':
            interp2D.doHorInterpolationIrregularGrid(myvar, grdROMS, grdMODEL, data)
        if myvar == 'salinity':
            interp2D.doHorInterpolationIrregularGrid(myvar, grdROMS, grdMODEL, data)
        if myvar == 'ssh':
            interp2D.doHorInterpolationSSHIrregularGrid(myvar, grdROMS, grdMODEL, data)
        if myvar == 'uvel':
            interp2D.doHorInterpolationIrregularGrid('uvel', grdROMS, grdMODEL, data)
        if myvar == 'vvel':
            interp2D.doHorInterpolationIrregularGrid('vvel', grdROMS, grdMODEL, data)

    return array1


def rotate(grdROMS, grdMODEL, data, u, v):
    """
    First rotate the values of U, V at rho points with the angle, and then interpolate
    the rho point values to U and V points and save the result
    """

    urot = np.zeros((int(grdMODEL.Nlevels), int(grdROMS.eta_rho), int(grdROMS.xi_rho)), np.float64)
    vrot = np.zeros((int(grdMODEL.Nlevels), int(grdROMS.eta_rho), int(grdROMS.xi_rho)), np.float64)

    urot, vrot = interp.interpolation.rotate(np.asarray(urot, order='Fortran'),
                                             np.asarray(vrot, order='Fortran'),
                                             np.asarray(u, order='Fortran'),
                                             np.asarray(v, order='Fortran'),
                                             np.asarray(grdROMS.angle, order='Fortran'),
                                             int(grdROMS.xi_rho),
                                             int(grdROMS.eta_rho),
                                             int(grdMODEL.Nlevels))
    return urot, vrot


def interpolate2UV(grdROMS, grdMODEL, urot, vrot):
    Zu = np.zeros((int(grdMODEL.Nlevels), int(grdROMS.eta_u), int(grdROMS.xi_u)), np.float64)
    Zv = np.zeros((int(grdMODEL.Nlevels), int(grdROMS.eta_v), int(grdROMS.xi_v)), np.float64)

    # Interpolate from RHO points to U and V points for velocities

    Zu = interp.interpolation.rho2u(np.asarray(Zu, order='Fortran'),
                                    np.asarray(urot, order='Fortran'),
                                    int(grdROMS.xi_rho),
                                    int(grdROMS.eta_rho),
                                    int(grdMODEL.Nlevels))


    #plotData.contourMap(grdROMS,grdMODEL,Zu[0,:,:],"1",'urot')

    Zv = interp.interpolation.rho2v(np.asarray(Zv, order='Fortran'),
                                    np.asarray(vrot, order='Fortran'),
                                    int(grdROMS.xi_rho),
                                    int(grdROMS.eta_rho),
                                    int(grdMODEL.Nlevels))


    #plotData.contourMap(grdROMS,grdMODEL,Zv[0,:,:],"1",'vrot')

    return Zu, Zv


def getTime(cdf, grdROMS, grdMODEL, year, ID, mytime, mytype):
    """
    Create a date object to keep track of Julian dates etc.
    Also create a reference date starting at 1948/01/01.
    Go here to check results:http://lena.gsfc.nasa.gov/lenaDEV/html/doy_conv.html
    """
    ref_date = date.Date()
    ref_date.day = 1
    ref_date.month = 1
    ref_date.year = 1948
    jdref = ref_date.ToJDNumber()

    if mytype == 'SODA':

        # Find the day and month that the SODA file respresents based on the year and ID number.
        # Each SODA file represents a 5 day average, therefore we let the date we find be the first day
        # of those 5 days. Thats the reason we subtract 4 below for day of month.

        days = 0.0;
        month = 1;
        loop = True

        while loop is True:

            d = date.NumberDaysMonth(month, year)
            if days + d < int(ID) * 5:
                days = days + d
                month += 1
            else:
                day = int(int(ID) * 5 - days)
                loop = False

        soda_date = date.Date()
        soda_date.day = day
        soda_date.month = month
        soda_date.year = year
        jdsoda = soda_date.ToJDNumber()

        grdROMS.time = (jdsoda - jdref)
        grdROMS.reftime = jdref

        print '\nCurrent time of SODA file : %s/%s/%s' % (soda_date.year, soda_date.month, soda_date.day)

    if mytype == 'SODAMONTHLY':
        # Find the day and month that the SODAMONTHLY file respresents based on the year and ID number.
        # Each SODA file represents a 1 month average.

        month = ID
        day = 15

        soda_date = date.Date()
        soda_date.day = day
        soda_date.month = month
        soda_date.year = year
        jdsoda = soda_date.ToJDNumber()

        grdROMS.time = (jdsoda - jdref)
        grdROMS.reftime = jdref

        print '\nCurrent time of SODAMONTHLY file : %s/%s/%s' % (soda_date.year, soda_date.month, soda_date.day)

    if mytype == 'GLORYS2V1':
        # Find the day and month that the SODAMONTHLY file respresents based on the year and ID number.
        # Each SODA file represents a 1 month average.

        month = ID
        day = 15

        glorys_date = date.Date()
        glorys_date.day = day
        glorys_date.month = month
        glorys_date.year = year
        jdglorys = glorys_date.ToJDNumber()

        grdROMS.time = (jdglorys - jdref)
        grdROMS.reftime = jdref

        print '\nCurrent time of GLORYS2V1 file : %s/%s/%s' % (glorys_date.year, glorys_date.month, glorys_date.day)

    if mytype == 'NORESM':
        # Find the day and month that the NORESM file. We need to use the time modules from
        # netcdf4 for python as they handle calendars that are no_leap.
        # http://www.esrl.noaa.gov/psd/people/jeffrey.s.whitaker/python/netcdftime.html#datetime
        mydays = cdf.variables["time"][mytime]
        mycalendar = cdf.variables["time"].calendar
        refdateP = cdf.variables["time"].units
        refdate = utime(refdateP, calendar=mycalendar)
        currentdate = refdate.num2date(mydays)

        noresm_date = date.Date()
        noresm_date.day = currentdate.day
        noresm_date.month = currentdate.month
        noresm_date.year = currentdate.year
        jdnoresm = noresm_date.ToJDNumber()

        grdROMS.time = (jdnoresm - jdref)
        grdROMS.reftime = jdref

        print '\nCurrent time of NORESM file : %s/%s/%s' % (noresm_date.year, noresm_date.month, noresm_date.day)


def getGLORYS2V1filename(year, ID, myvar, dataPath):
    # Month indicates month
    # myvar:S,T,U,V
    if ID < 10: filename = dataPath + 'global-reanalysis-phys-001-009-ran-fr-glorys2-grid' + str(
        myvar.lower()) + '/REGRID/GLORYS2V1_ORCA025_' + str(year) + '0' + str(ID) + '15_R20110216_grid' + str(
        myvar.upper()) + '_regrid.nc'
    if ID >= 10: filename = dataPath + 'global-reanalysis-phys-001-009-ran-fr-glorys2-grid' + str(
        myvar.lower()) + '/REGRID/GLORYS2V1_ORCA025_' + str(year) + str(ID) + '15_R20110216_grid' + str(
        myvar.upper()) + '_regrid.nc'

    return filename


def getNORESMfilename(year, ID, myvar, dataPath):
    if myvar in ["thetao", "so", "uo", "vo"]:
        # 3D variables
        filename = dataPath + str(myvar.lower()) + '_Omon_NorESM1-M_rcp85_r1i1p1_200601-200912_rectangular.nc'
    else:
        # 2D variables
        filename = dataPath + str(myvar.lower()) + '_Omon_NorESM1-M_rcp85_r1i1p1_200601-210012_rectangular.nc'

    return filename

def getSODAMONTHLYfilename(year, ID, myvar, dataPath):

    if ID < 10: filename = dataPath + 'SODA_2.0.2_' + str(year) + '0' + str(ID) + '.cdf'
    if ID >= 10: filename = dataPath + 'SODA_2.0.2_' + str(year) + str(ID) + '.cdf'

    return filename

def getSODAfilename(year, ID, myvar, dataPath):

    file = "SODA_2.0.2_" + str(year) + "_" + str(ID) + ".cdf"

    return dataPath + file

def getWOAMONTHLYfilename(year, ID, myvar, dataPath):

    if myvar == "temperature":
        filename = dataPath + 'temperature_monthly_1deg.nc'
    elif myvar == "salinity":
        filename = dataPath + 'salinity_monthly_1deg.nc'
    else:
        print "Could not find any input files in folder: %s"%(datapath)

    return filename

def get3Ddata(grdROMS, grdMODEL, myvar, mytype, year, ID, varNames, dataPath):

    # All variables for all time are now stored in arrays. Now, start the interpolation to the
    # new grid for all variables and then finally write results to file.
    indexROMS_S_U = (grdROMS.Nlevels, grdROMS.eta_u, grdROMS.xi_u)
    indexROMS_S_V = (grdROMS.Nlevels, grdROMS.eta_v, grdROMS.xi_v)
    indexROMS_S_ST = (grdROMS.Nlevels, grdROMS.eta_rho, grdROMS.xi_rho)

    if myvar == 'temperature': varN = 0; STdata = np.zeros((indexROMS_S_ST), dtype=np.float64)
    if myvar == 'salinity':    varN = 1; STdata = np.zeros((indexROMS_S_ST), dtype=np.float64)
    if myvar == 'uvel':        varN = 3; Udata = np.zeros((indexROMS_S_U), dtype=np.float64)
    if myvar == 'vvel':        varN = 4; Vdata = np.zeros((indexROMS_S_V), dtype=np.float64)

    # The variable splitExtract is defined in IOsubset.py and depends on the orientation
    # and mytype of grid (-180-180 or 0-360). Assumes regular grid.
    if grdMODEL.splitExtract is True:
        if mytype == "SODA":

            filename = getSODAfilename(year, ID, None, dataPath)
            cdf = Dataset(filename)

            data1 = cdf.variables[varNames[varN]][0, :,
                    int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                    int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])]
            data2 = cdf.variables[varNames[varN]][0, :,
                    int(grdMODEL.indices[1, 2]):int(grdMODEL.indices[1, 3]),
                    int(grdMODEL.indices[1, 0]):int(grdMODEL.indices[1, 1])]

        if mytype == "SODAMONTHLY":

            filename = getSODAMONTHLYfilename(year, ID, None, dataPath)
            cdf = Dataset(filename)

            data1 = cdf.variables[str(varNames[varN])][:,
                    int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                    int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])]
            data2 = cdf.variables[str(varNames[varN])][:,
                    int(grdMODEL.indices[1, 2]):int(grdMODEL.indices[1, 3]),
                    int(grdMODEL.indices[1, 0]):int(grdMODEL.indices[1, 1])]

        if mytype in ["WOAMONTHLY"]:

            filename = getWOAMONTHLYfilename(year, ID, myvar, dataPath)
            cdf = Dataset(filename)

            data1 = cdf.variables[str(varNames[varN])][ID - 1, :,
                    int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                    int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])]
            data2 = cdf.variables[str(varNames[varN])][ID - 1, :,
                    int(grdMODEL.indices[1, 2]):int(grdMODEL.indices[1, 3]),
                    int(grdMODEL.indices[1, 0]):int(grdMODEL.indices[1, 1])]

        if mytype == "GLORYS2V1":
            if myvar == 'temperature':
                cdf = Dataset(getGLORYS2V1filename(year, ID, 'T', dataPath))
                myunits = cdf.variables[str(varNames[varN])].units

            if myvar == 'salinity': cdf = Dataset(getGLORYS2V1filename(year, ID, 'S', dataPath))
            if myvar == 'uvel': cdf = Dataset(getGLORYS2V1filename(year, ID, 'U', dataPath))
            if myvar == 'vvel': cdf = Dataset(getGLORYS2V1filename(year, ID, 'V', dataPath))

            data1 = np.squeeze(cdf.variables[str(varNames[varN])][0, :,
                               int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                               int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])])
            data2 = np.squeeze(cdf.variables[str(varNames[varN])][0, :,
                               int(grdMODEL.indices[1, 2]):int(grdMODEL.indices[1, 3]),
                               int(grdMODEL.indices[1, 0]):int(grdMODEL.indices[1, 1])])

        if mytype == "NORESM":
            cdf = Dataset(getNORESMfilename(year, ID, varNames[varN], dataPath))
            myunits = cdf.variables[str(varNames[varN])].units

            data1 = np.squeeze(cdf.variables[str(varNames[varN])][0, :,
                               int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                               int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])])
            data2 = np.squeeze(cdf.variables[str(varNames[varN])][0, :,
                               int(grdMODEL.indices[1, 2]):int(grdMODEL.indices[1, 3]),
                               int(grdMODEL.indices[1, 0]):int(grdMODEL.indices[1, 1])])

        cdf.close()

        data = np.concatenate((data1, data2), axis=2)

    else:
        if mytype == "SODA":
            filename = getSODAfilename(year, ID, None, dataPath)
            cdf = Dataset(filename)

            data = cdf.variables[str(varNames[varN])][0, :,
                   int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                   int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])]

        if mytype == "SODAMONTHLY":
            filename = getSODAMONTHLYfilename(year, ID, None, dataPath)
            cdf = Dataset(filename)

            data = cdf.variables[str(varNames[varN])][:,
                   int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                   int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])]

        if mytype == "WOAMONTHLY":
            filename = getWOAMONTHLYfilename(year, ID, myvar, dataPath)
            cdf = Dataset(filename)

            data = cdf.variables[str(varNames[varN])][ID, :,
                   int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                   int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])]

        if mytype == "GLORYS2V1":
            if myvar == 'temperature':
                cdf = Dataset(getGLORYS2V1filename(year, ID, 'T', dataPath))

                myunits = cdf.variables[str(varNames[varN])].units
            if myvar == 'salinity': cdf = Dataset(getGLORYS2V1filename(year, ID, 'S', dataPath))
            if myvar == 'uvel': cdf = Dataset(getGLORYS2V1filename(year, ID, 'U', dataPath))
            if myvar == 'vvel': cdf = Dataset(getGLORYS2V1filename(year, ID, 'V', dataPath))

            data = np.squeeze(cdf.variables[str(varNames[varN])][0, :,
                              int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                              int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])])

        if mytype == "NORESM":
            cdf = Dataset(getNORESMfilename(year, ID, varNames[varN], dataPath))
            myunits = cdf.variables[str(varNames[varN])].units

            data = np.squeeze(cdf.variables[str(varNames[varN])][0, :,
                              int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                              int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])])
        cdf.close()

    if myvar == 'temperature' and mytype in ["GLORYS2V1", "NORESM"]:

        if myunits == "degree_Kelvin" or myunits == "K":
            if mytype in ["GLORYS2V1"]:
                data = np.where(data <= -32.767, grdROMS.fill_value, data)
            data = data - 273.15

        if time == 0 and myvar == myvars[0]:
            tmp = np.squeeze(data[0, :, :])
            #grdMODEL.mask = np.zeros(grdMODEL.lon.shape, dtype=np.float64)
            #grdMODEL.mask[:, :] = np.where(tmp == grdROMS.fill_value, 1, 0)

    if mytype == "GLORYS2V1":
        data = np.where(data <= -32.767, grdROMS.fill_value, data)
        data = np.ma.masked_where(data <= grdROMS.fill_value, data)


    if __debug__:
        print "Data range of %s just after extracting from netcdf file: %s - %s" % (str(varNames[varN]),
                                                                                    data.min(), data.max())

    return data

def get2Ddata(grdROMS, grdMODEL, myvar, mytype, year, ID, varNames, dataPath):

    indexROMS_SSH = (grdROMS.eta_rho, grdROMS.xi_rho)


    if myvar == 'ssh': varN = 2;  SSHdata = np.zeros((indexROMS_SSH), dtype=np.float64)
    if mytype == "NORESM":
        if myvar == 'ageice': varN = 0;  SSHdata = np.zeros((indexROMS_SSH), dtype=np.float64)
        if myvar == 'uice':   varN = 1;  SSHdata = np.zeros((indexROMS_SSH), dtype=np.float64)
        if myvar == 'sim':    varN = 2;  SSHdata = np.zeros((indexROMS_SSH), dtype=np.float64)
        if myvar == 'vice':   varN = 3;  SSHdata = np.zeros((indexROMS_SSH), dtype=np.float64)
        if myvar == 'sim2':   varN = 4;  SSHdata = np.zeros((indexROMS_SSH), dtype=np.float64)
        if myvar == 'iceconcentration': varN = 5;  SSHdata = np.zeros((indexROMS_SSH), dtype=np.float64)
        if myvar == 'icethickness':     varN = 6;  SSHdata = np.zeros((indexROMS_SSH), dtype=np.float64)
        if myvar == 'snowdepth':        varN = 7;  SSHdata = np.zeros((indexROMS_SSH), dtype=np.float64)

    if grdMODEL.splitExtract is True:
        if mytype == "SODA":
            filename = getSODAfilename(year, ID, None, dataPath)
            cdf = Dataset(filename)

            data1 = cdf.variables[varNames[varN]][0,
                    int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                    int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])]
            data2 = cdf.variables[varNames[varN]][0,
                    int(grdMODEL.indices[1, 2]):int(grdMODEL.indices[1, 3]),
                    int(grdMODEL.indices[1, 0]):int(grdMODEL.indices[1, 1])]

        if mytype == "SODAMONTHLY":
            filename = getSODAMONTHLYfilename(year, ID, None, dataPath)
            cdf = Dataset(filename)

            data1 = cdf.variables[str(varNames[varN])][
                    int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                    int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])]
            data2 = cdf.variables[str(varNames[varN])][
                    int(grdMODEL.indices[1, 2]):int(grdMODEL.indices[1, 3]),
                    int(grdMODEL.indices[1, 0]):int(grdMODEL.indices[1, 1])]

        if mytype == "GLORYS2V1":
            cdf = Dataset(getGLORYS2V1filename(year, ID, 'T', dataPath))

            data1 = np.squeeze(cdf.variables[str(varNames[varN])][0,
                               int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                               int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])])
            data2 = np.squeeze(cdf.variables[str(varNames[varN])][0,
                               int(grdMODEL.indices[1, 2]):int(grdMODEL.indices[1, 3]),
                               int(grdMODEL.indices[1, 0]):int(grdMODEL.indices[1, 1])])

        if mytype == "NORESM":
            cdf = Dataset(getNORESMfilename(year, ID, varNames[varN], dataPath))

            data1 = np.squeeze(cdf.variables[str(varNames[varN])][0,
                               int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                               int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])])
            data2 = np.squeeze(cdf.variables[str(varNames[varN])][0,
                               int(grdMODEL.indices[1, 2]):int(grdMODEL.indices[1, 3]),
                               int(grdMODEL.indices[1, 0]):int(grdMODEL.indices[1, 1])])

        cdf.close()
        data = np.concatenate((data1, data2), axis=1)

    else:
        if mytype == "SODA":
            filename = getSODAfilename(year, ID, None, dataPath)
            cdf = Dataset(filename)

            data = cdf.variables[str(varNames[varN])][0,
                   int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                   int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])]

        if mytype == "SODAMONTHLY":
            filename = getSODAMONTHLYfilename(year, ID, None, dataPath)
            cdf = Dataset(filename)

            data = cdf.variables[str(varNames[varN])][
                   int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                   int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])]

        if mytype == "GLORYS2V1":
            cdf = Dataset(getGLORYS2V1filename(year, ID, 'T', dataPath))

            data = np.squeeze(cdf.variables[str(varNames[varN])][0,
                          int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                          int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])])

        if mytype == "NORESM":
            cdf = Dataset(getNORESMfilename(year, ID, varNames[varN], dataPath))

            data = np.squeeze(cdf.variables[str(varNames[varN])][0,
                          int(grdMODEL.indices[0, 2]):int(grdMODEL.indices[0, 3]),
                          int(grdMODEL.indices[0, 0]):int(grdMODEL.indices[0, 1])])

        cdf.close()
        # data = np.where(abs(data) == grdMODEL.fill_value, grdROMS.fill_value, data)
        #data = np.ma.where(abs(data) > 1000, grdROMS.fill_value, data)

    if mytype == "GLORYS2V1":
            data = np.where(data <= -32.767, grdROMS.fill_value, data)
            data = np.ma.masked_where(data <= grdROMS.fill_value, data)

    if __debug__:
        print "Data range of %s just after extracting from netcdf file: %s - %s" % (str(varNames[varN]),
                                                                                    data.min(), data.max())

    return data


def convertMODEL2ROMS(years, IDS, climName, initName, dataPath, romsgridpath, myvars, show_progress, mytype, subset,
                      isClimatology, writeIce):
    """First opening of input file is just for initialization of grid"""

    if mytype == 'SODA':
        fileNameIn = dataPath + 'SODA_2.0.2_' + str(years[0]) + '_' + str(IDS[0]) + '.cdf'
    if mytype == 'SODAMONTHLY':
        fileNameIn = dataPath + 'SODA_2.0.2_' + str(years[0]) + '0' + str(IDS[0]) + '.cdf'
    if mytype == 'NORESM':
        fileNameIn = dataPath + 'thetao_Omon_NorESM1-M_rcp85_r1i1p1_200601-200912_rectangular.nc'

    if mytype == 'WOAMONTHLY':
        fileNameIn = dataPath + 'salinity_monthly_1deg.nc'

    if mytype == 'GLORYS2V1':
        fileNameIn = dataPath + 'global-reanalysis-phys-001-009-ran-fr-glorys2-grids/REGRID/GLORYS2V1_ORCA025_' + str(
            years[0]) + '0115_R20110216_gridS_regrid.nc'
    if mytype == 'HYCOM':
        fileNameIn = dataPath + 'archv.2003_307_00_3zt.nc'


    # First time in loop, get the essential old grid information
    # MODEL data already at Z-levels. No need to interpolate to fixed depths,
    # but we use the one we have
    grdMODEL = grd.grdClass(fileNameIn, mytype)
    grdROMS = grd.grdClass(romsgridpath, "ROMS")
    grdROMS.myvars = myvars

    # Now we want to subset the data to avoid storing more information than we need.
    # We do this by finding the indices of maximum and minimum latitude and longitude in the matrixes
    IOsubset.findSubsetIndices(grdMODEL, min_lat=subset[0], max_lat=subset[1], min_lon=subset[2], max_lon=subset[3])

    print 'Initializing done'
    print '\n--------------------------'

    time = 0
    firstRun = True
    for year in years:

        for ID in IDS:

            if mytype == 'SODA':
                filename = getSODAfilename(year, ID, None, dataPath)
                varNames = ['TEMP', 'SALT', 'SSH', 'U', 'V']

            if mytype == 'SODAMONTHLY':
                filename = getSODAMONTHLYfilename(year, ID, None, dataPath)
                varNames = ['temp', 'salt', 'ssh', 'u', 'v']

            if mytype == 'GLORYS2V1':
                filename = getGLORYS2V1filename(year, ID, "S", dataPath)
                varNames = ['votemper', 'vosaline', 'sossheig', 'vozocrtx', 'vomecrty']

            if mytype == 'WOAMONTHLY':
                filename = getWOAMONTHLYfilename(year, ID, "temperature", dataPath)
                varNames = ['t_an', 's_an']

            if mytype == 'NORESM':
                filename = getNORESMfilename(year, ID, "so", dataPath)
                writeIce = True
                varNames = ['thetao', 'so', 'zos', 'uo', 'vo', 'ageice', 'uice', 'vice', 'aice', 'hice', 'snd']
                varNames = ['ageice', 'transix', 'sim', 'transiy', 'sim', 'sic', 'sit', 'snd']

            # Now open the input file and get the time
            cdf = Dataset(filename)
            getTime(cdf, grdROMS, grdMODEL, year, ID, time, mytype)
            cdf.close()

            # Each MODEL file consist only of one time step. Get the subset data selected, and
            # store that time step in a new array:

            if firstRun is True:
                print "NOTICE!!: Make sure that these two arrays are in sequential order:"
                print "myvars:     %s" % (myvars)
                print "varnames: %s\n" % (varNames)
                firstRun = False

                # The first iteration we want to organize the subset indices we want to extract
                # from the input data to get the interpolation correct and to function fast
                IOsubset.organizeSplit(grdMODEL, grdROMS)

            for myvar in myvars:

                if myvar in ['temperature', 'salinity', 'uvel', 'vvel']:
                    data = get3Ddata(grdROMS, grdMODEL, myvar, mytype, year, ID, varNames, dataPath)

                if myvar in ['ssh', 'ageice', 'uice', 'sim', 'vice', 'sim2', 'iceconcentration', 'icethickness','snowdepth']:
                    data = get2Ddata(grdROMS, grdMODEL, myvar, mytype, year, ID, varNames, dataPath)

                    # if mytype=="NORESM":
                    #datacyclic, loncyclic = addcyclic(data, grdMODEL.lon[0,:])
                    #grdMODEL.lon, grdMODEL.lat = np.meshgrid(loncyclic,grdMODEL.lat[:,0])
                    #data=datacyclic

                # Take the input data and horizontally interpolate to your grid
                array1 = HorizontalInterpolation(myvar, grdROMS, grdMODEL, data, show_progress)

                if myvar in ['temperature', 'salinity']:
                    STdata = VerticalInterpolation(myvar, array1, array1, grdROMS, grdMODEL)
                    print "Data range of %s after interpolation: %3.3f to %3.3f" % (
                        myvar, STdata.min(), STdata.max())

                    for dd in xrange(len(STdata[:,0,0])):
                          STdata[dd,:,:] = np.where(grdROMS.mask_rho == 0, grdROMS.fill_value, STdata[dd,:,:])

                    STdata = np.where(abs(STdata) > 1000, grdROMS.fill_value, STdata)

                    IOwrite.writeClimFile(grdROMS, time, climName, myvar, isClimatology, writeIce, STdata)
                    if time == grdROMS.initTime and grdROMS.write_init is True:
                        IOinitial.createInitFile(grdROMS, time, initName, myvar, STdata)

                if myvar in ['ssh', 'ageice', 'iceconcentration', 'icethickness', 'snowdepth']:
                    SSHdata = array1[0, :, :]
                    print "Data range of %s after interpolation: %3.3f to %3.3f" % (
                        myvar, SSHdata.min(), SSHdata.max())

                    SSHdata = np.where(grdROMS.mask_rho == 0, grdROMS.fill_value, SSHdata)
                    SSHdata = np.where(abs(SSHdata) > 1000, grdROMS.fill_value, SSHdata)

                    IOwrite.writeClimFile(grdROMS, time, climName, myvar, isClimatology, writeIce, SSHdata)
                    if time == grdROMS.initTime:
                        IOinitial.createInitFile(grdROMS, time, initName, myvar, SSHdata)

                # The following are special routines used to calculate the u and v velocity
                # of ice based on the transport, which is divided by snow and ice thickenss
                # and then multiplied by grid size in dx or dy direction (opposite of transport).
                if myvar in ['uice', 'vice']:
                    array2 = array1

                if myvar in ['sim', 'sim2']:
                    if myvar == 'sim':
                        print "transix", array2.min(), array2.max()
                        print "sim", array1.min(), array1.max()

                        SSHdata = array2 / (array1) # * (1. / grdROMS.pm))
                        SSHdata = np.where(grdROMS.mask_u == 0, grdROMS.fill_value, SSHdata)
                       # SSHdata = np.where(abs(SSHdata) > 1000, grdROMS.fill_value, SSHdata)
                        print "UICE: Data range of %s after interpolation: %3.3f to %3.3f" % (
                            myvar, SSHdata.min(), SSHdata.max())
                    if myvar == 'sim2':
                        SSHdata = array2 / (array1) # * (1. / grdROMS.pn))
                        SSHdata = np.where(grdROMS.mask_v == 0, grdROMS.fill_value, SSHdata)
                      #  SSHdata = np.where(abs(SSHdata) > 1000, grdROMS.fill_value, SSHdata)

                        print "VICE: Data range of %s after interpolation: %3.3f to %3.3f" % (
                            myvar, SSHdata.min(), SSHdata.max())


                    if myvar == 'sim':
                        IOwrite.writeClimFile(grdROMS, time, climName, 'uice', isClimatology, writeIce, SSHdata)
                    if myvar == 'sim2':
                        IOwrite.writeClimFile(grdROMS, time, climName, 'vice', isClimatology, writeIce, SSHdata)

                    if time == grdROMS.initTime:
                        if myvar == 'sim':
                            IOinitial.createInitFile(grdROMS, time, initName, 'uice', SSHdata)
                        if myvar == 'sim2':
                            IOinitial.createInitFile(grdROMS, time, initName, 'vice', SSHdata)

                if myvar == 'uvel':
                    array2 = array1

                if myvar == 'vvel':
                    indexROMS_UBAR = (grdROMS.eta_u, grdROMS.xi_u)
                    indexROMS_VBAR = (grdROMS.eta_v, grdROMS.xi_v)
                    UBARdata = np.zeros((indexROMS_UBAR), dtype=np.float64)
                    VBARdata = np.zeros((indexROMS_VBAR), dtype=np.float64)

                    urot, vrot = rotate(grdROMS, grdMODEL, data, array2, array1)

                    u, v = interpolate2UV(grdROMS, grdMODEL, urot, vrot)

                    Udata, Vdata, UBARdata, VBARdata = VerticalInterpolation(myvar, u, v, grdROMS, grdMODEL)

                if myvar == 'vvel':
                    print "Data range of U after interpolation: %3.3f to %3.3f - V after scaling: %3.3f to %3.3f" % (
                        Udata.min(), Udata.max(), Vdata.min(), Vdata.max())

                    Udata = np.where(grdROMS.mask_u == 0, grdROMS.fill_value, Udata)
                    Udata = np.where(abs(Udata) > 1000, grdROMS.fill_value, Udata)
                    Vdata = np.where(grdROMS.mask_v == 0, grdROMS.fill_value, Vdata)
                    Vdata = np.where(abs(Vdata) > 1000, grdROMS.fill_value, Vdata)
                    UBARdata = np.where(grdROMS.mask_u == 0, grdROMS.fill_value, UBARdata)
                    UBARdata = np.where(abs(UBARdata) > 1000, grdROMS.fill_value, UBARdata)
                    VBARdata = np.where(grdROMS.mask_v == 0, grdROMS.fill_value, VBARdata)
                    VBARdata = np.where(abs(VBARdata) > 1000, grdROMS.fill_value, VBARdata)

                    IOwrite.writeClimFile(grdROMS, time, climName, myvar, isClimatology, writeIce, Udata, Vdata,
                                          UBARdata, VBARdata)
                    if time == grdROMS.initTime:
                        # We print time=initTime to init file so that we have values for ubar and vbar (not present at time=1)
                        IOinitial.createInitFile(grdROMS, time, initName, myvar, Udata, Vdata, UBARdata, VBARdata)

            time += 1