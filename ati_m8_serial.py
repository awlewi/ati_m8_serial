import serial
import time
import numpy as np
import platform


#todo: ask for data size from user(16, 32)

class atiM8serial:
    """

    """
    zeros = np.zeros(6)
    ser = serial.Serial()
    force = np.zeros(6)

    def __init__(self, com_num):
        """
        opens a serial link to the ATI sensor 
        at com number (linux assumed - /dev/ttyS#)
        does not close the serial port
        """
        sys = platform.system()
        if sys == 'Linux':
            ser_loc = '/dev/ttyS'
        elif sys == 'Windows':
            ser_loc = 'COM'
        else:
            ser_loc = ''
            print("OS unsupported, please input serial path directly to this function")

        self.ser = serial.Serial(ser_loc+str(com_num), 115200)
        self.ser.timeout = .01
        print("ATI serial opened")  

    def __del__(self):
        """
        close the serial port when the program is over
        """
        self.ser.close()
        print("ATI serial closed")  

    def close(self):
        """
        close the serial port associated with the sensor
        """
        self.ser.close()

    def readForce(self):
        """
        read the serial output until a single valid set is read
        sets the self.force to the valid reading

        return the valid data [Fx, Fy, Fz, Tx, Ty, Tz] (N, Nm)
        """
        val = ['']*6
        tries = 0

        #try to get a good line of data
        #sometimes readline gets a line with newline or return characters
        while True:
            tries = tries + 1
            try:
                cc =  str(self.ser.readline().decode("utf-8"))
                for j in range(6):      
                    idx = 1 + j*4
                    val[j] = cc[idx : idx + 4]
                    val[j] = int(val[j], 16)  / 15.258789
            except Exception as ex:
                if(tries > 5):
                    print(ex)
                    print(tries)
                    self.ser.reset_input_buffer()
                    print("buffer cleared \n")
                    time.sleep(0.01)
            else:
                break
        #copy good data into dat struct            
        for j in range(6):      
            self.force[j]  = val[j]

        return self.force

    def findRate(self, n):
        """
        read the sensor for n valid reads 
        to determine the read rate characteristics of the system

        return [size of data left in buffer (bytes), 
        max loop time, min loop time
        avg loop time, total run time (seconds),
        avg frequency (Hz)]
        """
        self.ser.reset_input_buffer()

        #try to bleed out some garbage lines on start
        self.ser.write(('s').encode())
        for i in range(10):
            self.ser.readline()

        max_time = 0
        min_time = time.time_ns()

        start_time = time.time_ns()

        for i in range(n):
            loop_start_time = time.time_ns()
            
            self.readForce()

            end_loop_time = time.time_ns()
            loop_time = end_loop_time - loop_start_time
            if(loop_time > max_time):
                max_time = loop_time
            if(loop_time < min_time):
                min_time = loop_time

        max_time = max_time / (10 ** 9)
        min_time = min_time / (10 ** 9)
        total_time = (end_loop_time - start_time)/ (10 ** 9)
        avg_time = total_time / n
        freq = 1 / avg_time

        print("waiting   - ", self.ser.in_waiting)
        print("max time  - ", max_time)
        print("min time  - ", min_time)
        print("avg time  - ", avg_time)
        print("tot time  - ", total_time)
        print("Frequency - ", 1/avg_time)

        return([self.ser.in_waiting, max_time, min_time, avg_time, total_time, freq])




    def zero(self, n):
        """
        sets the sensors zero levels with an average of 
        n  readings
        """
        self.ser.reset_input_buffer()

        dat = np.zeros((n, 6))

        #try to bleed out some garbage lines on start
        self.ser.write(('s').encode())
        for i in range(10):
            self.ser.readline()

        
        for i in range(n):
            dat[i] = self.readForce()

        for i in range(6):
            self.zeros[i] = sum(dat[:,i])/len(dat[:, i])

        return self.zeros


# testing script
np.set_printoptions(precision=3)
np.set_printoptions(suppress=True)
force = atiM8serial(3)

#print(force.zero(1000))
print(force.zero(100))
force.findRate(100)

