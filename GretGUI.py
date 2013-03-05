import os, platform
from Tkinter import *
from tkFileDialog import *
from tkSimpleDialog import *
from multiprocessing import Process, freeze_support
from GretProcess import GretProcess

Modelist=["Network - Small World",
        "Network - Efficiency",
        "Network - Assortativity",
        "Network - Hierarchy",
        "Network - Synchronization",
        "Node - Degree",
        "Node - Efficiency",
        "Node - Betweenness"]

class Mode(Frame):
    def __init__(self , parent=None , **options):
        Frame.__init__(self , parent , **options)
        self.config(bd=5, relief=RIDGE)
        self.pack(expand=YES , fill=BOTH)
        self.State=[]
        for key in Modelist:
            var=BooleanVar(value=True)
            Checkbutton(self,
                    bd=4,
                    text=key,
                    variable=var).pack(anchor=W)
            self.State.append(var)

class Input(Frame):
    def __init__(self, parent=None, **options):
        Frame.__init__(self , parent , **options)
        self.config(bd=5, relief=RIDGE)
        self.pack(expand=YES , fill=BOTH)
        
        self.text=StringVar()
        self.text.set(os.getcwd())

        InputEntry=Frame(self)
        InputEntry.pack(side=TOP , expand=NO , fill=X)
        DirEntry=Entry(InputEntry , textvariable=self.text)
        InputButton=Button(InputEntry , 
                text="..." ,
                command=self.Select)
        DirEntry.pack(side=LEFT , expand=YES , fill=X)
        InputButton.pack(side=RIGHT , expand=NO)

        self.InputList=Listbox(self ,
                relief=SUNKEN)

        vscroll=Scrollbar(self)
        hscroll=Scrollbar(self , orient="horizontal")

        self.InputList.config(relief=SUNKEN , 
                yscrollcommand=vscroll.set ,
                xscrollcommand=hscroll.set)
        vscroll.config(command=self.InputList.yview,
                relief=RAISED)
        hscroll.config(command=self.InputList.xview,
                relief=RAISED)

        hscroll.pack(side=BOTTOM , fill=X)
        self.InputList.pack(side=LEFT,
                expand=YES, fill=BOTH)
        vscroll.pack(side=RIGHT, fill=Y)

    def Select(self):
        fname=askopenfilenames(title="Select Networks",
                filetypes = [("Brain Network","*.txt")],
                initialdir=self.text.get())
        if fname:
            if platform.system()=="Windows":
                fname=fname.replace("/","\\")
                fname=fname.split()
            fd=os.path.split(fname[0])
            self.text.set(fd[0])
            OldList=self.InputList.get(0,END)
            for name in fname:
                Flag=OldList.count(name)
                if not Flag:
                    self.InputList.insert(END,name)

class EntryFrame(Frame):
    def __init__(self, 
            parent=None, 
            Num=None,
            tag=None,
            **options):
        Frame.__init__(self , parent , **options)
        self.pack(expand=YES , fill=BOTH)

        Button(self , 
                text=tag, 
                command=self.Change
                ).pack(side=LEFT , expand=YES, fill=BOTH)
        Entry(self , 
                textvariable=Num
                ).pack(side=RIGHT , expand=NO)

    def Change(self): pass

class TypeRadio(Frame):
    def __init__(self,
            parent=None,
            var=None, Key=None, Tag=None,
            **options):
        Frame.__init__(self, parent, **options)
        self.pack(expand=YES, fill=BOTH)

        Label(self, text=Tag).pack(side=LEFT, expand=YES)
        for key in range(len(Key)):
            Radiobutton(self, text=Key[key],
                    variable=var,
                    value=key
                    ).pack(side=LEFT, expand=YES, fill=X)

class RandNetEntry(EntryFrame):
    def __init__(self, parent=None, 
            var=None, **options):
        EntryFrame.__init__(self,
                parent,
                var,
                "Random Network", **options)
        self.pack(expand=YES, fill=BOTH)

        self.var=var

    def Change(self):
        var=askinteger("Random Networks",
                "Please ENTER\
                the number of Random Networks",
                initialvalue=self.var.get())
        if not var is None: self.var.set(var)

class RandNetFrame(Frame):
    def __init__(self, parent=None, 
            NumRand=None, GenAlgor=None, **options):
        Frame.__init__(self, parent, **options)
        self.config(bd=5, relief=RIDGE)
        self.pack(expand=YES, fill=BOTH)

        RandNetEntry(self,
                NumRand,
                bd=3, relief=GROOVE
                ).pack(side=LEFT, expand=YES, fill=BOTH)
        TypeRadio(self,
                GenAlgor,
                ["Randomize Edges",
                    "Randomize Edges and Nodes"],
                "Generate Way",
                bd=3, relief=GROOVE
                ).pack(side=RIGHT, expand=YES, fill=BOTH)

