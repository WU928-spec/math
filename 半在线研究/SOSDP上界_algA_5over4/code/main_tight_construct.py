"""main_tight_construct.py —— sliver 紧性引理的决定性构造实验。
紧性引理：可装箱+sliver ⟹ 全紧（JJJ={t,j1,j2} 和=1、SS 对和=1、SJ=互补对）。
构造全紧实例（seniors∈[1-2t,1-t]、SS 对和=1、juniors={j1,j2(和1-t)}∪{1-s_residual}），
逐例判：①角落有效性（assign_juniors：pair/mon2/fs/窗口）②可达性（fallback_event）。
  某例全过 ⟹ β 区真角落+可装箱=(P) 反例（重大告警，与 T'' 对撞，全员复核）
  全不过 ⟹ 输出每例的阻断约束=紧性结构的死因（β 引理最后一步）
"""
import numpy as np
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main_phantom_corner import assign_juniors
from main_reach_pack2 import packs_into_m
from toolbox import fallback_event

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main_tight_construct.jsonl')


def build_tight(m, t, rng, e=0):
    """构造一个全紧 sliver 实例：返回 (p, s, j) 或 None（自相矛盾则丢弃）。"""
    nS = m - 1
    # seniors: [1-2t, 1-t] 内随机，需含 SS 对和=1
    s = sorted(rng.uniform(1 - 2 * t, 1 - t, nS))
    # 强制一个 SS 对和=1：选 u, 令 v=1-u
    i = rng.integers(0, nS)
    u = s[i]
    if not (1 - 2 * t <= u <= 1 - t):
        return None
    v = 1.0 - u
    if v < 1 - 2 * t - 1e-9 or v > 1 - t + 1e-9:
        return None
    # 放入 v（若与现有 u 重复度低）
    s.append(v)
    s = sorted(s)
    if len(s) != nS + 1:
        return None
    # e=0: 需 nS seniors（SS 用 2 个）——随机删一个非 u/v 的 senior 使总数=nS
    others = [x for x in s if x is not u and abs(x - v) > 1e-12]
    if len(others) != nS - 1:
        return None
    # SS 对：u 与 v 都在；seniors 全集 = others + [u, v]... 需恰 nS：u,v + others(nS-1) = nS+1 多了 1
    # 重新采样：直接采 nS 个 senior 含 u,v
    while True:
        s = sorted(rng.uniform(1 - 2 * t, 1 - t, nS - 2).tolist() + [u, v])
        if len(s) == nS and all(1 - 2 * t - 1e-9 <= x <= 1 - t + 1e-9 for x in s):
            break
    # juniors: 残差 senior 的互补 + j1,j2（和=1-t）
    ss = {round(u, 12), round(v, 12)}
    residual = [x for x in s if not (round(x, 12) == round(u, 12) or round(x, 12) == round(v, 12))]
    # u,v 可能有同值副本，按计数移除：找 u,v 各一个下标删除
    s2 = list(s)
    for val in (u, v):
        for idx, x in enumerate(s2):
            if abs(x - val) < 1e-12:
                del s2[idx]
                break
    residual = s2
    comp = [1.0 - x for x in residual]
    # j1,j2: j1∈[t,(1-t)/2], j2=1-t-j1∈[(1-t)/2, 1-2t]
    j1 = rng.uniform(t, (1 - t) / 2)
    j2 = 1 - t - j1
    j = sorted(comp + [j1, j2])
    if len(j) != nS:
        return None
    # sliver 检查：j1+j2+j3>1（j3=第三小 junior）
    if j[0] + j[1] + j[2] <= 1 + 1e-12:
        return None
    # p: danger p+t>5/4, p<=1；M0={x,t}, x=p-t>1/2 区域取
    p = rng.uniform(max(5 / 4 - t + 0.001, 0.9), 1.0)
    return p, s, j, u, v


def main(mlo=6, mhi=14, nsample=200):
    rng = np.random.default_rng(42)
    pf = open(OUT, 'w')
    n_built = n_corner = n_reach = 0
    reasons = {}
    for m in range(mlo, mhi + 1):
        for t in [0.28, 0.30, 0.32, 1 / 3]:
            for _ in range(nsample):
                got = build_tight(m, t, rng)
                if got is None:
                    continue
                p, s, j, u, v = got
                n_built += 1
                nS = m - 1
                am = s[0]
                q1 = j[-1]
                ok, k, assign, reason = assign_juniors(s, j, p, t, am, q1)
                if not ok:
                    key = reason.split('（')[0].split(':')[0]
                    reasons[key] = reasons.get(key, 0) + 1
                    continue
                n_corner += 1
                seq = sorted([p] + s, reverse=True) + sorted(j + [t], reverse=True)
                ev = fallback_event(seq, m)
                if ev is None:
                    reasons['不可达'] = reasons.get('不可达', 0) + 1
                    continue
                n_reach += 1
                pk = packs_into_m([p] + s + j + [t], m)
                pf.write(json.dumps({'m': m, 't': t, 'p': p, 'reach': True, 'pack': pk,
                                     's': [round(x, 4) for x in s], 'j': [round(x, 4) for x in j]}) + '\n')
                if pk:
                    print(f'**警报：全紧实例可达且可装箱！ m={m} t={t} p={p:.4f}')
                    print(f'   s={np.round(s,3)}\n   j={np.round(j,3)}')
        print(f'm={m} 完成（构造 {n_built} 角落有效 {n_corner} 可达 {n_reach}）', flush=True)
    print(f'\n判决：构造 {n_built}，角落有效 {n_corner}，可达 {n_reach}')
    print(f'阻断分布: {reasons}')


if __name__ == '__main__':
    main()
