import serial
import threading
import sys
import time


class EcgSource (threading.Thread):

    def __init__(self,read_client,
                 mutex,
                 com=None,
                 processor=None):
        
        threading.Thread.__init__(self)
        self.daemon=True
        self.mutex=mutex
        self.read_client=read_client

        source = serial.Serial()

        source.port=com[0]
        source.baudrate=com[1]
        self.scale = 1
        self.fullScale = 1024

        # wait for opening the serial connection.
        try:
            source.open()
        except:
            print " Unable to open serial connection on ",com[0]
            print " To list ports from command line "
            print " python -m serial.tools.list_ports"
            sys.exit()

        print " Using USB serial input ",com[0]
        
        self.source=source
       
    # Read ECG values and feed the read_client
    def run(self):
       
       
     
        # Maximium value for raw ECG stream    
        ref=self.fullScale/2

        
        self.stopped=False
        
        while not self.stopped:
            

            response=self.source.readline()

            if response == None:
                    return
            print response
            
            if response=="":
                continue
            
            try:
                raw=float(response)
            except:
                print " Ignoring currupt ECG data :",response
                continue
    
            val=((raw-ref)/self.fullScale)*self.scale   # 4 is a hack until FPGA does the mult
            

            self.read_client.process(val,self)



        print " THREAD QUITTING "
            
    def quit(self):
        
        print " ASK ECG TRHEAD TO QUIT "
        
        self.stopped=True
        
        
        # join thread to avoid hanging pythons
        self.join()
        
        print " ECG THREAD QUIT "
        
        if self.fout:
            self.fout.close()
  
    def get_caption(self):
        if self.file_mode:
            return self.source.file_name
        else:
            return " LIVE "
        

