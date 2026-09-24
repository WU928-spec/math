"""口袋3残留角落的统一 Farkas 证书族（与 k、t 无关，权重为 m 的一次函数）。

来源：p3_big_scan.jsonl 全部 432 个精确证书的支撑集一致（x<=y, y<=z, x>=t, y>=1-2t,
mach_i>MO ∀i, vol<=m），权重比例恒定 ⟹ 归纳出统一族，此处构造并精确验证。

恒等式（权重 w = (3m-1, 3m, 6m-1, 3m+1, 3×(m-1)个 mach, 3) / S，S=1+(6m-2)MG）：
  (3m-1)(y-x) + 3m(z-y) + (6m-1)(x-t) + (3m+1)(y+2t-1-MG)
  + 3Σ_i(s_i+j_i-x-y-z-MG) + 3(m-t-x-y-z-Σ(s_i+j_i)) = -1-(6m-2)MG < 0
x,y,z,t,s_i,j_i 全部消去（bt^T y=0：-（6m-1)+2(3m+1)-3=0），除以 S 得 bc^T y=-1。

验证：m=4..30 全 k 精确核对 A^T y=0, bt^T y=0, bc^T y=-1, y>=0；配消融。
"""
from fractions import Fraction as F
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pocket13_fixed import build_p3f
from farkas_fixed import float_cert, MG


def build_uniform_p3(m, k):
    """统一证书 y（Fraction 列表），任意 k（证书不用 k 相关约束）。"""
    A, bc, bt, names, nv = build_p3f(m, k)
    S = 1 + (6 * m - 2) * MG
    y = [F(0)] * len(A)
    for i, n in enumerate(names):
        if n == 'x<=y':
            y[i] = F(3 * m - 1) / S
        elif n == 'y<=z':
            y[i] = F(3 * m) / S
        elif n == 'x>=t':
            y[i] = F(6 * m - 1) / S
        elif n == 'y>=1-2t':
            y[i] = F(3 * m + 1) / S
        elif n.startswith('mach'):
            y[i] = F(3) / S
        elif n == 'vol<=m':
            y[i] = F(3) / S
    return A, bc, bt, names, nv, y


def exact_check(A, bc, bt, y, nv):
    ok = all(sum(A[i][j] * y[i] for i in range(len(y))) == 0 for j in range(nv))
    ok = ok and sum(bt[i] * y[i] for i in range(len(y))) == 0
    ok = ok and sum(bc[i] * y[i] for i in range(len(y))) == -1
    ok = ok and all(v >= 0 for v in y)
    return ok


if __name__ == '__main__':
    print('统一证书精确验证（m=4..30 全 k）:', flush=True)
    bad = []
    for m in range(4, 31):
        for k in range(1, m):
            A, bc, bt, names, nv, y = build_uniform_p3(m, k)
            if not exact_check(A, bc, bt, y, nv):
                bad.append((m, k))
    print('  ', '全部通过 ✓ (369+63=432 个 (m,k))' if not bad else f'{len(bad)} 处失败: {bad[:5]}')

    print('消融（m=8, k=3：去掉证书用到的每一族，必须变 feasible）:', flush=True)
    for kill, tag in [('x<=y', '去x<=y'), ('y<=z', '去y<=z'), ('x>=t', '去x>=t'),
                      ('y>=1-2t', '去y>=1-2t'), ('mach', '去全部mach'), ('vol<=m', '去vol<=m')]:
        A, bc, bt, names, nv = build_p3f(8, 3)
        idx = [i for i, n in enumerate(names) if not (n == kill or (kill == 'mach' and n.startswith('mach')))]
        yf = float_cert([A[i] for i in idx], [bc[i] for i in idx], [bt[i] for i in idx])
        print(f'   {tag:12s}: {"feasible（必要 ✓）" if yf is None else "仍有证书（非必要!）"}')
