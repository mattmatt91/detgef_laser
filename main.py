# from hardware.mfc import MFC
from hardware.valve import Valve
from hardware.multimeter import Multimeter
import json
from time import sleep, time
from datetime import datetime, timedelta
import pandas as pd
from os.path import join
import os
from plot import make_plot as do_plot
import requests
import threading



program = "programs\\prog.json" # hier anderes proramm angeben
sensors = ["sensor laser", "sensor no laser"]


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
        
        conf_multimeter = self.configs["multimeter"]

        self.multimeter1 = Multimeter(conf_multimeter['address1'])
        self.multimeter2 = Multimeter(conf_multimeter['address2'])
        self.start_time = datetime.now()
        
        self.timestamps, self.dur = get_timestaps(self.steps)
        self.actual_step = 0
        self.data = []
        self.flag = True
        
    def fetch_data(self, key:str):
        if self.last_fetch + self.fetch_interval < time():
            data_m1 = self.multimeter1.get_data()
            data_m2 = self.multimeter2.get_data()
            if data_m1 == 0:
                data_m1 = self.data[-1][sensors[0]]
            if data_m2 == 0:
                data_m2 = self.data[-1][sensors[1]]
            timestamp = datetime.now()-self.start_time
            total_hours = timestamp.total_seconds() / 3600
            hours = int(total_hours)
            total_minutes = (total_hours - hours) * 60
            minutes = int(total_minutes)
            seconds = int((total_minutes - minutes) * 60)
            timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            new_data = {sensors[0]:data_m1, sensors[1]:data_m2, "timestamp":timestamp,"step_id":key}
            print(new_data)
            self.data.append(new_data)
            self.last_fetch = time()

    def update(self):
        key = list(self.steps.keys())[self.actual_step]
        step = self.steps[key]
        if self.flag:
            print(key)

            if self.steps[key]['laser']:
                data = {'pilot':step['pilot'], 'power':step['power'], 'duration':step['duration']}
                put_thread_mfc = threading.Thread(target=post_laser, args=(data,))
                put_thread_mfc.start()



            data = {"dry": step["flow_dry"], "wet": step["flow_wet"] }
            post_mfc(data)
            put_thread_laser = threading.Thread(target=post_mfc, args=(data,))
            put_thread_laser.start()

            self.flag = False
        if time() > self.timestamps[key]:
            self.actual_step += 1
            self.flag = True
        self.fetch_data(key)
        sleep(0.2)


    def save_data(self):
        data_dir = join('data', self.start_time.strftime("%m-%d-%Y_%H-%M-%S"))
        os.makedirs(data_dir, exist_ok=True)
        df = pd.DataFrame(self.data)
        path_data = join(data_dir, 'data.csv')
        path_param = join( data_dir, 'parameter.json')
        df.to_csv(path_data, index=False,header=True)
        with open(path_param, 'w', encoding='utf-8') as f:
            json.dump(self.steps, f, ensure_ascii=False, indent=3)
        do_plot(data_dir)


    def start_measurement(self):
        print('start measurement')
        try:
            while time() < self.dur:
                self.update()
        except KeyboardInterrupt:
            print('keyboard interrupt')
            self.save_data()
        finally:
            self.save_data()


def post_mfc(data:dict):
    requests.post("http://localhost:8000/set_points", json=data)

def post_laser(data:dict):
    # pass
    requests.post('http://192.168.2.123:8022/laser', json=data)

if __name__ == "__main__":
    meas = Measurement()
    meas.start_measurement()
