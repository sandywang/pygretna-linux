import os, platform
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
from Tkinter import *
from GretGUI import EntryFrame, TypeRadio
from GretGUI import ThresStart, ThresStop
from tkFileDialog import askopenfilename
from GretFunc import Read
from tkSimpleDialog import askfloat

def regress(y, X):
    if len(X.shape)==1:
        X=X[:,np.newaxis]
    n, ncolX=X.shape
    Q, R=np.linalg.qr(X)
    Xrank=np.linalg.matrix_rank(X)
    if Xrank < ncolX:
        R=R[0:Xrank,0:Xrank]
        Q=Q[:,0:Xrank]
    R=np.linalg.inv(R)
    Q=Q.transpose()
    b=R.dot(Q).dot(y)
    if Xrank < ncolX:
        tmp=np.zeros(ncolX)
        tmp[0:Xrank]=b
        b=tmp
    yhat=X.dot(b)
    r=y-yhat
    SSE=(r**2).sum()
    
    return b, r, SSE

def ttest2(Smp1, Smp2, Cov=None):
    y=np.concatenate((Smp1,Smp2))
    GroupL=np.concatenate((np.ones_like(Smp1), 
        np.ones_like(Smp2)*(-1)))
    GroupL=GroupL[:,np.newaxis]
    Df, =y.shape
    Df-=2
    if Cov is None:
        Cov=np.ones_like(GroupL)
        CovG=np.concatenate((Cov, GroupL), axis=1)
    else:
        Df-=Cov.shape[1]
        Cov=np.concatenate(
                (Cov, np.ones_like(GroupL)), axis=1)
        CovG=np.concatenate((Cov, GroupL), axis=1)

    b, r, SSE_H=regress(y, Cov)
    b, r, SSE=regress(y, CovG)

    F=(SSE_H-SSE)/(SSE/Df)
    P=1-st.f.cdf(F, 1, Df)

    return P

def PlotTTest2(XStart, XStop, Samp1, Samp2, Cov, PThr):
    FileName1=os.path.split(Samp1)[1]
    FileName1=os.path.splitext(FileName1)[0]
    FileName2=os.path.split(Samp2)[1]
    FileName2=os.path.splitext(FileName2)[0]
    
    Samp1=Read(Samp1)
    Samp2=Read(Samp2)

    if Cov is not None:
        Cov=Read(Cov)
        if len(Cov.shape)==1:
            Cov=Cov[:,np.newaxis]

    Mean1=Samp1.mean(axis=0)
    Mean2=Samp2.mean(axis=0)

    delta=(XStop-XStart)/(Mean1.shape[0]-1)
    if delta!=0:
        X=np.arange(XStart, XStop+0.5*delta, delta)
    else:
        delta=1
        XStart=1
        XStop=Mean1.shape[0]
        X=np.arange(Mean1.shape[0])

    Ymax=np.max([Mean1, Mean2])
    Ymin=np.min([Mean1, Mean2])
    Ylimit=Ymax-Ymin
    plt.ylim(Ymin-0.1*Ylimit, Ymax+0.5*Ylimit)
    plt.xlim(XStart-delta, XStop+delta)

    if PThr==0:
        Leg1, Leg2=plt.plot(X, Mean1, 'kx-', 
                X, Mean2, 'kx--')
        plt.legend((Leg1,Leg2),
            (FileName1, FileName2))
    else:
        P=np.zeros_like(Mean1, dtype="bool")
        for i in range(len(P)):
            P[i]=ttest2(Samp1[i,:], Samp2[i,:], Cov)<PThr
        if any(P==0):
            Leg1, Leg2=plt.plot(X, Mean1, 'kx-', 
                    X, Mean2, 'kx--')
            plt.legend((Leg1,Leg2),
                (FileName1, FileName2))
        else:
            YStar=np.max([Mean1, Mean2], axis=0)
            XStar=X
            YStar=YStar[P]
            XStar=XStar[P]

            Leg1, Leg2, Leg3=plt.plot(X, Mean1, 'kx-', 
                    X, Mean2, 'kx--',
                    XStar, YStar, 'ks')
            plt.legend((Leg1,Leg2,Leg3),
                (FileName1, FileName2, 'p < %s' % str(PThr)))

    plt.show()

