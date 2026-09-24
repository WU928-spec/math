"""a3_template_verify.py —— 任务③模板机：∀m 统一符号证书的机械验证（不解 LP）。

T2 模板（lean 版，候选全域统一证书；权重经 a3_template_fit.py 从 115 精确证书提取）：
  10·danger + 6·jmax<=q1 + 5·q1<=am + 10·(t<=1/3) + 5·B1_SS01 + 4·B4_{q=nS-k}
  + 5·A5_1 + 5·A5_2 + 1·HZ + 5·jrt_{nS-k+1} + 6·Σ_{r=nS-k+2}^{nS-1} jrt_r
手证（系数逐变量核对）：
  p: -10+5+5=0; am: -5+5=0; q1: -6+5+1=0; s1/s2: 5-5=0; s_{k+1}: 4-4=0;
  j_{nS-k+1}: -5+5=0; j_{nS-k+2}: -5+4-5+6=0; j_r(nS-k+2<r<nS): -6+6=0; j_nS: -6+6=0（k>2）
  k=2 时 j_nS=j_{nS-k+2}: -5+4-5+6=0 ✓
  bc^T w = -25/2+10/3+5+4-11MG = -1/6-11MG < 0; bt^T w = 10-10 = 0 ✓
行存在域：B4_q 需 q=nS-k ∈ [2a+1, nS-2] ⟺ k∈[2, m-2a-2] —— cnt1: k<=m-4; cnt2: k<=m-6。
  ⟹ 条件层（cnt1 k=m-3；cnt2 k=m-5..m-3）恰为 q=nS-k 跌出 B4 值域之处——
  任务②观测的 sjrev 顶薄层的结构解释。
T1a/T1b 同录（备选射线）。

验证方式：对 (m,cnt,k) 直接构造行组合，精确检查 A^T w=0 ∧ bc^T w<0 ∧ bt^T w=0（Fraction）。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as F
import a1_value_lp2 as V


def template_rows(m, cnt, k, which='T2'):
    """返回 [(row(Fraction 向量), bc, bt, name, weight)]——模板证书的行+权重。"""
    nS = m - 1
    nv = 3 + 2 * nS
    IP, IAM, IQ1 = 0, 1, 2
    vs = lambda r: 3 + (r - 1)
    vj = lambda r: 3 + nS + (r - 1)
    MG = F(1, 10000)
    q = nS - k
    a = cnt[0]
    assert 2 * a + 1 <= q <= nS - 2, f'B4 值域外: m={m} k={k} q={q}'

    out = []

    def add(coefs, bc, bt, nm, w):
        row = [F(0)] * nv
        for idx, c in coefs:
            row[idx] = F(c)
        out.append((row, F(bc), F(bt), nm, F(w)))

    # danger: -p <= -5/4 + t
    add([(IP, -1)], F(-5, 4), 1, 'danger', 10 if which == 'T2' else 30)
    # jmax<=q1: j_nS - q1 <= 0
    add([(vj(nS), 1), (IQ1, -1)], 0, 0, 'jmax<=q1', 6 if which == 'T2' else 18)
    # q1<=am: q1 - am <= 0
    add([(IQ1, 1), (IAM, -1)], 0, 0, 'q1<=am', 5 if which == 'T2' else 15)
    # t<=1/3: 0 <= 1/3 - t（仅 T2）
    if which == 'T2':
        add([], F(1, 3), -1, 't<=1/3', 10)
    else:
        # j1>=t: -j1 <= -t；B2: j1+j2 <= 1-t；jrt1: j1-j2 <= 0（T1a/T1b 的 bt 配平组）
        add([(vj(1), -1)], 0, -1, 'j1>=t', 20)
        add([(vj(1), 1), (vj(2), 1)], 1, -1, 'B2_JJJ01', 10)
        add([(vj(1), 1), (vj(2), -1)], 0, 0, 'jrt1', 10)
    # B1: s1+s2 <= 1
    add([(vs(1), 1), (vs(2), 1)], 1, 0, 'B1_SS01', 5 if which == 'T2' else 15)
    # B4_q: s_{nS+1-q} + j_{q+2} <= 1
    add([(vs(nS + 1 - q), 1), (vj(q + 2), 1)], 1, 0, f'B4_q{q}', 4 if which == 'T2' else 12)
    # A5_i: p - s_i - j_{nS-k+i} <= -MG
    add([(IP, 1), (vs(1), -1), (vj(nS - k + 1), -1)], -MG, 0, 'A5_1', 5 if which == 'T2' else (30 if which == 'T1b' else 15))
    # HZ: -4 s_{k+1} + 5am + q1 <= -MG
    add([(vs(k + 1), -4), (IAM, 5), (IQ1, 1)], -MG, 0, 'HZ', 1 if which == 'T2' else 3)
    if which in ('T2', 'T1a'):
        add([(IP, 1), (vs(2), -1), (vj(nS - k + 2), -1)], -MG, 0, 'A5_2', 5 if which == 'T2' else 15)
    else:  # T1b: srt1 代 A5_2
        add([(vs(1), 1), (vs(2), -1)], 0, 0, 'srt1', 15)
    # jrt 链：jrt_{nS-k+1} 首 + jrt_{nS-k+2..nS-1}
    if which == 'T2':
        first, rest = 5, 6
    elif which == 'T1a':
        first, rest = 15, 18
    else:
        first, rest = 30, 18
    add([(vj(nS - k + 1), 1), (vj(nS - k + 2), -1)], 0, 0, f'jrt{nS-k+1}', first)
    for r in range(nS - k + 2, nS):
        add([(vj(r), 1), (vj(r + 1), -1)], 0, 0, f'jrt{r}', rest)
    return out, nv


def verify(m, cnt, k, which='T2'):
    T, nv = template_rows(m, cnt, k, which)
    # A^T w：逐变量
    for v in range(nv):
        s = sum(w * row[v] for row, _, _, _, w in T)
        if s != 0:
            return False, f'变量 {v} 系数 {s}'
    bcT = sum(w * bc for _, bc, _, _, w in T)
    btT = sum(w * bt for _, _, bt, _, w in T)
    if btT != 0:
        return False, f'bt^T w = {btT}'
    if bcT >= 0:
        return False, f'bc^T w = {bcT} >= 0'
    if any(w < 0 for _, _, _, _, w in T):
        return False, '负权重'
    return True, f'bc^T w = {bcT}'


def main():
    for which in ['T2', 'T1a', 'T1b']:
        nok = nskip = nfail = 0
        fails = []
        for m in range(6, 61):
            for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
                a = cnt[0]
                for k in range(2, m - 2):
                    q = (m - 1) - k
                    if not (2 * a + 1 <= q <= (m - 1) - 2):
                        nskip += 1
                        continue
                    ok, msg = verify(m, cnt, k, which)
                    if ok:
                        nok += 1
                    else:
                        nfail += 1
                        if len(fails) < 5:
                            fails.append((m, cnt[0], k, msg))
        print(f'{which}: 验证通过 {nok}，值域外跳过 {nskip}，失败 {nfail}')
        for f in fails:
            print('   失败:', f)


if __name__ == '__main__':
    main()
