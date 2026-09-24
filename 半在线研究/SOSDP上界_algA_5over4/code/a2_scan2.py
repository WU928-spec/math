import sys, os, time, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main_phantom_corner import assign_juniors
from a2_g1_flow import typed_feasible
from fractions import Fraction as F
random.seed(20260924)
MG=1e-4

def sample_once(m, cnt, e):
    nS=m-1
    tlo=float(F(m-1,4*(m-2)))
    t=random.uniform(tlo+1e-3, 1/3)
    # sliver-friendly juniors: j1,j2 small, j3 large
    j1=random.uniform(t, (1-t)/2)
    j2=random.uniform(j1, 1-t-j1)
    if j1+j2 <= 0: return None
    j3=random.uniform(1-(j1+j2)+1e-3, 2*t)
    # remaining juniors in [j3, 2t]
    rest=[]
    for _ in range(nS-3):
        v=random.uniform(j3, 2*t)
        rest.append(v)
    j=sorted([j1,j2,j3]+rest)
    if j[0]+j[1]+j[2] <= 1+1e-9: return None
    if t+j[0]+j[1] > 1+1e-9: return None
    # seniors
    s=sorted(random.uniform(1-2*t+1e-4, 1-t-1e-4) for _ in range(nS))
    if not typed_feasible(list(s), list(j)+[t], cnt): return None
    p=5/4-t+MG
    am=s[0]; q1=j[-1]
    ok,k,assign,reason=assign_juniors(list(s),list(j),p,t,am,q1)
    sig=(nS-t)-(sum(s)+sum(j))
    return dict(m=m,cnt=cnt[0],t=round(t,6),sigma=round(sig,6),real=ok,k=k,s=[round(x,6) for x in s],j=[round(x,6) for x in j],reason=reason)

def main():
    stats={'sliver_packable':0,'real_sig0':0,'real_sigpos':0,'ghost':0}
    t0=time.time()
    examples={'real_sigpos':[]}
    for m in [6,7,8]:
        for e in [0,1]:
            cnt=(1,m-3,0,1,0,0) if e==0 else (2,m-5,0,1,1,0)
            n_attempts=0
            while time.time()-t0 < 360 and n_attempts < 300000:
                n_attempts+=1
                r=sample_once(m,cnt,e)
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
            print(f'm={m} e={e} attempts={n_attempts} sp={stats["sliver_packable"]}', flush=True)
    print('STATS', stats, 'elapsed', round(time.time()-t0,1))
    print('real_sigpos:', examples['real_sigpos'])

if __name__=='__main__':
    main()
