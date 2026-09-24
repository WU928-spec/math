"""敌意构造 #1: 零浪费精确打平族 (Family A) 穷举.

形态: m 台机, M0={p} 单子机, 他机 initials p_2..p_m ∈ [t, p),
填缝 = 每台恰一件 q_j = p - p_j (精确打平到 p), 末尾 t.
jobs = sort([p] + initials + fillers + [t]).
检验: algA 模拟 -> 是否真口袋2事件 (makespan 由 fallback 落到未动单子机产生);
若是, opt_float(前缀) 精确判定是否危险 (p+t > 5/4 OPT).
"""
import sys, time
from itertools import combinations_with_replacement
from toolbox import opt_float


def simulate(jobs, m):
    """返回 (makespan, event_or_None). event: 最后一个 fallback 落到恰1件机器(其初始任务) 且该机是 makespan 机."""
    loads = [0.0]*m; cnt=[0]*m
    L=None; fb_info=None
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
                fb_info=(j, p, mn)
    if fb_info is None: return max(loads), None
    j,p,mn = fb_info
    if cnt[mn]!=1:  # 落点前该机恰1件(未动单子机)
        return max(loads), None
    if abs(loads[mn]-max(loads))>1e-9:  # 必须是 makespan 机
        return max(loads), None
    return max(loads), {"idx":j, "t":p, "mach":mn, "pi":loads[mn]-p}


def familyA(m, t, p, lo, hi):
    """initials: m-1 个递减值 ∈ [lo,hi], fillers = p - x."""
    seen=0; hits=[]
    for init in combinations_with_replacement(range(hi, lo-1, -1), m-1):
        init=list(init)
        fillers=[p-x for x in init]
        if min(fillers) < t:  # 填缝须 >= t
            continue
        jobs = sorted([p]+init+fillers+[t], reverse=True)
        if jobs[-1]!=t:  # t 须为严格最小(允许并列但值须==t)
            continue
        seen+=1
        ca, ev = simulate(jobs, m)
        if ev is None: continue
        prefix = jobs[:ev["idx"]+1]
        o = opt_float(prefix, m)
        r = (ev["pi"]+ev["t"])/o
        hits.append((r, jobs, ev, o))
    return seen, hits


def main():
    t0=time.time()
    # (m, t, p, lo, hi) 盒子: 整数单位
    boxes = [
        (6, 5, 14, 5, 13),   # OPT<=15 时比值 19/15
        (6, 5, 13, 5, 12),   # p+t=18, OPT<=14 危险 (18>17.5)
        (7, 10, 28, 10, 27), # OPT<=30 -> 38/30
        (7, 10, 27, 10, 26), # 37 <= 29.6*1.25=37 -> OPT<=29 危险
        (8, 16, 45, 16, 44), # OPT<=48 -> 61/48
        (8, 16, 44, 16, 43), # 60 > 48*1.25=60 -> OPT<=47 危险
        (5, 5, 13, 5, 12),   # m=5 校验(据称已闭合, 应无危险)
        (4, 5, 13, 5, 12),   # m=4 校验
    ]
    grand=0
    for (m,t,p,lo,hi) in boxes:
        seen, hits = familyA(m,t,p,lo,hi)
        hits.sort(key=lambda h:-h[0])
        grand+=seen
        print(f"box m={m} t={t} p={p}: 组合 {seen}, 真口袋2事件 {len(hits)}, 用时 {time.time()-t0:.0f}s", flush=True)
        for r,jobs,ev,o in hits[:3]:
            flag = "  *** 危险!!! ***" if r>1.25 else ""
            print(f"    ratio={r:.5f} OPT={o:.4f} jobs={jobs}{flag}", flush=True)
    print(f"总组合 {grand}, 总用时 {time.time()-t0:.0f}s", flush=True)


if __name__=="__main__":
    main()
