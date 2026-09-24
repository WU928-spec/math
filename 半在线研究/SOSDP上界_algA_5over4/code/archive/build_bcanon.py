"""build_bcanon —— 路线 (b)：角落 LP 的装箱行换成 B 规范形（全部已证合法的必要条件行）。

装箱行设计（全部固定指标、值序坐标、逐条合法性出处见 JEL.md B 链）：
  SS  : 最小 2a seniors 的极端配对 s_{2i}+s_{2a-1-2i} ≤ 1        （S1，合法）
  SJ  : senior 中段 s_{2a+i} 与最小 b 个池件反序配对：
        s_{2a+i} + y_{b-1-i} ≤ 1                                  （Hall 必要性：∃匹配 ⟹ 此行组成立；
                                                                     支配：真实伴侣集 ⊇ 最小 b 逐分量）
  JJJ : 最小 3d 池件聚合：y_0+...+y_{3d-1} ≤ d（每三元组 ≤1 的聚合必要）
        + d=1 时的强形 y_0+y_1+y_2 ≤ 1                            （G2a，合法）
  JJ  : 最小 2e 池件反序配对 y_i+y_{2e-1-i} ≤ 1（在 SJ/JJJ 之后的剩余段上取）（JJ-REV+支配，合法）
  J   : 无帽（junior<1 恒真，免行）
值序坐标：角落 LP 的 junior 序只在 [0,jj] 由 mon2 合法给出（hole_close_lemma.md）。
  本构建器只在 k=m−1（jj=m−2，mon2 全序覆盖全部 junior）时断言值序可读；
  池序 = [t, j_0, ..., j_{m-2}]（t 最小，#7 合法）。
合法性边界登记：SJ 反序行的合法性依赖 senior 中段分割 w.l.o.g.（razor 带 G1 的
  精确残留——S1/S2 固定两端后中段为 SJ 集）；这是路线 (b) 承接的 (W'') 残余，
  比现行"SJ 保守形+中间三元组"的合法性缺口（中间三元组会破）严格更小。
"""
from fractions import Fraction as F
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed, float_cert, MG


def build_bcanon(m, cnt, k, use_mon2=True):
    """build_fixed(use_bins=False) + mon2 + B 规范形装箱行。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    A, bc, bt, names, nv = build_fixed(m, cnt, k, use_bins=False)

    def vs(i): return 2 + i
    def vj(i): return 2 + nS + i
    it = 1

    def con(row, c0, c1, nm):
        A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)

    def zero(): return [F(0)] * nv

    jj = k - 1
    if use_mon2:
        for i in range(jj):
            r = zero(); r[vj(i)] = 1; r[vj(i + 1)] = -1
            con(r, 0, 0, f'mon2_j{i}<=j{i+1}')

    # 池值序坐标：y[0]=t, y[i+1]=j_i（i=0..nS-1）。要求 mon2 覆盖：jj=nS-1（k=m-1）
    # 否则 hi 区 junior 无序，行引用机器序指标——合法性降级为"低端区值序"。
    full_order = (jj == nS - 1)
    pool = [it] + [vj(i) for i in range(nS)]   # y_0..y_{nS}，共 m 件

    def cap(idxs, nm):
        r = zero()
        for ix in idxs: r[ix] = 1
        con(r, 1, 0, nm)

    # SS：最小 2a 极端配对
    for kk in range(a):
        cap([vs(2 * kk), vs(2 * a - 1 - 2 * kk)], 'SS')
    # SJ：senior 中段 × 最小 b 池件反序（senior 升序配 junior 降序）
    for i in range(b):
        cap([vs(2 * a + i), pool[b - 1 - i]], 'SJ')
    # JJJ：最小 3d 聚合（≤d）+ 逐组强形（连续 3 件一组——合法性强形依赖 razor 近全等，
    #   保守默认只用聚合 + d=1 强形）
    if d >= 1:
        jjj = pool[b:b + 3 * d]
        r = zero()
        for ix in jjj: r[ix] = 1
        con(r, d, 0, 'JJJagg')          # 聚合：最小 3d 和 ≤ d
        if d == 1:
            cap(list(jjj), 'JJJ')       # d=1 时聚合=强形
    # JJ：JJJ 之后最小 2e 反序配对
    base = b + 3 * d
    for kk in range(e):
        cap([pool[base + kk], pool[base + 2 * e - 1 - kk]], 'JJ')
    return A, bc, bt, names, nv


if __name__ == '__main__':
    print("=== 路线(b) 洞族强度核验：build_bcanon(mon2+B规范形) 在洞族 (m=12..20, k=m-1) ===")
    from pairing_feasible import bin_count_solutions
    tot = 0; closed = 0
    for m in range(12, 21):
        cnt = (2, m - 5, 0, 1, 1, 0)
        k = m - 1
        A, bc, bt, names, nv = build_bcanon(m, cnt, k)
        yf = float_cert(A, bc, bt)
        tot += 1
        closed += (yf is not None)
        print(f"m={m} cnt={cnt} k={k}: {'INFEASIBLE ✓ 闭合' if yf is not None else 'FEASIBLE ✗ 洞存活'}")
    print(f"洞族闭合 {closed}/{tot}")
