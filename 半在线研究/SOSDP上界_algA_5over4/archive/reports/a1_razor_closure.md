# A 线：razor 带 k=m−1 全合法行 LP 扫描 — a1_

> 任务：razor 带 k=m−1 全合法行 LP（build_bcanon = mon2 + B 规范形全合法行）
> 全扫描验证。代码 code/a1_razor_closure.py（断点 a1_razor_closure_progress.jsonl）。

## 结果（m=4..30，全 cnt，k=m−1）
- **1907/1907 (m,cnt) 精确常数证书（Fraction 验证通过），0 洞**——razor 带 k=m−1
  LP 路线完全闭合（含洞族）。
- **承重结构（全域消融）**：SS（最小 2a 极端配对行）必要 1907/1907；JJJ（最小 3d
  聚合行）必要 1907/1907；**mon2 / SJ-REV / JJ-REV 必要 0/1907**（被 SS+JJJ+角落
  约束隐含）。
- 证书支撑抽样（m=30）：{JJJagg, SS, danger, fs_j15, j>=t 族, j28<=2t}——无 mon2
  行入支撑，与消融一致。

## 交叉验证（与 agent-3 收官一致）
agent-3 a3_razor_combinatorial.md 的 razor 带 (P) 收官承重 = {SS01 必要 46/46、
JJJ01 必要 40/46、挤压冗余}；本扫描（B 规范形全行版，k=m−1）独立得到
**SS+JJJ 双承重、其余冗余**——两路线在"SS/JJJ 双墙承重"上定量互证。
差异：agent-3 的 JJJ01 在 6/46 处被 SS 墙直杀覆盖；本扫描全行版下 JJJ 聚合行
全域必要（行形态不同：JJJ01 单箱强形 vs JJJagg 聚合）。

## 消融意外发现
mon2（保序 junior 升序）在 k=m−1 全行版下**非承重**——B 规范形的 SS/JJJ 行
（值序坐标）+ 角落约束已隐含 junior 排序所需全部强度。这提示 (W'') 的 mon2
依赖在 razor 带可被更弱的值序行替代（登记供主代理 WLOG 复核参考）。
