 #        Display stuff
import pygame,fontManager,numpy,math,time

#  GUI STUFF
BPM_MIN_DISP=45
BPM_MAX_DISP=110



# range of breath frequencies for Spectral Display
RESFREQ_MIN=4/60.0
RESFREQ_MID=8/60.0
RESFREQ_MAX=12/60.0

# COlours for spectrogram
C_LOW=(0,0,200)
C_MID=(0,255,0)
C_HIGH=(150,0,0)


class BPMDisplay:
    
    KEY_WIDTH=40
    
    def __init__(self,surf_bpm):
        # BPM
        self.bpmScreenPtLast=None
        self.surf_bpm=surf_bpm
        self.bpmPtr=0
        self.bpm_background=(50,50,50)
        self.surf_bpm.fill(self.bpm_background)
        self.xBPMright=int((surf_bpm.get_width()*6)/6)-1
        self.xBPM_ref=-BPMDisplay.KEY_WIDTH
    # map bpm to pixels
        self.tBPMscale=10
        self.draw_bpm_key(0,0,0)
        
     	self.bpmScreenPtLast=[0,0]
        self.bpm_data=[]

    def t2screen(self,t):
        return int(t*self.tBPMscale)-self.xBPM_ref
     
    
    def bpm2screen(self,bpm):
        H=self.surf_bpm.get_height()
        return int(H-(bpm-BPM_MIN_DISP)*H/(BPM_MAX_DISP-BPM_MIN_DISP))
          
    def t_bpm2screen(self,t,bpm):
        H=self.surf_bpm.get_height()
        return [self.t2screen(t),self.bpm2screen(bpm)]
    
    def draw_bpm_key(self,bpmVal,bpmAv,bpmAvF):
        global fontMgr
        bpmLine=40
        
        pygame.draw.rect(self.surf_bpm,(0,0,0),(0,0,BPMDisplay.KEY_WIDTH, self.surf_bpm.get_height()))
       
        y=self.bpm2screen(bpmVal)
        
        pygame.draw.rect(self.surf_bpm,(0,0,255),(0,y,BPMDisplay.KEY_WIDTH,self.surf_bpm.get_height()))
      
        y=self.bpm2screen(bpmAv)
        
        pygame.draw.line(self.surf_bpm,(0,255,255),(0,y),(BPMDisplay.KEY_WIDTH,y),5)
      
        y=self.bpm2screen(bpmAvF)
        
        pygame.draw.line(self.surf_bpm,(255,255,0),(0,y),(BPMDisplay.KEY_WIDTH,y),5)
       
       
        while True:  
            y=self.bpm2screen(bpmLine)
            if y < 0:
                break
            
            if y < self.surf_bpm.get_height():
                ttt=str(bpmLine)
                fontMgr.Draw(self.surf_bpm, 'Courier New', 16, ttt, (0,y), (20,255,255))
            
            bpmLine+=5

    def draw_time_key(self):
        
        tt=int(math.ceil((self.xBPM_ref+BPMDisplay.KEY_WIDTH)/self.tBPMscale))
        wid=self.surf_bpm.get_width()
        h=self.surf_bpm.get_height()
        
        while True:
            if tt % 10 == 0:
                xx=self.t2screen(tt)
                if xx > wid:
                    return
                pygame.draw.line(self.surf_bpm,(0,0,0),(xx,0),(xx,h-15))
                str = " {}:{:0>2d}".format((tt/60),tt%60)
      
                fontMgr.Draw(self.surf_bpm, 'Courier New', 16, str, (xx-30,h-15), (60,255,255))
    
            tt+=1
            
    
    def add_point(self,t,bpm):
        self.bpm_data.append((t,bpm))
        self.draw()
        
        
    def draw(self):
        
       # PLOT the BPM based values ------------------------------------------------------------
        
        
        
        while self.bpmPtr < len(self.bpm_data):
            
            
    #             bpmNew=rrtobpm.BPMraw[self.bpmPtr][1]
    #             timeNew=rrtobpm.BPMraw[self.bpmPtr][0]
    #             
    
            bpmNew=self.bpm_data[self.bpmPtr][1]
            timeNew=self.bpm_data[self.bpmPtr][0]
             
            xNew,tmp=self.t_bpm2screen(timeNew,bpmNew)
            
            xOver = xNew-self.xBPMright
            
            if xOver > 0 :
                self.xBPM_ref += xOver
                self.surf_bpm.scroll(-xOver)
                pygame.draw.rect(self.surf_bpm,self.bpm_background,(self.xBPMright-xOver+1,0,xOver,self.surf_bpm.get_height()))
                self.bpmScreenPtLast[0] -= xOver
                
                
            average=average_fast=bpm
            self.draw_bpm_key(bpmNew,average,average_fast)
             
            
            bpmScreenPtNew=self.t_bpm2screen(timeNew,bpmNew)
            if self.bpmScreenPtLast != None:
                pygame.draw.line(self.surf_bpm,(0,255,0),self.bpmScreenPtLast,bpmScreenPtNew,5)
                 
                        
            self.bpmLast=bpmNew
            self.bpmScreenPtLast=bpmScreenPtNew
            self.bpmPtr += 1
            self.draw_time_key()
     
