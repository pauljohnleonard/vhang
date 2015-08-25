__author__ = 'pjl'

import pyo,threading,time

from filters import DCBlock


import serialreader



SERIAL_PORT="/dev/tty.usbserial-14P02971"
SERIAL_PORT="/dev/tty.usbmodem1411"
BAUD_RATE=112500
COM=(SERIAL_PORT,BAUD_RATE)


mutex=threading.RLock()


class ReadClient:
    """
     Does the GUI control
     Handles values from the ECG stream.
     THis is called from the ECG thread so no gui stuff is allowed.
    """

    def __init__(self,mutex):
        self.mutex=mutex
#        self.block=DCBlock(.99)

    # Read ECG values and feed the processor
    def process(self,val):

        self.mutex.acquire()
        global ampRamp

        if val[0] < 0.2:
            val[0]=0.0
        else:
            val[0] -= 0.2

 #       valx=self.block.process(val[0])
        ampRamp.setValue(val[0])
        print val[0]
        self.mutex.release()



read_client=ReadClient(mutex)

reader=serialreader.SerialReader(read_client,
                                 mutex,fullscale=1024,ref=0,
                                 com=COM)



reader.start()

server = pyo.Server(buffersize=64).boot()



amp=pyo.Sig(0.0)

ampRamp=pyo.SigTo(amp,time=1.0/200)

sin=pyo.Sine(700,mul=ampRamp).out()

server.gui(locals())
