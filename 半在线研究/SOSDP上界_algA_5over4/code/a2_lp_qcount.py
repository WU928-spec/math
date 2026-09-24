"""Test: value-language corner LP + sliver + sigma>=eps + (LZ/HZ_k + Qcount_k) feasibility."""
import numpy as np, sys, os
from fractions import Fraction as F
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a1_value_lp2 as V

MG=F(1,10000)

def check(m, cnt, t0, sigma_eps=0.01):
    nS=m-1
    # build value-language corner (no b4, no sjrev, no s1v, no jjrev)
    A,bc,bt,names,leg,nv = V.build(m,cnt, use_a2=False, use_b4=False, use_sjrev=False,
                                    use_s1v=False, use_jjrev=False)
    IP, IAM, IQ1 = 0,1,2
    vs=lambda r: 3+(r-1); vj=lambda r: 3+nS+(r-1)
    def con(row,c0,c1,nm):
        A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)
    z=[F(0)]*nv
    # sliver j1+j2+j3 >= 1+MG  (strict > 1)
    r_=list(z); r_[vj(1)]=-1; r_[vj(2)]=-1; r_[vj(3)]=-1
    con(r_, -1-MG, 0, 'sliver')
    # sigma >= eps : sum(s)+sum(j) <= nS - t - eps
    r_=list(z)
    for rr in range(1,nS+1):
        r_[vs(rr)]=1; r_[vj(rr)]=1
    con(r_, nS-float(sigma_eps), -1, 'sigma_eps')
    Af=np.array([[float(x) for x in row] for row in A])
    bcf=np.array([float(x) for x in bc]); btf=np.array([float(x) for x in bt])
    b=bcf+btf*t0
    feas_k=[]
    for k in range(1,nS+1):
        # k = #{s <= K-q1}  (0-indexed: s_k = k-th smallest, indices 1..nS -> s_{k} is index k; s_{k+1} index k+1)
        # LZ: s_k + q1 <= K = 5/4(s_0+q1) -> s_k + q1 - 5/4 s_0 - 5/4 q1 <=0 -> s_k -5/4 s_0 -1/4 q1 <=0
        A2=[row[:] for row in A]; bc2=list(bc); bt2=list(bt)
        def con2(row,c0,c1,nm):
            A2.append([float(x) for x in row]); bc2.append(float(c0)); bt2.append(float(c1))
        if k<=nS:
            r_=[0.0]*nv; r_[vs(k)]=1; r_[IAM]=-1.25; r_[IQ1]=-0.25
            con2(r_,0,0,f'LZ_{k}')
        if k<nS:
            # HZ: s_{k+1} + q1 >= K+MG -> s_{k+1}+q1-5/4s0-5/4q1 >= MG -> -s_{k+1}+5/4 s0+1/4 q1 <= -MG
            r_=[0.0]*nv; r_[vs(k+1)]=-1; r_[IAM]=1.25; r_[IQ1]=0.25
            con2(r_,-float(MG),0,f'HZ_{k}')
        # Qcount: j_{nS-k+1} >= p - s0 + MG -> p - s0 - j_{nS-k+1} <= -MG
        r_=[0.0]*nv; r_[IP]=1; r_[IAM]=-1; r_[vj(nS-k+1)]=-1
        con2(r_,-float(MG),0,f'Qcount_{k}')
        Af2=np.array(A2); b2=np.array(bc2)+np.array(bt2)*t0
        res=linprog(c=np.zeros(nv), A_ub=Af2, b_ub=b2, bounds=(None,None), method='highs')
        if res.status==0:
            feas_k.append(k)
    return feas_k

def main():
    tmesh=[0.28,0.30,0.31,0.32,1/3]
    for m in [6,7,8,9]:
        nS=m-1
        for cnt in [(1,m-3,0,1,0,0),(2,m-5,0,1,1,0)]:
            for t0 in tmesh:
                if t0 <= float(F(m-1,4*(m-2))): continue
                fk=check(m,cnt,t0)
                if fk:
                    print(f'm={m} cnt={cnt[0]} t={t0}: FEASIBLE at k={fk}')
                else:
                    print(f'm={m} cnt={cnt[0]} t={t0}: all k INFEASIBLE (relaxation kills sigma>eps)')
if __name__=='__main__':
    main()
