from multiprocessing import *
from GretFunc import *
from shutil import rmtree
import numpy as np
import os, platform

def Node(N, n, Char):
    if N<100:
        return "Node%.2d_%s" % (n+1, Char)

    if N<1000:
        return "Node%.3d_%s" % (n+1, Char)

    if N<10000:
        return "Node%.4d_%s" % (n+1, Char)

def OutputDict(RDict, Dir):
    for item in RDict.keys():
        data=RDict.pop(item)
        name="%s%s%s.txt" % (Dir, os.path.sep, item)
        fd=open(name,"a")
        data.tofile(fd, sep="\t", format="%s")
        if platform.system()=="Windows":
            fd.write("\r")
        fd.write("\n")
        fd.close()

class GretProcess(Process):
    def __init__(self, Para):
        QSize=Para.pop('QueueSize')
        self.Para=Para
        self.queue=Queue(maxsize=QSize)

        Process.__init__(self)

    def run(self):
        #Metrics need be calculated
        Mode=self.Para.pop('ModeState')
        Rs=self.Para.pop('RandState')
        NumRand=self.Para.pop('NumRand')
        if Rs and NumRand:
            RandState=True
        else:
            RandState=False

        #Networks Files
        FileList=self.Para.pop('FileList')

        #Output Directory
        Dir=self.Para.pop('Directory')
        Dir="%s%sResult" % (Dir, os.sep)
        IsClear=self.Para.pop('IsClear')
        if not os.path.isdir(Dir):
            os.mkdir(Dir)
        elif IsClear:
            rmtree(Dir)
            os.mkdir(Dir)
        
        #Thres Array
        Th=self.Para.pop('ThresRegion')
        Range=np.arange(Th[0],Th[1]+0.5*Th[2],Th[2])
        T=len(Range)

        manager=Manager()
        queue=self.queue
        Para=self.Para
        print("Initialization")
        for File in FileList:
            print('Beginning: %s' % File)
            Subj=os.path.split(File)[1]

            M=Read(File)
            N=M.shape[0]

            R=manager.dict()
            #Network - Small World
            if Mode[0]:
                R['Cp']=np.zeros(T)
                for n in range(N):
                    node=Node(N, n, 'Cp')
                    R[node]=np.zeros(T)
                R['Lp']=np.zeros(T)
                for n in range(N):
                    node=Node(N, n, 'Lp')
                    R[node]=np.zeros(T)
                if RandState:
                    R['CpRand']=np.zeros(T)
                    for n in range(N):
                        node=Node(N, n, 'CpRand')
                        R[node]=np.zeros(T)
                    R['LpRand']=np.zeros(T)
                    for n in range(N):
                        node=Node(N, n, 'LpRand')
                        R[node]=np.zeros(T)

            #Network - Efficiency
            if Mode[1]:
                R['Eg']=np.zeros(T)
                for n in range(N):
                    node=Node(N, n, 'Eg')
                    R[node]=np.zeros(T)
                R['Eloc']=np.zeros(T)
                for n in range(N):
                    node=Node(N, n, 'Eloc')
                    R[node]=np.zeros(T)
                if RandState:
                    R['EgRand']=np.zeros(T)
                    for n in range(N):
                        node=Node(N, n, 'EgRand')
                        R[node]=np.zeros(T)
                    R['ElocRand']=np.zeros(T)
                    for n in range(N):
                        node=Node(N, n, 'ElocRand')
                        R[node]=np.zeros(T)

            #Network - Assortativity
            if Mode[2]:
                R['Ass']=np.zeros(T)
                if RandState:
                    R['AssRand']=np.zeros([T, NumRand])

            #Network - Hierarchy
            if Mode[3]:
                R['Hie']=np.zeros(T)
                if RandState:
                    R['HieRand']=np.zeros([T, NumRand])

            #Network - Synchronization
            if Mode[4]:
                R['Syn']=np.zeros(T)
                if RandState:
                    R['SynRand']=np.zeros([T, NumRand])

            #Node - Degree
            if Mode[5]:
                for n in range(N):
                    node=Node(N, n, 'Deg')
                    R[node]=np.zeros(T)

            #Node - Efficiency
            if Mode[6]:
                for n in range(N):
                    node=Node(N, n, 'Eg')
                    R[node]=np.zeros(T)

            #Node - Betweenness
            if Mode[7]:
                for n in range(N):
                    node=Node(N, n, 'Bet')
                    R[node]=np.zeros(T)
            
            P=[]
            for t in range(T):
                #Init Process
                p=RealProcess(M, Subj,
                        Mode, Para,
                        t, Range[t],
                        R, queue)
                print("Fork --> Subject: %s @ [Threshold: %2.2f] Real Network"\
                    % (Subj, Range[t]))
                queue.put("Done --> Subject: %s @ [Threshold: %2.2f] Real Network"\
                    % (Subj, Range[t]))
                p.start()
                P.append(p)
                while queue.full():
                    #P.reverse()
                    #P.pop().join()
                    #P.reverse()
                    for p in P:
                        p.join()
                    P=[]
                if RandState:
                    for rn in range(NumRand):
                        p=RandProcess(M, Subj,
                                Mode, Para,
                                t, Range[t], 
                                NumRand, rn,
                                R, queue)
                        print("Fork --> Subject: %s @ [Threshold: %2.2f] Random Network#%.4d"\
                            % (Subj, Range[t], rn+1))
                        queue.put("Done --> Subject: %s @ [Threshold: %2.2f] Random Network#%.4d"\
                            % (Subj, Range[t], rn+1))
                        p.start()
                        P.append(p)
                        while queue.full():
                            #P.reverse()
                            #P.pop().join()
                            #P.reverse()
                            for p in P:
                                p.join()
                            P=[]    
            #Start Process
            #for p in P:
            #    p.start()

            #while not queue.empty():
            #    pass

            for p in P:
                p.join()
            
            if Mode[0] and RandState:
                R['Gamma']=R['Cp']/R['CpRand']
                R['Lambda']=R['Lp']/R['LpRand']
                R['Sigma']=R['Gamma']/R['Lambda']

            if Mode[1] and RandState:
                R['GammaEff']=R['Eloc']/R['ElocRand']
                R['LambdaEff']=R['Eg']/R['EgRand']
                R['SigmaEff']=R['GammaEff']/R['LambdaEff']
            
            if Mode[2] and RandState:
                R['Ass_Z']=(R['Ass']-R['AssRand'].mean(axis=1))/\
                        (R['AssRand'].std(axis=1))
                R['AssRand']=R['AssRand'].mean(axis=1)
            
            if Mode[3] and RandState:
                R['Hie_Z']=(R['Hie']-R['HieRand'].mean(axis=1))/\
                        (R['HieRand'].std(axis=1))
                R['HieRand']=R['HieRand'].mean(axis=1)
            
            if Mode[4] and RandState:
                R['Syn_Z']=(R['Syn']-R['SynRand'].mean(axis=1))/\
                        (R['SynRand'].std(axis=1))
                R['SynRand']=R['SynRand'].mean(axis=1)
            OutputDict(R, Dir) 
        print("All Finished")    

