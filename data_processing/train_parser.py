import os
import sys
import json
import csv
import itertools as it
from datetime import datetime
from math import pi, sqrt, cos, sin, atan2

RAILWAY_STATIONS_FILENAME = "data/railway_stations.csv"

def create_stations_dict():
    with open(RAILWAY_STATIONS_FILENAME, 'r', newline='') as f:
        res_d = dict()
        reader = csv.reader(f)
        next(reader)        
        for name, lat, lon in reader:
            try:
                res_d[name] = (float(lat), float(lon))
            except:
                pass
        return res_d


def deg_to_rad(deg):
    return deg*pi/180
    
def rad_to_deg(rad):
    return rad*180/pi        
    
def rads_from_coors(coors):
    return deg_to_rad(coors[0]), deg_to_rad(coors[1])    


# formula from https://www.movable-type.co.uk/scripts/latlong.html
def middle_coor(coor1, coor2):
    lat1, lon1 = rads_from_coors(coor1)
    lat2, lon2 = rads_from_coors(coor2)
    B_x = cos(lat2) * cos(lon2-lon1) 
    B_y = cos(lat2) * sin(lon2-lon1) 
    lat_res = atan2(sin(lat1) + sin(lat2), sqrt((cos(lat1)+B_x)**2 + B_y**2))
    lon_res = lon1 + atan2(B_y, cos(lat1)+B_x)
    return rad_to_deg(lat_res), rad_to_deg(lon_res)
    

def train_file_to_csv(filename, writer, stations_dict):
    with open(filename) as f:
        try:
            data = json.load(f)
            rides_tab = data["schedules"]
        except:
            return        
        for ride_wrap in rides_tab:
            try:
                ride = ride_wrap["info"]
                for stat_1, stat_2 in it.pairwise(ride):
                    try:
                        # to decide - way of handling negative delays
                        # delay = max(stat_2["arrival_delay"] - stat_1["departure_delay"], 0)
                        delay = stat_2["arrival_delay"] - stat_1["arrival_delay"]
                        timestamp = stat_1["departure_time"]
                        date_str = timestamp[:timestamp.find("T")]
                        # date_dt = datetime.strptime(date_str, "%Y-%m-%d")
                        coor1 = stations_dict[stat_1["station_name"]]
                        coor2 = stations_dict[stat_2["station_name"]]
                        mid_coor = middle_coor(coor1, coor2)                        
                        writer.writerow([mid_coor[0], mid_coor[1], date_str, delay])                        
                    except:
                        pass
            except:
                pass


if __name__ == "__main__":
    stations_dict = create_stations_dict()

    if len(sys.argv) < 3:
        print(f'usage: {sys.argv[0]} ipa_dir output_file', file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[2], 'w', newline='') as res_f:
        writer = csv.writer(res_f, delimiter=',')
        parent_dir_name = sys.argv[1]
        dir_name = parent_dir_name + "/api/train"
        for filename in os.listdir(dir_name):
            train_file_to_csv(dir_name + "/" + filename, writer, stations_dict) 
