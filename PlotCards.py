import os
from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d

matplotlib.use('Agg')

first_loop = True
time_start_hour = int(input("Hour Start (24 hour clock): "))
time_stop_hour = int(input("Hour Stop (24 hour clock): "))
cards_per_graph = int(input("Cards per graph: "))
# time_between_start = float(input(str(cards_per_graph) + " cards every ______ minutes. "))
file_name = "Whitecap_2019-3-24_pumpcards.log"
split_filename = [s.strip() for s in file_name.split("_")]
date_stamp = split_filename[1]
# folder_name = input("")
dirpath = './Whitecap'

for filename in os.listdir(dirpath):
    if filename.endswith('.png'):
        os.unlink(dirpath + "/" + filename)


def make_dictionaries(fn):
    with open(fn, 'r') as f:
        all_lines = f.readlines()
    pos_lines = {}
    load_lines = {}
    first_minute = None
    for line in all_lines:
        if 'position' in line:
            split_line = [s.strip() for s in line.split(",")[:2]]
            split_line_values = [float(s.strip()) for s in line.split(",")[2:]]
            time_stamp = split_line[1]
            datetime_str = str(date_stamp + " " + time_stamp)
            datetime_object = datetime.strptime(datetime_str, '20%y-%m-%d %H:%M:%S:%f')
            readable_time = datetime_object.strftime("%H:%M:%S")
            if int(time_start_hour) <= int(datetime_object.hour) <= int(time_stop_hour):
                pos_lines[readable_time] = split_line_values[:]

        if 'load' in line:
            split_line = [s.strip() for s in line.split(",")[:2]]
            split_line_values = [float(s.strip()) for s in line.split(",")[2:]]
            time_stamp = split_line[1]
            datetime_str = str(date_stamp + " " + time_stamp)
            datetime_object = datetime.strptime(datetime_str, '20%y-%m-%d %H:%M:%S:%f')
            readable_time = datetime_object.strftime("%H:%M:%S")
            if first_minute is None:
                first_minute = datetime_object
            if int(time_start_hour) <= int(datetime_object.hour) <= int(time_stop_hour):
                load_lines[readable_time] = split_line_values[:]
    return pos_lines, load_lines


pos_dict, load_dict = make_dictionaries(file_name)
print(pos_dict)
print(load_dict)
first_card_series = True
card_counter = 0
plot_started = False
legend_list = []
for i, t in enumerate(pos_dict.keys()):
    if card_counter == cards_per_graph:
        plt.xlabel("Position")
        plt.ylabel("Load")
        plt.legend(legend_list, loc='center left',
                   bbox_to_anchor=(1, 0.5))
        plt.savefig(f'Whitecap/{plot_title}.png', bbox_inches='tight')
        plt.clf()
        legend_list.clear()
        card_counter = 0
        first_card_series = True
        plot_started = False
    try:
        if len(pos_dict[t]) == 128 and len(load_dict[t]) == 128:
            print(t)
            if first_card_series:
                plot_title = t
                first_card_series = False
            load_smoothed = gaussian_filter1d(load_dict[t], sigma=1.1)
            position_smoothed = gaussian_filter1d(pos_dict[t], sigma=1.1)
            position_smoothed = np.append(position_smoothed, position_smoothed[0])
            load_smoothed = np.append(load_smoothed, load_smoothed[0])
            plt.plot(position_smoothed, load_smoothed)
            legend_list.append(t)
    except:
        pass
    card_counter += 1
