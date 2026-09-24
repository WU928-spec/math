# senior 分割 w.l.o.g.（G1，一般 k）重启版 — a1_

> 背景：main 敌意复核证实 JJJ01@k<m−1 不合法（=我 B 线见解 2），razor 带 k=2..m−2
> 重开；main 修复=junior 对枚举（main_jjj_enum.py/jsonl）。本文 = 我在重开段的两项
> 检验结论 + senior 分割引理的定位修正。代码 code/a1_senior_wlog_test.py。

## 1. open 点结构发现：存活 JJJ 对 = hi 区对（全部）
main_jjj_enum.jsonl open 档（k<m−1 段）的 n_feas 精确 = **C(m−1−k, 2)** =
C(h,2)（h = hi 区机器数 = nS−jj−1+1 = m−1−k），且 feas_pairs 的下标恰为 hi 区
机器集 {k..nS−1}——**一切存活对（t+j_i+j_{i'}≤1 与角落兼容）都在 hi 区内部，
低端区对全部不可行**。
- 机理（=我见解 2 的放大确认）：低端区小 senior 的 pair 下界 j≥p−s 大；hi 区大
  senior 的 j 可小至 t——**全池最小 junior 系统性住在 hi 区**。
- 对 main 修复的确认与优化：对枚举的枚举域恰好该取 hi 区 C(h,2) 对（现行实现
  若枚举全对，低端对可全部预剪枝——省 ~C(nS,2)−C(h,2) 的 LP）。
- 同时确认：k=m−1 时 h=0，C(0,2)=0——"无存活对"与 k=m−1 用全序 j₀,j₁ 不矛盾
  （该段 JJ 行走全序坐标，合法 ✓）。

## 2. open 点的可装箱性检验：0/5（枚举器单测通过）
在 5 个 open (m,cnt,k,pair) 上解 LP 取点（t 参数化+挤压+pair+SS01，main 行基建），
typed 全装箱枚举（mask DP，单测：已知可装 12 解/已知不可装 0 解 ✓）：
**全部 0 装箱**——open 点是 (P)-幻影（LP 可行但不可装箱），与"可装箱性经验恒死"
一致。含义：
- 为 k<m−1 段 (P) 提供枚举级经验证据（agent-3 packs_exact 路线的同型确认）；
- **senior 分割 w.l.o.g. 在 razor 带无语义**：其前提"可装箱 razor 角落"为空集，
  引理的真战场在非 razor 形（见 §3）。

## 3. senior 分割 w.l.o.g. 引理（非 razor 形，值角色版）
razor 形前提既空，引理的标准形态应为（非 razor cnt、值双峰允许）：
**引理（候选）**：角落+可装箱 ⟹ 存在可行装箱使 SS = 值序最小 2a seniors 极端配对。
**反例机制（索引版失效的原因）**：SS 料机（小 senior）的 pair 下界强制 mid junior
（j ≥ p−s > τ）；mid 的宿主 senior 须 ≤ 1−mid ≈ 3t−1/4——该宿主是**值角色**
"small-mid senior"（值 ∈ (1−2t, 3t−1/4)），在索引序中不一定落在 [2a, 2a+b) 中段
（双峰时索引中段全是大 senior）。⟹ 任何"中段 b 个"的索引式 w.l.o.g. 为假；
真形态必须以值角色集陈述（SJ 槽 senior 集 = 值序集，非索引段）。
**证明路径（登记）**：支配法（main S1 已证：真实 SS 集⊇最小 2a 逐分量支配，razor
无关）+ 值角色簿记；交换法在 SJ 边界处被卡（顶替 senior 须 ≤1−j_w，无角落上界）——
razor 带外的 senior 上界须由值带+挤压给出（挤压预算簿记，同 §15.1 墙）。
**k<m−1 附加缺口**：hi 区 junior 无序 ⟹ 值序最小 junior 对不可 LP 指称（回到
mon3/对枚举；main 已选对枚举=case 分情形路线，逻辑合法）。

## 4. 分工内结论
- 我（w.l.o.g.+计数）：§1 枚举域剪枝确认、§2 幻影判决、§3 值角色版引理陈述与
  双证明路径登记。
- agent-3（动力学/反例/文档）：razor 带 k<m−1 的 (P) 机制主证；我的 §2 枚举
  证据可作其 packs_exact 数据的补充点源。
