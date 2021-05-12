import pandas as pd
import pyproj
import numpy as np
import os
import math
import time
start_time = time.time()

def txt2kml(p2txt, startcoordUTM, secondcoordUTM, secondTS, crs_target, crs_source, oDir, kml_oFile, name_kml, description_kml, icon_to_use, kml_style_scale, use_every_nth_value): 

    print('S : txt2kml')
    
    #%% Import Trajectory and get angle difference
    print('S : txt2kml > Import Trj')
    
    # Import
    Trj = pd.read_csv(p2txt, delimiter=" ", header=0).values
    
    # Get local coordiantes of control points
    startcoordlocal = Trj[0, 1:4]
    secondcoordlocal = Trj[ np.argmin( abs( Trj[:,0] - secondTS ) ), 1:4]
    
    # build local and global array
    vector_UTM = np.array([ secondcoordUTM[0] - startcoordUTM[0], secondcoordUTM[1] - startcoordUTM[1] ])
    vector_UTM = vector_UTM / np.linalg.norm( vector_UTM )
    
    vector_local = np.array([ secondcoordlocal[0] - startcoordlocal[0], secondcoordlocal[1] - startcoordlocal[1] ])
    vector_local = vector_local / np.linalg.norm( vector_local )
    
    # get angle in between
    theta = - np.arccos( np.dot(vector_UTM, vector_local) )
    
    print('I : txt2kml > Import Trj > angle difference is', str( round(theta * 180 / math.pi,3) ) + ' [deg]')
    print('E : txt2kml > Import Trj')
    
    #%% Transform xyz 2 wgs84
    print('S : txt2kml > Applying rotation')
    
    #Subsample
    if use_every_nth_value > 0:
        Trj = Trj[0 : len(Trj) : use_every_nth_value, :]
        
    # Reduced Timestamps    
    Ts = Trj[:,0] - np.min(Trj[:,0])
    
    # Rotate coordinates
    Rot2D = np.array(( (np.cos(theta), -np.sin(theta)), (np.sin(theta),  np.cos(theta)) ))
    
    xy_rotated = Rot2D.dot( Trj[:, 1:3].T ).T
    
    xyz_oriented = np.hstack([ xy_rotated,  np.expand_dims(Trj[:,4], axis=1) ])  + startcoordUTM
    
    # Transform from source 2 target coord system
    target_x, target_y = pyproj.transform( crs_source, crs_target, xyz_oriented[:,0].tolist(), xyz_oriented[:,1].tolist() )
    
    print('E : txt2kml > Applying rotation')
    
    #%% Write kml file
    print('S : txt2kml > Writing kml file')
          
    if not os.path.exists(oDir):
        os.mkdir(oDir) 
    
    f = open(oDir + '//' + kml_oFile + '.kml', "w")
    f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + '\n') 
    f.write("<kml xmlns=\"http://earth.google.com/kml/2.2\">" + '\n')
    f.write("<Document>" + '\n')
    f.write("<name>" + name_kml + "</name>"+ '\n' )
    f.write("<open>1</open>" + '\n')
    f.write("<description>" + description_kml + "</description>" + '\n\n')
    
    if icon_to_use:
        f.write("<Style id=\"mycol\">" + '\n')
        f.write("<IconStyle>" + '\n')
        f.write("<color>ff00aaff</color>" + '\n')
        f.write("<scale>" + str(kml_style_scale) + "</scale>" + '\n')
        f.write("<Icon><href>" + icon_to_use + "</href></Icon>" + '\n')
        f.write("</IconStyle>" + '\n')
        f.write("</Style>" + '\n\n')    
    
    f.write("<Folder>" + '\n')
    f.write("<name>Trajectory</name>" + '\n')
    f.write("<open>1</open>" + '\n')
    f.write("<Style>" + '\n')
    f.write("<ListStyle>" + '\n')
    f.write("<listItemType>checkHideChildren</listItemType>" + '\n')
    f.write("</ListStyle>" + '\n')
    f.write("</Style>" + '\n' + '\n')
    
    
    for idx, ts in enumerate(Ts):
           
        m, s = divmod(ts, 60)
        h, m = divmod(m, 60)
      
        f.write("<Placemark>" + '\n')
        f.write("<TimeStamp><when>" + "2021-01-01T" + "{:02d}".format(int(h)) + ':' + "{:02d}".format(int(m)) + ':' + "{:05.2F}".format(s) + "Z</when></TimeStamp>" + '\n')
        if icon_to_use:
            f.write("<styleUrl>#mycol</styleUrl>" + '\n')
        f.write("<Point>" + '\n')
        f.write("<extrude>1</extrude>" + '\n')
        f.write("<altitudeMode>absolute</altitudeMode>" + '\n')
        f.write("<coordinates>" + str(target_y[idx]) + ',' + str(target_x[idx]) + ',' + str(xyz_oriented[idx,2]) + "</coordinates>" + '\n')
        f.write("</Point>" + '\n')
        f.write("</Placemark>" + '\n')
    
    f.write("</Folder>" + '\n')
        
    f.write("</Document>")
    f.write("</kml>")     
    
    f.close()
    
    print('E : txt2kml > Writing kml file')
    
    #%%
    
    m, s = divmod(time.time() - start_time, 60)
    h, m = divmod(m, 60)
    print('I : txt2kml Excecuted in ' + str(int(h)) + ' hour(s) ' + str(int(m)) + ' min(s) ' + str(round(s,2)) + ' secs')
    print('E : txt2kml')
 
    
 
if __name__ == '__main__':
    
    txt2kml(p2txt = '2021-03-29_12-16-28_results_traj.txt',             # 1 header line, space separated
            startcoordUTM = [512671.810, 5403178.831, 253.460 + 48],    # coordinate of start point; maybe include constant offset to z due to geoid undulation
            secondcoordUTM = [512573.554, 5403141.547, 254.261],        # coordinate of arbitrary control point included in Trj
            secondTS = 1617016723.872510,                               # Timestamp of same arbitrary control point. Can be obtained in Geoslam viewer
            crs_target = pyproj.CRS("EPSG:4326"),                       # WGS 84
            crs_source = pyproj.CRS("EPSG:32632"),                      # UTM 32N
            oDir = 'KML', 
            kml_oFile = 'test', 
            name_kml = 'mykml',                                         #kml tag
            description_kml = 'written by Magic',                       #kml tag
            icon_to_use = 'http://maps.google.com/mapfiles/kml/shapes/horsebackriding.png', #examples at: http://kml4earth.appspot.com/icons.html
            kml_style_scale = 1,                                        # aka size of icon
            use_every_nth_value= 300                                    # subsample Trj. Recommended for large files
            )
 
