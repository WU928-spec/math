"""a3_endpoint_verify.py —— k=m−2（JJJ 墙）∀m 符号证书的机械验证（不解 LP）。

恒等式（自 374 发精确证书的支撑结构提取+手工配平，nS=m−1）：
  w = (4nS−2)·danger + 2(nS−1)·j1>=t + 2·A1_1 + 2·squeeze + (nS−1)·srt1
      + (nS−1)·B1_SS01 + 2(nS−1)·B2_JJJ01 + 2nS·A5_1 + 2·Σ_{i=2}^{nS−1} A5_i   (@k=m−2)
逐变量归零（手算，见 a3_endpoint_symbolic.md）：A^T w = 0；bt^T w = 0（t-uniform）；
bc^T w = −1/2 − 4(nS−1)·MG < 0。
行语义：danger/A1_1/squeeze/srt1/j1>=t/A5_i=(A) 类角落必要；B1=(B) 类 SS 存在必要（a>=1）；
B2=(B) 类 JJJ 存在必要（d>=1）的值语言合法形（j₁,j₂=全池最小两件）。
验证方式：Fraction 精确组合校验 m=5..60 × 两 razor cnt；并用 a1_value_lp2 实际行
独立对拍（防行定义笔误——宿疾纪律）。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as F
import a1_value_lp2 as V

MG = F(1, 10000)


def combo_check(m, cnt):
    """在 main 管线实际行上组装恒等式并校验。返回 (ok, msg)。"""
    nS = m - 1
    k = m - 2
    A, bc, bt, names, leg, nv = V.build(m, cnt, use_sjrev=False, use_s1v=False, use_jjrev=False)
    A, bc, bt, names = list(A), list(bc), list(bt), list(names)
    IP, IAM, IQ1 = 0, 1, 2
    vs = lambda r: 3 + (r - 1); vj = lambda r: 3 + nS + (r - 1)
    # 追加 A5/LZ/HZ @k=m−2（与 main_cegar3.build_k 同构）
    for i in range(1, k + 1):
        row = [F(0)] * nv; row[IP] = 1; row[vs(i)] = -1; row[vj(nS - k + i)] = -1
        A.append(row); bc.append(-MG); bt.append(F(0)); names.append(f'A5_{i}')
    row = [F(0)] * nv; row[vs(k)] = 4; row[IAM] = -5; row[IQ1] = -1
    A.append(row); bc.append(F(0)); bt.append(F(0)); names.append('LZ')
    row = [F(0)] * nv; row[vs(k + 1)] = -4; row[IAM] = 5; row[IQ1] = 1
    A.append(row); bc.append(-MG); bt.append(F(0)); names.append('HZ')

    wmap = {'danger': 4 * nS - 2, 'j1>=t': 2 * (nS - 1), 'A1_1': 2, 'squeeze': 2,
            'srt1': nS - 1, 'B1_SS01': nS - 1, 'B2_JJJ01': 2 * (nS - 1), 'A5_1': 2 * nS}
    for i in range(2, nS):
        wmap[f'A5_{i}'] = 2
    y = []
    for nm in names:
        y.append(F(wmap.get(nm, 0)))
    # A^T y
    for v in range(nv):
        s = sum(y[i] * A[i][v] for i in range(len(A)))
        if s != 0:
            return False, f'变量 {v} 系数 {s}'
    bcs = sum(y[i] * bc[i] for i in range(len(A)))
    bts = sum(y[i] * bt[i] for i in range(len(A)))
    if bts != 0:
        return False, f'bt^T y = {bts}'
    if bcs >= 0:
        return False, f'bc^T y = {bcs}'
    if any(w < 0 for w in y):
        return False, '负权重'
    return True, f'bc^T y = {bcs}（理论 −1/2−4(nS−1)MG = {F(-1,2) - 4 * (nS - 1) * MG}）'


def main():
    nok = nfail = 0
    for m in range(5, 61):
        for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
            if cnt[1] < 1:
                continue
            ok, msg = combo_check(m, cnt)
            if ok:
                nok += 1
            else:
                nfail += 1
                if nfail <= 5:
                    print(f'失败 m={m} cnt={cnt}: {msg}', flush=True)
        if m % 10 == 0:
            print(f'm={m} 通过（累计 OK {nok}）', flush=True)
    print(f'\n判决：OK {nok} / FAIL {nfail}')


if __name__ == '__main__':
    main()
