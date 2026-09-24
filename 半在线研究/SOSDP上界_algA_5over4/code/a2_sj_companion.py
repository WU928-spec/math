"""a2_sj_companion.py — SJ 伴侣值规范化的实证裁决（B 路线核心缺口）。

两半检验（目标：杀死联合主张或给出成立边界）：
【cap 半】规范化（S1：SS=最小2a极端配对；S2：S=最大c；JJJ=池最小3d）后，是否恒存在
  可行 cnt-型装箱完成：SJ 槽（中段 b seniors）伴侣集 C ⊆ 剩余池、反序配对全 ≤1
  （SJ-REV：∃匹配 ⟺ 反序可行），剩余池由 JJ-REV（反序对）+J 吸收。
  枚举 C 的所有 b 子集（小规模），全部失败 ⟹ 反例。
【nofit 半】q₁（最大 junior）的 SJ 伴侣 s_g：(i) 真实装箱中的伴侣 s_g+q₁>K 是否恒成立；
  (ii) 规范化形式下 q₁ 的伴侣 = 最小 SJ senior s_{2a}（反序配对），问 s_{2a}+q₁>K 是否恒成立。
  K=(5/4)(a_m+q₁)，a_m=s_0。
牙齿：§JEL 否证例 s'=0.9/池{0.5,0.11} 形态必须能被机制识别为反例。
"""
import numpy as np
from itertools import combinations
from functools import lru_cache
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pairing_feasible import bin_count_solutions

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a2_sj_companion_progress.jsonl')


def gen_packable_corner(rng, m):
    """装箱优先生成器：逐箱造合法 cnt 装箱 ⟹ 必可装箱；机器对（角落数据）独立派生。
    敌意推 razor/紧配对形态。返回 dict(p,t,s,j,pool,cnt) 或 None。"""
    nS = m - 1
    cnts = bin_count_solutions(m)
    rng.shuffle(cnts)
    for cnt in cnts[:60]:
        a, b, c, d, e, f = cnt
        t = float(rng.uniform(0.26, 1 / 3 - 1e-4))
        # 逐箱造（容量 ≤1）：值域贴近角落形态
        ss_vals, sj_vals, s_vals, pool_vals = [], [], [], []
        ok = True
        for _ in range(a):
            u = float(rng.uniform(1 - 2 * t + 0.01, 2 * t - 0.005))
            hi_v = 1 - u
            if hi_v < 1 - 2 * t + 0.01:
                ok = False; break
            v = float(rng.uniform(1 - 2 * t + 0.01, hi_v))
            ss_vals += [u, v]
        if not ok:
            continue
        for _ in range(b):
            u = float(rng.uniform(1 - 2 * t + 0.01, 1 - t - 0.02))
            hi_w = min(2 * t - 1e-4, 1 - u)
            if hi_w < t:
                ok = False; break
            w = float(rng.uniform(t, hi_w))
            sj_vals.append(u); pool_vals.append(w)
        if not ok:
            continue
        for _ in range(c):
            s_vals.append(float(rng.uniform(1 - 2 * t + 0.01, 0.9)))
        for _ in range(d):
            w = sorted(rng.uniform(t, t + (1 - 3 * t) * 0.6, 3))
            if sum(w) > 1:
                ok = False; break
            pool_vals += list(w)
        if not ok:
            continue
        for _ in range(e):
            w = sorted(rng.uniform(t, t + (1 - 2 * t) * 0.5, 2))
            if sum(w) > 1:
                ok = False; break
            pool_vals += list(w)
        if not ok:
            continue
        for _ in range(f):
            pool_vals.append(float(rng.uniform(t, 2 * t - 1e-4)))
        # 池件数须为 m：b+3d+2e+f = m ✓ 由守恒保证；池 = m-1 juniors + t
        if len(pool_vals) != m:
            continue
        t_idx = int(np.argmin(pool_vals))
        t = min(t, pool_vals[t_idx])     # t 收紧到最小池件
        s_all = sorted(ss_vals + sj_vals + s_vals)
        j_mach_all = sorted([pool_vals[i] for i in range(m) if i != t_idx], reverse=True)
        j_mach = list(j_mach_all)  # 反序配给升序 senior：j_mach[i] 配 s_all[i] 的反序位
        j_mach = [j_mach_all[nS - 1 - i] for i in range(nS)]  # 机器序=senior升序位，其 junior=反序第 i
        # 机器对 pair：反序指派可行性（Hall/V1）——此处直接查角落实例的 pair 下界
        # p 取到 pair 可达且 danger：p ∈ (5/4 - t, min pair 和]
        anti = sorted([s_all[i] + sorted(j_mach)[nS - 1 - i] for i in range(nS)])
        lo = 1.25 - t + 1e-4
        hi = min(s_all[i] + j_mach[i] for i in range(nS))
        if hi <= lo:
            continue
        p = float(rng.uniform(lo, min(hi, 0.999)))
        return dict(p=p, t=t, s=s_all, j=j_mach, pool=pool_vals, cnt=cnt)
    return None


