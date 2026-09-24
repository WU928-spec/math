"""探查 §4.5 的支配论证：找 L0>=c-1/3、p4->M3、且 M1 的第二件 < q* (或不存在) 的实例。"""
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

def opt_groups(p):
    n=len(p); best=(float('inf'),None)
    for a in itertools.product(range(3), repeat=n):
        l=[0.0]*3; g=[[],[],[]]
        for i,x in enumerate(a): l[x]+=p[i]; g[x].append(i+1)
        m=max(l)
        if m<best[0]-1e-12: best=(m,[sorted(x) for x in g])
    return best

random.seed(17); hits=[]; distinct=0
for _ in range(60000):
    n=random.choice([6,7,8])
    p=sorted([max(random.random()**random.choice([1,2]), LOW+1e-9) for _ in range(n)], reverse=True)
    ov,groups = opt_groups(p)
    p=[x/ov for x in p]; ov=1.0
    mos,asg,mode,L0 = A3_det(p)
    if mode!="step3" or L0 < c-1/3-1e-12: continue
    # 最优解的分组里找含 p1 的那台
    # 重新求分组（归一化后 same 分组）
    ov2,groups = opt_groups(p)
    g1 = [i for i in groups if 1 in i][0]
    if len(g1)!=2: continue
    qstar = max(i for i in g1 if i!=1)
    qHeur = [i for i in asg[0] if i!=1]
    qH = min(qHeur) if qHeur else None      # 下标越小 = 工件越大
    # 判据：M1 的第二件(qH) 是否 >= q*(下标 <= qstar)
    ok = (qH is not None and qH <= qstar)
    distinct+=1
    if not ok:
        hits.append((p[:], mos, ov, qstar, qH, asg, g1, groups))
print("step3 且 L0>=c-1/3 且 |M1*|=2 的样本数:", distinct)
print("其中 M1 的第二件 缺失/小于 q* 的样本数:", len(hits))
for h in hits[:5]:
    p,mos,ov,qs,qH,asg,g1,groups = h
    print("  p=%s  C_A3=%.4f  q*(下标)=%d  M1第二件(下标)=%s" % (["%.4f"%x for x in p], mos, qs, qH))
    print("      A3分组=%s  最优分组=%s" % (asg, groups))
