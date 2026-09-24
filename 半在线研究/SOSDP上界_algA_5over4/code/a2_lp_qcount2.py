"""Compute max sigma over value-language corner + sliver + LZ/HZ_k + Qcount_k relaxation."""
import os
import numpy as np, sys
from fractions import Fraction as F
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a1_value_lp2 as V
MG=F(1,10000)

def maxsig(m, cnt, t0):
    nS=m-1
    A,bc,bt,names,leg,nv = V.build(m,cnt, use_a2=False, use_b4=False, use_sjrev=False,
                                    use_s1v=False, use_jjrev=False)
    IP, IAM, IQ1 = 0,1,2
    vs=lambda r: 3+(r-1); vj=lambda r: 3+nS+(r-1)
    def con(row,c0,c1,nm):
        A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)
    z=[F(0)]*nv
    r_=list(z); r_[vj(1)]=-1; r_[vj(2)]=-1; r_[vj(3)]=-1
    con(r_, -1-MG, 0, 'sliver')
    Af=np.array([[float(x) for x in row] for row in A])
    bcf=np.array([float(x) for x in bc]); btf=np.array([float(x) for x in bt])
    b=bcf+btf*t0
    cmax=np.zeros(nv)
    for rr in range(1,nS+1): cmax[vs(rr)]=1; cmax[vj(rr)]=1
    res={}
    for k in range(1,nS+1):
        A2=[row[:] for row in A]; bc2=list(bc); bt2=list(bt)
        def con2(row,c0,c1,nm):
            A2.append([float(x) for x in row]); bc2.append(float(c0)); bt2.append(float(c1))
        if k<=nS:
            r_=[0.0]*nv; r_[vs(k)]=1; r_[IAM]=-1.25; r_[IQ1]=-0.25
            con2(r_,0,0,f'LZ_{k}')
        if k<nS:
            r_=[0.0]*nv; r_[vs(k+1)]=-1; r_[IAM]=1.25; r_[IQ1]=0.25
            con2(r_,-float(MG),0,f'HZ_{k}')
        r_=[0.0]*nv; r_[IP]=1; r_[IAM]=-1; r_[vj(nS-k+1)]=-1
        con2(r_,-float(MG),0,f'Qcount_{k}')
        Af2=np.array(A2); b2=np.array(bc2)+np.array(bt2)*t0
        rres=linprog(c=-cmax, A_ub=Af2, b_ub=b2, bounds=(None,None), method='highs')
        if rres.status==0:
            res[k]=(nS-t0)-(-rres.fun)
    return res

def main():
    tmesh=[0.28,0.30,0.31,0.32,1/3]
    for m in [6,7,8]:
        for cnt in [(1,m-3,0,1,0,0),(2,m-5,0,1,1,0)]:
            for t0 in tmesh:
                if t0 <= float(F(m-1,4*(m-2))): continue
                res=maxsig(m,cnt,t0)
                mx=max(res.values()) if res else None
                print(f'm={m} cnt={cnt[0]} t={round(t0,4)}: max sigma over k = {mx:.5f}  (per-k: { {k:round(v,5) for k,v in res.items()} })')
if __name__=='__main__':
    main()
