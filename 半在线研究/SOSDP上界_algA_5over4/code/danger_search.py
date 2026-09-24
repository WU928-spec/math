"""危险区真口袋2事件存在性测量（合规版）。

目标: 找 fallback 落到未动单子机 {p_i} 且 p_i+t > (5/4)OPT(前缀) 的实例。
若大规模搜索为零 ⟹ 角落危险区经验为空 ⟹ 中等强度不等式可收口。
合规: 断点续跑 + 进度打印 + opt_float 只在 c==1 且前缀<=16 时调用。
预估: 8 万模拟 ~3-5 分钟。
"""
import json, os, random, time
from toolbox import opt_float

STATE = "danger_state.json"
OUT = "danger_hits.jsonl"


def trace(jobs, m):
    loads = [0.0]*m; cnt = [0]*m; fbs = []; L = None
    for j, p in enumerate(jobs):
        if j < m:
            loads[j] += p; cnt[j] += 1
        else:
            if j == m: L = jobs[m-1] + jobs[m]
            cap = 1.25 * L
            best = -1
            for i in range(m):
                if loads[i] + p <= cap + 1e-12 and (best < 0 or loads[i] > loads[best]):
                    best = i
            if best >= 0:
                loads[best] += p; cnt[best] += 1
            else:
                mn = min(range(m), key=lambda i: loads[i])
                fbs.append((j, p, cnt[mn], loads[mn]))
                loads[mn] += p; cnt[mn] += 1
    return max(loads), fbs


def gen(rng):
    m = rng.choice((4, 5, 6, 7, 8))
    n = rng.randint(m + 1, 3 * m - 2)
    mode = rng.random()
    if mode < 0.4:
        jobs = sorted([round(rng.uniform(0.75, 1.05), 4)] +
                      [round(rng.uniform(0.35, 0.75), 4) for _ in range(n - 1)], reverse=True)
    elif mode < 0.75:
        jobs = sorted([round(rng.uniform(0.8, 1.1), 4)] +
                      [round(rng.uniform(0.4, 0.9), 4) for _ in range(n - 1)], reverse=True)
    else:
        jobs = sorted([random.randint(5, 12)] + [random.randint(3, 8) for _ in range(n - 1)], reverse=True)
    return jobs, m


def main(N=80000):
    st = {"done": 0}
    if os.path.exists(STATE):
        st = json.load(open(STATE))
    rng = random.Random(99)
    rng_random = random.random
    for _ in range(st["done"]):
        rng.random()
    t0 = time.time()
    hits = 0
    danger = 0
    for it in range(st["done"], N):
        jobs, m = gen(rng)
        ca, fbs = trace(jobs, m)
        if not fbs:
            continue
        jidx, p, c, l = fbs[-1]
        if c != 1 or jidx + 1 > 16:
            continue
        hits += 1
        o = opt_float(jobs[:jidx + 1], m)
        if l + p > 1.25 * o:    # 危险: 单子机负载 + t 超过 5/4 OPT(前缀)
            danger += 1
            with open(OUT, "a") as f:
                f.write(json.dumps({"r": round((l+p)/o, 5), "jobs": jobs, "m": m,
                                    "pi": l, "t": p}) + "\n")
        if it % 20000 == 19999:
            print(f"it={it+1} {time.time()-t0:.0f}s hits={hits} danger={danger}", flush=True)
        st["done"] = it + 1
        if it % 5000 == 4999:
            json.dump(st, open(STATE, "w"))
    json.dump(st, open(STATE, "w"))
    print(f"\n完成: {time.time()-t0:.0f}s, 真口袋2事件 {hits}, 其中危险区 {danger}")


if __name__ == "__main__":
    main()
