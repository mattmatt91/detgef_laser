import pyfirmata
import time


address = 'COM5'


class Valve():
    def __init__(self, address: str, pins: dict):
        self.pins = pins
        self.state = False
        self.board = pyfirmata.Arduino(address)
        self.board.digital[13].write(1)
        for pin in pins:
            self.board.digital[pins[pin]].write(0)

    def toggle_valves(self):
        for pin in pins:
            self.board.digital[self.pins[pin]].write(not self.state)
        self.state = not self.state

    def set_valves(self, state:bool):
        for pin in self.pins:
            self.board.digital[self.pins[pin]].write(state)


if __name__ == '__main__':
    pins = {'valve1': 12, 'valve2': 11, }
    valves = Valve(address, pins)
    for i in range(10):
        valves.toggle_valves()
        time.sleep(1)
