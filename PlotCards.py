import os
import statistics
import time
from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pyforms
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlButton
from pyforms.controls import ControlCheckBox
from pyforms.controls import ControlCombo
from pyforms.controls import ControlFile
from pyforms.controls import ControlText
from scipy.ndimage import gaussian_filter1d

import RotationDetection

matplotlib.use('Agg')


### Gui code

class Hawkiiiiplotter(BaseWidget):

    def __init__(self):
        super(Hawkiiiiplotter, self).__init__('Card Generator')

        # Mode Selector
        self._mode_selector = ControlCombo("Select a mode")
        self._mode_selector.add_item("")
        self._mode_selector.add_item("Rod Rotator", "0")
        self._mode_selector.add_item("Pump Cards", "1")
        # self._mode_selector.add_item("Pump Animation", "2")

        # Save vs View (matplotlib)
        self._submit_mode = ControlButton('Start Analysis')

        # Definition of the plot card fields
        self._testfile = ControlFile('File Name')
        self._time_start_hour = ControlText('Start Time (hour)', default="0")
        self._time_start_minute = ControlText('Start Time (minute)', default="0")
        self._duration = ControlText('Duration of Analysis (hours)', default="24")
        self._cards_per_graph = ControlText('Cards Per Graph', default="5")
        self._time_between_cards = ControlText('Time Between Cards', '0')
        self._generate_cards = ControlButton('Generate Cards')

        # Definition of the Rod Rotator fields
        self._testfile_magnetometer = ControlFile('File Name')
        self._save_selector = ControlCheckBox("Save Graphs")
        self._use_algorithm = ControlCheckBox("Process with algorithm")
        self._generate_plots = ControlButton('Generate Plots')

        # Hide the menu items
        self._testfile.hide()
        self._time_start_hour.hide()
        self._time_start_minute.hide()
        self._duration.hide()
        self._cards_per_graph.hide()
        self._time_between_cards.hide()
        self._generate_cards.hide()
        self._save_selector.hide()
        self._generate_plots.hide()
        self._testfile_magnetometer.hide()
        self._use_algorithm.hide()

        self.pos_lines = {}
        self.load_lines = {}
        self.average_load = {}
        self.load_standard_deviation = {}
        self.accel = []
        self.magx = []
        self.magy = []
        self.magz = []
        self.time = []
        self.rotating = []
        self.moving = []
        self.date_stamp = None

        # self._testfile.changed_event = self.__make_dictionaries #Doesnt allow reset...
        # self._testfile_magnetometer.changed_event = self.__make_dictionaries_magnetometer
        self._generate_cards.value = self.__make_cards
        self._submit_mode.value = self.__menu_view
        self._generate_plots.value = self.__plot_log_file

    def __menu_view(self):
        if self._mode_selector.value == "1":  # pump card generator
            self._testfile.show()
            self._time_start_hour.show()
            # self._time_start_minute.show()
            self._duration.show()
            self._cards_per_graph.show()
            # self._time_between_cards.show()
            self._generate_cards.show()
            self._mode_selector.hide()
            self._save_selector.hide()
            self._submit_mode.hide()
        elif self._mode_selector.value == "0":  # rr plot generator
            self._testfile_magnetometer.show()
            # self._save_selector.show() #not incorporated yet...
            self._use_algorithm.hide()
            self._generate_plots.show()
            self._mode_selector.hide()
            self._submit_mode.hide()
        else:
            pass

    def __make_dictionaries(self):
        if self._testfile == "":
            pass
        else:
            fn = self._testfile.value
            filename = self._testfile.value.split("/")[-1]
            self.date_stamp = filename.split("_")[-2]
            if fn is "":
                pass
            else:
                with open(fn, 'r') as f:
                    all_lines = f.readlines()
                for line in all_lines:
                    if 'position' in line:
                        if len(line)
                        print("position: " + str(len(line)))
                        # split_line = [s.strip() for s in line.split(",")[:2]]
                        # split_line_values = [float(s.strip()) for s in line.split(",")[2:]]
                        # time_stamp = split_line[1]
                        # datetime_str = str(self.date_stamp + " " + time_stamp)
                        # datetime_object = datetime.strptime(datetime_str, '20%y-%m-%d %H:%M:%S:%f')
                        # readable_time = datetime_object.strftime("%H:%M:%S")
                        # # if int(time_start_hour) <= int(datetime_object.hour) <= int(time_stop_hour):
                        # self.pos_lines[readable_time] = split_line_values[:]
                        # self._generate_cards.show()

                    if 'load' in line:
                        print("load: " + str(len(line)))

                        # split_line = [s.strip() for s in line.split(",")[:2]]
                        # split_line_values = [float(s.strip()) for s in line.split(",")[2:]]
                        # time_stamp = split_line[1]
                        # datetime_str = str(self.date_stamp + " " + time_stamp)
                        # datetime_object = datetime.strptime(datetime_str, '20%y-%m-%d %H:%M:%S:%f')
                        # readable_time = datetime_object.strftime("%H:%M:%S")
                        # load_avg = statistics.mean(split_line_values)
                        # load_std = statistics.stdev(split_line_values)
                        # self.average_load[readable_time] = load_avg
                        # self.load_standard_deviation[readable_time] = load_std
                        # # if int(time_start_hour) <= int(datetime_object.hour) <= int(time_stop_hour):
                        # self.load_lines[readable_time] = split_line_values[:]
                        # self._generate_cards.show()

    def __make_dictionaries_magnetometer(self):
        if self._testfile == "":
            pass
        else:
            fn = self._testfile_magnetometer.value
            filename = self._testfile_magnetometer.value.split("/")[-1]
            self.date_stamp = filename.split("_")[-1][:-4]
            if fn is "":
                pass
            else:
                with open(fn, 'r') as f:
                    all_lines = f.readlines()
                for line in all_lines:
                    if 'Magnetometer' in line:
                        if 'sequence' not in line:
                            split_line = [s.strip() for s in line.split(",")]
                            split_line_values = [float(s.strip()) for s in line.split(",")[5:]]
                            time_stamp_rtu = split_line[4]
                            accely = split_line_values[1]
                            magz = split_line_values[4]
                            datetime_object = datetime.strptime(time_stamp_rtu, '%H-%M-%S-%f')
                            readable_time = datetime_object.strftime("%H:%M:%S")
                            self.magz_lines[datetime_object] = magz
                            self.accely_lines[datetime_object] = accely

    def __make_cards(self):
        self.__make_dictionaries()
        first_card_series = True
        card_counter = 0
        legend_list = []
        log_name = self._testfile.value
        log_name = log_name.split("/")[-1]
        self._testfile = log_name.split("_")[0]
        if not os.path.exists(self._testfile):
            os.mkdir(self._testfile)

        for filename in os.listdir(self._testfile):
            if filename.endswith('.png'):
                os.unlink(self._testfile + "/" + filename)

        for i, t in enumerate(self.pos_lines.keys()):
            # self._generate_cards.hide()
            if card_counter == int(self._cards_per_graph.value):
                plt.xlabel("Position")
                plt.ylabel("Load")
                plt.legend(legend_list, loc='center left', bbox_to_anchor=(1, 0.5))
                plt.savefig(f'Whitecap/{plot_title}.png', bbox_inches='tight')
                plt.clf()
                legend_list.clear()
                card_counter = 0
                first_card_series = True

            if len(self.pos_lines[t]) == 128 and len(self.load_lines[t]) == 128:
                datetime_str = str(self.date_stamp + " " + t)
                datetime_object = datetime.strptime(datetime_str, '20%y-%m-%d %H:%M:%S')
                readable_time = datetime_object.strftime("20%y-%m-%d %H:%M:%S")
                if first_card_series:
                    plot_title = t
                    first_card_series = False
                if int(self._time_start_hour.value) <= int(datetime_object.hour) <= (int(
                        self._time_start_hour.value) + int(self._duration.value)):
                    load_smoothed = gaussian_filter1d(self.load_lines[t], sigma=1.2)
                    position_smoothed = gaussian_filter1d(self.pos_lines[t], sigma=1.2)
                    position_smoothed = np.append(position_smoothed, position_smoothed[0])
                    load_smoothed = np.append(load_smoothed, load_smoothed[0])
                    plt.plot(position_smoothed, load_smoothed)
                    legend_list.append(readable_time)
                    card_counter += 1

    def __plot_log_file(self):
        matplotlib.use("Qt5Agg")

        """plots a "log" file with a specific name format - and data format.  

        example log_file_name is CRC5_2019-3-20_554_minutes.log

        first couple of rows of an example data file are

        DF:8D:7F:A0:31:36,Magnetometer,Raw,sequence,rtu_time(H-M-S-uS edmonton TZ),pod_time,accel_y,mag_x,mag_y,mag_z
        DF:8D:7F:A0:31:36,Magnetometer,b'f10d01030a2100770d17a49136f3ffa2fe9002',0,13-28-45-722903,672112.8415527344,13969,-13,-350,656

        TODO: deal with the 
        """
        # if self._use_algorithm.value is True:
        #     RotationDetection.init()
        log_file_name = self._testfile_magnetometer.value
        split_name = os.path.basename(log_file_name).split("_")
        crc_name = split_name[0]
        date_part = split_name[1][:-4]
        print(date_part)
        year, month, day = [int(d) for d in date_part.split("-")]

        with open(log_file_name, 'r') as f:
            all_lines = f.readlines()
        for line in all_lines:
            if "CD:2C:9A:5E:B2:98" in line:
                if "sequence" not in line:
                    if len(line) > 100:
                        line = line.split(',')
                        time_string = line[4]
                        time_pod = float(line[5])
                        accel_y = float(line[6])
                        mag_x = float(line[7])
                        mag_y = float(line[8])
                        mag_z = float(line[9])
                        datetime_object = datetime.strptime(time_string, '%H-%M-%S-%f')
                        self.time.append(datetime_object)
                        self.accel.append(accel_y)
                        self.magx.append(mag_x)
                        self.magy.append(mag_y)
                        self.magz.append(mag_z)
                        # if self._use_algorithm.value is True:
                        #     RotationDetection.process(mag_x, mag_y, mag_z, time_pod)
                        #     if RotationDetection.currently_moving():
                        #         self.moving.append(1)
                        #     else:
                        #         self.moving.append(0)
                        #     if RotationDetection.currently_rotating():
                        #         self.rotating.append(1)
                        #     else:
                        #         self.rotating.append(0)

        fig, ax = plt.subplots(nrows=3, ncols=1, sharex=True)
        ax[0].plot(self.time, self.magx, label='X')
        ax[0].plot(self.time, self.magy, label='Y')
        ax[0].plot(self.time, self.magz, label='Z')
        ax[0].legend()
        ax[0].grid()
        ax[0].set_ylabel("magnetometer")
        ax[0].set_title(log_file_name)

        ax[1].plot(self.time, self.accel)
        ax[1].set_ylabel("accelerometer")
        ax[1].grid()
        ax[1].set_xlabel('Edmonton Time')

        # ax[2].plot(self.time, self.rotating, label='rotating')
        # ax[2].plot(self.time, self.moving, label='moving')
        # ax[2].legend()
        # ax[2].grid()
        # ax[2].set_ylabel("Algorithm")
        # ax[2].set_xlabel('Edmonton Time')
        # ax[2].set_title(log_file_name)

        fig.tight_layout()
        fig.show()

    # Execute the application


if __name__ == "__main__":
    pyforms.start_app(Hawkiiiiplotter, geometry=(50, 50, 300, 300))

####
