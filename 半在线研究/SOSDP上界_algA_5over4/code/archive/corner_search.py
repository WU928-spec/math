"""角落定向精确搜索（合规版）：口袋 2 残留角落（i=1 为主）能否逼近 5/4。

合规: 断点续跑(state json) + 每 5000 次打印进度 + 分两阶段(粗筛 LB -> 精确 OPT 只算粗筛过的)。
预估: chunk=2 万约 3~4 分钟(含守卫 opt_float), 3 chunks ~10 分钟。
"""
import json, os, random, time
from toolbox import algA, opt_float

STATE = "corner_state.json"
OUT = "corner_hits.jsonl"


def gen_corner(rng):
    m = rng.choice((5, 6, 7, 8))
    t = rng.uniform(0.26, 1/3 + 0.01)
    p1 = rng.uniform(1.26 - t, 1.06)
    jobs = [p1]
    for j in range(2, m + 1):
        pj = rng.uniform(max(t, p1 - 0.4), p1 - 0.01)
        lo = max(t, p1 - pj + 0.005)
        hi = min(2 * t - 0.001, p1 + t - pj)
        if lo >= hi:
            return None
        qj = rng.uniform(lo, hi)
        jobs += [pj, qj]
    jobs.append(t)
    jobs.sort(reverse=True)
    return jobs, m


def gen_general(rng):
    """对照组：一般定向形（大单子机 + 杂色）"""
    m = rng.choice((4, 5, 6, 7, 8))
    pi = random.choice([rng.uniform(0.8, 1.0)])
    n = rng.randint(m + 1, 3 * m - 1)
    jobs = sorted([pi] + [rng.uniform(0.3, 0.75) for _ in range(n - 1)], reverse=True)
    return jobs, m


def main(chunks=3, chunk_size=20000):
    st = {"chunk": -1}
    if os.path.exists(STATE):
        st = json.load(open(STATE))
    for c in range(st["chunk"] + 1, chunks):
        rng = random.Random(1000 + c)
        t0 = time.time()
        for it in range(chunk_size):
            g = gen_corner(rng) if rng.random() < 0.7 else gen_general(rng)
            if g is None:
                continue
            jobs, m = g
            if len(jobs) > 16:   # 复杂度守卫
                continue
            ca = algA(jobs, m)
            lb = max(sum(jobs) / m, jobs[0], jobs[m-1] + jobs[m])
            if ca / lb < 1.08:      # 粗筛
                continue
            o = opt_float(jobs, m)
            r = ca / o
            if r > 1.05:
                with open(OUT, "a") as f:
                    f.write(json.dumps({"chunk": c, "ratio": round(r, 6),
                                        "jobs": jobs, "m": m}) + "\n")
            if it % 5000 == 4999:
                print(f"chunk={c} it={it+1} {time.time()-t0:.0f}s", flush=True)
        st["chunk"] = c
        json.dump(st, open(STATE, "w"))
        print(f"chunk {c} done {time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    main()