class SpectralDisplay:
     
     
    def __init__(self,surf,spectral):
        self.surf=surf
        self.spectral=spectral
    
        
        
    def draw(self):
        if self.spectral.XX == None:
            return
             
        self.surf.fill((0,0,0))
        
        n=self.surf.get_height()
        wid=self.surf.get_width()
          
        cnt=0
        fact=0.2
        XX=self.spectral.XX
        freqs=self.spectral.freqBin
        
        cnt=0
        WID=20
        WIDO2=WID/2
        str=""
        for xx in XX:
            
            val=abs(xx)
            val=val*fact
            fBin=self.spectral.freqBin[cnt]
            if fBin < RESFREQ_MIN:
                col=C_LOW
            elif fBin < RESFREQ_MID:
                fact1=(RESFREQ_MID-fBin)/(RESFREQ_MID-RESFREQ_MIN)
                fact2=1.0-fact1
                r=C_LOW[0]*fact1+C_MID[0]*fact2
                g=C_LOW[1]*fact1+C_MID[1]*fact2
                b=C_LOW[2]*fact1+C_MID[2]*fact2
                col=(r,g,b)
            elif self.spectral.freqBin[cnt] < RESFREQ_MAX:
                fact1=(RESFREQ_MID-fBin)/(RESFREQ_MID-RESFREQ_MAX)
                fact2=1.0-fact1
                r=C_HIGH[0]*fact1+C_MID[0]*fact2
                g=C_HIGH[1]*fact1+C_MID[1]*fact2
                b=C_HIGH[2]*fact1+C_MID[2]*fact2
                col=(r,g,b)
            else:
                col=C_HIGH
#             else:
#                 str+= "%3.2f "      % (spectral.freqs[cnt]*60)
#                 col=(255,255,0)
#                 
            pygame.draw.line(self.surf,col,(cnt*WID+WIDO2,n-1),(cnt*WID+WIDO2,n-val),WID-1)
        
            cnt+=1
            if cnt*WID> wid:
                break
             

class Gui:
    
    
    def __init__(self):    
        global fontMgr
        pygame.init()
        modes=pygame.display.list_modes()
        fontMgr = fontManager.cFontManager((('Courier New', 16), (None, 48), (None, 24), ('arial', 24)))
        
        height=400
        width=600
        
        dim_display=(width,height)
        
        dim_bpm=dim_display
    
        self.display = pygame.display.set_mode(dim_display)
                    
        #  GUI stuff ---------------------------------------------------------
        
        self.bpm_surf=pygame.Surface(dim_bpm)
        self.bpm_display=BPMDisplay(self.bpm_surf)
        
    def bpm(self,t,bpm):
        self.bpm_display.add_point(t,bpm)
        
        self.display.blit(self.bpm_surf,(0,0))
        pygame.display.flip()

        print t,bpm
        
        
if __name__ == "__main__":
    
    
    class HRV:
    
        def __init__(self,data_file):
            self.fin=open(data_file,"r")
               
        def read_data(self):
                line=self.fin.readline()
                if line:
                       
                    toks=line.split()
                    
                    tim=float(toks[0])
                    bpm=float(toks[1])
                
                    return tim,bpm
                
                return None
        

    hrv=HRV("../../../../wellstoneData/cloud/rose_session_1_Aug13_17_00_27.hrv")
    
    gui=Gui()
    
    while True:
        
        tim,bpm=hrv.read_data()
        if tim ==  None:
            break
        
        gui.bpm(tim,bpm)
        time.sleep(.5)