def PlotCorr(Samp1, Samp2, Cov, PThr): 
    FileName1=os.path.split(Samp1)[1]
    FileName1=os.path.splitext(FileName1)[0]
    FileName2=os.path.split(Samp2)[1]
    FileName2=os.path.splitext(FileName2)[0]
    
    Samp1=Read(Samp1)
    Samp2=Read(Samp2)

    if Cov is not None:
        Cov=Read(Cov)
        if len(Cov.shape)==1:
            Cov=Cov[:,np.newaxis]
        Cov=np.concatenate(
                (Cov, np.ones_like(Samp1)), axis=1)
        b, Samp1, SSE=regress(Samp1, Cov)
        b, Samp2, SSE=regress(Samp2, Cov)

    b, intercept=np.polyfit(Samp1, Samp2, 1)
    r=np.corrcoef(Samp1, Samp2)[0,1]

    Line=b*Samp1+intercept

    Xmax=Samp1.max()
    Xmin=Samp1.min()
    Ymax=np.max([Samp2, Line])
    Ymin=np.min([Samp2, Line])
    Xlimit=Xmax-Xmin
    Ylimit=Ymax-Ymin

    plt.plot(Samp1, Samp2, 'kx', 
        Samp1, Line, 'k-')
    func="y=%.2fx+%.2f, r=%.2f" % (b, intercept, r)
    plt.text(Xmax-0.2*Xlimit, Ymax+0.05*Ylimit,
            '$%s$' % func)

    plt.xlim(Xmin-0.1*Xlimit, Xmax+0.3*Xlimit)
    plt.ylim(Ymin-0.1*Ylimit, Ymax+0.3*Ylimit)
    plt.xlabel("X (Sample 1)")
    plt.ylabel("Y (Sample 2)")

    plt.show()

class PValueEntryFrame(EntryFrame):
    def __init__(self, parent=None,
            Num=None, Tag=None, **options):
        EntryFrame.__init__(self,
                parent,
                Num,
                Tag,
                **options)
        self.pack(expand=YES, fill=BOTH)
        self.Num=Num
        self.Tag=Tag

    def Change(self):
        Num=askfloat(self.Tag,
                "Please ENTER P Threshold",
                initialvalue=self.Num.get())
        if not Num is None: self.Num.set(Num)

class SampEntryFrame(EntryFrame):
    def __init__(self, parent=None,
            Str=None, Tag=None,
            **options):
        EntryFrame.__init__(self, 
                parent,
                Str,
                Tag,
                **options)
        self.config(bd=5, relief=RIDGE)
        self.pack(expand=YES, fill=BOTH)
        self.Str=Str
        self.Tag=Tag

    def Change(self):
        fname=self.Str.get()
        if fname:
            if platform.system()=="Windows":
                fname=fname.replace("/","\\")
            fd=os.path.split(fname)
            Dir=fd[0]
        else:
            Dir=os.getcwd()

        fname=askopenfilename(title="Select %s" % self.Tag,
                filetypes=[("Sample Text", "*.txt"),
                    ("All Files", "*.*")],
                initialdir=Dir)
        if fname:
            self.Str.set(fname)

class PlotTypeFrame(TypeRadio):
    def __init__(self, parent=None, var=None, 
            XRegion=None, **options):
        TypeRadio.__init__(self,
                parent,
                var,
                ["Two Sample T test", "Correlation"],
                "Statistical Type",
                **options)
        self.var=var
        self.config(bd=5, relief=RIDGE)
        self.pack(expand=YES, fill=BOTH)

class XRegion(Frame):
    def __init__(self, parent=None,
            Start=None,
            Stop=None,
            **options):
        Frame.__init__(self, parent, **options)
        self.config(bd=5, relief=RIDGE)
        self.pack(expand=YES, fill=BOTH)

        ThresStart(self, Start).pack(side=LEFT)
        ThresStop(self, Stop).pack(side=RIGHT)

class StatsMain(Frame):
    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.pack(expand=YES, fill=BOTH)

        self.PlotType=BooleanVar()
        self.Samp1FileName=StringVar()
        self.Samp2FileName=StringVar()
        self.CovFileName=StringVar()
        self.PThr=DoubleVar()
        self.XStart=DoubleVar()
        self.XStop=DoubleVar()

        PlotTypeFrame(self, self.PlotType).pack()
        SampEntryFrame(self, 
                self.Samp1FileName,
                "Sample #1").pack()
        SampEntryFrame(self, 
                self.Samp2FileName,
                "Sample #2").pack()
        SampEntryFrame(self, 
                self.CovFileName,
                "Covarites").pack()
        XRegion(self, self.XStart, self.XStop).pack()
        PValueEntryFrame(self, 
                self.PThr,
                "P Threshold").pack(side=LEFT, expand=NO)
        Button(self,
                text="Fetch",
                command=self.Run,
                bd=2,
                relief=RAISED).pack(side=RIGHT,
                        expand=YES, fill=BOTH)
    
    def Run(self):
        Samp1=self.Samp1FileName.get()
        Samp2=self.Samp2FileName.get()
        Cov=self.CovFileName.get()
        PThr=self.PThr.get()
        if not os.path.isfile(Cov):
            Cov=None
        IsCorr=self.PlotType.get()

        if IsCorr: 
            PlotCorr(Samp1, Samp2, Cov, PThr)
        else:
            XStart=self.XStart.get()
            XStop=self.XStop.get()
            PlotTTest2(XStart, XStop,
                    Samp1, Samp2,
                    Cov, PThr)

if __name__=='__main__':
    root=Tk()
    StatsMain(root).pack()
    root.mainloop()
