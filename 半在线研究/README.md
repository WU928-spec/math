# 半在线（Semi-Online）调度研究 · 总目录

> 主题：SOSDP（decreasing processing times 半在线调度）及其近亲模型。
> 核心问题轴：**上界 5/4（CKK Algorithm A）↔ 下界 (1+√37)/6 ≈ 1.18046（SSW）之间的 gap**。

## 目录结构与三条线

### SOSDP上界_algA_5over4/（上界线·当前主项目）
CKK 2012 Algorithm A 竞争比 ≤ 5/4 的证明：razor 带 (P) 攻坚全程（2026-09-19..23）。
- **second_proof.md** —— razor 带 (P) 的 LP 第二证明·完整版（本线主成果，今日闭合：端点三段 + uncond 层 T2+B4 + 薄层 α'/β，全域 ∀m）；
- **proof.md** —— 第一证明（原始证明+我们路线融合版，五轮敌意复核）；
- **razor_closure.md** —— 闭合总结（组装级终审 VALID）；
- main_alpha_tight.md / main_beta_proof_v2.md / a3_beta_hi.md —— 薄层 α'/β 证明全文；
- hole_close_lemma.md、pocket1/2/3*.md —— 洞族与各口袋攻击笔记；
- BOARD/JEL/SEMANTICS/LP_CONSTRAINTS/PROTOCOL/OWNERS/STATUS/NOTES/OPTIMIZE/opt_db.json —— 研究账本与协作协议；
- artifact/（制品包）、archive/（reports 代理报告 / drafts 废稿 / data 大证书 gzip）；
- CKK2012_SOSDP_Algorithms_better_than_LPT.md —— 原始论文（md 版）。

### SOSDP下界_SSW系列/（下界线）
Seiden–Sgall–Woeginger 2000 系列下界与探索：
- SSW_m3下界_c等于1加根号37除6_完整证明.md —— m=3 下界 (1+√37)/6 完整证明（对抗序列+配平分析）；
- m2证明_紧界7除6.md —— m=2 最优 LPT 7/6 完整证明；
- m4下界试点扫描报告.md、m4_search/、research/（ssw_m4_dim01_construction.md）—— m=4 下界构造与试点扫描（gap 下界侧探索）；
- SSW_m3_配平图.png —— m=3 配平图。

### 序数调度_n4/（近亲模型线，独立问题）
Liu–Sidney–van Vliet 1996 开启的 ordinal scheduling 模型（与 SOSDP 不同）：
- lsv1996.pdf / lsv1996.txt —— 原始论文；
- 序数调度_模型识别与n4真实开放区间.md —— 模型识别、猜想证否、n=4 真实开放区间 [23/16, 101/70]（30 年开放情形）；
- 统一构造_人工证明.md、填充提升引理_详细证明.md —— 构造与引理证明；
- n4_compute/ —— 计算件（scan_n3/n4.jsonl、cover_1e11_matrix.npy.gz、compute.py、results.md）。

### 方法库/（跨线沉淀）
- 复盘_可复用证明技巧_2026-09.md —— 可复用技巧（LP 证书/组合计数/动力学/证明工程纪律）；
- 可复用引理库_2026-09.md —— 32 条可复用引理（精确陈述+证明状态+复用场景）。

## 线间关系
上界线证明的 razor 带（5/4 证明最硬段）正是上界与下界 gap 的硬点；下界线的 m=4 探索（把 (1+√37)/6 往上抬）与上界线的 razor 带在数值结构上同域。序数调度线独立（不同模型），仅方法论共享（对抗构造、配平图、计算封底）。
