import itertools, math, random
import numpy as np
c=(1+math.sqrt(37))/6; LOW=1.5*(c-1)

def A3(p):
    n=len(p); load=[0.0]*3; asg=[[] for _ in range(3)]
    def put(j,m): load[m]+=p[j]; asg[m].append(j+1)
    put(0,0); put(1,1); put(2,2)
    if n==3: return max(load),asg,load
    L0=max(p[0],p[2]+p[3])
    if p[0]+p[3] <= c*L0:
        put(3,0)
        if n>4:
            put(4,1)
            for j in range(5,n):
                m=min(range(3),key=lambda k:(load[k],k)); put(j,m)
    else:
        put(3,2)
        if n>4:
            L=max(L0,min(p[1]+p[4],p[2]+p[3]+p[4]))
            for j in range(4,n):
                if len(asg[0])==1 and p[0]+p[j] <= c*L: put(j,0)
                else:
                    m=min(range(3),key=lambda k:(load[k],k)); put(j,m)
    return max(load),asg,load

def make_opt(n):
    A=np.array(list(itertools.product(range(3),repeat=n)))
    M=np.stack([(A==m).astype(float) for m in range(3)])      # (3, 3^n, n)
    return M
OPTS={n:make_opt(n) for n in (6,7,8,9)}
def opt(n,p):
    loads=np.einsum('mkn,n->mk',OPTS[n],np.asarray(p))
    return loads.max(axis=0).min()

def main():
    random.seed(11)
    worst_ratio=(0,None); worst_claim=(0,None)
    import os
    N={6:int(os.environ.get("S6",6000)),7:int(os.environ.get("S7",6000)),8:int(os.environ.get("S8",6000)),9:int(os.environ.get("S9",6000))}
    for n,samples in N.items():
        for _ in range(samples):
            p=[random.random()**random.choice([1,2,3]) for _ in range(n)]
            p=sorted(p,reverse=True)
            p=[max(x,LOW+1e-9) for x in p]; p=sorted(p,reverse=True)
            ov=opt(n,p)
            if ov>1: p=[x/ov for x in p]; ov=1.0
            r,asg,load=A3(p)
            if r/ov>worst_ratio[0]: worst_ratio=(r/ov,(n,p[:]))
            d=r-(p[0]+p[3]+p[n-1])
            if d>worst_claim[0]: worst_claim=(d,(n,p[:],r,p[0]+p[3]+p[n-1],asg,load))
        print("done n=%d"%n, flush=True)

    print()
    print("max A3/C* (random, C*<=1) =", "%.5f"%worst_ratio[0], "  c = %.5f"%c)
    if worst_ratio[1]:
        n,p=worst_ratio[1]; print("   n=%d  p=%s"%(n,["%.4f"%x for x in p]))
    print()
    print("max (A3makespan - (p1+p4+pn)) =", "%.5f"%worst_claim[0],
      "  <- 该项只在\"z 是失败工件\"的设定下才有意义；脱离该设定可为正，见 n9_claim.py")
    if worst_claim[1]:
        n,p,r,b,asg,load=worst_claim[1]
        print("   n=%d p=%s"%(n,["%.4f"%x for x in p]))
        print("   makespan=%.4f  p1+p4+pn=%.4f  asg=%s loads=%s"%(r,b,asg,["%.4f"%x for x in load]))


if __name__ == "__main__":
    main()
