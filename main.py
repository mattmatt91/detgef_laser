# from hardware.mfc import MFC
from hardware.valve import Valve
from hardware.multimeter import Multimeter
import json
from time import sleep, time
from datetime import datetime
import pandas as pd
from os.path import join
import plotly.express as px
from plot import plot as do_plot
import requests



program = "programs\\prog.json" # hier anderes proramm angeben
sensors = ["sensor 1", "sensor 2"]


def read_json(path: str):
    with open(path) as f:
        return json.load(f)


def get_timestaps(data: dict):
    timestamps = {}
    dur = time()
    for i in data:
        dur += data[i]["duration"]
        timestamps[i] = dur
    return timestamps, dur


class Measurement:
    def __init__(self):
        self.configs = read_json("config\\config.json")
        self.steps = read_json(program)
        
        self.last_fetch = 0
        self.fetch_interval = 1
        
        print('init meaurement')
        
        # conf_mfc_dry = self.configs["mfc"]["dry"]
        # conf_mfc_wet = self.configs["mfc"]["wet"]
        conf_multimeter = self.configs["multimeter"]
        # self.mfc_wet = MFC(conf_mfc_dry["hostname"], conf_mfc_dry["port"], conf_mfc_dry["max_flow"])
        # self.mfc_dry = MFC(conf_mfc_wet["hostname"], conf_mfc_wet["port"], conf_mfc_wet["max_flow"])

        self.multimeter1 = Multimeter(conf_multimeter['address1'])
        self.multimeter2 = Multimeter(conf_multimeter['address2'])
        self.start_time = datetime.now()
        
        # self.mfc_dry.open_valve(True)
        # self.mfc_wet.open_valve(True)
        self.timestamps, self.dur = get_timestaps(self.steps)
        self.actual_step = 0
        self.data = []
        self.flag = True
        
    def fetch_data(self):
        if self.last_fetch + self.fetch_interval < time():
            data_m1 = self.multimeter1.get_data()
            data_m2 = self.multimeter2.get_data()
            if data_m1 == 0:
                data_m1 = self.data[-1][sensors[0]]
            if data_m2 == 0:
                data_m2 = self.data[-1][sensors[1]]
            timestamp = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
            # timestamp = (self.start -datetime.now()).strftime("%H-%M-%S")
            new_data = {sensors[0]:data_m1, sensors[1]:data_m2, "timestamp":timestamp}
            print(new_data)
            self.data.append(new_data)
            self.last_fetch = time()

    def update(self):
        key = list(self.steps.keys())[self.actual_step]
        step = self.steps[key]
        if self.flag:
            print(key)
            url = "http://localhost:8000/set_points"  # Replace with your FastAPI app's URL
            data = {"dry": step["flow_dry"], "wet": step["flow_wet"]}
            response = requests.post(url, json=data)
            # self.mfc_dry.set_point(step["flow_dry"])
            # self.mfc_wet.set_point(step["flow_wet"])
            result = requests.get('http://localhost:8000/get_data')
            print(result)
            # print(self.mfc_dry.get_point())
            # print(self.mfc_wet.get_point())
            self.flag = False
        if time() > self.timestamps[key]:
            self.actual_step += 1
            self.flag = True
        self.fetch_data()
        sleep(0.2)


    def save_data(self):
        # print(self.data)
        df = pd.DataFrame(self.data)
        name = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")+ '.csv'
        path = join('data', name)
        df.to_csv(path, index=False,header=True)
        do_plot(path)


    def start_measurement(self):
        print('start measurement')
        try:
            while time() < self.dur:
                self.update()
        except KeyboardInterrupt:
            print('keyboard interrupt')
            self.save_data()
        finally:
            # self.mfc_wet.close_valve(True)
            # self.mfc_dry.close_valve(True)
            self.save_data()


if __name__ == "__main__":
    meas = Measurement()
    meas.start_measurement()
