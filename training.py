from libs.geoloc import *
from libs.planes import *

import numpy as np
import argparse
import json
import matplotlib.pyplot as plt
import os
import time
import psycopg2
from psycopg2.extensions import adapt, register_adapter, AsIs

PSQL_DB = "planes"
PSQL_TABLE = "planes"

def main():
    parser  = argparse.ArgumentParser()
    parser.add_argument("-daydir", type=str)
    parser.add_argument("-psql_user", type=str)
    parser.add_argument("-psql_pass", type=str)
    args  = parser.parse_args()
    list_of_files = sorted(os.listdir(args.daydir))

    conn = psycopg2.connect(host='localhost', dbname=PSQL_DB, user=args.psql_user, password=args.psql_pass)
    curs = conn.cursor()
    register_adapter(Coordinates, adapt_point)
    #register_adapter([Coordinates], adapt_path)
    # For each file of the day
    for filename in list_of_files:
        os.system('clear')
        print('loading planes from file ' + filename)
        print('loading planes from db')
        curs.execute('SELECT * FROM planes')
        list_db_planes = curs.fetchall()
        with open(args.daydir + '/' + filename, encoding='utf-8') as f:
            try:
                j = json.load(f)
                aviatos_list_from_file = j['acList']
                leng = len(aviatos_list_from_file)
                for i, aviato in enumerate(aviatos_list_from_file):
                    path = []
                    os.sys.stdout.write('\r' + str(i+1) + '/' + str(leng))
                    webi = aviato.get('Reg')
                    numb = aviato.get('Reg')
                    callsign = aviato.get('Call')
                    latitude = aviato.get('Lat')
                    longitude = aviato.get('Long')
                    flg = False

                    # search for plane in whole db
                    #for plane_obj in list_db_planes:
                    if any(plane_obj[0]==numb for plane_obj in list_db_planes) and latitude is not None:
                        #if plane_obj[0] == numb and latitude is not None:
                        flg = True
                        curs.execute('SELECT path from planes WHERE number =  %s ', (numb,))
                        path_tuple = curs.fetchone()
                        path_array = []
                        for tuple in path_tuple:
                            coord = Coordinates(tuple)
                            print(coord)
                        path_array.append(Coordinates(coord) for coord in path_tuple)
                        point_to_add_to_path = Coordinates(latitude, longitude)
                        path_array.append( point_to_add_to_path)
                        curs.execute('UPDATE planes SET path = %s  WHERE number =  %s ', (path_array, numb))

                        # Else it is not yet in db. Add to db if we have number and position
                    if not flg and numb is not None and latitude is not None:
                        plane = Plane(webi, numb, callsign, latitude, longitude)
                        point = Coordinates(latitude, longitude)
                        path = []
                        path.append(point)
                        curs.execute('INSERT INTO planes(number, callsign, path) values (%s, %s, %s)', (plane.numb, plane.call, path))
                        conn.commit()
                print("")
                time.sleep(0.1)
            except ValueError as e:
                pass


    print('Enter interesting plane to check path')
    plane_numb = input()
    if any(plane.numb == plane_numb for plane in f):
        plt.plot(plane.path)
        plt.savefig(str(plane.numb)+'.png')

def printpath_and_classify(array):
    plt.plot(array)
    plt.show()

def adapt_point(point):
    x = adapt(point.latitude).getquoted()
    y = adapt(point.longitude).getquoted()
    return AsIs("'%s, %s'" % (x, y))

def adapt_path(path):
    pts = []
    for point in path:
        pt_ad = adapt_point(point)
        pts.append(pt_ad)
    return AsIs("'[%s]'" % pts)


if __name__ == "__main__":
    main()
