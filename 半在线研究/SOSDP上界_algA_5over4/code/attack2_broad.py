"""敌意构造 #2: 广义角落定向搜索 + 爬山.

结构族: [B x a (封死大任务, >p), p (单子机), valves (v 个, [t,p)), fillers (f 个, [t,2t)), t]
其中 a+1+v = m. 也撒一般形. 事件判定: 真口袋2 (makespan=fallback 落到恰1件未动机).
危险判定: n<=18 用 opt_float 精确; 否则用 FFD 上界 UB (p+t > 1.25*UB => 危险成立, 因 OPT<=UB).
"""
import json, os, random, time, sys
from toolbox import opt_float

STATE = "attack2_state.json"
OUT = "attack2_hits.jsonl"


def simulate(jobs, m):
    loads = [0.0]*m; cnt=[0]*m
    L=None; fb=None
    for j,p in enumerate(jobs):
        if j < m:
            loads[j]+=p; cnt[j]+=1
        else:
            if j==m: L = jobs[m-1]+jobs[m]
            cap = 1.25*L
            best=-1
            for i in range(m):
                if loads[i]+p <= cap+1e-12 and (best<0 or loads[i]>loads[best]):
                    best=i
            if best>=0:
                loads[best]+=p; cnt[best]+=1
            else:
                mn=min(range(m), key=lambda i: loads[i])
                loads[mn]+=p; cnt[mn]+=1
                fb=(j,p,mn)
    if fb is None: return max(loads), None
    j,p,mn = fb
    if cnt[mn]!=1: return max(loads), None
    if abs(loads[mn]-max(loads))>1e-9: return max(loads), None
    return max(loads), {"idx":j,"t":p,"mach":mn,"pi":loads[mn]-p}


def ffd_ub(jobs, m):
    """First-fit decreasing 装箱上界 (m 箱). 不可行返回 inf."""
    bins=[0.0]*m
    for p in sorted(jobs, reverse=True):
        k=min(range(m), key=lambda i: bins[i])
        bins[k]+=p
    return max(bins)   # 注意: 这是 LPT 上界, 恒可行, >= OPT


def gen_struct(rng):
    m = rng.choice((4,5,6,7,8,9,10,12,14,16,20))
    t = rng.uniform(0.251, 0.4)
    p = rng.uniform(1.251 - t, min(1.0, 1.0 - t/(m-1) + 0.02))
    if p <= 1.25 - t or p > 1.0:
        return None
    i = rng.choice([1,1,1,2,3,m//2])  # 单子机 rank
    i = max(1, min(i, m-1))
    a = i - 1   # 封死大任务数 (rank i => 前面 i-1 个更大)
    bigs = [rng.uniform(p+0.01, min(1.0, p+0.15)) for _ in range(a)]
    v = m - 1 - a
    valves = [rng.uniform(t, p) for _ in range(v)]
    # 填缝: 围绕亏空 p - valve, 加噪声 (浪费控制)
    f = v + rng.choice((0,0,0,1,2,3))
    fills = []
    for j in range(f):
        base = p - valves[j % v] if j < v else rng.uniform(t, p - t)
        q = base + rng.uniform(-0.3*base, 0.6*base)
        q = min(max(q, t), 2*t - 1e-4)
        fills.append(q)
    jobs = sorted(bigs + [p] + valves + fills + [t], reverse=True)
    if len(jobs) > 24: return None
    return jobs, m


def gen_tightlike(rng):
    """紧实例扰动族: 整数."""
    m = rng.choice((6,7,8,9,10,12))
    t = rng.randint(4, 8)
    p = rng.randint(int(1.25*t*1.0)+1, int(1.6*t)+4)
    a = rng.randint(0, m//2)
    bigs = [rng.randint(p+1, p+3) for _ in range(a)]
    v = m - 1 - a
    if v < 1: return None
    valves = [rng.randint(t, p-1) for _ in range(v)]
    f = v + rng.choice((0,0,1,2))
    hi_f = min(2*t-1, p-t+2)
    if hi_f < t: return None
    fills = [rng.randint(t, hi_f) for _ in range(f)]
    jobs = sorted(bigs+[p]+valves+fills+[t], reverse=True)
    if len(jobs) > 22: return None
    return jobs, m


def evaluate(jobs, m, best, hits_file):
    ca, ev = simulate(jobs, m)
    if ev is None: return best
    prefix = jobs[:ev["idx"]+1]
    s = ev["pi"] + ev["t"]
    if len(prefix) <= 18:
        o = opt_float(prefix, m)
        r = s / o
        exact = True
    else:
        o = ffd_ub(prefix, m)
        r = s / o
        exact = False
    if r > best + 0.003 and r > 1.04:
        best = r
        hits_file.write(json.dumps({"r": round(r,6), "exact": exact, "m": m,
                                    "jobs": [round(x,5) for x in jobs],
                                    "pi": round(ev["pi"],5), "t": round(ev["t"],5),
                                    "opt": round(o,5)}) + "\n")
        hits_file.flush()
    return best


def main(N=120000):
    st = {"done":0, "best":0.0}
    if os.path.exists(STATE):
        st = json.load(open(STATE))
    rng = random.Random(4242)
    for _ in range(st["done"]*2):  # 粗略推进 rng 状态
        rng.random()
    hf = open(OUT, "a")
    t0=time.time(); evcnt=0
    for it in range(st["done"], N):
        g = gen_struct(rng) if rng.random()<0.6 else gen_tightlike(rng)
        if g is None: continue
        jobs, m = g
        before = st["best"]
        st["best"] = evaluate(jobs, m, st["best"], hf)
        if st["best"] != before: evcnt+=1
        if it % 10000 == 9999:
            print(f"it={it+1} {time.time()-t0:.0f}s best={st['best']:.5f} new_hits={evcnt}", flush=True)
            st["done"]=it+1
            json.dump(st, open(STATE,"w"))
    st["done"]=N
    json.dump(st, open(STATE,"w"))
    print(f"完成 {time.time()-t0:.0f}s best={st['best']:.5f}", flush=True)


if __name__=="__main__":
    main(int(sys.argv[1]) if len(sys.argv)>1 else 120000)
