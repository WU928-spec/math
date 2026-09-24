"""口袋 2 角落的精确峰值计算（决定性实验）。

在角落结构族（i=1, 他机全 2 件, 窄带 [t,2t)）内爬山/采样，
对每个候选实例算精确 OPT(opt_float)，记录 C_A/OPT。
目标: 判定角落（比值 > 5/4）是否为空。
合规: 进度打印 + 只在前缀 n<=13 上算 OPT（守卫）。
"""
import random, time
from toolbox import opt_float


def trace(jobs, m):
    """返回 (makespan, 最后一个 fallback 落点件数, 落点负载)"""
    loads = [0.0]*m; cnt = [0]*m; fbs = []; L = None
    for j, p in enumerate(jobs):
        if j < m:
            loads[j] += p; cnt[j] += 1
        else:
            if j == m:
                L = jobs[m-1] + jobs[m]
            cap = 1.25 * L
            best = -1
            for i in range(m):
                if loads[i] + p <= cap + 1e-12 and (best < 0 or loads[i] > loads[best]):
                    best = i
            if best >= 0:
                loads[best] += p; cnt[best] += 1
            else:
                mn = min(range(m), key=lambda i: loads[i])
                fbs.append((p, cnt[mn], loads[mn]))
                loads[mn] += p; cnt[mn] += 1
    return max(loads), fbs


def gen_corner(m, rng):
    """角落形态: p 大, 他机 2 件台, 负载 > p, 窄带填缝"""
    t = rng.uniform(0.26, 0.3335)
    p = rng.uniform(1.25 - t, min(1.0, 1.05 - t / (m - 1) + 0.02))
    jobs = [p]
    for _ in range(m - 1):
        pj = rng.uniform(t, p)
        qj = rng.uniform(t, min(2 * t - 1e-4, p + t - pj + 0.05))
        jobs += [pj, qj]
    jobs.append(t)
    return sorted(jobs, reverse=True)


def main(N=40000, seed=5):
    rng = random.Random(seed)
    best = (0.0, None)
    p2cnt = 0
    t0 = time.time()
    for it in range(N):
        m = rng.choice((5, 6, 7, 8))
        jobs = gen_corner(m, rng)
        if len(jobs) > 13:
            continue
        ca, fbs = trace(jobs, m)
        if not fbs:
            continue
        # 只要 makespan 机的末事件是 fallback 到单子机
        p_, c_, l_ = fbs[-1]
        if c_ != 1:
            continue
        p2cnt += 1
        o = opt_float(jobs, m)
        r = ca / o
        if r > best[0]:
            best = (r, jobs, m)
            print(f"  新高 ratio={r:.5f} (m={m}, t={jobs[-1]:.4f})", flush=True)
        if it % 10000 == 9999:
            print(f"it={it+1} {time.time()-t0:.0f}s p2事件={p2cnt} best={best[0]:.5f}", flush=True)
    print(f"\n完成 {time.time()-t0:.0f}s: 真口袋2事件 {p2cnt} 个")
    r, jobs, m = best
    if jobs:
        print(f"角落精确峰值 = {r:.6f} (m={m})")
        print("jobs =", [round(x, 4) for x in jobs])
        print("OPT =", round(opt_float(jobs, m), 5), " C_A =", round(algA(jobs, m), 5) if False else "")
        ca, _ = trace(jobs, m)
        print("C_A =", round(ca, 5))
    else:
        print("没有任何真口袋2事件")


if __name__ == "__main__":
    main()
