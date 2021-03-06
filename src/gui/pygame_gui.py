 #        Display stuff
import pygame,fontManager,numpy,time




DRAW_RAW_ECG=True

FPS = 20             # pygame frames per second refresh rate.


cols=[(255,0,0),(0,255,0)]


class ECGDisplay:


    """
     200Hz data ECG processing stuff
    """

    def __init__(self,surf,src):

        self.cnt=0
        self.surf=surf

        self.src=src
        self.N=surf.get_width()
        N=surf.get_width()
        self.x_points=numpy.zeros(N,dtype='i')    #  time axis

        for i in range(N):
            self.x_points[i]=i

        self.ecg_points=[]
        #  Y axis- displays
        for i in range(src.nChan):
            self.ecg_points.append(numpy.zeros(N,dtype='i'))    #  val of ECG


        self.timeLeft=0
        self.windowTime=self.src.DT*N
  

    def is_full(self):
       return self.cnt >= self.N

    #  scroll the  ECG by n samples
    def scroll(self,fact):


        print "SCROLL",fact
        # scroll by n samples
        n=int(self.N*fact)

        i1=self.N-n
        for pts in self.g_points:
            pts[0:self.N-n]=pts[n:self.N]
        self.cnt -= n
        self.timeLeft = self.timeLeft+n*self.src.DT

        # This is not very clever Eventually will be a problem  . . .
        self.peakPtrStart=0

    def reset(self):
        self.cnt=0
        self.timeLeft=self.src.time

    def draw(self):
        self.surf.fill((0,0,0))

        if self.cnt > 2:
            cnt=self.cnt
            for i,ee in enumerate(self.ecg_points):
                points=numpy.column_stack((self.x_points,ee))
                pygame.draw.lines(self.surf, cols[i], False, points[:(cnt-1)])



    def add_points(self,vals):


        for i,v in enumerate(vals):
           self.ecg_points[i][self.cnt]=self.ecg2screen(v)


        self.cnt  += 1
       #y print "ADD PTS ",self.cnt

    def f2screen(self,val):
        """
        map value -640-640  to the height
        """
        return self.surf.get_height()*0.5*(.8-val/500.0)

    def ecg2screen(self,val):
        """
        map val in range -1 to 1 to screen
        """
        return self.surf.get_height()*0.5*(1-val)

    def val2Screen(self,val):
            # moving average to screen value
            return self.surf.get_height()*(1.0-val/config.MAX_MV_AV)




space_hit=False


def run(ecg_src,
        fps=FPS,
        fullscreen=False):


    global fontMgr,space_hit
    pygame.display.init()
    clock=pygame.time.Clock()
    modes=pygame.display.list_modes()
    fontMgr = fontManager.cFontManager((('Courier New', 16), (None, 48), (None, 24), ('arial', 24)))

    caption=" HIT ESCAPE TO QUIT"

    # Allocate screen space.

    # full=modes[0]
    # MAC puts puts screen below menu so take a bit off the height.
    # dim_display=(full[0],full[1]-50)


    height=800
    width=1280

    dim_display=(width,height)


    #----------  0
    #    ECG
    #----------  y1
    #   Spectral
    #----------- y2
    #   Breath
    #----------  y3
    #     BPM                        CHAOS
    #----------- height   ----    |              |
    #                             x1           width

    y1=height
    x1=width

    dim_ecg=(width,y1)

    if fullscreen:
        display = pygame.display.set_mode(dim_display,pygame.FULLSCREEN)
    else:
        display = pygame.display.set_mode(dim_display)


    ecg_surf=pygame.Surface(dim_ecg)
    ecg_display=ECGDisplay(ecg_surf,ecg_src)
    ecg_src.read_client.ui=ecg_display


    ecg_src.start()

    """
    main gui loop
    """
    while True:


        k = pygame.key.get_pressed()

        if k[pygame.K_ESCAPE] or pygame.event.peek(pygame.QUIT):
            space_hit=True
            time.sleep(.2)
            ecg_src.quit()
            pygame.quit()
            break

        if k[pygame.K_SPACE]:
            space_hit=True


        # Make sure the data does not get tweaked during disply.
        ecg_src.mutex.acquire()

        # ECG based values  --------------------------------------------------

        ecg_display.draw()



        ecg_src.mutex.release()

        display.blit(ecg_display.surf,(0,0))

        pygame.display.flip()
        clock.tick(fps)
