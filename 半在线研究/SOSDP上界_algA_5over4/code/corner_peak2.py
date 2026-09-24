"""角落峰值爬山：i=1, 他机 2 件台形内逼近真实上确界（口袋 2 角落）。

流程: 随机采样角落盒 -> 记录好的 -> 对每个好的做局部爬山(微调任务大小, 改善则留)。
精确 OPT(opt_float, n<=13 快)。判定危险区 (p+t > 5/4 OPT) 可达性。
"""
import random, time
from toolbox import opt_float


def trace(jobs, m):
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


def eval_ratio(jobs, m):
    """若末事件是 fallback 到单子机则返回精确比值，否则 None"""
    ca, fbs = trace(jobs, m)
    if not fbs:
        return None
    p_, c_, l_ = fbs[-1]
    if c_ != 1:
        return None
    o = opt_float(jobs, m)
    return ca / o, ca, o


def gen_corner(m, rng):
    t = rng.uniform(0.26, 0.3335)
    p = rng.uniform(1.25 - t, min(1.0, 1.06 - t / (m - 1)))
    jobs = [p]
    for _ in range(m - 1):
        pj = rng.uniform(t, p)
        lo = max(t, p - pj + 0.005)
        hi = min(2 * t - 1e-4, p + t - pj)
        if lo >= hi:
            return None
        qj = rng.uniform(lo, hi)
        jobs += [pj, qj]
    jobs.append(t)
    return sorted(jobs, reverse=True)


def hillclimb(jobs, m, iters, rng):
    best_r = None
    cur = list(jobs)
    out = eval_ratio(cur, m)
    if out is None:
        return None
    best_r, best = out[0], list(cur)
    for _ in range(iters):
        cand = [max(0.02, x + rng.uniform(-0.02, 0.02)) for x in cur]
        cand.sort(reverse=True)
        out = eval_ratio(cand, m)
        if out and out[0] > best_r:
            best_r, best = out[0], cand
            cur = cand
    return best_r, best


def main(N=6000, seed=9):
    rng = random.Random(seed)
    t0 = time.time()
    p2 = 0
    best = (0.0, None, 0)
    for it in range(N):
        m = rng.choice((5, 6, 7, 8))
        jobs = gen_corner(m, rng)
        if jobs is None or len(jobs) > 13:
            continue
        out = eval_ratio(jobs, m)
        if out is None:
            continue
        p2 += 1
        if out[0] > best[0]:
            hc = hillclimb(jobs, m, 40, rng)
            r = hc[0] if hc else out[0]
            jobs2 = hc[1] if hc else jobs
            best = (r, jobs2, m)
            print(f"  新高 {r:.5f} (m={m}) @it={it}", flush=True)
        if it % 2000 == 1999:
            print(f"it={it+1} {time.time()-t0:.0f}s 真口袋2={p2} best={best[0]:.5f}", flush=True)
    print(f"\n完成 {time.time()-t0:.0f}s。角落精确上确界(采样+爬山) ≈ {best[0]:.6f}")
    if best[1]:
        print("jobs =", [round(x, 4) for x in best[1]])
        r2 = eval_ratio(best[1], best[2])
        print(f"复核: ratio={r2[0]:.6f} C_A={r2[1]:.5f} OPT={r2[2]:.5f}")


if __name__ == "__main__":
    main()
