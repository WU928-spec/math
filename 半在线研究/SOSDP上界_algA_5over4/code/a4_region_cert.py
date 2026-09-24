"""区域证书管线（fallback 预备，agent-4）：胞腔极小形箱内容驱动的角落 LP。

背景（JEL.md §③）：若 region-portability 猜想失败（模板权重不可搬运），需逐区域重解证书。
本管线 = fast_lp.rows_fixed 去掉默认装箱行 + 按输入的极小形箱内容加容量行。

输入箱形格式（物品用变量索引描述；junior 槽位 0..nS-1 为 j_i，nS 为 t）：
  bins = {"SS":  [(u,v), ...],   每对 senior 索引（s_u+s_v<=1）
          "SJ":  [(i,p), ...],   senior i + junior 槽位 p（s_i+J_p<=1）
          "JJJ": [(p,q,r), ...], 三个 junior 槽位
          "JJ":  [(p,q), ...]}
校验：组数须等于 cnt=(a,b,c,d,e,f) 的 (a,b,d,e)；SS 与 SJ 的 senior 索引互不相交；
所有 junior 槽位在全箱形中至多出现一次（每件 junior 至多入一个容量行）；
c（独箱 senior）与 f（独箱 junior）不产生容量行（与 rows_fixed 一致）。

装箱行名编号唯一化（SS#0/SJ#3/...）——规避重名行按名指派陷阱（opt_db P02）。

冒烟：python a4_region_cert.py smoke
CLI：  python a4_region_cert.py cert '<bins_json>' m cnt k   → 打印证书/可行
"""
import sys, os, json
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fast_lp import rows_fixed, float_cert_rows, exact_verify_support

CAPNAMES = {'SS', 'SJ', 'JJJ', 'JJ'}


def nS_of(m):
    return m - 1


def validate_bins(m, cnt, bins):
    """返回规范化 bins 或抛 ValueError。"""
    a, b, c, d, e, f = cnt
    nS = nS_of(m)
    SS = [tuple(x) for x in bins.get('SS', [])]
    SJ = [tuple(x) for x in bins.get('SJ', [])]
    JJJ = [tuple(x) for x in bins.get('JJJ', [])]
    JJ = [tuple(x) for x in bins.get('JJ', [])]
    if (len(SS), len(SJ), len(JJJ), len(JJ)) != (a, b, d, e):
        raise ValueError(f'组数不符 cnt={cnt}: 得到 SS{len(SS)} SJ{len(SJ)} JJJ{len(JJJ)} JJ{len(JJ)}')
    ss_sen = [i for p in SS for i in p]
    sj_sen = [i for i, _ in SJ]
    if len(set(ss_sen)) != len(ss_sen) or len(set(sj_sen)) != len(sj_sen):
        raise ValueError('senior 索引在 SS/SJ 内重复')
    if set(ss_sen) & set(sj_sen):
        raise ValueError('senior 索引跨 SS/SJ 相交')
    for i in ss_sen + sj_sen:
        if not (0 <= i < nS):
            raise ValueError(f'senior 索引越界 {i}（nS={nS}）')
    slots = [p for _, p in SJ] + [p for t_ in JJJ for p in t_] + [p for p_ in JJ for p in p_]
    if len(set(slots)) != len(slots):
        raise ValueError('junior 槽位重复入箱')
    for p in slots:
        if not (0 <= p <= nS):
            raise ValueError(f'junior 槽位越界 {p}（0..{nS}，{nS}=t）')
    return {'SS': SS, 'SJ': SJ, 'JJJ': JJJ, 'JJ': JJ}


def canonical_bins(m, cnt):
    """rows_fixed 的默认规范形转为本管线输入格式（用于冒烟对照）。"""
    a, b, c, d, e, f = cnt
    nS = nS_of(m)
    SS = [(2 * kk, 2 * kk + 1) for kk in range(a)]
    SJ = [(2 * a + kk, kk) for kk in range(b)]
    jidx = b
    JJJ = []
    for kk in range(d):
        JJJ.append((jidx, jidx + 1, jidx + 2)); jidx += 3
    JJ = []
    for kk in range(e):
        JJ.append((jidx, jidx + 1)); jidx += 2
    return {'SS': SS, 'SJ': SJ, 'JJJ': JJJ, 'JJ': JJ}


