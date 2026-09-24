# a3_beta_lemma.md —— β 引理攻关（agent-3；main DIRECTIVE：razor 带 (P) 第二证明最后命题）

> **β 引理**（main 2026-09-23 定形）：razor 角落+可装箱+sliver（J=j₁+j₂、jᵢ>1−J ∀i≥3、
> t+J≤1）+s_{nS}<J ⟹ 矛盾（不可装箱）。sliver 结构定理（main (a)）：JJJ={t,j₁,j₂}
> 唯一强制 ⟹ 装箱自由度只剩 SS 对选择 ⟹ **移除选择的直接匹配问题**。
> 本文：①移除-坏隙博弈归约（SJ-REV+A1 严格化）；②**S2 纯 senior 杀（已证，覆盖 95.8%）**；
> ③S0 分解与定理 P（剩余核心）；④幻影族 ord 杀（main 尖端论证的形）。

## 1. 归约：移除选择 ⟺ 坏隙博弈（严格）

设 packable。JJJ={t,j₁,j₂}（sliver (a)）⟹ 残差= seniors S + juniors {j₃..j_{nS}}，
SS 对 {u,v}（合法 s_u+s_v≤1）+ 残差 SJ 匹配。SJ-REV（§21.1）：匹配存在 ⟺ 反序可行。
记 desc[r]=第 r 大 senior（=s_{nS+1−r}），移除位 q1<q2。残差反序第 r 对：
residual_desc[r] + j_{2+r} ≤ 1。由 A1_{r+2}（j_{2+r} ≥ p−desc[r+2]）得必要条件

> **(C) residual_desc[r] ≤ desc[r+2] + (1−p)** ∀r∈[1, nS−2]

分位展开 residual_desc（r<q1: desc[r]；q1≤r<q2−1: desc[r+1]；r≥q2−1: desc[r+2]）：

> **packable ⟹ ∃合法 (q1,q2)（desc[q1]+desc[q2]≤1）：
> prom2(r) := desc[r]−desc[r+2] ≤ 1−p (∀r<q1) ∧ prom1(r) := desc[r]−desc[r+1] ≤ 1−p (∀r∈[q1+1,q2])**

**β 充分杀（senior-only）**：上述 (q1,q2) 不存在 ⟹ 不可装箱。（j 侧只经 A1 下界进入，
故此杀对 j 分布自由成立——它杀的是"senior 序列形状"。）

## 2. S2 情形（∃ 2-bad：prom2(r)>1−p 某处）——纯 senior 杀已证

数值（a3_beta_probe+senior_kill，m=6..16×2cnt，3840 样本）：**3677/3840=95.8% 满足
充分杀条件**（所有合法移除 (q1,q2) 要么 q1 前有 2-bad、要么 [q1+1,q2] 含 1-bad）。
机理：razor senior 序列的 1/2-隙超出 1−p=t−1/4± 的位置网住了一切和 ≤1 的对——
配对合法的对必含小 senior（高 q 位），而坏隙把 [q1,q2) 中段全部污染。
**定理（S2 杀）**：角落+sliver+s_{nS}<J ∧ （senior 序列使 §1 充分杀条件成立）⟹ 不可装箱。
证明=SJ-REV 反序准则+A1_{r+2} 下界+(C) 逐位展开（§1，已严格化）。
残余 4.2%=S0（无 2-bad，prom2≤1−p 恒成立）——此时 canonical 移除 {s₁,s₂} 总躲开
（(q1,q2)=(nS−1,nS)：前段全 prom2≤1−p ✓、中段空 ✓、和≤1 由 B1 ✓）。

## 3. S0 情形（prom2≤1−p 恒成立）——分解为定理 P

S0 ⟹ canonical SS={s₁,s₂} senior 侧可行 ⟹ 残差可行性纯为 j 侧问题：
> **残差可行 ⟺ all-fit：j_{2+r} ≤ 1−desc[r] ∀r∈[1,nS−2]**。

**定理 P（β 的剩余核心）**：角落+sliver+s_{nS}<J+S0+all-fit ⟹ 该点非真角落
（machine-pairing+ord/mon2 不可行）。**证明路线（两部分）**：
- (P1) all-fit+A5 钉扎出幻影形状：A5_i（j_{nS−k+i}≥p−s_i）与 all-fit 联立 ⟹
  低端隙链 s_{k+2}−s₁ ≤ 1−p、s_{k+1}−s₂ ≤ 1−p、…（k+1/k/… 隙全 ≤1−p）；
  叠加 S0（全 2-隙≤1−p）⟹ senior 全序列准刚性；squeeze+挤压（Σℓ≤nS−t）+j∈[t,2t]
  ⟹ junior 侧 j₁=j₂→t、j_{nS}→q1 双向夹紧 ⟹ **t→1/3 且全钉扎的幻影边界族**
  （探针证实：S0+all-fit 的 8 个样本全部 t=1/3、j₁=j₂=1/3、j₃..=1/3+ε、
  seniors 0.5..0.583、A1 全紧——无例外）。
- (P2) 幻影族 ord 杀（main α'(2b) 尖端论证的一般形）：low-zone ord 要求 junior
  随 senior 秩升序，但 pair 要求机 i 收 j≥p−s_i；幻影形状下小 senior 机所需 junior
  ≥p−s₁≈5/12 只有顶部 2 件够，ord 升序却迫使它们拿最小 junior ⟹ 矛盾。
  （main 已于尖端 t=1/3,p=1 证死"鬼影本影非合法角落"；(P2)=该论证的族化。）

## 4. 探针证据（a3_beta_probe.py / a3_beta_candidates.json）

- β 区（值角落+sliver+s_{nS}<J）3840 样本：残差失配边际典型 **−0.12..−0.20**
  （不 razor-thin，由 rank-1 驱动）；**可装箱多重集仅 8 个=同一 t=1/3 幻影族**，
  全部 ord/mon2 不可行（逐点核验：小 senior 机 pair 需 j≥5/12 仅 j₅,j₆ 够，
  low-zone 全 senior ⟹ ord 全升序矛盾）。
- S2 杀覆盖率随 m 稳定 ~95-97%（m=6..16，无 m 效应）。

## 5. 剩余义务（诚实清单）

1. (P1) 的严格化：all-fit+A5+squeeze ⟹ 幻影形状的符号推导（钉扎链已列出，
   缺"⟹t=1/3 边界"的末端不等式）。
2. (P2) 的族化：ord 杀从 t=1/3 尖端到整个幻影族（main 尖端论证+mon2 合法行）。
3. cnt2（a=2, e=1）：SS 两对移除的坏隙博弈+JJ 对消耗——同构待写。
4. 与 main 分工：S2 杀+S0 分解+探针=agent-3（本文）；(P1)(P2) 与 α'(2b) 薄楔
   合流（main 续攻中）；s_{nS}+p≤1+2t 新行合法性复核=agent-3 待办（见 BOARD 16:10 main 条）。
