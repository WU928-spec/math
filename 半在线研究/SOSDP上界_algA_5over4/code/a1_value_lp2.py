"""值语言 LP（main 设计, a1 实施）: razor 带 k=2..m-3 open 段的合法松弛闭合尝试。
变量 x=[p, am, q1, s_1..s_{nS}, j_1..j_{nS}]（值序, srt/jrt 升序行定义）, t 参数(bt)。
每行注释=合法性方向+一句证明。若全域 INFEASIBLE(常数 Farkas 证书) ⟹ open 段合法闭合。
"""
import numpy as np, sys, os, json, time
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import float_cert, rationalize_verify, MG

F5 = F(5, 4)

def build(m, cnt, use_a1=True, use_a2=True, use_a3=True, use_b1=True, use_b2=True, use_b3=True, use_b4=True,
          use_s1v=True, use_jjrev=True, use_sjrev=True):
    nS = m - 1
    nv = 3 + 2 * nS
    IP, IAM, IQ1 = 0, 1, 2
    def vs(r): return 3 + (r - 1)          # s_r, r=1..nS
    def vj(r): return 3 + nS + (r - 1)       # j_r, r=1..nS
    A, bc, bt, names, leg = [], [], [], [], []

    def con(row, c0, c1, nm, proof):
        A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1))
        names.append(nm); leg.append(proof)

    def zero(): return [F(0)] * nv
    z = zero()

    # 值序定义行(语言本身, 非约束)
    for r in range(1, nS):
        r_ = list(z); r_[vs(r)] = 1; r_[vs(r + 1)] = -1
        con(r_, 0, 0, f'srt{r}', '值语言坐标定义(srt 升序)')
        r_ = list(z); r_[vj(r)] = 1; r_[vj(r + 1)] = -1
        con(r_, 0, 0, f'jrt{r}', '值语言坐标定义(jrt 升序)——junior 天然全序, 索引问题消失')

    # A4 值域
    r_ = list(z); r_[IP] = -1
    con(r_, -F5, 1, 'danger', '角落: p+t>5/4')
    r_ = list(z); r_[IP] = 1
    con(r_, 1, 0, 'p<=1', '角落: p 是负载<=OPT=1')
    r_ = list(z); r_[vj(1)] = -1
    con(r_, 0, -1, 'j1>=t', '窄带 j>=t + 升序传播(合法: 全序下 j1 全局最小)')
    for rr in range(1, nS + 1):
        r_ = list(z); r_[vj(rr)] = 1
        con(r_, 0, 2, f'j{rr}<=2t', '窄带 j<2t(逐行, 合法)')
    r_ = list(z); r_[vs(1)] = -1
    con(r_, -1, 2, 's1>=1-2t', 'senior 非小引理 s>1-2t + 升序传播')
    r_ = list(z); r_[vs(nS)] = 1
    con(r_, 1, 0, 'smax<=1', 'senior<=1')
    r_ = list(z); r_[vj(nS)] = 1; r_[IQ1] = -1
    con(r_, 0, 0, 'jmax<=q1', 'q1=最大 junior')
    r_ = list(z); r_[IQ1] = 1; r_[IAM] = -1
    con(r_, 0, 0, 'q1<=am', '递减 q1<=a_m')
    r_ = list(z); r_[IAM] = 1; r_[vs(1)] = -1
    con(r_, 0, 0, 'am<=s1', 'a_m=min senior(值语言 s1)')
    r_ = list(z); r_[IAM] = 1; r_[IQ1] = 1
    con(r_, 1, 0, 'L<=1', 'L=a_m+q1<=OPT=1')
    r_ = list(z); r_[IQ1] = -1
    con(r_, 0, -1, 't<=q1', 'q1 是后续件>=t')
    tlo = F(m - 1, 4 * (m - 2))
    con(list(z), -tlo, 1, 't>=tlo', 't 窗口下界(归一化推论)')
    con(list(z), F(1, 3), -1, 't<=1/3', 't 窗口上界')

    # A1: 反序 pair 下界 j_r + s_{nS+1-r} >= p
    # 合法: 真实机器配对全 >=p; 反序(小 j 配大 s)是 maximin 配对(交换论证: 若 sa<=sb,jc<=jd
    # 则 min(sa+jd, sb+jc) >= min(sa+jc, sb+jd))——反序最小和 >= 任意配对最小和 >= p。
    if use_a1:
        for rr in range(1, nS + 1):
            r_ = list(z); r_[IP] = 1; r_[vs(nS + 1 - rr)] = -1; r_[vj(rr)] = -1
            con(r_, 0, 0, f'A1_{rr}', '反序 maximin: 真实配对>=p ⟹ 反序>=p')

    # A2: 反序负载帽 j_r + s_{nS+1-r} <= K=5(am+q1)/4
    # 合法: 真实机器负载<=K(best-fit 放置帽, 负载单调) ⟹ 某配对全<=K ⟹ 反序 minimax
    # (交换论证: max(sa+jd, sb+jc) <= max(sa+jc, sb+jd)) 全<=K。
    if use_a2:
        for rr in range(1, nS + 1):
            r_ = list(z); r_[vs(nS + 1 - rr)] = 4; r_[vj(rr)] = 4
            r_[IAM] = -5; r_[IQ1] = -5
            con(r_, 0, 0, f'A2_{rr}', '反序 minimax: 真实负载<=K ⟹ 反序<=K')

    # A3 挤压: Σ(s+j) <= nS - t
    # 合法: 挤压引理(Σℓ<=m-1-t, LP_ROUTE/挤压引理)。
    if use_a3:
        r_ = list(z)
        for rr in range(1, nS + 1):
            r_[vs(rr)] = 1; r_[vj(rr)] = 1
        con(r_, nS, -1, 'squeeze', '挤压引理 Σℓ<=nS-t')

    # B1: s1+s2<=1 (a>=1 ⟹ SS 对存在; 值语言最小两件和<=1)
    if use_b1:
        r_ = list(z); r_[vs(1)] = 1; r_[vs(2)] = 1
        con(r_, 1, 0, 'B1_SS01', 'a=d+e+f>=1 ⟹ 存在 SS 对(和<=1) ⟹ 最小两件和<=1')
    # B2: j1+j2<=1-t (d>=1 ⟹ 最小三元组 t+两最小 junior<=1; 值语言 j1,j2 全局最小——合法!)
    if use_b2:
        r_ = list(z); r_[vj(1)] = 1; r_[vj(2)] = 1
        con(r_, 1, -1, 'B2_JJJ01', 'd=1+c+f>=1 ⟹ 三元组存在 ⟹ 池最小三件=t+j1+j2<=1')
    # B3: s_nS <= 1-t (c=0: 最大 senior 若>1-t 则既不可 SJ(伴>=t) 亦不可 SS(伴>=1-2t, 和>2-3t>1))
    if use_b3:
        r_ = list(z); r_[vs(nS)] = 1
        con(r_, 1, -1, 'B3', 'c=0 ⟹ 无独箱 ⟹ s_max 必须配 junior(<=1-t)')
    # B4: threshold-Hall (main 引理候选的链图线性形): s_{nS+1-q} + j_{q+2} <= 1, q=2a+1..nS-2
    # 合法: 若该行破(j_{q+2} > 1-s_{nS+1-q}), 则最大的 q 个 senior 的可配 junior 只剩
    # j_1..j_{q+1} 共 q+1 件, JJJ(d>=1) 取走最小 2 件后余 q-1 < q — Hall 亏缺
    # (q>2a 时 SS 对吸收不了大 senior: 其配对 senior 须 <2t 且 >=1-2t, 被 a 对名额限制)。
    if use_b4:
        a = cnt[0]
        for q in range(2 * a + 1, nS - 1):
            r_ = list(z); r_[vs(nS + 1 - q)] = 1; r_[vj(q + 2)] = 1
            con(r_, 1, 0, f'B4_q{q}', 'threshold-Hall: q 大 senior 对 q+1 候选 junior, JJJ 取 2 后亏缺')
    # S1v: SS=最小 2a 极端配对(S1 已证, 值语言合法)
    if use_s1v:
        a = cnt[0]
        for r in range(1, a + 1):
            r_ = list(z); r_[vs(r)] = 1; r_[vs(2 * a + 1 - r)] = 1
            con(r_, 1, 0, f'S1v_{r}', 'S1: SS=最小2a 极端配对(支配, 主代理已证)')
    # 消耗序规范行(G2a 集合规范=池最小 3d): JJJ 取 t+j_1..j_{3d-1}
    # JJ-REV: 其后最小 2e 反序(G2a 同支配论证)
    a, b, c, d, e, f = cnt
    base = 3 * d - 1   # JJJ 消耗的 junior 数(池=t+j_1+...)
    if use_jjrev and e > 0:
        for i in range(1, e + 1):
            r_ = list(z); r_[vj(base + i)] = 1; r_[vj(base + 2 * e + 1 - i)] = 1
            con(r_, 1, 0, f'JJrev_{i}', 'JJ-REV: JJJ 后最小 2e 反序(G2a 支配)')
    # SJ-REV: 再后最小 b 与 senior 中段反序(合法性=匹配存在性, (W'') 残余缺口, 试验行)
    if use_sjrev and b > 0:
        for i in range(1, b + 1):
            r_ = list(z); r_[vs(2 * a + i)] = 1; r_[vj(base + 2 * e + b + 1 - i)] = 1
            con(r_, 1, 0, f'SJrev_{i}', 'SJ-REV: 中段 senior×池后段反序(匹配必要性, 试验)')
    return A, bc, bt, names, leg, nv