class RealProcess(Process):
    def __init__(self, Matrix, Subj,
            State, Para,
            NThr, Thr,
            RDict, Q):
        self.Subj=Subj
        self.Matrix=Matrix
        self.State=State
        self.Para=Para
        self.NThr=NThr
        self.Thr=Thr
        self.RDict=RDict
        self.Q=Q
        Process.__init__(self)

    def run(self):
        Para=self.Para
        State=self.State
        RDict=self.RDict
        NThr=self.NThr
        M=Thres(self.Matrix, self.Thr,
                Para['NetType'], 
                Para['ThresType'],
                Para['IsNormalize'])
        N=M.shape[0]

        if State[0]:
            Cp=Clustercoeff(M, Para['ClusterAlgor'])
            Tmp=RDict['Cp']
            Tmp[NThr]=Cp.mean()
            RDict['Cp']=Tmp
            for n in range(N):
                node=Node(N, n, 'Cp')
                Tmp=RDict[node]
                Tmp[NThr]=Cp[n]
                RDict[node]=Tmp

        if State[0] or State[1]:
            Eg=Efficiency(M)
            if State[0]:
                Lp=np.zeros_like(Eg)
                Lp[Eg!=0]=1/Eg[Eg!=0]
                Tmp=RDict['Lp']
                Tmp[NThr]=1/Eg.mean()
                RDict['Lp']=Tmp
                for n in range(N):
                    node=Node(N, n, 'Lp')
                    Tmp=RDict[node]
                    Tmp[NThr]=Lp[n]
                    RDict[node]=Tmp
            if State[1]:
                Tmp=RDict['Eg']
                Tmp[NThr]=Eg.mean()
                RDict['Eg']=Tmp
                for n in range(N):
                    node=Node(N, n, 'Eg')
                    Tmp=RDict[node]
                    Tmp[NThr]=Eg[n]
                    RDict[node]=Tmp

        if State[1]:
            Eloc=LocalEfficiency(M)
            Tmp=RDict['Eloc']
            Tmp[NThr]=Eloc.mean()
            RDict['Eloc']=Tmp
            for n in range(N):
                node=Node(N, n, 'Eloc')
                Tmp=RDict[node]
                Tmp[NThr]=Eloc[n]
                RDict[node]=Tmp

        if State[2]:
            Ass=Assortativity(M)
            Tmp=RDict['Ass']
            Tmp[NThr]=Ass
            RDict['Ass']=Tmp

        if State[5]:
            Deg=Degree(M)
            for n in range(N):
                node=Node(N, n, 'Deg')
                Tmp=RDict[node]
                Tmp[NThr]=Deg[n]
                RDict[node]=Tmp

        if State[3]:
            if not State[5]:
                Deg=Degree(M)
            if not State[0]:
                Cp=Clustercoeff(M, Para['ClusterAlgor'])
            Hie=Hierarchy(Deg, Cp)
            Tmp=RDict['Hie']
            Tmp[NThr]=Hie
            RDict['Hie']=Tmp

        if State[4]:
            Syn=Synchronization(M)
            Tmp=RDict['Syn']
            Tmp[NThr]=Syn
            RDict['Syn']=Tmp

        if State[6] and not State[1]:
            Eg=Efficiency(M)
            for n in range(N):
                node=Node(N, n, 'Eg')
                Tmp=RDict[node]
                Tmp[NThr]=Eg[n]
                RDict[node]=Tmp

        if State[7]:
            Bet=Betweenness(M)
            for n in range(N):
                node=Node(N, n, 'Bet')
                Tmp=RDict[node]
                Tmp[NThr]=Bet[n]
                RDict[node]=Tmp

        data=self.Q.get()
        print(data)

