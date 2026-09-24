"""Algorithm A (CKK 2012) <= 5/4 证明项目工具箱.

移植自 k3_research/m4_search（修复死路径 /mnt/agents/output），扩展：
- fallback_event: 记录 fallback 事件全貌（负载、机器件数、单子机），供口袋定向模糊测试
- opt_exact: Fraction 精确 OPT（小 n），供符号断言的数值裁决
运行环境: /Users/a123456/math/.venv (python3.12)
"""

from fractions import Fraction
from functools import lru_cache


# ---------------------------------------------------------------- Algorithm A
def algA(jobs, m):
    """CKK Algorithm A. jobs 递减序。返回 makespan。"""
    loads = [0.0] * m
    L = None
    for j, p in enumerate(jobs):
        if j < m:
            loads[j] += p
        else:
            if j == m:
                L = jobs[m - 1] + jobs[m]
            cap = 1.25 * L
            best = -1
            for i in range(m):
                if loads[i] + p <= cap + 1e-12 and (best < 0 or loads[i] > loads[best]):
                    best = i
            if best >= 0:
                loads[best] += p
            else:
                mn = min(range(m), key=lambda i: loads[i])
                loads[mn] += p
    return max(loads)


def algA_fb(jobs, m):
    """返回 (makespan, makespan 机的末任务是否 fallback 放入)。"""
    loads = [0.0] * m
    lastfb = [False] * m
    for j, p in enumerate(jobs):
        if j < m:
            loads[j] += p
        else:
            L = jobs[m - 1] + jobs[m]
            cap = 1.25 * L
            best = -1
            for i in range(m):
                if loads[i] + p <= cap + 1e-12 and (best < 0 or loads[i] > loads[best]):
                    best = i
            if best >= 0:
                loads[best] += p
                lastfb[best] = False
            else:
                mn = min(range(m), key=lambda i: loads[i])
                loads[mn] += p
                lastfb[mn] = True
    mi = max(range(m), key=lambda i: loads[i])
    return loads[mi], lastfb[mi]


def fallback_event(jobs, m):
    """模拟 Algorithm A，返回 makespan 由 fallback 产生时的事件记录：
    {t, loads, machine_jobs, fb_machine, n, L, K, ratio_to_K}
    makespan 由 best-fit(<=K) 产生时返回 None（该情形平凡 <= 5/4）。
    """
    loads = [0.0] * m
    mach = [[] for _ in range(m)]
    for j, p in enumerate(jobs):
        if j < m:
            loads[j] += p
            mach[j].append(p)
        else:
            L = jobs[m - 1] + jobs[m]
            cap = 1.25 * L
            best = -1
            for i in range(m):
                if loads[i] + p <= cap + 1e-12 and (best < 0 or loads[i] > loads[best]):
                    best = i
            if best >= 0:
                loads[best] += p
                mach[best].append(p)
            else:
                mn = min(range(m), key=lambda i: loads[i])
                loads[mn] += p
                mach[mn].append(p)
                # 若此后这台不再是 makespan 机，最终 makespan 仍可能由 K 封顶
    mi = max(range(m), key=lambda i: loads[i])
    if max(loads) <= 1.25 * (jobs[m - 1] + jobs[m]) + 1e-9:
        return None  # K 封顶，平凡
    # makespan 机 = fb 机（fallback 后最满机不会再被选中，见证明注记）
    return {
        "t": mach[mi][-1],
        "loads": sorted(loads),
        "machine_jobs": sorted(mach, key=lambda mm: sum(mm)),
        "fb_machine": mi,
        "n": len(jobs),
        "L": jobs[m - 1] + jobs[m],
        "K": 1.25 * (jobs[m - 1] + jobs[m]),
    }


# ---------------------------------------------------------------- OPT
def opt_float(jobs, m):
    """浮点 OPT（子集和 + DFS 装箱判定 + 二分）。n <= ~20 可用。"""
    n = len(jobs)
    tot = sum(jobs)
    lb = max(tot / m, max(jobs))
    subsum = [0.0] * (1 << n)
    for mask in range(1, 1 << n):
        lsb = mask & (-mask)
        subsum[mask] = subsum[mask ^ lsb] + jobs[lsb.bit_length() - 1]

    def can(cap):
        @lru_cache(maxsize=None)
        def dfs(mask, k):
            if mask == 0:
                return True
            if k == 0:
                return False
            if subsum[mask] > k * cap + 1e-9:
                return False
            sub = mask
            while sub:
                if subsum[sub] <= cap + 1e-9 and dfs(mask ^ sub, k - 1):
                    return True
                sub = (sub - 1) & mask
            return False
        return dfs((1 << n) - 1, m)

    lo, hi = lb, tot
    for _ in range(50):
        mid = (lo + hi) / 2
        if can(mid):
            hi = mid
        else:
            lo = mid
    return hi


def opt_exact(jobs, m):
    """Fraction 精确 OPT（n <= 14 左右）。jobs 可为 float/Fraction。"""
    jobs = [Fraction(str(p)).limit_denominator(10**9) for p in jobs]
    n = len(jobs)
    tot = sum(jobs)
    best = [tot]  # 上界：全塞一台

    @lru_cache(maxsize=None)
    def dfs(mask, k):
        """mask 未装任务，k 剩余机器；返回恰好装满 mask 的最小 makespan（机器数 <= k）。"""
        if mask == 0:
            return Fraction(0)
        s = sum(jobs[i] for i in range(n) if mask >> i & 1)
        if k == 1:
            return s
        res = None
        sub = mask
        # 枚举第一台机器装的子集（含最大位任务以去重），剪枝：子集和 <= 当前最优
        hi_bit = n - 1 - (mask.bit_length() - 1)
        # 找到 mask 最高位
        hb = max(i for i in range(n) if mask >> i & 1)
        sub = mask
        while sub:
            if sub >> hb & 1:  # 第一台必含 mask 中最大任务，去重
                first = sum(jobs[i] for i in range(n) if sub >> i & 1)
                if best[0] is None or first <= best[0]:
                    rest = dfs(mask ^ sub, k - 1)
                    if rest is not None:
                        v = max(first, rest)
                        if res is None or v < res:
                            res = v
            sub = (sub - 1) & mask
        return res

    full = (1 << n) - 1
    v = dfs(full, m)
    return v


def normalize(jobs, m):
    """缩放使 OPT = 1，返回 (scaled_jobs, exact_opt 原值)。"""
    o = opt_exact(jobs, m)
    return [Fraction(str(p)).limit_denominator(10**9) / o for p in jobs], o
