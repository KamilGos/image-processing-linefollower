

class PID():
    def __init__(self, set_point):
        print("Initializing PID...")
        self.KP = 1
        self.KI = 1
        self.KD = 1
        self.P = 0
        self.I = 0
        self.D = 0
        self.set_point = set_point
        self.error = 0
        self.prev_error = 0
        self.control = 0
        print("PID Initialized...")
        self.ready = True
        print("SET POINT: ", self.set_point)

    def return_state(self):
        return self.ready

    def update_factors(self, KP, KI, KD):
        self.KP = KP
        self.KI = KI
        self.KD = KD

    def print_factors(self):
        print("\n\nKP: {} \nKI: {} \nKD: {}".format(self.KP, self.KI, self.KD))

    def calcualte_PID(self, possition):
        self.error = possition - self.set_point
        self.P = self.error
        self.I = self.I + self.error
        self.D = self.error - self.prev_error
        self.prev_error = self.error
        self.control = (self.P*self.KP) + (self.I*self.KI) + (self.D*self.KD)
    
    def return_control(self):
        return int(self.control)
    
if __name__=="__main__":
    PID = PID(10)
    PID.print_factors()
    print("READY: ", PID.return_state())

    for i in range(0, 11):
        PID.calcualte_PID(i)
        print("CONTROL: ", PID.return_control() )