class RandProcess(Process):
    def __init__(self, Matrix, Subj,
            State, Para,
            NThr, Thr,
            NumRand, LabRand,
            RDict, Q):
        self.Matrix=Matrix
        self.Subj=Subj
        self.State=State
        self.Para=Para
        self.NThr=NThr
        self.Thr=Thr
        self.NumRand=NumRand
        self.LabRand=LabRand
        self.RDict=RDict
        self.Q=Q
        Process.__init__(self)

    def run(self):
        Para=self.Para
        State=self.State
        RDict=self.RDict
        NThr=self.NThr
        NumRand=self.NumRand
        Nr=self.LabRand
        M=Thres(self.Matrix, self.Thr,
                Para['NetType'], 
                Para['ThresType'],
                Para['IsNormalize'])
        M=RandNet(M, Para['RandGen'])
        N=M.shape[0]

        if State[0]:
            Cp=Clustercoeff(M, 
                    Para['ClusterAlgor'])
            Cptmp=Cp/NumRand
            Tmp=RDict['CpRand']
            Tmp[NThr]+=Cptmp.mean()
            RDict['CpRand']=Tmp
            for n in range(N):
                node=Node(N, n, 'CpRand')
                Tmp=RDict[node]
                Tmp[NThr]+=Cptmp[n]
                RDict[node]=Tmp

        if State[0] or State[1]:
            Eg=Efficiency(M)
            if State[0]:
                Lp=np.zeros_like(Eg)
                Lp[Eg!=0]=1/Eg[Eg!=0]
                Lp=Lp/NumRand
                Tmp=RDict['LpRand']
                Tmp[NThr]+=(1/Eg.mean())/NumRand
                RDict['LpRand']=Tmp
                for n in range(N):
                    node=Node(N, n, 'LpRand')
                    Tmp=RDict[node]
                    Tmp[NThr]+=Lp[n]
                    RDict[node]=Tmp
            if State[1]:
                Eg=Eg/NumRand
                Tmp=RDict['EgRand']
                Tmp[NThr]+=Eg.mean()
                RDict['EgRand']=Tmp
                for n in range(N):
                    node=Node(N, n, 'EgRand')
                    Tmp=RDict[node]
                    Tmp[NThr]+=Eg[n]
                    RDict[node]=Tmp

        if State[1]:
            Eloc=LocalEfficiency(M)/NumRand
            Tmp=RDict['ElocRand']
            Tmp[NThr]+=Eloc.mean()
            RDict['ElocRand']=Tmp
            for n in range(N):
                node=Node(N, n, 'ElocRand')
                Tmp=RDict[node]
                Tmp[NThr]+=Eloc[n]
                RDict[node]=Tmp

        if State[2]:
            Ass=Assortativity(M)
            tmp=RDict['AssRand']
            tmp[NThr, Nr]=Ass
            RDict['AssRand']=tmp

        if State[3]:
            Deg=Degree(M)
            if not State[0]:
                Cp=Clustercoeff(M, 
                        Para['ClusterAlgor'])
            Hie=Hierarchy(Deg, Cp)
            tmp=RDict['HieRand']
            tmp[NThr, Nr]=Hie
            RDict['HieRand']=tmp

        if State[4]:
            Syn=Synchronization(M)
            tmp=RDict['SynRand']
            tmp[NThr, Nr]=Syn
            RDict['SynRand']=tmp
        data=self.Q.get()
        print(data)