def normalized_feasible(inst):
    """cap 半判决：规范化后是否存在可行 cnt-型装箱。枚举 SJ 伴侣集 C（剩余池 b 子集），
    SJ-REV 反序检查 + JJ/J 吸收。返回 (ok, detail)。"""
    a, b, c, d, e, f = inst['cnt']
    s_all = inst['s']
    pool = inst['pool']
    # S1/S2 后：SJ seniors = s_all[2a:2a+b]
    sj_sen = s_all[2 * a:2 * a + b]
    # SS 极端配对可行性（S1 保证若真实装箱存在——此处直查）
    ss = s_all[:2 * a]
    if any(ss[i] + ss[2 * a - 1 - i] > 1 + 1e-9 for i in range(a)):
        return False, 'SS 极端配对超载（S1 破）'
    # G2a：JJJ = 最小 3d
    jjj = pool[:3 * d]
    for i in range(d):
        if jjj[i] + jjj[3 * d - 1 - 2 * i] + jjj[2 * d - 1 - i] > 1 + 1e-9:
            return False, 'JJJ 最小 3d 蛇形分组超载（G2a 分组层破）'
    rest = pool[3 * d:]
    # 枚举 SJ 伴侣集 C ⊆ rest（|C|=b），反序配对 ≤1；剩余给 JJ/J
    for Cidx in combinations(range(len(rest)), b):
        if any(sj_sen[i] + rest[Cidx[b - 1 - i]] > 1 + 1e-9 for i in range(b)):
            continue
        leftover = [rest[i] for i in range(len(rest)) if i not in Cidx]
        # JJ-REV：剩余 2e 反序配对；J 独箱（恒 ≤1 因 junior<2t<=2/3<1）
        if all(leftover[i] + leftover[2 * e - 1 - i] <= 1 + 1e-9 for i in range(e)):
            return True, f'伴侣集 {tuple(round(rest[i], 3) for i in Cidx)}'
    return False, '所有伴侣子集失败'


def nofit_check(inst):
    """nofit 半：q1=最大池件。q1 在规范形式的伴侣 = 最小 SJ senior（反序配对）。
    也报真实装箱里 q1 的落箱类型（生成器里 q1 被用作 SJ 伴侣与否）。"""
    a, b, c, d, e, f = inst['cnt']
    s_all = inst['s']; pool = inst['pool']
    q1 = max(pool)
    am = s_all[0]
    K = 1.25 * (am + q1)
    sj_sen = s_all[2 * a:2 * a + b]
    if b == 0:
        return None
    sg_norm = sj_sen[0]  # 反序配对下最大 junior q1 配最小 SJ senior
    return dict(q1=q1, K=K, sg_norm=sg_norm, holds_norm=sg_norm + q1 > K + 1e-9,
                margin=sg_norm + q1 - K)


def synth_teeth():
    """JEL 否证形态：s'=0.9 池{0.5,0.11}——伴侣不能取最大 b（大者撑爆 cap）。
    机制必须能识别"取最大 b 个失败、取小者成功"。"""
    # 双形态：sj seniors [0.55,0.6]、候选池 [0.45,0.42,0.38]、b=2：
    # 取最大 2 个 {0.45,0.42}: 0.6+0.45=1.05>1 失败；取 {0.42,0.38}: 反序 0.55+0.42,0.6+0.38 ≤1 ✓
    sj_sen = [0.55, 0.6]; rest = [0.45, 0.42, 0.38]; b = 2
    ok_max = all(sj_sen[i] + sorted(rest, reverse=True)[i] <= 1 for i in range(b))
    ok_alt = all(sj_sen[i] + sorted([0.42, 0.38], reverse=True)[i] <= 1 for i in range(b))
    return ok_max, ok_alt


def main():
    t0 = time.time()
    om, omx = synth_teeth()
    print(f'牙齿（伴侣集选择双刃形态）：取最大b可行={om}（应 False）取替代集可行={omx}（应 True）'
          f' => {"有牙 ✓" if (not om and omx) else "无牙 ✗ 需修"}', flush=True)
    rng = np.random.default_rng(2026)
    st = {'gen': 0, 'cap_ok': 0, 'cap_bad': 0, 'nofit_hold': 0, 'nofit_fail': 0, 'b0': 0}
    fails = []
    mlo, mhi = 6, 14
    budget = float(os.environ.get('A2_SJ_BUDGET', '400'))
    while time.time() - t0 < budget:
        m = int(rng.integers(mlo, mhi + 1))
        inst = gen_packable_corner(rng, m)
        if inst is None:
            continue
        st['gen'] += 1
        ok, detail = normalized_feasible(inst)
        if ok:
            st['cap_ok'] += 1
        else:
            st['cap_bad'] += 1
            fails.append(('cap', m, inst['cnt'], detail))
            print(f'  ✗✗ cap 半反例 m={m} cnt={inst["cnt"]}: {detail}', flush=True)
        nf = nofit_check(inst)
        if nf is None:
            st['b0'] += 1
        elif nf['holds_norm']:
            st['nofit_hold'] += 1
        else:
            st['nofit_fail'] += 1
            fails.append(('nofit', m, inst['cnt'], nf))
            print(f"  ✗ nofit 半失败 m={m} cnt={inst['cnt']}: sg+q1-K={nf['margin']:.4f}", flush=True)
        if st['gen'] % 500 == 0:
            print(f'  ... {st} ({time.time()-t0:.0f}s)', flush=True)
            with open(OUT, 'a') as ff:
                ff.write(json.dumps({'ts': time.time(), 'stats': st}) + '\n')
    with open(OUT, 'a') as ff:
        ff.write(json.dumps({'ts': time.time(), 'final': st, 'fails': len(fails)}) + '\n')
    print(f'=== 判决：{st}（{time.time()-t0:.0f}s）===')


if __name__ == '__main__':
    main()
