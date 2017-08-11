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
import re

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
    #register_adapter(Coordinates, adapt_point)
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

                    if any(plane_obj[0]==numb for plane_obj in list_db_planes) and latitude is not None:
                        #if plane_obj[0] == numb and latitude is not None:
                        flg = True
                        curs.execute('SELECT * from path where number = %s ORDER BY index DESC LIMIT 1', (numb,)) # order by index
                        path_obj = curs.fetchone()
                        path_index = path_obj[1]
                        print('Path index is ' + str(path_index))
                        path_index = path_index + 1
                        curs.execute('INSERT INTO path (number, index, point_x, point_y) values (%s, %s) WHERE number =  %s', (numb, path_index, latitude, longitude))
                        conn.commit()

                        # Else it is not yet in db. Add to db if we have number and position
                    if not flg and numb is not None and latitude is not None:
                        #plane = Plane(webi, numb, callsign, latitude, longitude)
                        #coords = Coordinates(latitude, longitude)
                        curs.execute('INSERT INTO planes(number, callsign) values (%s, %s)', (numb, callsign))
                        conn.commit()
                        curs.execute('INSERT INTO path (number, index, point_x, point_y) values (%s, %s, %s, %s)', (numb, 0, latitude, longitude))
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

def adapt_point(coord):
    x = adapt(coord.latitude).getquoted()
    y = adapt(coord.longitude).getquoted()
    return AsIs("'(%s, %s)'" % (x, y))

# should return an array of coordinates
def cast_path(tuple_of_tuples_str, curs):
    arr = []
    actual_tuple = eval(tuple_of_tuples_str)
    for tuple in actual_tuple:
        arr.append(Coordinates(tuple[0], tuple[1]))
    return arr


if __name__ == "__main__":
    main()
