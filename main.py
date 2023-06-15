from hardware.mfc import MFC
from hardware.valve import Valve
from hardware.multimeter import Multimeter
import json
from time import sleep, time
from datetime import datetime
import pandas as pd
from os.path import join

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
        self.steps = read_json("programs\\prog.json")
        
        self.last_fetch = 0
        self.fetch_interval = 1
        
        print('init meaurement')
        
        conf_mfc = self.configs["mfc"]
        conf_valves = self.configs["valves"]
        conf_multimeter = self.configs["multimeter"]
        
        self.mfc = MFC(conf_mfc["hostname"], conf_mfc["port"], conf_mfc["max_flow"])
        self.valves = Valve(conf_valves["port"], conf_valves["pins"])
        self.multimeter1 = Multimeter(conf_multimeter['address1'])
        self.multimeter2 = Multimeter(conf_multimeter['address2'])
        self.mfc.open_valve(True)
        
        self.timestamps, self.dur = get_timestaps(self.steps)
        self.actual_step = 0
        self.data = []
        
    def fetch_data(self):
        if self.last_fetch + self.fetch_interval < time():
            data_m1 = self.multimeter1.get_data()
            data_m2 = self.multimeter2.get_data()
            timestamp = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
            new_data = {'multi1':data_m1, 'multi2':data_m2, "timestamp":timestamp}
            print(new_data)
            self.data.append(new_data)
            self.last_fetch = time()

    def update(self):
        key = list(self.steps.keys())[self.actual_step]
        step = self.steps[key]
        self.mfc.set_point(step["flow"])
        self.valves.set_valves(step["analyt"])
        if time() > self.timestamps[key]:
            self.actual_step += 1
            print(key)
        self.fetch_data()
        sleep(0.2)

    def save_data(self):
        print(self.data)
        df = pd.DataFrame(self.data)
        name = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")+ '.csv'
        path = join('data', name)
        df.to_csv(path, index=False,header=True)

    def start_measurement(self):
        print('start measurement')
        while time() < self.dur:
            self.update()
        self.mfc.close_valve(True)
        self.save_data()


if __name__ == "__main__":
    meas = Measurement()
    meas.start_measurement()
