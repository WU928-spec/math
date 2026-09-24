import itertools, math, random
c = (1+math.sqrt(37))/6
LOW = 1.5*(c-1)

def A3(p, report=False):
    n=len(p); load=[0.0]*3; asg=[[] for _ in range(3)]
    def put(j,m):
        load[m]+=p[j]; asg[m].append(j+1)
    if n<3: return None
    put(0,0); put(1,1); put(2,2)
    if n==3: return max(load), asg, load
    L0=max(p[0], p[2]+p[3])
    if p[0]+p[3] <= c*L0:
        put(3,0)
        if n>4:
            put(4,1)
            for j in range(5,n):
                m=min(range(3), key=lambda k:(load[k],k)); put(j,m)
    else:
        put(3,2)
        if n>4:
            L=max(L0, min(p[1]+p[4], p[2]+p[3]+p[4]))
            for j in range(4,n):
                if len(asg[0])==1 and p[0]+p[j] <= c*L: put(j,0)
                else:
                    m=min(range(3), key=lambda k:(load[k],k)); put(j,m)
    return max(load), asg, load

def opt(p):
    n=len(p); best=float('inf')
    for a in itertools.product(range(3), repeat=n):
        l=[0.0]*3
        for i,x in enumerate(a): l[x]+=p[i]
        best=min(best,max(l))
    return best

random.seed(7)
worst_ratio=(0,None); worst_claim=(0,None)
for _ in range(300000):
    n=random.choice([6,7,8,9])
    p=sorted([random.random()**random.choice([1,2,3]) for _ in range(n)], reverse=True)
    p=[max(x, LOW+1e-9) for x in p]        # 满足所有工件 > (3/2)(c-1)
    p=sorted(p, reverse=True)
    optv=opt(p)
    if optv>1:                              # 归一化到 C* <= 1
        p=[x/optv for x in p]; optv=1.0
    r,s,l = A3(p)
    if r/optv > worst_ratio[0]: worst_ratio=(r/optv, p[:])
    d = r - (p[0]+p[3]+p[-1])               # 检验 makespan <= p1+p4+pn ?
    if d > worst_claim[0]: worst_claim=(d, (p[:], r, p[0]+p[3]+p[-1], s, l))

print("max A3/C* over random n=6..9 (C*<=1):", "%.5f"%worst_ratio[0], " c=%.5f"%c)
print("  worst instance:", ["%.4f"%x for x in worst_ratio[1]])
print()
print("max (A3makespan - (p1+p4+pn)) =", "%.5f"%worst_claim[0])
if worst_claim[1]:
    p,r,b,s,l = worst_claim[1]
    print("  instance:", ["%.4f"%x for x in p])
    print("  makespan=%.4f  p1+p4+pn=%.4f  assignments=%s  loads=%s"%(r,b,s,["%.4f"%x for x in l]))
