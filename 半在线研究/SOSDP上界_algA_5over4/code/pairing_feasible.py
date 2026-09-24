"""配对级装箱可行性 LP：口袋 2 角落（i=1，他机全 2 件形态）。

判定问题：危险区（p + t > 5/4）下，"OPT=1 装箱可行 + 角落约束" 是否可同时成立？
若对所有箱型计数都 infeasible ⟹ 角落 OPT > 1 ⟹ 与归一化 OPT=1 矛盾 ⟹ p+t ≤ 5/4，闭合。

任务多重集（他机全 2 件 = 最紧形态）：
  p          单子机任务（最大初始任务），danger: p + t > 5/4
  t          fallback 任务，窄带 [t, 2t)
  s_1..s_{m-1}  他机 senior（该机最大件），非小引理: s > 1-2t
  j_1..j_{m-1}  他机 junior（该机其余件），窄带 [t, 2t)

两套配对（错配结构）：
  机器对（算法历史）: s_i + j_i > p   对每台他机 i
  OPT 箱对（重新打包）: 装箱分配，每箱容量 ≤ 1

LP 求解器自动把件大小调到最利于 feasible 的角点；若那样仍 infeasible，则强成立。
feasibility 用零目标向量。结论必须配消融测试。
"""
import numpy as np
from scipy.optimize import linprog
import itertools, sys, json, time, os

MARGIN = 1e-4


