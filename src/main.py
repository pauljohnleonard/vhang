
import threading
import sys
import traceback


from filters import DCBlock

import serialreader

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

    def __init__(self,mutex):
        self.mutex=mutex
        self.block=DCBlock(.99999)


    # Read ECG values and feed the processor
    def process(self,val):


        valx=self.block.process(val[0])
        val[1]=valx
        if self.ui != None:
            if self.ui.is_full():
                if False:

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

        if self.ui != None:
            self.ui.add_points(val)


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


read_client=ReadClient(mutex)


ecg_src= serialreader.SerialReader(read_client,
                             mutex,1024,0,
                             com=COM)

import gui.pygame_gui as pygame_gui

pygame_gui.run(ecg_src,fullscreen=False)
