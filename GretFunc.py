import numpy as np
from random import randrange,shuffle
def Diag(Matrix):
    M=abs(Matrix)
    M=M-np.diag(M.diagonal())
    return M

def Read(FileName):
    Matrix=np.genfromtxt(FileName,
            autostrip=True)
    return Matrix


def Thres(Matrix , thr , 
        NetType=1 ,ThresType=0, IsNorm=0):
    Matrix=Diag(Matrix)
    N=Matrix.shape[0]

    if ThresType==0:
        rthr=thr
    else:
        if ThresType==1:
            sparsity=thr
            K=int(np.ceil(sparsity*N*(N-1)))
        else:
            K=int(2*thr)
        
        Wvec=Matrix.flatten(1)
        Wvec.sort()
        rthr=Wvec[-K]

    if rthr==0:
        A=Matrix>rthr
    else:
        A=Matrix>=rthr
        
    if NetType:
        A=Matrix*A
        if IsNorm:
            A=A/A.max()
    return A

def RandNet(Matrix , NetAlgorithm=0):
    Arand=Matrix.copy()
    TrilArand=np.tril(Arand)

    [i1,j1]=TrilArand.nonzero()
    i1.setflags(write=True)
    j1.setflags(write=True)
    Ne=i1.size

    if NetAlgorithm==1:
        if TrilArand.dtype=="bool":
            K=TrilArand.sum()
            N=TrilArand.shape[0]

            randp=np.arange(N*(N-1)/2)
            shuffle(randp)

            Value=np.zeros(randp.shape,dtype="bool")
            Value[randp[0:K]]=True

            a=np.ones([N,N],dtype="bool")
            a=np.tril(a,-1)

            Arand=np.zeros([N,N],dtype="bool")
            Arand[a!=0]=Value
            Arand=Arand+Arand.conj().transpose()

            return Arand
        else:    
            Arand=Arand!=0

    ntry=2*Ne

    for i in np.arange(ntry):
        e1=randrange(Ne)
        e2=randrange(Ne)
        v1=i1[e1]
        v2=j1[e1]
        v3=i1[e2]
        v4=j1[e2]

        if v1!=v3 and v1!=v4 and v2!=v3 and v2!=v4:
            if bool(randrange(2)):
                Temp=v3
                v3=v4
                v4=Temp

            if Arand[v1,v3]==0 and Arand[v2,v4]==0:
                Arand[v1,v3]=Arand[v1,v2]
                Arand[v2,v4]=Arand[v3,v4]
                Arand[v3,v1]=Arand[v2,v1]
                Arand[v4,v2]=Arand[v4,v3]

                Arand[v3,v4]=0
                Arand[v2,v1]=0
                Arand[v4,v3]=0
                Arand[v1,v2]=0

                i1[e1]=v1
                j1[e1]=v3
                i1[e2]=v2
                j1[e2]=v4

    if NetAlgorithm==1:
        weivec=TrilArand[TrilArand!=0]
        shuffle(weivec)
        Mid=np.tril(Arand)
        Mid[Mid!=0]=weivec
        Arand=Mid+Mid.conj().transpose()

    return Arand        

def Clustercoeff(Matrix , Algorithm=0):
    if Algorithm==1:
        W=Matrix.copy()
        A=W.astype("bool").astype("float")
        S=W**(1./3)+(W.conj().transpose())**(1./3)
        
        K=(A+A.conj().transpose()).sum(axis=1)
        S=S.dot(S.dot(S))
        cyc3=S.diagonal()/2.
        K[cyc3==0]=np.inf
        A=A.dot(A)
        CYC3=K*(K-1)-2*(A.diagonal())

        cci=cyc3/CYC3

        return cci

    N=Matrix.shape[0]
    cci=np.zeros(N)
    for i in np.arange(N):
        [NV,]=Matrix[i,:].nonzero()
        if NV.size<2:
            cci[i]=0
        else:
            nei=Matrix[NV,:]
            nei=nei[:,NV]
            [X,Y]=nei.nonzero()
            cci[i]=float(Matrix[i,NV[X]].sum()\
                    +Matrix[i,NV[Y]].sum())/\
                    (2*(NV.size-1)*float(Matrix[i,:].sum()))
    return cci

def Degree(Matrix):
    ki=Matrix.sum(axis=0)
    return ki

def Efficiency(Matrix):
    N=Matrix.shape[0]
    D=Distance(Matrix)

    D=D+np.diag(np.ones(N)*np.inf)
    D=1/D

    gEi=D.sum(axis=0)/(N-1)

    return gEi

def LocalEfficiency(Matrix):
    N=Matrix.shape[0]
    LocEi=np.zeros(N)

    for i in np.arange(N):
        [NV,]=Matrix[i,:].nonzero()
        if len(NV)>1:
            B=Matrix[:,NV]
            B=B[NV,:]
            LocEi[i]=Efficiency(B).mean()

    return LocEi

def Distance(Matrix):
    N=Matrix.shape[0]
    G=Matrix.copy()
    G[G.nonzero()]=1/G[G.nonzero()]
    D=np.ones_like(G)*np.inf
    D[np.eye(N).nonzero()]=0

    for i in np.arange(N):
        S=np.ones(N,dtype="bool")
        G1=G.copy()
        V=np.array([i])
        while True:
            S[V]=False
            G1[:,V]=0

            for v in V:
                [Nei,]=G1[v,:].nonzero()
                for w in Nei:
                    D[i,w]=min(D[i,w],D[i,v]+G1[v,w])

            [s,]=S.nonzero()
            if s.size==0:
                break
            else:
                minD=D[i,s].min()
                if minD==np.inf:
                    break

            B=D[i,:]==minD
            [V,]=B.nonzero()
    return D

