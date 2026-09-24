"""E-nec：必要条件行的 LP 强度裁决（agent-4）。

变体 = fast_lp.rows_fixed 去掉全部嫌疑固定分组行（SS/SJ/JJJ/JJ caps），换成合法必要条件行族
（packable ⟹ 自动满足，支配论证免费合法，见 JEL.md 架构澄清节）：

  ①XSS i（i<a，需 srt senior 全序）：极端配对 s_i + s_{2a-1-i} <= 1。
     合法性：存在 a 对互不相交 senior 对和≤1 ⟹ 最小 2a 个的极端配对逐对≤1（重排/交换论证）。
  ⑤V XVOL（机器对称，无需 junior 序）：Σ_p j_p + t + Σ_{i<b} s_i <= b+d+e+f。
     合法性：池（全部 junior+t）恰好装入 SJ(b)/JJJ(d)/JJ(e)/J(f) 共 b+d+e+f 个箱，
     每箱≤1 ⟹ 池和 ≤ b+d+e+f −（SJ 箱内 senior 和）；SJ 箱 senior 是某 b 个 senior，
     其和 ≥ 最小 b 个 senior 和（srt 给序，Σ_{i<b}s_i 合法）。
  ⑤B XBIG（srt 合法）：s_{nS-1-(c+a+b)} <= 1/2（索引出界则跳过=vacuous）。
     合法性：>1/2 的 senior 每个独占一箱（c 独箱 + a SS 每箱至多1大 + b SJ 每箱至多1大）
     ⟹ #大senior ≤ c+a+b ⟺ 第 c+a+b+1 大 senior ≤1/2。

设计风险记录（brief 要求）：junior 全局值序无 w.l.o.g. 依据（hi 区 junior 与低端 junior 无已知序），
故②最小3d聚合/③最小2e反序对/④Hall 的本版一律不用值序行，改用 ⑤V/⑤B 机器对称行替代；
值序强化版留待序结构引理（反馈见 a4_enec.md）。

用法：
  python a4_enec.py ghost    # razor/鬼影洞族在新行下的命运（无保序基底，隔离计数行杀伤力）
  python a4_enec.py retain [m_hi]   # m=4..m_hi 全 cnt 全 k 保持率（含保序基底）
  python a4_enec.py ablate   # 闭合代表逐族去行消融（定位承重行）
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fast_lp import rows_fixed, float_cert_rows
from pairing_feasible import bin_count_solutions
from fractions import Fraction as F

CAPNAMES = {'SS', 'SJ', 'JJJ', 'JJ'}


def build_enec(m, cnt, k, use_order=True, use_xss=True, use_xvol=True, use_xbig=True):
    """rows_fixed 去 caps + 必要条件行族。返回 (R, nv)。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    R, nv = rows_fixed(m, cnt, k, use_order=use_order)
    R = [r for r in R if r[3] not in CAPNAMES]

    def vs(i): return 2 + i
    def vj(i): return 2 + nS + i
    it = 1

    def zero(): return [0.0] * nv
    if use_xss:
        for i in range(a):
            r = zero(); r[vs(i)] = 1; r[vs(2 * a - 1 - i)] = 1
            R.append((r, F(1), F(0), f'XSS{i}'))
    if use_xvol:
        r = zero()
        for p in range(nS):
            r[vj(p)] = 1
        r[it] = 1
        for i in range(b):
            r[vs(i)] = 1
        R.append((r, F(b + d + e + f), F(0), 'XVOL'))
    if use_xbig:
        idx = nS - 1 - (c + a + b)
        if 0 <= idx < nS:
            r = zero(); r[vs(idx)] = 1
            R.append((r, F(1, 2), F(0), 'XBIG'))
    return R, nv


def is_inf(R, nv):
    return float_cert_rows(R, nv) is not None


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'ghost'
    t0 = time.time()

    if cmd == 'ghost':
        # 洞族命运：基底 use_order=False（隔离 ord 杀伤力，纯看必要条件行）
        holes = [json.loads(l) for l in open(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'p2_holes_big.jsonl'))]
        holes = [h for h in holes if h['m'] <= 20]
        print(f'洞族命运测试（{len(holes)} 个 m=12..20 一步洞，基底=无保序无caps）：')
        n_kill = 0
        for h in holes:
            m, cnt, k = h['m'], tuple(h['cnt']), h['k']
            base = build_enec(m, cnt, k, use_order=False,
                              use_xss=False, use_xvol=False, use_xbig=False)
            assert not is_inf(*base), f'基准不 feas?! m={m} cnt={cnt} k={k}'
            full = build_enec(m, cnt, k, use_order=False)
            if is_inf(*full):
                n_kill += 1
                # 定位哪族咬的
                who = []
                for fam, kw in [('XSS', dict(use_xvol=False, use_xbig=False)),
                                ('XVOL', dict(use_xss=False, use_xbig=False)),
                                ('XBIG', dict(use_xss=False, use_xvol=False))]:
                    if is_inf(*build_enec(m, cnt, k, use_order=False, **kw)):
                        who.append(fam)
                print(f'  *** 杀死 m={m} cnt={cnt} k={k}  凶手={who}')
        print(f'结果: {n_kill}/{len(holes)} 个洞点被必要条件行单独杀死（无保序）  ({time.time()-t0:.0f}s)')

    elif cmd == 'retain':
        m_hi = int(sys.argv[2]) if len(sys.argv) > 2 else 14
        print(f'保持率裁决 m=4..{m_hi} 全 cnt 全 k（基底含保序；基线=rows_fixed(use_order=True) 已知全闭）:')
        n_tot = n_keep = 0
        losses = []
        for m in range(4, m_hi + 1):
            cnts = bin_count_solutions(m)
            for k in range(1, m):
                for cnt in cnts:
                    n_tot += 1
                    R, nv = build_enec(m, cnt, k, use_order=True)
                    if is_inf(R, nv):
                        n_keep += 1
                    else:
                        losses.append((m, cnt, k))
            print(f'  m={m}: 累计 {n_keep}/{n_tot} 保持 ({time.time()-t0:.0f}s)', flush=True)
        print(f'保持率: {n_keep}/{n_tot} = {n_keep/n_tot:.4f}')
        print(f'强度损失 {len(losses)} 处:', losses[:15])

    elif cmd == 'ablate':
        for m, cnt, k in [(8, (1, 5, 0, 1, 0, 0), 7), (12, (2, 7, 0, 1, 1, 0), 11), (10, (1, 7, 0, 1, 0, 0), 9)]:
            R, nv = build_enec(m, cnt, k, use_order=True)
            full = is_inf(R, nv)
            print(f'消融 m={m} cnt={cnt} k={k} 基准（含保序+新行）: {"INF" if full else "FEAS"}')
            for fam, kw in [('去XSS', dict(use_xss=False)), ('去XVOL', dict(use_xvol=False)),
                            ('去XBIG', dict(use_xbig=False)),
                            ('去保序', dict(use_order=False)),
                            ('去保序+留新行', dict(use_order=False))]:
                R2, nv2 = build_enec(m, cnt, k, **kw)
                print(f'   {fam:12s}: {"仍 INF" if is_inf(R2, nv2) else "FEASIBLE（承重/回弹）"}')
