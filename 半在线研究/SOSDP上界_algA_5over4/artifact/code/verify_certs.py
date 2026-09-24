"""全口袋统一证书复核器：只读证书文件 + 重建约束矩阵 + 纯 Fraction 算术复核。
不调 linprog（防求解器相关假阳性）。复核 Aᵀy=0、btᵀy=0、bcᵀy=−1、y≥0。

支持文件：
  1) 统一 jsonl（builder 字段重建）：
     - build_fixed(m,cnt,k)     口袋2一步
     - build_fixed2(m,cnt,k,jj2) 口袋2二步
  2) agent-1 口袋1 txt（=== m=.. cnt=(..) [jj=..] [nofs|S12|jj2=..] (den<=..) === 头 + 名字: 权重 行），
     重建 build_p1b(m,cnt,jj,use_s2,jj2)；重名约束按出现顺序对齐。
用法: python verify_certs.py [文件 ...]（缺省复核全部已知文件）
"""
import sys, os, json, re
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))


def exact_check(A, bc, bt, y, nv):
    """纯 Fraction 复核；返回失败原因或 None。零权重行跳过。"""
    sup = [i for i in range(len(y)) if y[i] != 0]
    for j in range(nv):
        s = sum((A[i][j] * y[i] for i in sup), F(0))
        if s != 0:
            return f'A^T y 第{j}列 = {s} ≠ 0'
    s = sum((bt[i] * y[i] for i in sup), F(0))
    if s != 0:
        return f'bt^T y = {s} ≠ 0'
    s = sum((bc[i] * y[i] for i in sup), F(0))
    if s != -1:
        return f'bc^T y = {s} ≠ -1'
    if any(v < 0 for v in y):
        return 'y 有负分量'
    return None


def verify_jsonl(path):
    from farkas_fixed import build_fixed
    from second_step import build_fixed2
    npass = nfail = 0
    fails = []
    for ln, line in enumerate(open(path), 1):
        r = json.loads(line)
        b = r['builder']
        if b == 'build_fixed':
            A, bc, bt, names, nv = build_fixed(r['m'], tuple(r['cnt']), r['k'])
        elif b == 'build_fixed2':
            A, bc, bt, names, nv = build_fixed2(r['m'], tuple(r['cnt']), r['k'], jj2=r['jj2'])
        else:
            fails.append((ln, f'未知 builder {b}')); nfail += 1; continue
        y = [F(0)] * len(A)
        ok = True
        for idx, w in r['y']:
            if not (0 <= idx < len(A)):
                fails.append((ln, f'索引越界 {idx}')); ok = False; break
            y[idx] = F(w)
        if not ok:
            nfail += 1; continue
        err = exact_check(A, bc, bt, y, nv)
        if err:
            fails.append((ln, f"m={r['m']} cnt={r['cnt']} k={r.get('k')} jj2={r.get('jj2')}: {err}"))
            nfail += 1
        else:
            npass += 1
    return npass, nfail, fails


CAPNAMES = {'SS', 'SJ', 'JJJ', 'JJ'}