def Assortativity(Matrix):
    H=Matrix.sum()/2
    Mat=Matrix.astype("bool")
    deg=Mat.sum(axis=0)
    [i,j]=(np.triu(Matrix,1)).nonzero()
    v=Matrix[i,j]

    K=len(i)
    degi=np.zeros(K)
    degj=np.zeros_like(degi)
    for k in np.arange(K):
        degi[k]=deg[i[k]]
        degj[k]=deg[j[k]]

    C=(v*degi*degj).sum()/H -\
            ((((0.5*v*(degi+degj)).sum()/H)**2))
    M=((0.5*v*(degi**2+degj**2)).sum()/H) -\
            ((0.5*v*(degi+degj)).sum()/H)**2

    r=C/M
    return r

def Hierarchy(ki,cci):
    Index=ki.astype("bool")*cci.astype("bool")
    [i,]=Index.nonzero()
    ki=ki[i]
    cci=cci[i]
    if not all(cci) or not all(ki):
        return np.nan

    [b , a]=np.polyfit(np.log(ki),np.log(cci),1)

    return -b

def Synchronization(Matrix):
    Deg=Matrix.sum(axis=0)
    
    D=np.diag(Deg,0)
    G=D-Matrix

    Eigenvalue=np.linalg.eig(G)[0]
    Eigenvalue.sort()
    S=Eigenvalue[1]/Eigenvalue[-1]

    return S

def Modularity(Matrix):
    N=Matrix.shape[0]
    e=Matrix.copy()/Matrix.sum()

    cs=e.sum(axis=0)

    Ci=np.arange(N)
    Ci_tmp=Ci

    Q=e.trace()-e.dot(e).sum()
    Q_tmp=Q

    while e.shape[0]>1:
        Cs=cs[np.newaxis,:]*cs[:,np.newaxis]*(e>0)

        Ls=np.kron(np.ones((e.shape[0],1)),cs)
        Ls_tmp=Ls.transpose()
        Ls_tmp=Ls-Ls_tmp
        Ls=Ls-Ls_tmp*(Ls_tmp>0)
        Ls[Ls==0]=np.inf

        dQ=2*(e-Cs)
        dQp=dQ/Ls
        
        [i,j]=(dQp==dQp.max()).nonzero()
        i=i[0]
        j=j[0]
        if i>j:
            tmp=i
            i=j
            j=tmp

        loop_best_dQp=dQp[i,j]
        saved_dQ=dQ[i,j]

        Ci_tmp[Ci_tmp==j]=i
        Ci_tmp[Ci_tmp>j]=Ci_tmp[Ci_tmp>j]-1

        e[i,:]=e[i,:]+e[j,:]
        e[:,i]=e[:,i]+e[:,j]
        e[i,i]=0
        e[j,:]=0
        e[:,j]=0
        [n,]=e.sum(axis=0).nonzero()
        e=e[n,:]
        e=e[:,n]

        cs[i]=cs[i]+cs[j]
        cs[j]=0
        [n,]=cs.nonzero()
        cs=cs[n]

        Q_tmp=Q_tmp+saved_dQ
        if Q_tmp>Q:
            Q=Q_tmp
            Ci=Ci_tmp.copy()

    Node=np.arange(1,N+1)
    Mode=list(np.empty(Ci.max()))
    for i in np.arange(Ci.max()):
        [n,]=(Ci==i).nonzero()
        Mode[i]=Node[n]

    M=[Q,Mode]

    return M

def Betweenness(Matrix):
    N=Matrix.shape[0]
    G=Matrix.copy()
    G[G.nonzero()]=1/G[G.nonzero()]
    D=np.ones_like(G)*np.inf
    D[np.eye(N).nonzero()]=0
    NP=np.eye(N)

    BC=np.zeros(N)
    for i in np.arange(N):
        S=np.ones(N,dtype="bool")
        P=np.zeros(G.shape,dtype="bool")
        Q=np.zeros(N,dtype="int")
        q=N-1

        G1=G.copy()
        V=np.array([i])

        while True:
            S[V]=False
            G1[:,V]=0

            for v in V:
                Q[q]=v
                q=q-1
                [Nei,]=G1[v,:].nonzero()
                for w in Nei:
                    Dw=D[i,v]+G1[v,w]
                    if Dw<D[i,w]:
                        D[i,w]=Dw
                        NP[i,w]=NP[i,v]
                        P[w,:]=False
                        P[w,v]=True
                    elif Dw==D[i,w]:
                        NP[i,w]=NP[i,w]+NP[i,v]
                        P[w,v]=True

            [s,]=S.nonzero()
            if s.size==0:
                break
            else:
                minD=D[i,s].min()
                if minD==np.inf:
                    [x,]=(D[i,:]==np.inf).nonzero()
                    x.setflags(write=True)
                    Q[:q+1]=x
                    break

            B=D[i,:]==minD
            [V,]=B.nonzero()

        DP=np.zeros(N)
        for w in Q[:-1]:
            BC[w]=BC[w]+DP[w]
            for v in P[w,:].nonzero()[0]:
                DP[v]=DP[v]+(1+DP[w])*NP[i,v]/NP[i,w]

    return BC

if __name__=='__main__':
    print('Begin')
    M=Read("p001.txt")
    A=Thres(M, 0.05, 1, 0)
    Cp=Clustercoeff(A,Algorithm=1)
    print(Cp)
    print(Cp.mean())
