"""口袋2角落（2件形态）统一手验证书族：全 m>=4、全 cnt、全 t 窗口。

族 k=1（纯计数，无需 LP）：
  守恒式相减得 d = 1+c+f >= 1（JJJ箱必存在）、a >= 1（SS箱必存在）。
  k=1 时 fs+jq+q1<=j0 链 => 全部 junior 相等 J；SS箱 2(p-J)<1 => J > 3/4-t；
  JJJ箱任取3件必含>=2个J（池中只有一个t）：(J,J,J)=>J<=1/3=>t>5/12矛盾；
  (J,J,t)=>2J+t<=1=>t>1/2矛盾。=> k=1 角落全 m 全 cnt 全窗口闭合。

族 k=2 / k>=3（显式 Farkas 常数证书，权重与 m,cnt,t 无关）：
  k=2:  j0>=t, danger, j0<=q1, q1<=am, p<K  各 120000/10031（q1<=am 为 200000/10031）
        nofit0=10000/1433, srt0=20000/1433, SS首箱=20000/1433
  k>=3: 同上但 nofit0=nofit1=5000/1433（无 srt0）
验证：m=4..30 全 cnt 全 k 精确验证 A^T y=0, bt^T y=0, bc^T y=-1, y>=0；配消融。
"""
from fractions import Fraction as F
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_constant import build_frac, float_cert
from pairing_feasible import bin_count_solutions

W = F(120000, 10031)
WQ = F(200000, 10031)
WN2 = F(10000, 1433)   # k=2 nofit0
WN = F(5000, 1433)     # k>=3 nofit_i
WS = F(20000, 1433)    # srt0 / SS


def build_uniform(m, cnt, k):
    """构造统一证书 y（Fraction 列表）。k=1 返回 'COUNTING'。"""
    if k == 1:
        return 'COUNTING'
    A, bc, bt, names, nv = build_frac(m, cnt, k)
    y = [F(0)] * len(A)

    def setw(nm, w, occ=0):
        idxs = [i for i, n in enumerate(names) if n == nm]
        assert len(idxs) > occ, f'{nm} 第{occ}个不存在 (m={m},cnt={cnt},k={k})'
        y[idxs[occ]] = w

    setw('j0>=t', W)
    setw('danger', W)
    setw('j0<=q1', W)
    setw('q1<=am', WQ)
    setw('p<K', W)
    setw('SS', WS, occ=0)          # SS 首箱 s0+s1<=1（a>=1 恒成立）
    if k == 2:
        setw('nofit0', WN2)
        setw('srt0', WS)
    else:  # k>=3
        setw('nofit0', WN)
        setw('nofit1', WN)
    return A, bc, bt, names, nv, y


def exact_check(A, bc, bt, y, nv):
    ok = all(sum(A[i][j] * y[i] for i in range(len(y))) == 0 for j in range(nv))
    ok = ok and sum(bt[i] * y[i] for i in range(len(y))) == 0
    ok = ok and sum(bc[i] * y[i] for i in range(len(y))) == -1
    ok = ok and all(v >= 0 for v in y)
    return ok


def verify_cnt_identities(m, cnt):
    """k=1 计数引理：d == 1+c+f（>=1）、a == 1+c+e+2f（>=1）对所有合法 cnt 成立。"""
    a, b, c, d, e, f = cnt
    assert 2 * a + b + c == m - 1 and b + 3 * d + 2 * e + f == m
    return d == 1 + c + f >= 1 and a == 1 + c + e + 2 * f >= 1


if __name__ == '__main__':
    # 1) k=1 计数恒等式：全 m 全 cnt
    print('k=1 计数恒等式 d=1+c+f>=1, a=1+c+e+2f>=1：', end=' ')
    bad = 0
    for m in range(4, 31):
        for cnt in bin_count_solutions(m):
            if not verify_cnt_identities(m, cnt):
                bad += 1
                print(f'\n  反例 m={m} cnt={cnt}', end='')
    print('全部成立 ✓' if bad == 0 else f'{bad} 个反例')

    # 2) k>=2 统一证书：m=4..30 全 cnt 全 k 精确验证
    print('k>=2 统一 Farkas 证书精确验证（m=4..30 全 cnt 全 k）:')
    bad = []
    for m in range(4, 31):
        for cnt in bin_count_solutions(m):
            for k in range(2, m):
                A, bc, bt, names, nv, y = build_uniform(m, cnt, k)
                if not exact_check(A, bc, bt, y, nv):
                    bad.append((m, cnt, k))
    print('  ', '全部通过 ✓' if not bad else f'{len(bad)} 处失败: {bad[:5]}')

    # 3) 消融：去掉证书用到的每一类约束，LP 应变 feasible（约束皆必要）
    print('消融（m=6, cnt=(1,3,0,1,0,0)）：')
    A, bc, bt, names, nv, y = build_uniform(6, (1, 3, 0, 1, 0, 0), 3)
    for kill in ['j0>=t', 'danger', 'j0<=q1', 'q1<=am', 'p<K', 'SS', 'nofit0', 'nofit1']:
        idx = [i for i, n in enumerate(names) if n != kill]
        A2 = [A[i] for i in idx]; bc2 = [bc[i] for i in idx]; bt2 = [bt[i] for i in idx]
        yf = float_cert(A2, bc2, bt2)
        print(f'   去 {kill:8s}: {"feasible（必要 ✓）" if yf is None else "仍有证书（非必要!）"}')