def bin_count_solutions(m):
    """枚举 rest 箱型计数 (a,b,c,d,e,f):
       a=#SS(2senior) b=#SJ c=#S(独占) d=#JJJ e=#JJ f=#J
       senior 守恒: 2a+b+c = m-1
       junior 守恒: b+3d+2e+f = m      (m-1 台他机 junior + t 自己)
       rest 箱数:  a+b+c+d+e+f = m-1   (推出 a = d+e+f)
    """
    nS = m - 1
    nJ = m
    out = []
    for a in range(nS // 2 + 1):
        for b in range(nS + 1):
            c = nS - 2 * a - b
            if c < 0:
                continue
            for d in range(nJ + 1):
                for e in range(nJ + 1):
                    f = a - d - e
                    if f < 0:
                        continue
                    if b + 3 * d + 2 * e + f != nJ:
                        continue
                    out.append((a, b, c, d, e, f))
    return out


def build_lp(m, cnt, t_fix=None,
             use_pair=True, use_senior_lb=True, use_narrow=True,
             use_danger=True, use_monotone=True, use_kcap=True, t_lo=None,
             L_max=1.0, use_firststep=False, q1_target=None):
    """对给定箱型计数构造 LP，判 feasibility。
    变量: [p, t, s_0..s_{m-2}, j_0..j_{m-2}, a_m, q_1]
    use_kcap: 口袋2本质约束 p<K=5L/4, L=a_m+q_1 (min senior + max 后续)
    q1_target=k (1-indexed): best-fit 第一步——q_1(最大后续)填第 k 大 senior 机
        ⟹ senior 排序 s_0≥...≥s_{nS-1}; q_1=j_{k-1}(该机junior=最大junior);
            前 k-1 大 senior 放不下 q_1(s_i+q_1>K); 第 k 大放得下(s_{k-1}+q_1<=K)
        use_firststep=True 等价于 q1_target=1 (填最大 senior 机)
    L_max: L=a_m+q_1 的上界（OPT 归一化下 ≤1）
    返回 (status, x or None)。status: 0=feasible, 2=infeasible
    """
    a, b, c, d, e, f = cnt
    nS = m - 1
    nv = 2 + 2 * nS + 2
    ip, it = 0, 1
    iam, iq1 = 2 + 2 * nS, 2 + 2 * nS + 1

    def vs(k): return 2 + k
    def vj(k): return 2 + nS + k

    A_ub, b_ub = [], []
    bounds = [(None, None)] * nv

    # p 范围: (0, 1]
    bounds[ip] = (0, 1)
    # t 窗口
    if t_fix is not None:
        bounds[it] = (t_fix, t_fix)
    else:
        tl = t_lo if t_lo is not None else (m - 1) / (4 * (m - 2))
        bounds[it] = (tl + MARGIN, 1 / 3)
    # senior 范围: 非小引理下界；上界 ≤ 1（箱容量）
    for k in range(nS):
        bounds[vs(k)] = ((1 - 2 * (t_fix if t_fix is not None else 1/3) + MARGIN) if use_senior_lb else (MARGIN), 1)
    # junior 窄带 [t, 2t)
    for k in range(nS):
        if use_narrow:
            bounds[vj(k)] = (None, 2 * (t_fix if t_fix is not None else 1/3) - MARGIN)
        else:
            bounds[vj(k)] = (MARGIN, 1)

    # 窄带 junior 下界 j >= t  （线性约束 -t + j >= 0）
    if use_narrow:
        for k in range(nS):
            row = [0.0] * nv
            row[it] = 1.0
            row[vj(k)] = -1.0
            A_ub.append(row); b_ub.append(0.0)   # t - j <= 0  ⟺ j >= t

    # danger: p + t >= 5/4  ⟺  -p - t <= -5/4 - MARGIN
    if use_danger:
        row = [0.0] * nv
        row[ip] = -1.0; row[it] = -1.0
        A_ub.append(row); b_ub.append(-(5 / 4) - MARGIN)

    # 机器对和: s_i + j_i >= p + MARGIN  ⟺  p - s_i - j_i <= -MARGIN
    if use_pair:
        for i in range(nS):
            row = [0.0] * nv
            row[ip] = 1.0; row[vs(i)] = -1.0; row[vj(i)] = -1.0
            A_ub.append(row); b_ub.append(-MARGIN)

    # 递减到达（序动态核心）: 后续任务 ≤ 最小初始任务 = min senior
    # （他机全2件最紧形态下 senior=初始任务；p 最大故 min初始=min_i s_i）
    #   j_i <= s_k ∀i,k ；t <= s_k ∀k
    if use_monotone:
        for i in range(nS):
            for k in range(nS):
                row = [0.0] * nv
                row[vj(i)] = 1.0; row[vs(k)] = -1.0
                A_ub.append(row); b_ub.append(0.0)
        for k in range(nS):
            row = [0.0] * nv
            row[it] = 1.0; row[vs(k)] = -1.0
            A_ub.append(row); b_ub.append(0.0)

    # 口袋2本质约束: 他机负载≤K（best-fit累积不超K），fallback到单子机 ⟹ p 最空 ⟹ p<K
    #   K=5L/4, L=a_m+q_1, a_m=min senior, q_1=max 后续(≥j_i,≥t), 递减 q_1≤a_m
    if use_kcap:
        for i in range(nS):
            row = [0.0] * nv; row[iam] = 1.0; row[vs(i)] = -1.0
            A_ub.append(row); b_ub.append(0.0)          # a_m <= s_i
            row = [0.0] * nv; row[vj(i)] = 1.0; row[iq1] = -1.0
            A_ub.append(row); b_ub.append(0.0)          # j_i <= q_1
        row = [0.0] * nv; row[it] = 1.0; row[iq1] = -1.0
        A_ub.append(row); b_ub.append(0.0)              # t <= q_1
        row = [0.0] * nv; row[iq1] = 1.0; row[iam] = -1.0
        A_ub.append(row); b_ub.append(0.0)              # q_1 <= a_m (递减)
        row = [0.0] * nv; row[ip] = 1.0; row[iam] = -1.25; row[iq1] = -1.25
        A_ub.append(row); b_ub.append(-MARGIN)          # p <= 5(a_m+q_1)/4 - margin = K
        row = [0.0] * nv; row[iam] = 1.0; row[iq1] = 1.0
        A_ub.append(row); b_ub.append(L_max)            # L = a_m+q_1 <= L_max

    # best-fit 第一步: q_1(最大后续)填第 q1_target 大 senior 机
    kt = q1_target if q1_target is not None else (1 if use_firststep else None)
    if kt is not None:
        # senior 排序 s_0>=s_1>=...>=s_{nS-1}
        for i in range(nS - 1):
            row = [0.0] * nv; row[vs(i)] = 1.0; row[vs(i + 1)] = -1.0
            A_ub.append(row); b_ub.append(0.0)
        # 第 kt 台(索引kt-1)的 junior = q_1 = 最大 junior: j_{kt-1}>=j_i 且 q_1=j_{kt-1}
        jj = kt - 1
        for i in range(nS):
            row = [0.0] * nv; row[vj(jj)] = 1.0; row[vj(i)] = -1.0
            A_ub.append(row); b_ub.append(0.0)          # j_{kt-1} >= j_i
        row = [0.0] * nv; row[iq1] = 1.0; row[vj(jj)] = -1.0
        A_ub.append(row); b_ub.append(0.0)              # q_1 <= j_{kt-1} (结合>= ⟹ =)
        # 前 kt-1 大 senior 放不下 q_1: s_i+q_1>K ⟺ 4s_i+4q_1>5(a_m+q_1) ⟺ -4s_i+5a_m+q_1<0
        for i in range(kt - 1):
            row = [0.0] * nv; row[vs(i)] = -4.0; row[iam] = 5.0; row[iq1] = 1.0
            A_ub.append(row); b_ub.append(-MARGIN)
        # 第 kt 大放得下: s_{kt-1}+q_1<=K ⟺ 4s_{kt-1}+4q_1<=5(a_m+q_1) ⟺ 4s_{kt-1}-5a_m-q_1<=0
        row = [0.0] * nv; row[vs(kt - 1)] = 4.0; row[iam] = -5.0; row[iq1] = -1.0
        A_ub.append(row); b_ub.append(0.0)

    # 装箱容量（固定分组代表；件为对称连续变量，固定分组不失一般性）
    # senior 分组: SS 箱用 s_0..s_{2a-1} 两两配对; SJ 箱用 s_{2a}..s_{2a+b-1}; S 箱其余
    # junior 池 = nS 个他机 junior + t 自己（t 也是 junior-sized，须装进某 rest 箱）
    jslots = [vj(k) for k in range(nS)] + [it]   # 长度 m
    def cap(idxs):
        row = [0.0] * nv
        for ix in idxs:
            row[ix] = 1.0
        A_ub.append(row); b_ub.append(1.0)

    # SS 箱
    for k in range(a):
        cap([vs(2 * k), vs(2 * k + 1)])
    # SJ 箱: senior s_{2a+k} 配 junior 池第 k 件（错配: senior 与其机器 junior 一般不同槽）
    for k in range(b):
        cap([vs(2 * a + k), jslots[k]])
    # JJJ 箱
    jidx = b
    for k in range(d):
        cap([jslots[jidx], jslots[jidx + 1], jslots[jidx + 2]])
        jidx += 3
    # JJ 箱
    for k in range(e):
        cap([jslots[jidx], jslots[jidx + 1]])
        jidx += 2
    # J 箱与 S 箱容量恒真（单件 ≤ 1），略

    res = linprog(c=np.zeros(nv), A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  bounds=bounds, method="highs")
    return res.status, (res.x if res.status == 0 else None)


def scan(m, t_values, **kw):
    cnts = bin_count_solutions(m)
    print(f"m={m}: {len(cnts)} 种箱型计数组合", flush=True)
    summary = {}
    for t in t_values:
        feas = []
        for cnt in cnts:
            st, x = build_lp(m, cnt, t_fix=t, **kw)
            if st == 0:
                feas.append((cnt, x))
        summary[t] = feas
        tag = "FEASIBLE(危险可达!)" if feas else "infeasible(角落空)"
        print(f"  t={t:.4f}: {tag}  (可行箱型数 {len(feas)}/{len(cnts)})", flush=True)
    return summary


if __name__ == "__main__":
    t0 = time.time()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"

    if cmd == "scan":
        for m in [6, 7, 8]:
            tl = (m - 1) / (4 * (m - 2))
            tvs = np.linspace(tl + 0.005, 1 / 3, 6)
            scan(m, tvs)
        print(f"\n总耗时 {time.time()-t0:.0f}s")

    elif cmd == "scanfs":
        # 加 best-fit 第一步约束(max后续填max senior机)后扫描
        for m in [6, 7, 8, 9, 10]:
            tl = (m - 1) / (4 * (m - 2))
            tvs = np.linspace(tl + 0.005, 1 / 3, 6)
            scan(m, tvs, use_firststep=True)
        print(f"\n总耗时 {time.time()-t0:.0f}s")

    elif cmd == "ablate":
        m = 6
        tl = (m - 1) / (4 * (m - 2))
        t = (tl + 1 / 3) / 2
        cnts = bin_count_solutions(m)
        base = sum(build_lp(m, c, t_fix=t)[0] == 0 for c in cnts)
        print(f"m={m} t={t:.4f}  全约束可行箱型数: {base}/{len(cnts)}")
        for name, kw in [
            ("去机器对和", dict(use_pair=False)),
            ("去senior非小", dict(use_senior_lb=False)),
            ("去窄带", dict(use_narrow=False)),
            ("去danger", dict(use_danger=False)),
            ("去递减约束", dict(use_monotone=False)),
            ("去p<K约束", dict(use_kcap=False)),
        ]:
            n = sum(build_lp(m, c, t_fix=t, **kw)[0] == 0 for c in cnts)
            print(f"  消融[{name}]: 可行箱型数 {n}/{len(cnts)}")

    elif cmd == "Lsweep":
        # 扫 L_max 下界: 找角落静态可行的最小 L（L 小则 K 小、p<K 紧）
        # 若角落静态可行需 L>=L*，而 L* 大（K>>p），配合 best-fit K 封顶形成夹击
        for m in [6, 7, 8, 9, 10]:
            tl = (m - 1) / (4 * (m - 2))
            cnts = bin_count_solutions(m)
            for t in np.linspace(tl + 0.004, 1 / 3, 5):
                Lcrit = 1 - 4 * t / 5   # 口袋2 ⟹ L>此（否则 K<p）
                # 二分/线扫 L_max 从 Lcrit 升到 1，找可行区间
                feas_Ls = []
                for L in np.linspace(Lcrit + 1e-3, 1.0, 24):
                    n = sum(build_lp(m, c, t_fix=t, L_max=L)[0] == 0 for c in cnts)
                    if n > 0:
                        feas_Ls.append(L)
                if feas_Ls:
                    print(f"  m={m} t={t:.4f}: 角落静态可行 L∈[{min(feas_Ls):.4f},{max(feas_Ls):.4f}]"
                          f"  (L下界Lcrit={Lcrit:.4f}, K=5L/4 最小≈{5*min(feas_Ls)/4:.4f}, p>={5/4-t:.4f})")
                else:
                    print(f"  m={m} t={t:.4f}: 全 L 静态不可行（角落闭合）")

    elif cmd == "sanity":
        # 已知可行配置: 远离危险的宽松配置应判 FEASIBLE
        m = 6
        cnts = bin_count_solutions(m)
        n = sum(build_lp(m, c, t_fix=0.30, use_danger=False)[0] == 0 for c in cnts)
        print(f"sanity(无danger宽松配置) 可行箱型数 {n}/{len(cnts)}  —— 应 >0 才说明 LP 没把可行判成不可行")

    elif cmd == "reach":
        # 序动态可达性验证: 抓 LP feasible 代表解, 构造真实递减序列, 实跑 Algorithm A
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from toolbox import fallback_event, opt_float, algA
        ms_range = [int(a) for a in sys.argv[2].split(",")] if len(sys.argv) > 2 else [6, 7, 8]
        total_none, total_fb = 0, 0
        worst = 0.0
        for m in ms_range:
            tl = (m - 1) / (4 * (m - 2))
            for t in np.linspace(tl + 0.004, 1 / 3, 8):
                for cnt in bin_count_solutions(m):
                    st, x = build_lp(m, cnt, t_fix=t)
                    if st != 0:
                        continue
                    nS = m - 1
                    p, tt = x[0], x[1]
                    s = x[2:2 + nS]; j = x[2 + nS:2 + 2 * nS]
                    seq = sorted([p] + list(s), reverse=True) + sorted(list(j) + [tt], reverse=True)
                    ev = fallback_event(seq, m)
                    if ev is None:
                        total_none += 1
                    else:
                        total_fb += 1
                        opt = opt_float(seq, m) if len(seq) <= 22 else ev["L"]
                        r = algA(seq, m) / opt
                        worst = max(worst, r)
                        print(f"  ★真fallback m={m} t={t:.4f}: 比值={r:.4f}")
        print(f"\n汇总 m∈{ms_range} 全t窗口: K封顶/平凡 {total_none} 例, 真fallback {total_fb} 例, 最高比值 {worst:.4f}")

    elif cmd == "find":
        # 抓出唯一 feasible 箱型，重构装箱，看每箱 slack 是否 < t
        for m in [6, 7, 8]:
            tl = (m - 1) / (4 * (m - 2))
            t = (tl + 1 / 3) / 2
            cnts = bin_count_solutions(m)
            for cnt in cnts:
                st, x = build_lp(m, cnt, t_fix=t)
                if st != 0:
                    continue
                a, b, c, d, e, f = cnt
                nS = m - 1
                p, tt = x[0], x[1]
                s = x[2:2 + nS]
                j = x[2 + nS:2 + 2 * nS]
                print(f"\n=== m={m} t={t:.4f}  唯一feasible箱型 (SS,SJ,S,JJJ,JJ,J)=({a},{b},{c},{d},{e},{f}) ===")
                print(f"  p={p:.4f}  t={tt:.4f}  p+t={p+tt:.4f}")
                print(f"  senior s_i: {np.round(s,4)}")
                print(f"  junior j_i: {np.round(j,4)}")
                # 重构装箱: 按固定分组算每箱体积与 slack
                jslots = list(j) + [tt]
                bins = []
                for k in range(a):
                    bins.append(("SS", s[2*k] + s[2*k+1]))
                for k in range(b):
                    bins.append(("SJ", s[2*a+k] + jslots[k]))
                for k in range(c):
                    bins.append(("S ", s[2*a+b+k]))
                jidx = b
                for k in range(d):
                    bins.append(("JJJ", jslots[jidx]+jslots[jidx+1]+jslots[jidx+2])); jidx += 3
                for k in range(e):
                    bins.append(("JJ", jslots[jidx]+jslots[jidx+1])); jidx += 2
                for k in range(f):
                    bins.append(("J ", jslots[jidx])); jidx += 1
                print(f"  rest 装箱 (m-1={m-1}箱) + p独占:")
                for nm, vol in bins:
                    slack = 1 - vol
                    flag = "  <-- slack>=t, t可进!" if slack >= tt - 1e-6 else ""
                    print(f"    [{nm}] vol={vol:.4f} slack={slack:.4f}{flag}")
