# 动力学三件武器攻 razor 带 (P)/(W'')（a3_，2026-09-23）

> 任务：seniors≥juniors 序分离 + best-fit 同向绑定（mon3 候选）+ 挤压近紧 攻 razor 带。
> 主攻猜想（主代理提，已自我修正）：同向绑定机器配对 vs OPT 反配不相容。
> 实验：code/a3_dynamics_diag.py + fast_lp 判定（全可复跑）。

## 1. 主攻猜想判决：razor 区不显现（值近全等 ⟹ 同向≈反序）

razor 带角落 LP 可行点的值分层（a3_dynamics_diag.py 提取，m=6/8/12）：
**seniors 一层全等（~0.55–0.68）、juniors 一层全等（~t..0.44）、t** ——razor 形态。
值近全等 ⟹ 同向配对≈反序配对≈任意配对等价 ⟹ "同向绑定 vs 反配不相容"的主攻猜想
**在 razor 区不显现为主因**（值全等时配对无关）。与主代理的自我修正一致
（动力学钉死值域、OPT 装箱自由）。

## 2. razor 带角落点不可装箱的真实机理（诊断，三层递进）

(a) **体积临界**：部分点 rest 体积 > m−1（容量）——平凡不可装箱（无装箱帽 LP 无 vol 约束，
体积自由超）；含装箱帽后体积 ≤m−1 自动。
(b) **"t 无处放"**：seniors > 1−2t（非小引理恒真）⟹ 每 senior 箱余量 1−s_i < 2t ⟹
每 senior 箱至多再装 1 件 junior（2 件 ≥2t 超余量）⟹ m−1 senior 箱至多吸纳 m−1 件
junior 类件 ⟹ **第 m 件（=t）无处可放**——razor 带角落点全等值下 seniors 独占全部
m−1 箱（两 senior 和 >1：~0.56×2>1）⟹ juniors 各配一 senior ⟹ t 无家。
（= pocket2.md 会话18"'t 无家可归'引理"的 razor 化身。）
(c) **SS 计数缺口（计数恒等式位置）**：装箱存在 ⟹ a=1+c+e+2f ≥ 1（恒等式，SS 箱必存在）
⟹ 需两 senior 同箱 ≤1；razor 点 seniors 近全等且大（低端全等 ~0.55+）⟹ 两 senior 和 >1
⟹ SS 不存在 ⟹ 装箱不可能。**这是 razor 带 (P) 的最干净机理**：
**装箱存在 ⟹ SS 对存在 ⟹ razor 角落点 seniors 大且近全等（无两小者配对）⟹ 矛盾**。

## 3. 判决与精确卡点

- **razor 带 (P) 的机理 = 计数恒等式 a≥1 的 SS 需求 vs razor 角落点 seniors 大近全等
  （无两小配对）的张力**——比 §14 的"SS 单侧只杀 k=1"更深：那是 LP 判定层；
  这里是值结构层（razor 角落点 seniors 全等大使 a≥1 不可满足）。
- **卡点（诚实）**：角落 LP（保序无装箱帽）允许 s₀+s₁≤1 的点存在（§14 k≥2 FEAS）——
  即角落 LP 区域含"SS 可存在"的点（seniors 有小者）；这些点也不可装箱（§13 0/1495）
  但失败原因转移到 JJJ/SJ 兼容层。**(P) 的完整证明仍需"seniors 有小者时 JJJ/SJ 兼容
  失败"的论证**——与 §15 的配对兼容层卡点同源（同一面墙）。
- **seniors≥juniors 序分离武器的判决**：s_i≥j_k ∀i,k（mon_j_s 合法行）给了跨型配对的
  方向（大 senior 恒≥大 junior），但 razor 区值近全等使其不咬——razor 区 seniors≈juniors
  值域重叠（seniors ~0.55、juniors ~0.44，重叠小）。序分离在 razor 区是弱武器。
- **mon3（hi 区 junior 序）**：razor 带 k=m−1 时 hi 区为空（jj=m−2=nS−1）⟹ mon3 空真；
  k<m−1 razor 带的 hi 区 junior 序未证——但 razor 带主战场 k=m−1 洞区已由 mon2 闭合。

## 4. 结论

razor 带 (P) 的最干净机理成形：**装箱存在 ⟹ 计数恒等式 a≥1（SS 必存在）⟹ 两 senior
同箱 ≤1；razor 角落点 seniors 大且近全等（razor 挤压+低端刚性 §18.3）⟹ 无两小者
配对 ⟹ 矛盾**。剩余卡点：角落 LP 允许 seniors 有小者的点（s₀+s₁≤1 可达）——这些点
的装箱失败在 JJJ/SJ 兼容层（§15 同墙）。主攻猜想（动力学不相容）在 razor 区由
值近全等化解为计数+值结构问题——动力学武器的真实贡献 = 把角落点钉成 razor 形态
（值分层全等），使装箱可行性坍缩为"seniors 大近全等 ⟹ SS 不存在"的纯结构矛盾。
