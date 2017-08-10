from libs.geoloc import *
from libs.planes import *

import numpy as np
import argparse
import json
import matplotlib.pyplot as plt
import os
import time
import psycopg2

PSQL_DB = "planes"
PSQL_TABLE = "planes"

def main():
    parser  = argparse.ArgumentParser()
    parser.add_argument("-daydir", type=str)
    parser.add_argument("-psql_user", type=str)
    parser.add_argument("-psql_pass", type=str)
    args  = parser.parse_args()
    path = []
    list_of_planes = []
    list_of_files = sorted(os.listdir(args.daydir))

    conn = psycopg2.connect(host='localhost', dbname=PSQL_DB, user=args.psql_user, password=args.psql_pass)
    curs = conn.cursor()

    # For each file of the day
    for filename in list_of_files:
        os.system('clear')
        print('loading planes from file ' + filename)
        print('loading planes from db')
        curs.execute('SELECT * FROM planes')
        list_db_planes = curs.fetchall()
        print(list_db_planes)
        with open(args.daydir + '/' + filename, encoding='utf-8') as f:
            try:
                j = json.load(f)
                aviatos_list_from_file = j['acList']
                leng = len(aviatos_list_from_file)
                for i, aviato in enumerate(aviatos_list_from_file):
                    os.sys.stdout.write('\r' + str(i+1) + '/' + str(leng))
                    webi = aviato.get('Reg')
                    numb = aviato.get('Reg')
                    callsign = aviato.get('Call')
                    latitude = aviato.get('Lat')
                    longitude = aviato.get('Long')
                    if any(plane.numb == numb for plane in list_db_planes):
                        print('Plane already in list ! Append position to the path')
                        plane.path.append(Coordinates(latitude, longitude))

                    # Else it is not yet in db. Add to db if we have number and position
                    elif numb is not None and latitude is not None:
                        plane = Plane(webi, numb, callsign, latitude, longitude)
                        path = (plane.coordinates.latitude, plane.coordinates.longitude)
                        curs.execute('INSERT INTO planes(number, callsign, path) values (%s, %s, \'%s\')', (plane.numb, plane.call, path))
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



if __name__ == "__main__":
    main()