class NetworkTypeFrame(TypeRadio):
    def __init__(self, parent=None, var=None, **options):
        TypeRadio.__init__(self, 
                parent, 
                var, 
                ["Binary","Weighted"],
                "Network Type",
                **options)
        self.config(bd=5, relief=RIDGE)
        self.pack(expand=YES, fill=BOTH)

class NormalizeFrame(Frame):
    def __init__(self, parent=None, Flag=None, **options):
        Frame.__init__(self, parent, **options)
        self.config(bd=5, relief=RIDGE)
        self.pack(expand=YES, fill=BOTH)

        Checkbutton(self, 
                text="Normalized Network Matrix",
                variable=Flag).pack(expand=YES, fill=BOTH)

class ClusteringFrame(TypeRadio):
    def __init__(self, parent=None, var=None, **options):
        TypeRadio.__init__(self, 
                parent, 
                var, 
                ["Barrat","Onnela"],
                "Clustering Algorithm",
                **options)
        self.config(bd=5, relief=RIDGE)
        self.pack(expand=YES, fill=BOTH)

class ThresTypeFrame(TypeRadio):
    def __init__(self, parent=None, var=None, **options):
        TypeRadio.__init__(self, 
                parent, 
                var, 
                ["Correlation Value", 
                    "Sparsity",
                    "Number of Edges"],
                "Threshold Type",
                **options)
        self.config(bd=5, relief=RIDGE)
        self.pack(expand=YES, fill=BOTH)

class ThresRegionFrame(Frame):
    def __init__(self, parent=None,
            Start=None,
            Stop=None,
            Step=None,
            **options):
        Frame.__init__(self, parent, **options)
        self.config(bd=5, relief=RIDGE)
        self.pack(expand=YES, fill=BOTH)

        ThresStart(self, Start).pack(side=TOP)
        ThresStep(self, Step).pack(side=TOP)
        ThresStop(self, Stop).pack(side=TOP)

class ThresStart(EntryFrame):
    def __init__(self, parent=None, Num=None, **options):
        self.Tag="Threshold Start"
        EntryFrame.__init__(self,
                parent, 
                Num,
                self.Tag,
                **options)
        self.pack(expand=YES, fill=BOTH)
        self.Num=Num

    def Change(self):
        Num=askfloat(self.Tag,
                "Please ENTER the START of Threshold",
                initialvalue=self.Num.get())
        if not Num is None: self.Num.set(Num)

class ThresStop(EntryFrame):
    def __init__(self, parent=None, Num=None, **options):
        self.Tag="Threshold Stop"
        EntryFrame.__init__(self,
                parent, 
                Num,
                self.Tag,
                **options)
        self.pack(expand=YES, fill=BOTH)
        self.Num=Num

    def Change(self):
        Num=askfloat(self.Tag,
                "Please ENTER the STOP of Threshold",
                initialvalue=self.Num.get())
        if not Num is None: self.Num.set(Num)

class ThresStep(EntryFrame):
    def __init__(self, parent=None, Num=None, **options):
        self.Tag="Threshold Step"
        EntryFrame.__init__(self,
                parent, 
                Num,
                self.Tag,
                **options)
        self.pack(expand=YES, fill=BOTH)
        self.Num=Num

    def Change(self):
        Num=askfloat(self.Tag,
                "Please ENTER the STEP of Threshold",
                initialvalue=self.Num.get())
        if not Num is None: self.Num.set(Num)

class OutputDirFrame(EntryFrame):
    def __init__(self, parent=None, Dir=None, **options):
        self.Tag="Results Folder"
        EntryFrame.__init__(self,
                parent,
                Dir,
                self.Tag,
                **options)
        self.pack(expand=YES, fill=BOTH)
        
        self.Dir=Dir

    def Change(self):
        Dir=askdirectory(title=self.Tag,
                initialdir=self.Dir.get())
        if not Dir is None:
            if platform.system()=="Windows":
                Dir=Dir.replace("/","\\")
            self.Dir.set(Dir)

class ClearDirFrame(Frame):
    def __init__(self, parent=None, Flag=None, **options):
        Frame.__init__(self, parent, **options)
        self.pack(expand=YES, fill=BOTH)

        Checkbutton(self, 
                text='Clear "Result" Folder',
                variable=Flag).pack(expand=YES, fill=BOTH)

