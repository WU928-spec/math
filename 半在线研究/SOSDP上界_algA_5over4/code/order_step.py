"""保序约束 LP：在二步基础上加保序引理（h 枚举），杀 tiered ghost。
引理（已证）：s_i < s_k 且 j_i > j_k ⟹ s_k + j_i > K。
推论：senior <= K−q1 的机器段上 junior 单调不降。参数 h = 高端自由区高度：
  机器 0..nS−h−1：s <= K−q1（−MG），junior 升序 j_i <= j_{i+1}；
  机器 nS−h..nS−1：s > K−q1（自由区，可逆序）。
h 遍历 0..nS（h=0 表示全部 junior 升序；h=nS 表示无约束=原 LP）。每个真实配置必有某 h 成立。
"""
from fractions import Fraction as F
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from second_step import build_fixed2
from farkas_fixed import float_cert, rationalize_verify, MG


def add_order(A, bc, bt, names, nv, nS, h):
    """在 build_fixed2 的矩阵上追加保序约束。变量索引：p=0,t=1,s_i=2+i,j_i=2+nS+i,am=2+2nS,q1=2+2nS+1。"""
    def vs(i): return 2 + i
    def vj(i): return 2 + nS + i
    iam, iq1 = 2 + 2 * nS, 2 + 2 * nS + 1

    def con(row, c0, c1, nm):
        A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)

    def zero(): return [F(0)] * nv

    top = nS - h   # 自由区起点
    for i in range(top):
        # s_i <= K−q1 ⟺ s_i + q1 <= K ⟺ 4s_i+4q1 <= 5a_m+5q1 ⟺ 4s_i − 5a_m − q1 <= 0
        r = zero(); r[vs(i)] = 4; r[iam] = -5; r[iq1] = -1; con(r, 0, 0, f'lowzone{i}')
    for i in range(top, nS):
        # s_i > K−q1 ⟺ 4s_i − 5a_m − q1 >= MG（>K ⟺ −4s_i+5a_m+q1 <= −MG）
        r = zero(); r[vs(i)] = -4; r[iam] = 5; r[iq1] = 1; con(r, -MG, 0, f'hizone{i}')
    for i in range(top - 1):
        # junior 升序（低端区）
        r = zero(); r[vj(i)] = 1; r[vj(i + 1)] = -1; con(r, 0, 0, f'ord{i}')
    return A, bc, bt, names, nv


def build_fixed3(m, cnt, k, jj2, h):
    A, bc, bt, names, nv = build_fixed2(m, cnt, k, jj2=jj2)
    return add_order(A, bc, bt, names, nv, m - 1, h)


if __name__ == '__main__':
    print('=== 保序 LP 杀 tiered ghost（m=18..20 残留）===')
    residuals = [
        (18, (3, 11, 0, 1, 2, 0), 15), (18, (3, 11, 0, 1, 2, 0), 16), (18, (3, 11, 0, 1, 2, 0), 17),
        (19, (3, 12, 0, 1, 2, 0), 16), (19, (3, 12, 0, 1, 2, 0), 17), (19, (3, 12, 0, 1, 2, 0), 18),
        (20, (3, 13, 0, 1, 2, 0), 17), (20, (3, 13, 0, 1, 2, 0), 18), (20, (3, 13, 0, 1, 2, 0), 19),
    ]
    for m, cnt, k in residuals:
        nS = m - 1
        jj = k - 1
        # 先找二步残留 jj2
        rem2 = []
        for j2 in range(nS):
            if j2 == jj:
                continue
            A, bc, bt, names, nv = build_fixed2(m, cnt, k, jj2=j2)
            if float_cert(A, bc, bt) is None:
                rem2.append(j2)
        if not rem2:
            print(f'm={m} cnt={cnt} k={k}: 二步已闭')
            continue
        allclosed = True
        for j2 in rem2:
            kill_h = []
            for h in range(nS + 1):
                A, bc, bt, names, nv = build_fixed3(m, cnt, k, j2, h)
                if float_cert(A, bc, bt) is None:
                    kill_h.append(h)
            if kill_h:
                allclosed = False
                print(f'  m={m} k={k} jj2={j2}: 保序仍未杀 h={kill_h}')
        if allclosed:
            print(f'm={m} cnt={cnt} k={k}: 保序全杀（残留 jj2={rem2}）✓')
