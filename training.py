from libs.geoloc import *
from libs.planes import *

import numpy as np
import argparse
import json
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import os
import psycopg2
from psycopg2.extensions import adapt, register_adapter, AsIs
import re
import time
from  time import time, sleep

PSQL_DB = "planes"
PSQL_TABLE = "planes"

mean_times = {}
plane_path_index = {} # Because querying took too long

def timer(func):
    def wrap(*args, **kwargs):
        before = time()
        rv = func(*args, **kwargs)
        after = time()
        array = []
        if func.__name__ in mean_times:
            array = mean_times[func.__name__]
        else:
            pass
        array.append(after-before)
        mean_times.update({func.__name__:array})
        print("%s Mean\t%.5f" % (func.__name__, sum(mean_times[func.__name__])/len(mean_times[func.__name__])))
        return rv
    return wrap


# OK
#@timer
def insert_db_plane(numb, callsign, curs):
    curs.execute('INSERT INTO planes(number, callsign) VALUES (%s, %s)', (numb, callsign))
    return None
#OK
#@timer
def insert_db_path(numb, index, latitude, longitude, curs):
    curs.execute('INSERT INTO path (number, index, point_x, point_y) VALUES (%s, %s, %s, %s)', (numb, index, latitude, longitude))
    return None


# FIXME SLOWS DOWN has to do with postgres mechanism.
# We could store a dict instead with the path and the index in memory
#   @timer
def get_db_plane_path_index(numb, curs):
    curs.execute('SELECT MAX(index) from path where number = %s', (numb,))
    return curs.fetchone()

# FIXME SLOWS DOWN but not that much
#@timer
def get_db_plane(numb, curs):
    curs.execute('SELECT * FROM planes WHERE number = %s', (numb,))
    return curs.fetchone()


#@timer
def get_path(plane_numb, curs):
    curs.execute('SELECT point_x, point_y from path where number = %s order by index DESC', (plane_numb,))
    return curs.fetchall()

#@timer
def printpath_and_classify(array):
    plt.plot(array)
    plt.show()

# OK
# @timer
def create_plane(plane_dict):
    numb = plane_dict.get('Reg')
    callsign = plane_dict.get('Call')
    latitude = plane_dict.get('Lat')
    longitude = plane_dict.get('Long')
    return Plane(numb, numb, callsign, latitude, longitude)

def main():
    parser  = argparse.ArgumentParser()
    parser.add_argument("--plot", action="store_true")
    parser.add_argument("--reg", type=str)
    parser.add_argument("-daydir", type=str)
    parser.add_argument("-psql_user", type=str)
    parser.add_argument("-psql_pass", type=str)
    args  = parser.parse_args()
    list_of_files = sorted(os.listdir(args.daydir))
    conn = psycopg2.connect(host='localhost', dbname=PSQL_DB, user="postgres", password="oijojio3")
    curs = conn.cursor()

    if args.plot:
        plane_numb = args.reg
        path = get_path(plane_numb, curs)
        print('Path is: ' + str(path))
        plt.scatter(*zip(*path))
        plt.savefig(str(plane_numb)+'.png')

    else:
        # For each file of the day
        for a, filename in enumerate(list_of_files):
            os.system('clear')
            with open(args.daydir + '/' + filename, encoding='utf-8') as f:
                try:
                    print('loading planes from file ' + filename)
                    j = json.load(f) # Loads the whole thing when we don't really need it
                    aviatos_list_from_file = j['acList']
                    leng = len(aviatos_list_from_file)

                    # For every plane dict in the list from the json file
                    for i, aviato in enumerate(aviatos_list_from_file):
                        os.sys.stdout.write('\r' + str(i+1) + '/' + str(leng) + '\n')
                        plane = create_plane(aviato)

                        if plane.numb is not None and plane.coords.latitude is not None:
                            # Query for current plane
                            entry = get_db_plane(plane.numb, curs)

                            if entry is not None:   # If the plane is already in the DB, update path
                                rep = get_db_plane_path_index(plane.numb, curs)
                                if rep[0] is None:     # No path yet. Insert with index 0
                                    path_index = 0
                                else:               # There's a path !
                                    path_index = rep[0] + 1
                                insert_db_path(plane.numb, path_index, plane.coords.latitude, plane.coords.longitude, curs)
                                conn.commit()

                            # Else plane not yet in db. Insert it
                            else:
                                insert_db_plane(plane.numb, plane.call, curs)
                                conn.commit()
                        else: # Planes with no reg or no position
                            pass
                        #time.sleep(0.001)
                    #if a > 3:
                    #    return True
                    #time.sleep(0.5) # Pause between files


                except ValueError as e:
                    pass


if __name__ == "__main__":
    main()
