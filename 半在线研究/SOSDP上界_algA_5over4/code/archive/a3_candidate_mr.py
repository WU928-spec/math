"""a3_ 候选原料：MR（高端区 junior 反向单调，best-fit 收件下成立）。
行：j_i >= j_{i+1} 对 i>jj（高端区），即 j_{i+1} - j_i <= 0。"""
def candidate_rows(m, k, ctx):
    nS = ctx['nS']; jj = ctx['jj']
    rows = []
    for i in range(jj + 1, nS - 1):
        rows.append(({f'j{i+1}': 1.0, f'j{i}': -1.0}, 0, 0, f'mr{i}'))
    return rows
