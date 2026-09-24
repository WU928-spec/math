import sys, os, time, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a1_tight_real import realizable
from a2_g1_flow import typed_feasible
from fractions import Fraction as F
random.seed(20260924)
MG=1e-4

def sample_once(m, cnt):
    nS=m-1
    tlo=float(F(m-1,4*(m-2)))
    t=random.uniform(tlo+1e-3, 1/3)
    s=sorted(random.uniform(1-2*t+1e-4, 1-t-1e-4) for _ in range(nS))
    j=sorted(random.uniform(t+1e-4, 2*t-1e-4) for _ in range(nS))
    if not (j[0]+j[1]+j[2] > 1 + 1e-9): return None
    if not (t+j[0]+j[1] <= 1 + 1e-9): return None
    if not typed_feasible(list(s), list(j)+[t], cnt): return None
    p=5/4-t+MG
    q1=max(j)
    K=1.25*(s[0]+q1)
    ok,k=realizable(list(s),list(j),p,q1,K)
    sig=(nS-t)-(sum(s)+sum(j))
    return dict(m=m,cnt=cnt[0],t=round(t,6),sigma=round(sig,6),real=ok,k=k,s=[round(x,6) for x in s],j=[round(x,6) for x in j])

def main():
    stats={'sliver_packable':0,'real_sig0':0,'real_sigpos':0,'ghost':0}
    t0=time.time()
    examples={'real_sigpos':[]}
    for m in [6,7,8]:
        for cnt in [(1,m-3,0,1,0,0),(2,m-5,0,1,1,0)]:
            n_attempts=0
            while time.time()-t0 < 300 and n_attempts < 400000:
                n_attempts+=1
                r=sample_once(m,cnt)
                if r is None: continue
                stats['sliver_packable']+=1
                if not r['real']:
                    stats['ghost']+=1
                elif abs(r['sigma'])<1e-6:
                    stats['real_sig0']+=1
                else:
                    stats['real_sigpos']+=1
                    if len(examples['real_sigpos'])<5: examples['real_sigpos'].append(r)
                    print('[BREAKING] real sigma>0', r, flush=True)
            print(f'm={m} cnt={cnt[0]} attempts={n_attempts}', flush=True)
    print('STATS', stats, 'elapsed', round(time.time()-t0,1))
    print('real_sigpos examples:', examples['real_sigpos'])

if __name__=='__main__':
    main()
