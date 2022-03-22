from opensky_api import OpenSkyApi
import time
import math
import numpy as np
import os
def monitor(icao):
    positions = []
    api = OpenSkyApi()
    accumulated_angle = 0.0
    old_alpha = 0
    url = 'https://globe.adsbexchange.com/?icao={}'.format(icao)
    hovering = False
    icao = icao.lower()
    
    while True:
        s = api.get_states(icao24=icao)
        if s is not None and len(s.states) > 0:
            positions.append(
                    np.array([
                        (s.states)[0].latitude,
                        (s.states)[0].longitude
                        ])
                    )
            # Computes angle between two vectors:
            # v1 between last and penultimate position
            # v2 between penultimate and antepenultimate position
            if len(positions) >= 3:
                v1 = positions[-1] - positions[-2]
                v2 = positions[-2] - positions[-3]
                angle = np.degrees(np.math.atan2(np.linalg.det([v1,v2]),np.dot(v1,v2)))
                if not math.isnan(angle):
                    accumulated_angle += angle
        if math.fabs(accumulated_angle) > 360:
            hovering = True
        else:
            hovering = False
        os.system('clear')
        print("==========================================")
        print("AVOSINT - Monitoring 👀")
        print("Monitoring URL {}".format(url))
        print("==========================================")
        if len(positions) > 0:
            print("🌎 Last known position:\t{}".format(positions[-1]))
        print("🕴️ Is it hovering:\t{}".format(hovering))
        print("🧭 Accumulated angle:\t{}".format(accumulated_angle))
        time.sleep(2)


