import numpy as np
import os

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
    
class DistFile(object):
    def __init__(self, distfname=None):
        try:
            self.read(distfname)
        except:
            self.distArr=np.array([])
            self.dtArr=np.array([])
            self.nptsArr=np.array([])
            self.T0Arr=np.array([])
            self.VredArr=np.array([])
        return
    
    def read(self, distfname):
        """
        Read Distance file 
        DIST DT NPTS T0 VRED
        """
        InArr=np.loadtxt(distfname)
        self.distArr=InArr[:,0]
        self.dtArr=InArr[:,1]
        self.nptsArr=InArr[:,2]
        self.T0Arr=InArr[:,3]
        self.VredArr=InArr[:,4]
        return
    
    def write(self, distfname):
        outArr=np.append(self.distArr, self.dtArr)
        outArr=np.append(outArr, self.nptsArr)
        outArr=np.append(outArr, self.T0Arr)
        outArr=np.append(outArr, self.VredArr)
        outArr=outArr.reshape(5, self.distArr.size)
        outArr=outArr.T
        np.savetxt(distfname, outArr, fmt='%f %f %d %f %f')
        return
    
    def add(self, dist, dt=0.1, N2=14, T0=0.0, Vred=0.0):
        """Add a single distance point
        -----------------------------------------------------------------------------------------------------
        Input Parameters:
        dist     - distance for origin point
        dt         - sampling interval in synthetic seismograms
        N2        - NPTS = 2**N2
        T0         - time of first sample is T0 + DIST/VRED
        Vred     - see above
        
        Output:
        self.distArr, dtArr, nptsArr, T0Arr, VredArr
        -----------------------------------------------------------------------------------------------------
        """
        self.distArr=np.append(self.distArr, dist)
        self.dtArr=np.append(self.dtArr, dt)
        self.nptsArr=np.append(self.nptsArr, 2**N2)
        self.T0Arr=np.append(self.T0Arr, T0)
        self.VredArr=np.append(self.VredArr, Vred)
        return
    
    def addEqualDist(self, dist0, dD, Nd, dt=0.1, N2=14, T0=0.0, Vred=0.0):
        """Add equal distance list.
        -----------------------------------------------------------------------------------------------------
        Input Parameters:
        dist0    - distance for origin point
        dD       - distance interval
        Nd       - number of distance point 
        dt         - sampling interval in synthetic seismograms
        N2        - NPTS = 2**N2
        T0         - time of first sample is T0 + DIST/VRED
        Vred     - see above
        
        Output:
        self.distArr, dtArr, nptsArr, T0Arr, VredArr
        -----------------------------------------------------------------------------------------------------
        """
        self.distArr=np.append(self.distArr, np.arange(Nd)*dD+dist0 )
        self.dtArr=np.append(self.dtArr, np.ones(Nd)*dt)
        self.nptsArr=np.append(self.nptsArr, np.ones(Nd)*2**N2)
        self.T0Arr=np.append(self.T0Arr, np.ones(Nd)*T0)
        self.VredArr=np.append(self.VredArr, np.ones(Nd)*Vred)
        return
    
class DispCurve(object):
    def __init__(self, period=np.array([]), Vph=np.array([]), Vgr=np.array([]), header={'type': 'N/A', 'mode': -1}):
        self.period=period
        self.Vph=Vph
        self.Vgr=Vgr
        self.header=header
        if period.size !=Vph.size and period.size !=Vgr.size:
            raise ValueError('Inconsistent dispersion curve!')
        return
    
    def gethdr(self, instr, verbose=True):
        strLst=instr.split()
        self.header={'type': strLst[0], 'mode': int(strLst[4])}
        if verbose ==True:
            print 'Read dispersion curve for:', instr
        return
    
    def write(self, outfname, datatype='phase'):
        if datatype=='phase':
            outArr=np.append(self.period, self.Vph)
            outArr=outArr.reshape((2, self.period.size))
            outArr=outArr.T
            np.savetxt(outfname, outArr, fmt='%g')
            print 'Write dispersion curve for:', self.header['type'], 'mode',self.header['mode']
        else:
            outArr=np.append(self.period, self.Vgr)
            outArr=outArr.reshape((2, self.period.size))
            outArr=outArr.T
            np.savetxt(outfname, outArr, fmt='%g')
            print 'Write dispersion curve for:', self.header['type'], 'mode',self.header['mode']
        return
    
    def InterpDisp(self, T0=5., dT=1., NT=155):
        Tinterp=T0+np.arange(NT)*dT
        if self.Vph.size == self.period.size:
            self.Vph=np.interp(Tinterp, self.period, self.Vph)
        if self.Vgr.size == self.period.size:
            self.Vgr=np.interp(Tinterp, self.period, self.Vgr)
        self.period=Tinterp
        return
        
class DispFile(object):
    def __init__(self, dispfname=None):
        self.DispLst={}
        # self.ModeLst=np.array([])
        if os.path.isfile(dispfname):
            self.read(dispfname)
        return
    
    def read(self, dispfname=None):
        with open(dispfname, 'r') as f:
            for line in f.readlines():
                cline=line.split()
                if len(cline)==0:
                    continue
                if len(cline)==5:
                    try:
                        self.DispLst[dispcurve.header['mode']]=dispcurve
                        dispcurve=DispCurve()
                        dispcurve.gethdr(line)
                    except:
                        dispcurve=DispCurve()
                        dispcurve.gethdr(line)
                    continue
                if is_int(cline[0]):
                    dispcurve.period=np.append( dispcurve.period, float(cline[1]) )
                    dispcurve.Vph=np.append( dispcurve.Vph, float(cline[2]) )
            self.DispLst[dispcurve.header['mode']]=dispcurve
        return
                
    def write(self, outfname, mode=0, T0=5., dT=1., NT=155 ):
        if T0!=None and dT != None and NT !=None:
            self.DispLst[mode].InterpDisp(T0=T0, dT=dT, NT=NT )
        self.DispLst[mode].write(outfname)
        return
    