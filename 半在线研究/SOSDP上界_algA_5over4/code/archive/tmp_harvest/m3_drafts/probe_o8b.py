import math, random, itertools
import numpy as np
c=(1+math.sqrt(37))/6; LOW=1.5*(c-1)
def A3_det(p):
    n=len(p); load=[0.0]*3; asg=[[] for _ in range(3)]
    def put(j,m): load[m]+=p[j]; asg[m].append(j+1)
    put(0,0); put(1,1); put(2,2)
    L0=max(p[0],p[2]+p[3])
    if p[0]+p[3] <= c*L0:
        put(3,0); mode="step2"
        if n>4:
            put(4,1)
            for j in range(5,n):
                m=min(range(3),key=lambda k:(load[k],k)); put(j,m)
    else:
        put(3,2); mode="step3"
        if n>4:
            L=max(L0,min(p[1]+p[4],p[2]+p[3]+p[4]))
            for j in range(4,n):
                if len(asg[0])==1 and p[0]+p[j] <= c*L: put(j,0)
                else:
                    m=min(range(3),key=lambda k:(load[k],k)); put(j,m)
    return max(load), asg, mode, L0
OPTS={}
def opt_best(n,p):
    if n not in OPTS:
        A=np.array(list(itertools.product(range(3),repeat=n)))
        OPTS[n]=np.stack([(A==m).astype(float) for m in range(3)])
    M=OPTS[n]; loads=np.einsum('mkn,n->mk',M,np.asarray(p))
    k=int(loads.max(axis=0).argmin()); return loads.max(axis=0)[k], [ (lambda g:[i+1 for i in g])([i for i in range(n) if M[m][k][i]>0.5]) for m in range(3)]
random.seed(17); hits=[]; n_step3=0; n_case=0
for _ in range(4000):
    n=random.choice([6,7,8])
    p=sorted([max(random.random()**random.choice([1,2]), LOW+1e-9) for _ in range(n)], reverse=True)
    ov,groups=opt_best(n,p)
    p=[x/ov for x in p]
    mos,asg,mode,L0=A3_det(p)
    if not(mode=="step3" and L0>=c-1/3-1e-12): continue
    n_step3+=1
    ov2,groups=opt_best(n,p)
    g1=[g for g in groups if 1 in g]
    if not g1 or len(g1[0])!=2: continue
    g1=g1[0]; qstar=max(i for i in g1 if i!=1)
    qH=[i for i in asg[0] if i!=1]; qH=min(qH) if qH else None
    n_case+=1
    if not (qH is not None and qH<=qstar): hits.append((p[:],mos,qstar,qH,asg,groups))
print("n=6..8 随机实例 4000；其中 step3 且 L0>=c-1/3 的:",n_step3,"；其中最优解 |M1*|=2 的:",n_case)
print("这些样本里 不满足 q(M1 第二件)>=q* 的:",len(hits))
for h in hits[:6]:
    p,mos,qs,qH,asg,groups=h
    print("  p=%s  C_A3=%.4f  q*(%d)  M1第二件(%s)"%(["%.4f"%x for x in p],mos,qs,qH))
    print("     A3=%s  最优=%s"%(asg,groups))