def build_region_rows(m, cnt, k, bins, use_order=True):
    """rows_fixed 去默认装箱行 + 输入极小形的容量行。返回 (R, nv)。"""
    bins = validate_bins(m, cnt, bins)
    R, nv = rows_fixed(m, cnt, k, use_order=use_order)
    R = [r for r in R if r[3] not in CAPNAMES]
    nS = nS_of(m)

    def vs(i): return 2 + i
    def vj(i): return 2 + nS + i

    def jslot(p): return vj(p) if p < nS else 1  # it=1

    def cap(idxs, nm):
        row = [0.0] * nv
        for ix in idxs:
            row[ix] = 1.0
        R.append((row, F(1), F(0), nm))

    for n, (u, v) in enumerate(bins['SS']):
        cap([vs(u), vs(v)], f'SS#{n}')
    for n, (i, p) in enumerate(bins['SJ']):
        cap([vs(i), jslot(p)], f'SJ#{n}')
    for n, (p, q, r_) in enumerate(bins['JJJ']):
        cap([jslot(p), jslot(q), jslot(r_)], f'JJJ#{n}')
    for n, (p, q) in enumerate(bins['JJ']):
        cap([jslot(p), jslot(q)], f'JJ#{n}')
    return R, nv


def region_cert(m, cnt, k, bins, use_order=True):
    """求解+精确验证。返回 ('cert', cert列表) / ('feasible', None) / ('ratfail', None)。"""
    R, nv = build_region_rows(m, cnt, k, bins, use_order=use_order)
    yf = float_cert_rows(R, nv)
    if yf is None:
        return 'feasible', None
    y, sup = exact_verify_support(R, nv, yf)
    if y is None:
        return 'ratfail', None
    return 'cert', [(R[i][3], str(w)) for i, w in zip(sup, y)]


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'smoke'
    if cmd == 'smoke':
        m, cnt, k = 12, (2, 7, 0, 1, 1, 0), 11
        print(f'== 冒烟1：规范形输入 m={m} cnt={cnt} k={k}（已知闭合）==')
        st, cert = region_cert(m, cnt, k, canonical_bins(m, cnt))
        print(f'  规范形: {st}' + (f'（{len(cert)} 项）' if cert else ''))
        assert st == 'cert', '规范形未出证书——管线有 bug!'
        # 对照：与 rows_fixed 默认装箱同源 —— 规范形应等价于主管线闭合结论
        print('== 冒烟2：合法非规范形（有牙检查）==')
        # 变体A：SS 改交叉配对 (0,3),(1,2)；SJ 的 junior 槽位 0/1 对调
        alt = canonical_bins(m, cnt)
        alt['SS'] = [(0, 3), (1, 2)]
        alt['SJ'] = [(4, 1), (5, 0)] + alt['SJ'][2:]
        st2, cert2 = region_cert(m, cnt, k, alt)
        print(f'  变体A（SS交叉配对+SJ槽对调）: {st2}' + (f'（{len(cert2)} 项）' if cert2 else ''))
        # 变体B：JJJ 换成含 t 槽（11=t）与原 JJ 的 junior 互换位置
        altB = canonical_bins(m, cnt)
        altB['JJJ'] = [(8, 9, 11)]   # 11 = t 槽
        altB['JJ'] = [(7, 10)]
        st3, cert3 = region_cert(m, cnt, k, altB)
        print(f'  变体B（JJJ含t，JJ重排）: {st3}' + (f'（{len(cert3)} 项）' if cert3 else ''))
        # 非法输入必须被拒
        print('== 冒烟3：非法输入拒绝 ==')
        for bad, tag in [({'SS': [(0, 1)]}, '组数不足'),
                         ({'SS': [(0, 1), (1, 2)], 'SJ': [(3, p) for p in range(7)],
                           'JJJ': [(7, 8, 9)], 'JJ': [(10, 11)]}, 'senior重复'),
                         ({'SS': [(0, 1), (2, 3)], 'SJ': [(i + 4, i) for i in range(7)],
                           'JJJ': [(7, 8, 9)], 'JJ': [(7, 11)]}, 'junior槽位重复')]:
            try:
                region_cert(m, cnt, k, bad)
                print(f'  {tag}: 未拒绝!!（bug）')
            except ValueError as ex:
                print(f'  {tag}: 拒绝 ✓ ({ex})')
        print('冒烟完成')
    elif cmd == 'cert':
        bins = json.loads(sys.argv[2])
        m = int(sys.argv[3])
        cnt = tuple(json.loads(sys.argv[4]))
        k = int(sys.argv[5])
        st, cert = region_cert(m, cnt, k, bins)
        print(json.dumps({'m': m, 'cnt': list(cnt), 'k': k, 'status': st,
                          'cert': cert}, ensure_ascii=False))
