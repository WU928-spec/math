"""方向2：razor 带 ∀m 符号证书——只用已证合法行（agent-4）。

在 a4_enec3.build_v3（mon2 + XSS/XVOL/XBIG + 挤压 XSQZ + 值带 XVB，无固定身份装箱行）上，
加入主代理今日合法化的计数恒等式必要行（BOARD 恒等式修正条）：
  XPAIR: s₀+s₁≤1（a≥1 时；计数恒等式 a=d+e+f≥1 ⟹ SS 箱必存在 ⟹ 支配 ⟹ 最小两件配对≤1）
  ——注意 v2a 的 XSS0 当 a=1 与此重合（已含）；a=2 时 XSS 极端配对更强，保留。
  XTRI: 最小三元组和≤1（d≥1 ⟹ JJJ 箱必存在 ⟹ 支配 ⟹ 池中最小 3 件和≤1）。
    **索引合法性护栏**：池最小件=t（jᵢ≥t 全域）；两件最小 junior 的机器序索引依赖
    mon2 低端序覆盖——本行写成 t+j₀+j₁≤1，仅当 hi 区 junior ≥ j₁ 时合法；
    razor 带该条件未证 ⟹ XTRI 标记 SUSPECT-索引，单独消融（若闭合依赖它，需离散度引理
    或 hi 区 junior 下界补证）。另测保守合法变体 XTRI-t：三最小件的纯体积替代=挤压行已含。
  XJJ: 最小 junior 对 j₀+j₁≤1（e≥1 ⟹ JJ 箱存在 ⟹ 最小两件≤1；同索引护栏，SUSPECT）。

判决：razor 带（m=4..14 全 cnt 全 k 的 v3 残留 + 洞族 m=12..20）在 +XTRI(+XJJ) 下是否全闭。
闭合则提取代表证书支撑→归纳 ∀m 符号恒等式（望远镜结构，模板=引理2）。

用法：python a4_razor_symbolic.py scan | extract
"""
import sys, os, json, time
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a4_enec3 import build_v3
from a4_enec2 import is_inf, build_v2a
from farkas_fixed import float_cert
from pairing_feasible import bin_count_solutions

HERE = os.path.dirname(os.path.abspath(__file__))


def build_v4(m, cnt, k, use_tri=True, use_jj=True, **kw):
    """build_v3 + XTRI（t+j₀+j₁≤1）+ XJJ（j₀+j₁≤1）。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    A, bc, bt, names, nv = build_v3(m, cnt, k, **kw)

    def vj(i): return 2 + nS + i
    it = 1

    def zero(): return [F(0)] * nv
    if use_tri and d >= 1 and nS >= 2:
        r = zero(); r[it] = 1; r[vj(0)] = 1; r[vj(1)] = 1
        A.append(r); bc.append(F(1)); bt.append(F(0)); names.append('XTRI')
    if use_jj and e >= 1 and nS >= 2:
        r = zero(); r[vj(0)] = 1; r[vj(1)] = 1
        A.append(r); bc.append(F(1)); bt.append(F(0)); names.append('XJJ')
    return A, bc, bt, names, nv


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'scan'
    t0 = time.time()

    if cmd == 'scan':
        # 阶梯：v3 → +XTRI → +XTRI+XJJ；razor 带判决 m=4..14 全量
        print('== 阶梯判决（m=4..14 全 cnt 全 k 保持率）==', flush=True)
        for tag, kw in [('v3（对照）', dict(use_tri=False, use_jj=False)),
                        ('v3+XTRI', dict(use_jj=False)),
                        ('v3+XTRI+XJJ', dict())]:
            n_tot = n_keep = 0
            loss = []
            for m in range(4, 15):
                for k in range(1, m):
                    for cnt in bin_count_solutions(m):
                        n_tot += 1
                        if is_inf(*build_v4(m, cnt, k, **kw)[:3]):
                            n_keep += 1
                        else:
                            loss.append((m, cnt, k))
            print(f'  {tag}: {n_keep}/{n_tot} = {n_keep/n_tot:.4f}  损失 {len(loss)}'
                  + (f'  样例 {loss[:6]}' if loss else ''), flush=True)

        print('== 洞族 20 处 ==', flush=True)
        holes = [json.loads(l) for l in open(os.path.join(HERE, 'p2_holes_big.jsonl'))
                 if json.loads(l)['m'] <= 20]
        for tag, kw in [('v3+XTRI', dict(use_jj=False)), ('v3+XTRI+XJJ', dict())]:
            n_surv = 0
            for h in holes:
                if not is_inf(*build_v4(h['m'], tuple(h['cnt']), h['k'], **kw)[:3]):
                    n_surv += 1
            print(f'  {tag}: 存活 {n_surv}/20  ({time.time()-t0:.0f}s)', flush=True)

    elif cmd == 'extract':
        # 闭合代表的证书支撑结构（找符号恒等式原料）
        from farkas_fixed import rationalize_verify
        for m, cnt, k in [(8, (1, 5, 0, 1, 0, 0), 2), (10, (1, 7, 0, 1, 0, 0), 2),
                          (12, (1, 9, 0, 1, 0, 0), 2), (10, (2, 5, 0, 1, 1, 0), 4),
                          (12, (2, 7, 0, 1, 1, 0), 11)]:
            A, bc, bt, names, nv = build_v4(m, cnt, k)
            yf = float_cert(A, bc, bt)
            if yf is None:
                print(f'm={m} cnt={cnt} k={k}: FEASIBLE')
                continue
            y, N = rationalize_verify(A, bc, bt, yf)
            if y is None:
                print(f'm={m} cnt={cnt} k={k}: RATFAIL')
                continue
            sup = [(names[i], str(y[i])) for i in range(len(y)) if y[i] != 0]
            print(f'm={m} cnt={cnt} k={k}: 支撑 {len(sup)} 行:')
            print('   ', ' '.join(f'{n}:{w}' for n, w in sup))