class QueueFrame(EntryFrame):
    def __init__(self, parent=None, Num=None, **options):
        self.Tag="Queue Size"
        EntryFrame.__init__(self,
                parent, 
                Num,
                self.Tag,
                **options)
        self.config(bd=2, relief=RAISED)
        self.pack(expand=YES, fill=BOTH)
        self.Num=Num

    def Change(self):
        Num=askinteger(self.Tag,
                "Please ENTER the SIZE of Queue",
                initialvalue=self.Num.get())
        if not Num is None: self.Num.set(Num)

class RunStateFrame(Frame):
    def __init__(self, parent=None,
            Dir=None, IsClear=None, QueueSize=None,
            **options):
        Frame.__init__(self, parent, **options)
        self.config(bd=5, relief=RIDGE)
        self.pack(expand=YES, fill=BOTH)

        OutputDirFrame(self, Dir).pack(side=LEFT)
        ClearDirFrame(self, IsClear).pack(side=LEFT)
        QueueFrame(self, QueueSize).pack(side=LEFT)

class Config(Frame):
    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.pack(expand=YES, fill=BOTH)
        self.NetType=BooleanVar(value=1)
        self.IsNormalize=BooleanVar(value=0)
        self.ClusterAlgor=BooleanVar(value=0)

        self.ThresType=IntVar(value=1)

        self.NumRand=IntVar(value=1000)
        self.GenAlgor=BooleanVar(value=0)

        self.ThresStart=DoubleVar(value=0.1)
        self.ThresStop=DoubleVar(value=0.4)
        self.ThresStep=DoubleVar(value=0.05)
        
        self.Dir=StringVar(value=os.getcwd())
        self.IsClear=BooleanVar(value=1)
        self.QueueSize=IntVar(value=4)

        RunStateFrame(self,
                self.Dir,
                self.IsClear,
                self.QueueSize
                ).pack(side=BOTTOM, expand=YES, fill=BOTH)
        RandNetFrame(self, 
                self.NumRand, 
                self.GenAlgor
                ).pack(side=BOTTOM, expand=YES, fill=BOTH)
        ThresTypeFrame(self,
                self.ThresType
                ).pack(side=BOTTOM, expand=YES, fill=BOTH)
        ThresRegionFrame(self,
                self.ThresStart,
                self.ThresStop,
                self.ThresStep
                ).pack(side=RIGHT, expand=YES, fill=BOTH)

        NetworkTypeFrame(self, self.NetType).pack()
        NormalizeFrame(self, self.IsNormalize).pack()
        ClusteringFrame(self, self.ClusterAlgor).pack()

class Interface(Frame):
    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.pack(expand=YES, fill=BOTH)

        self.RunBtn=Button(self, 
                text="Run",
                command=self.Run,
                bd=5,
                relief=RAISED,
                width=50)
        self.RunBtn.pack(side=BOTTOM, expand=NO)
        self.Config=Config(self)
        self.Config.pack(side=BOTTOM)

        self.Mode=Mode(self)
        self.Mode.pack(side=LEFT)
        self.Input=Input(self)
        self.Input.pack(side=RIGHT)

    def Run(self):
        self.RunBtn.config(state=DISABLED)
        self.update()
        Para={}
        ModeState=[]
        for State in self.Mode.State:
            ModeState.append(State.get())
        RandState=any(ModeState[:5])
        #The metrics will be calculated
        Para['ModeState']=ModeState
        #The metrics need random networks
        Para['RandState']=RandState
        #The Input Network File List
        FileList=self.Input.InputList.get(0,END)
        Para['FileList']=FileList
        #The Type of Network: BIN or WEI
        Para['NetType']=self.Config.NetType.get()
        #Whether to normalize networks or not
        Para['IsNormalize']=self.Config.IsNormalize.get()
        #The algorithm of clustering
        Para['ClusterAlgor']=\
                self.Config.ClusterAlgor.get()
        #The Region of Threshold: Corr, Sparsity, NumEdge
        Para['ThresRegion']=[self.Config.ThresStart.get(),
                self.Config.ThresStop.get(),
                self.Config.ThresStep.get()]
        #The Type of Threshold
        Para['ThresType']=self.Config.ThresType.get()
        #The number of Random Networks
        Para['NumRand']=self.Config.NumRand.get()
        #The algorithm for generate random networks
        Para['RandGen']=self.Config.GenAlgor.get()
        #The Directory
        Para['Directory']=self.Config.Dir.get()
        #Whether to clear folder or not
        Para['IsClear']=self.Config.IsClear.get()
        #QueueSize
        Para['QueueSize']=self.Config.QueueSize.get()

        #Init a Process
        p=GretProcess(Para)
        p.start()

class MainWindow(Tk):
    def __init__(self, **options):
        Tk.__init__(self, **options)
        self.title("PyGretna")
        Interface(self).pack()

if __name__=='__main__': 
    freeze_support()
    MainWindow().mainloop()
