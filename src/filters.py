__author__ = 'pjl'

import array,math

def make_array(N,init_val=0.0):
    #return array.array('d',N*[init_val])      #  array of floats broken in micropython
    return N*[init_val]

def halfLifeFactors(nsamp):
#  fact ^ nsamp = 0.5
#  nsamp*ln(fact) = ln(0.5)
#  ln(fact)= ln(0.5)/nsamp
#  fact=exp(ln(0.5)/nsamp)

    fact=math.exp(math.log(0.5)/nsamp)
    return fact,1.0-fact


class Median:

    def __init__(self,N,init_val=0.0):
        self.N=N
        self.x=make_array(N,float(init_val))
        self.ptr=0
        self.N_MED=int(N/2)

    def process(self,data):


        self.x[self.ptr]=data

        self.ptr += 1

        if self.ptr == self.N:
            self.ptr=0

        return self

    def median_val(self):
        return  sorted(self.x)[self.N_MED]




class DCBlock:
    """
    https://ccrma.stanford.edu/~jos/filters/DC_Blocker.html
    """

    def __init__(self,R):
        self.R=R
        self.yLast=0
        self.xLast=0
        self.y=0.0

    def process(self,x):

        self.y=x-self.xLast+self.yLast*self.R

        self.xLast=x
        self.yLast=self.y

        return self.y

"""
static int y1 = 0, y2 = 0, x[26], n = 12;
int y0;
x[n] = x[n + 13] = data;
y0 = (y1 << 1) - y2 + x[n] - (x[n + 6] << 1) + x[n + 12];
y2 = y1;
y1 = y0;
y0 >>= 5;
if(--n < 0)
n = 12;
return(y0);
"""
class LPF:

    def __init__(self):
        self.y1 = 0
        self.y2 = 0
        self.x=make_array(26)
        self.n = 12
        self.y0=0.0


    def process(self,data):

        self.x[self.n] = self.x[self.n + 13] = data;
        self.y0 = 2*self.y1 - self.y2 + self.x[self.n] - (2*self.x[self.n + 6]) + self.x[self.n + 12];
        self.y2 = self.y1
        self.y1 = self.y0
        self.y0 *= 32
        self.n -= 1
        if self.n < 0:
            self.n = 12
        return self.y0

"""
static int y1 = 0, x[66], n = 32;
int y0;
x[n] = x[n + 33] = data;
y0 = y1 + x[n] - x[n + 32];
y1 = y0;
if(--n < 0)
n = 32;
return(x[n + 16] - (y0 >> 5));
}
"""

class HPF:

    def __init__(self):
        self.y1 = 0.0
        self.x=make_array(66)
        self.n = 32
        self.y0=0.0

    def process(self,data):

        self.x[self.n] = self.x[self.n + 33] = data;
        self.y0 = self.y1 + self.x[self.n] - self.x[self.n + 32]
        self.y1 = self.y0;
        self.n -=1
        if self.n < 0:
            self.n = 32
        return self.x[self.n+16]-self.y0/32.0


"""
int Derivative(int data)
{
int y, i;
static int x_derv[4];
/*y = 1/8 (2x( nT) + x( nT - T) - x( nT - 3T) - 2x( nT -  4T))*/
y = (data << 1) + x_derv[3] - x_derv[1] - ( x_derv[0] << 1);
y >>= 3;
for (i = 0; i < 3; i++)
x_derv[i] = x_derv[i + 1];
x_derv[3] = data;
return(y);
"""
class Dervivative:

    def __init__(self):
        self.y = 0
        self.x_derv=make_array(4)

    def process(self,data):

        self.y = 2*data + self.x_derv[3] -self.x_derv[1]- 2*self.x_derv[0]
        self.y = self.y/8       #  don't really need this using floats
        self.x_derv[0]=self.x_derv[1]
        self.x_derv[1]=self.x_derv[2]
        self.x_derv[2]=self.x_derv[3]
        self.x_derv[3]=data
        return self.y

"""
static int x[32], ptr = 0;
static long sum = 0;
long ly;
int y;
if(++ptr == 32)
ptr = 0;
sum -= x[ptr];
sum += data;
x[ptr] = data;
ly = sum >> 5;
if(ly > 32400) /*check for register overflow*/
y = 32400;
else
y = (int) ly;
return(y);
"""

class MovingAverge:

    def __init__(self):
        self.sum = 0
        self.ptr = 0
        self.x=make_array(32)

    def process(self,data):

        self.ptr+=1
        if self.ptr== 32:
            self.ptr=0
        self.sum -= self.x[self.ptr]
        self.sum += data
        self.x[self.ptr]=data

        return self.sum/32.0


class MovingAvergeN:

    def __init__(self,N):
        self.sum = 0.0
        self.ptr = 0
        self.x=make_array(N)
        self.N=N

    def process(self,data):

        self.ptr+=1
        if self.ptr == self.N:
            self.ptr=0
        self.sum -= self.x[self.ptr]
        self.sum += data
        self.x[self.ptr]=data

        return self.sum/self.N

class MovingDecayAverge:

    def __init__(self,samps_per_half_life,init_value):
        self.sum = init_value
        self.ptr = 0
        self.fact1,self.fact2=halfLifeFactors(samps_per_half_life)


    def process(self,data):

        self.sum=self.sum*self.fact1+data*self.fact2
        return self.sum

    def get_value(self):
        return self.sum


class Delay:

    def __init__(self,N):

        self.buff=make_array(N)
        self.N=N
        self.ptr=0
        self.ret=0


    def process(self,data):

        self.ret=self.buff[self.ptr]
        self.buff[self.ptr]=data
        self.ptr+=1

        if self.ptr == self.N:
            self.ptr=0

        return self.ret



