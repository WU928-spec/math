"""a2_candidate_spec.py — 候选转移引理的声明式编码接口（agent-3 与证伪器的契约）。

候选引理 = 一组关于角落变量 {p, t, s_i, j_i, a_m, q_1}（可按 m,k 参数化）的线性约束。
编码：实现 candidate_rows(m, k, ctx) 返回 [(coef, bc, bt, name)]：
  coef: {var: float}，var ∈ {'p','t','am','q1','s0'.., 'j0'..}（'s{i}'/'j{i}'）
  约束语义：Σ coef·var <= bc + bt*t（t 即 var 't'；bt 一般 0）
  ctx: {'nS': m-1, 'jj': k-1}。
示例：把占位实现换成候选；验证器调用方：a2_transfer_falsifier.py。
"""


def candidate_rows(m, k, ctx):
    """占位示例（空 = 不附加约束）。真实候选由 agent-3 粘贴到此处或新建
    a2_candidate_<name>.py 并在 falsifier 里 --spec 指定模块。"""
    return []
