import os
import sys
import json
import csv
import itertools as it
from datetime import datetime

def train_file_to_csv(filename, writer):
    with open(filename) as f:
        data = json.load(f)
        rides_tab = data["schedules"]
        for ride_wrap in rides_tab:
            ride = ride_wrap["info"]
            for stat_1, stat_2 in it.pairwise(ride):
                # to decide - way of handling negative delays
                # delay = max(stat_2["arrival_delay"] - stat_1["departure_delay"], 0)
                delay = stat_2["arrival_delay"] - stat_1["departure_delay"]
                timestamp = stat_1["departure_time"]
                date_str = timestamp[:timestamp.find("T")]
                # date_dt = datetime.strptime(date_str, "%Y-%m-%d")
                writer.writerow([stat_1["station_name"], stat_2["station_name"], date_str, delay])


if __name__ == "__main__":
    with open('delays.csv', 'w', newline='') as res_f:
        writer = csv.writer(res_f, delimiter=',')
        parent_dir_name = sys.argv[1]
        dir_name = parent_dir_name + "/api/train"
        for filename in os.listdir(dir_name):
           train_file_to_csv(dir_name + "/" + filename, writer) 
               


