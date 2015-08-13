
import threading
import time
import sys
import traceback
from os.path import expanduser

import source

# Defaults
loggerRR=None
loggerECG=None

# ---- Interactive viewing or processing to dump ECG and RR
headless = False

SONIFY=False
ARDUINO=None
COM=None

    # If we are in live capture mode these need to be set to the USB port
SERIAL_PORT="/dev/tty.usbserial-14P02971"
SERIAL_PORT="/dev/tty.usbmodem1411"
BAUD_RATE=112500
COM=(SERIAL_PORT,BAUD_RATE)




class ReadClient:
    """
     Does the GUI control
     Handles values from the ECG stream.
     THis is called from the ECG thread so no gui stuff is allowed.
    """

    def __init__(self,processor,mutex):
        self.processor=processor
        self.mutex=mutex


    # Read ECG values and feed the processor
    def process(self,val,replay):


        if self.ui != None:
            if self.ui.is_full():
                if replay:

                    print " Hit key to continue "

                    pygame_gui.space_hit=False


                    self.mutex.acquire()

                    self.ui.scroll(.1)

                    self.mutex.release()

                else:

                  #  print " RESETING CNT"
                    self.mutex.acquire()
                    self.ui.reset()
                    self.mutex.release()

        self.mutex.acquire()

        self.processor.process(val)


        if self.ui != None:
            self.ui.add_points(processor)


        self.mutex.release()



def myexit():
    e = sys.exc_info()[0]
    print e
    traceback.print_exc()
    usage()
    sys.exit(2)


#


# Lock for the gui thread.
# aquire this before messing around with data that is used o  the GUI thread
mutex=threading.RLock()



class Processor:


    def __init__(self):
        self.time=0
        self.DT=0.01


    def process(self,val):
        self.val=val
        self.time += self.DT

processor=Processor()

#  read ecg on a seperate thread feeding into the processor
#  DON'T DO ANY GUI STUFF ON THIS THREAD
#  aquire the lock before playing around with and display data

read_client=ReadClient(processor,
                       mutex)


ecg_src= source.EcgSource(read_client,
                             mutex,
                             com=COM,
                             processor=processor)

import gui.pygame_gui as pygame_gui

pygame_gui.run(ecg_src,processor,
               fullscreen=False)