def _p2fast_one(arg):
    """单条复核（供多进程调用）。返回 (ok, err)。

    重名装箱行（SS/SJ/JJJ/JJ）对齐：非装箱约束名全部唯一，先行指派并累加列和 B；
    每个装箱行的列被且仅被一个装箱行覆盖 ⟹ 其权重被列平衡唯一强制（w_r=-B_j，
    要求行内各列 -B_j 相等）；最后比对强制得到的 (name,w) 多重集与文件记录。"""
    from fast_lp import rows_fixed
    ln, line = arg
    r = json.loads(line)
    if r.get('hole'):
        return False, f"洞记录混入 m={r['m']} cnt={r['cnt']} k={r['k']}"
    R, nv = rows_fixed(r['m'], tuple(r['cnt']), r['k'], use_order=True)
    names = [nm for _, _, _, nm in R]
    idx_by_name = {}
    caps = []
    for i, nm in enumerate(names):
        if nm in CAPNAMES:
            caps.append(i)
        else:
            idx_by_name[nm] = i
    y = [F(0)] * len(R)
    B = [F(0)] * nv
    cert_caps = []
    for nm, w in r['cert']:
        w = F(w)
        if nm in CAPNAMES:
            cert_caps.append((nm, w))
            continue
        i = idx_by_name.get(nm)
        if i is None:
            return False, f'约束名 {nm} 不存在'
        if y[i] != 0:
            return False, f'约束 {nm} 重复指派'
        y[i] = w
        row = R[i][0]
        for j in range(nv):
            if row[j]:
                B[j] += F(row[j]) * w
    forced_caps = []
    for ri in caps:
        row = R[ri][0]
        vals = {-B[j] for j in range(nv) if row[j]}
        if len(vals) != 1:
            return False, (f'装箱行 {names[ri]} 各列残差不等 {sorted(str(v) for v in vals)}'
                           f' ⟹ 该证书无解（非装箱权重与文件不符）')
        w = vals.pop()
        if w < 0:
            return False, f'装箱行 {names[ri]} 强制权重为负 {w}'
        y[ri] = w
        if w:
            forced_caps.append((names[ri], w))
    if sorted(forced_caps) != sorted(cert_caps):
        return False, (f'装箱多重集不符: 记录 {sorted((n, str(w)) for n, w in cert_caps)}'
                       f' vs 列平衡强制 {sorted((n, str(w)) for n, w in forced_caps)}')
    Af = [[F(x) for x in row] for row, _, _, _ in R]
    bcf = [c0 for _, c0, _, _ in R]
    btf = [c1 for _, _, c1, _ in R]
    err = exact_check(Af, bcf, btf, y, nv)
    if err:
        return False, f"m={r['m']} cnt={r['cnt']} k={r['k']}: {err}"
    return True, None


def verify_p2fast(path, workers=2):
    """fast_scan 格式 {'m','cnt','k','cert':[(name,weight)]}，用 fast_lp.rows_fixed 重建。
    row 系数二进制精确（F(float) 无损），bc/bt 已是精确 Fraction。多进程纯 Fraction 复核。
    断点续跑：sidecar <path>.vprog 记录 done/pass/fail，失败详情追加 <path>.vfails。
    8min 硬顶分片：环境变量 A4_VERIFY_SLICE=N 时每片最多新验 N 条即自退（exit 0）。"""
    import concurrent.futures as cf
    import multiprocessing as mp
    slice_max = int(os.environ.get('A4_VERIFY_SLICE', '0')) or None
    sidecar = path + '.vprog'
    npass = nfail = ndone = 0
    if os.path.exists(sidecar):
        with open(sidecar) as f:
            st = json.load(f)
        npass, nfail, ndone = st['pass'], st['fail'], st['done']
    lines = list(enumerate(open(path), 1))
    if ndone >= len(lines):
        return npass, nfail, []
    todo = lines[ndone:]
    ctx = mp.get_context('spawn')
    t0 = __import__('time').time()
    batch = 0
    with cf.ProcessPoolExecutor(max_workers=workers, mp_context=ctx) as ex:
        strm = ex.map(_p2fast_one, todo, chunksize=64)
        for (ln, _), (ok, err) in zip(todo, strm):
            if ok:
                npass += 1
            else:
                nfail += 1
                with open(path + '.vfails', 'a') as fe:
                    fe.write(f'行{ln}: {err}\n')
            ndone += 1
            batch += 1
            if batch % 5000 == 0 or (slice_max and batch >= slice_max):
                with open(sidecar, 'w') as f:
                    json.dump({'done': ndone, 'pass': npass, 'fail': nfail}, f)
                print(f'  ... {ndone}/{len(lines)} pass={npass} fail={nfail} '
                      f'({__import__("time").time()-t0:.0f}s)', flush=True)
            if slice_max and batch >= slice_max:
                print(f'  分片自退：本片 {batch} 条，断点 {ndone}/{len(lines)}', flush=True)
                ex.shutdown(wait=False, cancel_futures=True)
                return npass, nfail, []
    with open(sidecar, 'w') as f:
        json.dump({'done': ndone, 'pass': npass, 'fail': nfail}, f)
    fails = []
    if nfail and os.path.exists(path + '.vfails'):
        fails = [(0, l.rstrip('\n')) for l in list(open(path + '.vfails'))[-8:]]
    return npass, nfail, fails


