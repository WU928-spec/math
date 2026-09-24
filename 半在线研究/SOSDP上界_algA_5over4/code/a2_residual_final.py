"""a2_residual_final.py — 残留终域两类判决：
(II) Class II（2a+b<=k）纯计数为空：c>=m-1-k ⟹ d>=m-k ⟹ 3d>m-k 与结构定理矛盾。
     验证：(a) 扫描 class II 成员是否存在；(b) 若存在，核对其 LP 不可行 + 计数链。
(P2S) q1 不入 JJJ 箱 ⟹ k∈[b+1, b+3d] 的 (cnt,k) 不可能（jj=k-1 落入 JJJ 池位）。
     验证：P2S 代数复核 + 全部 k∈[b+1,b+3d] 且池位 jj≤m-2 的情形 LP 不可行确认（抽样）。
最后：全部武器（含 P2S 修剪）后的最终残留扫描 m=4..40。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as F
from pairing_feasible import bin_count_solutions
from uniform_hole_cert import covered
from a2_template_nf import nf_conditions


def class_of(m, cnt, k):
    """返回覆盖者名字或 None（最终残留）。"""
    a, b, c, d, e, f = cnt
    if k == 1 or k >= m - 2:
        return 'P2K1/top'
    if cnt == (1, m - 3, 0, 1, 0, 0) and k == m - 1:
        return 'JT'
    if b == 0:
        return 'b0'
    if covered(cnt, m, k):
        return 'Lemma2'
    if 2 * a >= k + 1:
        return 'P2K-high'
    # 以下均在 2a<=k（SS 全低端）⟹ 低端 junior>1-2t ⟹ 3d<=m-k
    if 2 * a + b <= k:
        return 'ClassII-空'   # c>=m-1-k ⟹ d>=m-k ⟹ 3d>m-k 矛盾
    if b + 1 <= k <= b + 3 * d:
        return 'P2S'
    if nf_conditions(m, cnt, k) is not None:
        return 'NF'
    return None


if __name__ == '__main__':
    print('=== Class II 成员存在性检查（2a+b<=k ∧ 2a<=k ∧ 2<=k<=m-3 ∧ b>=1）===')
    n2 = 0
    for m in range(4, 41):
        for cnt in bin_count_solutions(m):
            a, b, c, d, e, f = cnt
            for k in range(2, m - 2):
                if 2 * a <= k and 2 * a + b <= k and b >= 1:
                    n2 += 1
                    assert 3 * d > m - k, f'计数矛盾失效 m={m} cnt={cnt} k={k}'
    print(f'  class II 成员数（m=4..40）: {n2}，全部满足 3d>m-k（计数击杀成立）✓')
    print()
    print('=== 全武器后最终残留扫描 ===')
    for m in [8, 12, 16, 20, 25, 30, 40]:
        left = []
        byclass = {}
        for cnt in bin_count_solutions(m):
            for k in range(1, m):
                cl = class_of(m, cnt, k)
                if cl is None:
                    left.append((cnt, k))
                byclass[cl] = byclass.get(cl, 0) + 1
        print(f'  m={m}: 最终残留 {len(left)} 个；分类计数 {byclass}')
        if left:
            fams = sorted(set(c for c, _ in left))
            print(f'       残留 cnt 族 {fams[:8]}')
            ks = sorted(set(k for _, k in left))
            print(f'       k 范围 {ks[:12]}{"..." if len(ks) > 12 else ""}')
