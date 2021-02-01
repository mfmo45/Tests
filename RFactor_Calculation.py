import numpy as np
import pandas as pd
import os
import glob
import sys
import time
import re
import math
start_time = time.time()

##FUNCTIONS##

#To check if the input and output directories exist
def CheckPath(path):
    if os.path.exists(path) == True:
        pass
    else:
        sys.exit("ERROR: The file directory doesn't exist")

#To calculate the monthly factor
##Input: m = number for each month
def Monthly_Factor (m):
    fm = 0.3696*(1-1.0888*math.cos(2*math.pi*m/(2.9048+m))) ##Formula with cos(x), with x in radians
    print("f(m) for month ", m, " = ", fm)
    return fm

def RFactor(m, precip_raster, raster_EL, R_factor):

    #Calculate the monthly factor f(m):
    fm = Monthly_Factor(m)

    #Calculate the R factor for each cell in the raster
    for i in range(0, original_rows-1): ##loop through every row
        for j in range (0, original_columns-1): ##Loop through every columns
            if precip_raster[i][j] >= 0: ##If cell has a value of 0 or greater (different from -9999)

                #Calculate R factor with Diodato and Belocchi equation
                R_factor[i][j] = 0.207*math.pow(precip_raster[i][j]*(fm + raster_EL[i][j]), 1.561)
    return R_factor

def Save_RFactor(RFactor, name, path):
    save_name = path + '\\'+'RFactor_'+name[0:7] + ".txt"

    df_head = pd.DataFrame(
        [['ncols', int(original_columns)], ['nrows', int(original_rows)], ['xllcorner', xllcorner],
         ['yllcorner', yllcorner], ['cellsize', cellsize],
         ['nodata_value', -9999.000000]])  # Header for .txt file into data frame
    RFactor_Export = pd.concat([df_head, pd.DataFrame(RFactor)], axis=0)

    RFactor_Export.to_csv(save_name, header=False, index=False, sep='\t', na_rep="")

## MAIN CODE ##

#-User Inputs-#

#INPUT 1: Directory with location of precipitation rasters, which must be in .txt/ASCII format
input_path = r'Y:\Abt1\hiwi\Oreamuno\SY_062016_082019\Calculations\Monthly_Precipitation\Rasters_25x25\Rasters_ASCII'

#INPUT 2: Output directory, where the created rasters will be saved.
output_path= r'Y:\Abt1\hiwi\Oreamuno\SY_062016_082019\Calculations\RFactor\ASCII_Rasters'

#INPUT 3: Location of EL raster, which must be in ASCII format, and with the same extensions and cell resolution as precipitation raster and other rasters
fEL_path = r'Y:\Abt1\hiwi\Oreamuno\SY_062016_082019\Calculations\F_LE_ASCII\f_le.txt'

#-Constants to be modified by user-#
#ASCII Header: must change manually depending on the input files. These values are specificic for the Banja daily corrected precipitation files
original_rows = 2742
original_columns = 3588
xllcorner = 418688.72265149
yllcorner = 4474649.3636851
cellsize = 25

#-Code-#

CheckPath(input_path)
CheckPath(output_path)

##Create a Numpy Array to save the R factor values:
R_factor = np.full((original_rows, original_columns), -9999.0)

##Extract the f_E_L raster to a Numpy form: Since it originally is comma delimited, must change it to point delimited
raster_EL = np.array(pd.read_csv(fEL_path, delimiter=' ', decimal=',', header=None, skiprows=6))
#print("Time to save EL Raster: ", time.time()-start_time)

#Save all file names in a list
filenames=glob.glob(input_path+"\*.txt")
print(filenames)
print("Amount of files: ", len(filenames))

i=0; ##counter for files in loop

#-Main Loop-#

for file in filenames:
    name = os.path.basename(filenames[i])  # Get name of the file, including file extension
    month = float(re.search(r'\d+', name[6:7]).group()) ##save the month corresponding to the file being analyzed

    print("Iteration: ", i)
    print(name)
    print("month: ", month)

    #Save the raster file in an array.
    #monthly_precip = np.genfromtxt(file, delimiter=' ', skip_header=6)  ##Extract values from .txt files into a Numpy array
    time_before = time.time()
    monthly_precip =np.array(pd.read_csv(file, delimiter=' ', decimal=',', header=None, skiprows=6))
    print("Time to save monthly Raster: ", time.time()-time_before)


    #Calculate R factor for each cell in file "i":
    R_factor = RFactor(month, monthly_precip, raster_EL, R_factor)

    #Save R Factor raster for each month/year
    Save_RFactor(R_factor, name, output_path)

    #Reset the R_Factor array to original format, with only 0s:
    np.place(R_factor, R_factor >= -9999.0, -9999.0)  ##reset all values greater or equal than -9999 to 0

    i += 1


print('Total time: ', time.time() - start_time)





