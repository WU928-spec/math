"""验证：m=6 的常数 Farkas 证书是否对所有 m>=4 成立（即证书 m 无关）。
若成立，大 m 渐近平凡解决——一份证书覆盖所有 m 与 t。
做法：取 m=6 证书的非零约束（按 变量索引+系数 签名），在 m' 的 LP 中找同签名行，
组装 y' 后精确验证 A'^T y'=0, bt'^T y'=0, bc'^T y'=-1。
"""
from fractions import Fraction
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_constant import build_frac, float_cert, rationalize_verify


def logic_name(j, nS):
    if j == 0: return 'p'
    if j == 1: return 't'
    if 2 <= j < 2 + nS: return f's_{j - 2}'
    if 2 + nS <= j < 2 + 2 * nS: return f'j_{j - 2 - nS}'
    if j == 2 + 2 * nS: return 'a_m'
    return 'q_1'


def row_signature(row, nS):
    return tuple(sorted((logic_name(j, nS), c) for j, c in enumerate(row) if c != 0))


if __name__ == '__main__':
    # 1. m=6 提证书（nS=5）
    nS6 = 5
    A6, bc6, bt6, names6, nv6 = build_frac(6, (1, 3, 0, 1, 0, 0), 1)
    yf6 = float_cert(A6, bc6, bt6)
    y6, N6 = rationalize_verify(A6, bc6, bt6, yf6)
    sig_w = {}
    for i in range(len(y6)):
        if y6[i] != 0:
            sig_w[row_signature(A6[i], nS6)] = (y6[i], bc6[i], bt6[i])
    print(f'm=6 证书非零约束数: {len(sig_w)}')

    # 2. 对每个 m'，按逻辑签名匹配，组装 y' 并验证
    print('跨 m 验证（m=6 证书 -> m\' LP，逻辑签名匹配）:')
    ok_ms = []
    for mp in range(4, 25):
        nSp = mp - 1
        A, bc, bt, names, nv = build_frac(mp, (1, mp - 3, 0, 1, 0, 0), 1)
        sig_rows = {}
        for i in range(len(A)):
            s = row_signature(A[i], nSp)
            sig_rows.setdefault(s, []).append(i)
        yp = [Fraction(0)] * len(A)
        ok = True
        for s, (w, c0, c1) in sig_w.items():
            if s not in sig_rows:
                ok = False; break
            i = sig_rows[s][0]
            yp[i] = w
            if bc[i] != c0 or bt[i] != c1:
                ok = False; break
        if not ok:
            print(f'  m={mp}: 逻辑签名不匹配（证书对该 m 需独立版）')
            continue
        okv = all(sum(A[i][j] * yp[i] for i in range(len(yp))) == 0 for j in range(nv))
        okv = okv and sum(bt[i] * yp[i] for i in range(len(yp))) == 0
        okv = okv and sum(bc[i] * yp[i] for i in range(len(yp))) == -1
        okv = okv and all(v >= 0 for v in yp)
        print(f'  m={mp}: {"OK 证书适用" if okv else "组合后验证失败"}')
        if okv:
            ok_ms.append(mp)
    print(f'结论: m=6 证书覆盖 m = {ok_ms}' + ('（含所有 m>=6 则大 m 渐近平凡）' if ok_ms and max(ok_ms) >= 20 else ''))