HDR = re.compile(r'^=== m=(\d+) cnt=\(([^)]*)\)\s+(.*?)\s*\(den<=(\d+)\) ===$')


def parse_p1_header(tag):
    """返回 (jj, use_s2, jj2, h)。h≠None ⟹ use_order=True（保序引理枚举记录）。"""
    toks = tag.split()
    hs = [t for t in toks if t.startswith('h=')]
    h = int(hs[0][2:]) if hs else None
    if 'nofs' in toks:
        return None, False, None, h
    jj = int([t for t in toks if t.startswith('jj=')][0][3:])
    jj2s = [t for t in toks if t.startswith('jj2=')]
    if jj2s:
        return jj, True, int(jj2s[0][4:]), h
    if 'S12' in toks or h is not None:
        return jj, True, None, h
    return jj, False, None, h


def verify_p1_txt(path):
    from pocket1_bins import build_p1b
    npass = nfail = 0
    fails = []
    cur = None
    entries = []

    def flush():
        nonlocal npass, nfail
        if cur is None:
            return
        m, cnt, jj, s2, jj2, h, hdrline = cur
        try:
            A, bc, bt, names, nv = build_p1b(m, cnt, jj=jj, use_s2=s2, jj2=jj2,
                                             use_order=(h is not None), h=h)
        except Exception as e:
            fails.append((hdrline, f'重建异常 {e}')); nfail += 1; return
        y = [F(0)] * len(A)
        ptr = 0
        ok = True
        for nm, w, wline in entries:
            while ptr < len(A) and names[ptr] != nm:
                ptr += 1
            if ptr >= len(A):
                fails.append((wline, f'约束名 {nm} 无剩余匹配')); ok = False; break
            y[ptr] = F(w)
            ptr += 1
        if ok:
            err = exact_check(A, bc, bt, y, nv)
            if err:
                fails.append((hdrline, f'm={m} cnt={cnt} jj={jj} s2={s2} jj2={jj2}: {err}'))
                ok = False
        if ok:
            npass += 1
        else:
            nfail += 1

    for ln, line in enumerate(open(path), 1):
        line = line.rstrip('\n')
        h = HDR.match(line)
        if h:
            flush()
            m = int(h.group(1))
            cnt = tuple(int(x) for x in h.group(2).split(','))
            jj, s2, jj2, hh = parse_p1_header(h.group(3))
            cur = (m, cnt, jj, s2, jj2, hh, ln)
            entries = []
        elif line.strip():
            nm, w = line.strip().rsplit(': ', 1)
            entries.append((nm.strip(), w, ln))
    flush()
    return npass, nfail, fails


DEFAULTS = [
    ('jsonl', 'pocket2_certificates.jsonl'),
    ('jsonl', 'p2_s2_certificates.jsonl'),
    ('p1txt', 'pocket1b_certificates.txt'),
    ('p1txt', 'pocket1b_certificates_s2.txt'),
    ('p1txt', 'pocket1b_certificates_13_20.txt'),
    ('p2fast', 'pocket2_onestep_order_certs.txt'),
    ('p2fast', 'pocket2_onestep_order_certs_31_45.txt'),
]

if __name__ == '__main__':
    args = sys.argv[1:]
    targets = []
    if args:
        for a in args:
            if 'onestep_order' in os.path.basename(a):
                kind = 'p2fast'
            elif a.endswith('.txt'):
                kind = 'p1txt'
            else:
                kind = 'jsonl'
            targets.append((kind, a))
    else:
        targets = [(k, os.path.join(HERE, f)) for k, f in DEFAULTS]
    total_p = total_f = 0
    for kind, path in targets:
        if not os.path.exists(path):
            print(f'{os.path.basename(path):38s}: 不存在，跳过')
            continue
        if kind == 'jsonl':
            np_, nf, fails = verify_jsonl(path)
        elif kind == 'p2fast':
            np_, nf, fails = verify_p2fast(path)
        else:
            np_, nf, fails = verify_p1_txt(path)
        total_p += np_; total_f += nf
        print(f'{os.path.basename(path):38s}: PASS {np_}, FAIL {nf}')
        for ln, msg in fails[:8]:
            print(f'    行{ln}: {msg}')
    print(f'{"总计":38s}: PASS {total_p}, FAIL {total_f}')
