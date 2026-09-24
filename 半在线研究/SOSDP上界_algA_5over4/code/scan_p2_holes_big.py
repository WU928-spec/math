"""口袋2洞图大 m 扫描：build_fixed 的 float_cert 扫全 cnt 全 k，记录所有洞 (m,k,cnt)。

加速：monkeypatch farkas_fixed.F 为 float 运算（同进程内生效，不改文件）；
自检：patch 前后对 ~80 个随机 (m,cnt,k) 比较 float 矩阵完全一致，否则中止。
断点续跑：每 (m,k) 完成写一行 progress jsonl；洞写 holes jsonl（含可行点复核标记）。
用法: python scan_p2_holes_big.py SHARD_ID M1 [M2 ...]
"""
import sys, os, json, time, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import farkas_fixed as ff
from pairing_feasible import bin_count_solutions

HERE = os.path.dirname(os.path.abspath(__file__))


def reference_samples():
    """patch 前取参考 float 矩阵。"""
    rng = random.Random(20260921)
    refs = []
    for m in [12, 15, 20, 25, 30]:
        cnts = bin_count_solutions(m)
        pick = [cnts[0], cnts[-1]] + rng.sample(cnts, min(3, len(cnts)))
        for cnt in pick:
            for k in {1, m // 2, m - 1, max(1, m - 3)}:
                A, bc, bt, names, nv = ff.build_fixed(m, cnt, k)
                Af = np.array([[float(x) for x in row] for row in A])
                refs.append((m, cnt, k, Af,
                             np.array([float(x) for x in bc]),
                             np.array([float(x) for x in bt]), list(names)))
    return refs


def patch_float():
    ff.F = lambda a=0, b=1: a / b
    ff.MG = ff.F(1, 10000)


def selfcheck(refs):
    bad = 0
    for m, cnt, k, Af0, bc0, bt0, names0 in refs:
        A, bc, bt, names, nv = ff.build_fixed(m, cnt, k)
        Af = np.array(A, dtype=float)
        if not (np.allclose(Af, Af0) and np.allclose(bc, bc0) and np.allclose(bt, bt0)
                and list(names) == names0):
            bad += 1
            print(f'  自检不符 m={m} cnt={cnt} k={k}', flush=True)
    return bad == 0


def primal_point(m, cnt, k):
    """洞的可行点复核：合并 bt 到 t 列求原 LP 可行点。"""
    from scipy.optimize import linprog
    A, bc, bt, names, nv = ff.build_fixed(m, cnt, k)
    Af = np.array(A, dtype=float)
    bcf = np.array(bc, dtype=float)
    btf = np.array(bt, dtype=float)
    A2 = Af.copy(); A2[:, 1] -= btf
    res = linprog(c=np.zeros(nv), A_ub=A2, b_ub=bcf, bounds=(None, None), method='highs')
    return res.x if res.status == 0 else None


if __name__ == '__main__':
    shard = sys.argv[1]
    ms = [int(x) for x in sys.argv[2:]]
    PROG = os.path.join(HERE, f'p2_prog_{shard}.jsonl')
    HOLES = os.path.join(HERE, f'p2_holes_{shard}.jsonl')

    print('取 patch 前参考样本...', flush=True)
    refs = reference_samples()
    patch_float()
    if not selfcheck(refs):
        print('自检失败，中止！', flush=True)
        sys.exit(1)
    print(f'自检通过（{len(refs)} 组矩阵一致）。shard={shard} m={ms}', flush=True)

    done = set()
    if os.path.exists(PROG):
        with open(PROG) as f:
            for line in f:
                try:
                    done.add((json.loads(line)['m'], json.loads(line)['k']))
                except Exception:
                    pass
    print(f'已完成 {len(done)} 个 (m,k)，续跑。', flush=True)

    t0 = time.time()
    n_holes = 0
    for m in ms:
        cnts = bin_count_solutions(m)
        tm = time.time()
        for k in range(1, m):
            if (m, k) in done:
                continue
            holes = []
            for cnt in cnts:
                A, bc, bt, names, nv = ff.build_fixed(m, cnt, k)
                if ff.float_cert(A, bc, bt) is None:
                    holes.append(cnt)
            rec = {'m': m, 'k': k, 'n_holes': len(holes)}
            with open(PROG, 'a') as f:
                f.write(json.dumps(rec) + '\n')
            for cnt in holes:
                x = primal_point(m, cnt, k)
                info = {'m': m, 'k': k, 'cnt': list(cnt),
                        'primal_feasible': bool(x is not None)}
                if x is not None:
                    info['t'] = float(x[1]); info['p'] = float(x[0])
                with open(HOLES, 'a') as f:
                    f.write(json.dumps(info) + '\n')
                n_holes += 1
            if holes:
                print(f'  m={m} k={k}: {len(holes)} 洞 {holes[:3]}', flush=True)
        el = time.time() - t0
        print(f'm={m} 完成 ({len(cnts)} cnt × {m-1} k)，本 m 用时 {time.time()-tm:.0f}s，累计 {el:.0f}s', flush=True)
    print(f'shard {shard} 结束，总洞数 {n_holes}，总用时 {time.time()-t0:.0f}s', flush=True)
