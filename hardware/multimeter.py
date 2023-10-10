
import pyvisa as visa

rm = visa.ResourceManager()
# print(rm.list_resources())


def transform_string_to_int(string:str):
    return float(string.split('\r')[0])


class Multimeter():
    def __init__(self, address:str):
        self.myU1282A = rm.open_resource(address)
        # self.myU1282A.write("*IDN?")     
        # print(self.myU1282A.read())

    def get_data(self):
        self.myU1282A.write("FETC?") 
        data = transform_string_to_int(self.myU1282A.read())
        return data

    def close(self):
        self.myU1282A.close()
        
        
if __name__ == '__main__':
    multi1 = Multimeter('ASRL3::INSTR')
    multi2 = Multimeter('ASRL4::INSTR')
    print(multi1.get_data())
    print(multi2.get_data())
    multi1.close()
    multi2.close()
