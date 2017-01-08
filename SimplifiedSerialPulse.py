#!/usr/bin/env python
import sys, serial, argparse, datetime
from dateutil import parser as dateparser
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class LiveDataPoint(object):
    def __init__(self, time, data): 
        if [d & 0x80 != 0 for d in data] != [True, False, False, False, False]:
           raise ValueError("Invalid data packet.")

        self.time = time

        # 1st byte
        self.signalStrength = data[0] & 0x0f
        self.fingerOut = bool(data[0] & 0x10)
        self.droppingSpO2 = bool(data[0] & 0x20)
        self.beep = bool(data[0] & 0x40)

        # 2nd byte
        self.pulseWaveform = data[1]

        # 3rd byte
        self.barGraph = data[2] & 0x0f
        self.probeError = bool(data[2] & 0x10)
        self.searching = bool(data[2] & 0x20)
        self.pulseRate = (data[2] & 0x40) << 1

        # 4th byte
        self.pulseRate |= data[3] & 0x7f

        # 5th byte
        self.bloodSpO2 = data[4] & 0x7f

    def __str__(self):
        return str(self.pulseRate)


class CMS50Dplus(object):
    def __init__(self, port):
        self.port = port
        self.conn = None

    def isConnected(self):
        return type(self.conn) is serial.Serial and self.conn.isOpen()

    def connect(self):
        if self.conn is None:
            self.conn = serial.Serial(port = self.port,
                                      baudrate = 19200,
                                      parity = serial.PARITY_ODD,
                                      stopbits = serial.STOPBITS_ONE,
                                      bytesize = serial.EIGHTBITS,
                                      timeout = 5,
                                      xonxoff = 1)
        elif not self.isConnected():
            self.conn.open()

    def disconnect(self):
        if self.isConnected():
            self.conn.close()

    def getByte(self):
        char = self.conn.read()
        if len(char) == 0:
            return None
        else:
            return ord(char)

    def animate(self, i):
        ax1.clear()
        ax1.plot(xArray,yArray)
    
    def getLiveData(self):
        try:
            self.connect()
            packet = [0]*5
            idx = 0
            while True:
                byte = self.getByte()
            
                if byte is None:
                    break

                if byte & 0x80:
                    if idx == 5 and packet[0] & 0x80:
                        yield LiveDataPoint(datetime.datetime.utcnow(), packet)
                    packet = [0]*5
                    idx = 0
            
                if idx < 5:
                    packet[idx] = byte
                    idx+=1
        except:
            self.disconnect()

def animate(i,oximeter,measurements,xArray,yArray,ax1):
    for liveData in oximeter.getLiveData():
        xArray.append(measurements)
        yArray.append(int(str(liveData)))
        measurements += 1
        ax1.clear()
        ax1.plot(xArray, yArray)

def dumpLiveData(port):
    xArray = []
    yArray = []
    oximeter = CMS50Dplus(port)
    measurements = 0
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)
    ani = animation.FuncAnimation(fig, animate, interval=1000, fargs=(oximeter,measurements,xArray,yArray,ax1))
    plt.show()    

if __name__ == "__main__":
##    parser = argparse.ArgumentParser(description="cms50dplus.py v1.0 - Contec CMS50D+ GUI (c) 2016 J.J. Gerschler")
##    parser.add_argument("serialport", help="Virtual serial port where pulse oximeter is connected.")
##
##    args = parser.parse_args()

##    dumpLiveData(args.serialport)
    dumpLiveData('COM5')
else:
    dumpLiveData('COM5')
