"""检验 §4.1(i)：在"z=p_n 是失败工件"的设定下，C_A3 <= p1+p4+pn。
（同时报告无该设定时的原始差值，用以说明该估计不能作为普遍命题。）"""
import math, random, itertools
import numpy as np
c=(1+math.sqrt(37))/6; LOW=1.5*(c-1)

def A3_steps(p):
    """返回 (每步后的负载快照列表, 每步放入的机器, 最终分配)"""
    n=len(p); load=[0.0]*3; asg=[[] for _ in range(3)]; snaps=[]; where=[]
    def put(j,m):
        load[m]+=p[j]; asg[m].append(j+1); snaps.append(list(load)); where.append(m)
    put(0,0); put(1,1); put(2,2)
    if n>3:
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
    return snaps, where, asg

def is_last_job_first_failure(p):
    """z=p_n 是否为"第一个"使某机负载 >c 的工件（等价：前 n-1 步所有负载 <=c，末步 >c）"""
    snaps,_,_ = A3_steps(p); n=len(p)
    before = snaps[n-2] if n>=2 else [0.0,0.0,0.0]
    return max(before) <= c and max(snaps[-1]) > c

def main():
    random.seed(5)
    worst_fail=-9.0; worst_any=-9.0; wf=None
    for _ in range(4000):
        p=sorted([max(random.random()**random.choice([1,2,3]), LOW+1e-9) for _ in range(9)], reverse=True)
        snaps,where,asg = A3_steps(p)
        mos = max(snaps[-1]); bound = p[0]+p[3]+p[8]
        if is_last_job_first_failure(p):
            if mos - bound > worst_fail: worst_fail = mos-bound; wf=(p[:],mos,bound,asg,snaps[-1])
        if mos - bound > worst_any: worst_any = mos-bound
    print("失败设定下 max( C_A3 - (p1+p4+p9) ) = %.6f   （应为 <=0）"%worst_fail)
    if wf: print("   witness p=%s C_A3=%.4f p1+p4+p9=%.4f"%(["%.4f"%x for x in wf[0]],wf[1],wf[2]))
    print("无该设定时  max( C_A3 - (p1+p4+p9) ) = %.6f   （可为正，说明该估计不是普遍命题）"%worst_any)


if __name__ == "__main__":
    main()