def scan(m_lo=6, m_hi=16, **kw):
    res = {}
    for m in range(m_lo, m_hi + 1):
        for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
            A, bc, bt, names, leg, nv = build(m, cnt, **kw)
            yf = float_cert(A, bc, bt)
            key = (m, cnt)
            if yf is None:
                res[key] = ('FEAS', None)
                print(f'm={m} {cnt}: FEASIBLE(见证!)', flush=True)
                continue
            y, N = rationalize_verify(A, bc, bt, yf)
            res[key] = ('cert' if y is not None else 'ratfail', N)
            print(f'm={m} {cnt}: INFEASIBLE 证书 den<={N}', flush=True)
    return res

def ablation():
    for fam, kw in [('B4', dict(use_b4=False)), ('B1', dict(use_b1=False)), ('B2', dict(use_b2=False)),
                    ('B3', dict(use_b3=False)), ('A1', dict(use_a1=False)), ('A2', dict(use_a2=False)),
                    ('A3', dict(use_a3=False))]:
        res = scan(**kw)
        feas = sum(1 for v in res.values() if v[0] == 'FEAS')
        print(f'消融去{fam}: FEAS {feas}/22')

if __name__ == '__main__':
    res = scan()
    certs = sum(1 for v in res.values() if v[0] == 'cert')
    feas = [k for k, v in res.items() if v[0] == 'FEAS']
    print(f'\n== 值语言 LP 一测: cert {certs}/{len(res)}, FEAS {len(feas)}')
    for k in feas: print('  见证:', k)
