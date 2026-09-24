# LP 管线速度优化清单（全体代理必读，2026-09-21）

> 基线：口袋2 一步+保序 m=4..30 全量 43981 情形 + 精确证书 = **102s**（优化前单个 m=18 浮点 23s）。
> 以下优化均做过等价性验证（与旧管线答案一致），可安全组合。

## 优化 1：去 mon 块（行数 O(m²)→O(m)）
`mon_j{i}_s{kk}`（j_i≤s_kk ∀i,kk，O(m²) 行）与 `mon_t_s{kk}` 被 kcap 组
（j_i≤q₁、t≤q₁、q₁≤a_m、a_m≤s_kk）传递蕴涵 ⟹ 整块删除可行性不变。
已验证：m=6..12 全 (cnt,k) 与含 mon 版一致。fast_lp.py `rows_fixed(use_mon=False)` 默认删。

## 优化 2：保序 h 强制（省一整个 m 因子）
保序 LP 的"高端自由区高度 h"被 firststep 结构**强制为 nS−1−jj**：
i>jj ⟹ nofit s_i>K−q₁（hi 区）；i≤jj ⟹ fit+srt s_i≤K−q₁（low 区）。
枚举 0..nS 多余，单一 h 即可。已验证与全枚举一致（fast_lp.py 主程序验证 2）。

## 优化 3：精确验证只查支撑行（10 倍+）
常数证书 y 的非零行只有 ~10–20 条。rationalize_verify 不必在全矩阵做 Fraction 算术：
先过滤支撑行，只对支撑行重建验证。fast_lp.py `exact_verify_support`。

## 优化 4：证书缓存复用（免 LP 求解）
同 (m,k) 相邻 cnt 的证书大量重复。迭代序 k 外 cnt 内；缓存上一次的 (y, 支撑行名)，
对新 rows 先按行名匹配做廉价精确复核（Aᵀy=0、btᵀy=0、bcᵀy=−1），命中即免解 LP。
fast_scan2.py。命中率实测见 NOTES（预期 60–90%，进一步数倍提速）。

## 优化 5：手证覆盖 k 段剪枝
k=1（P2K1 手证，全 m）与 k≥m−2（P2K-top 手证，全 m）无需计算证书，
扫描默认跳过（fast_scan2.py，`--full` 保留全量交叉验证）。

## 坑（血泪）：浮点 MARGIN 不可有理化
浮点 1e-4 不是 1/10000（二进制），`Fraction(1e-4)` ≠ `Fraction(1,10000)`——
曾致 43981 个假洞（全量 ratfail）。**bc/bt 必须存精确 Fraction**（MG=F(1,10000)），
只有矩阵系数（0,±1,±4,±5,±1.25，二进制精确）允许 `F(float)` 还原。

## 多进程
`ProcessPoolExecutor(max_workers=8, mp_context=mp.get_context('spawn'))`（macOS 下
fork+numpy/Accelerate 有崩溃风险，spawn 安全）。chunksize≥4 摊薄启动成本。
断点续跑：进度 jsonl，重跑跳过已完成 (m,cnt,k)。

## CPU 控制（用户指令 2026-09-21，最高优先级）
- 任何并行扫描 **max_workers ≤ 2**；单代理同时只允许一个扫描进程。
- 主代理同时最多挂 1 个重型扫描；轻量分析代理（无 LP 批跑）不限。
- 长扫描一律 `nice -n 15` 降优先级运行。
- 断点续跑是硬要求：任何停止都必须可无损恢复。

## 坑 2：重名约束禁止按名指派（agent-4，00:50）
证书文件里 SS/SJ/JJJ/JJ 等装箱行重名，复核时"按名找行"会错位 → 假 FAIL（曾误报 43041 条）。
正确做法：列平衡强制指派（非装箱名唯一匹配，装箱行权重由列残差唯一强制，再比对多重集）。
verify_certs.py 已修，前 500 复测全 PASS。

## 停机 SOP（血泪条款，2026-09-22）
停代理四步，缺一不可：①inbox 写 STOP（保上下文）→ ②TaskStop → ③按模式 pkill
进程树（pocket|scan|verify|fuzz|topk|template|audit|hole|order_step|uniform|fast_lp）
→ ④30 秒后**复查** `ps`，确认归零。TaskStop 不回收子进程树，第 ③④ 步永远要做。
## 禁用自动重启包装（事故源）
扫描/复核脚本**禁止**用 `until cmd; do sleep 2; done` / `while` 自动重启包装——
被 kill 后会复活，这次的 verify_certs 就是这么"杀不死"的。重试逻辑只能写在
脚本内部的断点续跑里，进程退出即终止。

## 8 分钟硬顶（用户指令 2026-09-22，最高优先级）
- **任何单次 python 进程运行不得超过 8 分钟**（对齐后台任务默认 600s 上限）。
- 预计超限的任务**必须拆分**：按 m/cnt/k/行号区间分片，每片独立进程；
  每片结束进度落盘（jsonl/sidecar），下一片从断点续跑——分片就是断点，断点就是分片。
- 脚本自带时间盒：主循环每迭代检查耗时预算（如 440s 自退），预算耗尽前保存断点干净退出，
  禁止"跑死等超时"。
- 复核/长扫类脚本必须输出可机读的进度行（done/total/pass/fail），供 watcher 与代理轮询。

## 代理 30 分钟硬顶（用户指令 2026-09-22，最高优先级）
- **任何子代理任务最长运行 30 分钟**：到点必须汇报进度（上 BOARD）并停止。
- 超 30 分钟的任务**必须拆成多个 30 分钟以内的子任务**串行续跑（断点恢复，与
  8 分钟进程硬顶配套：任务 30min 拆段、进程 8min 分片）。
- brief 必带 deadline（开工时间+30min）与"到点汇报即停"字样；代理每完成一个
  子任务自查时间（bash `date`）。
- 主代理职责：派发时写明 deadline；超 30min 未停 → inbox DIRECTIVE-STOP；
  再不停 → 请用户面板强停（TaskStop 对 agent 不生效是已登记缺陷）。
