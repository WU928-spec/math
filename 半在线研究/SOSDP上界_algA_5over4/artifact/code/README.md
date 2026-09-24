# artifact/code 逐文件说明

| 文件 | 作用 | 输入 → 输出 |
|---|---|---|
| `fast_lp.py` | 快管线核心。`rows_fixed(m,cnt,k,use_order=True)` 生成约束行（浮点系数 + 精确 Fraction 右端）；`float_cert_rows` 浮点解 Farkas 对偶定位；`exact_verify_support` 只对支撑行做 Fraction 精确验证。等价性（去 mon 块、强制 h=nS−1−jj）在该文件 `__main__` 内自带验证。 | (m,cnt,k) → (rows, nv) / 证书 y |
| `fast_scan.py` | m=4..30 一步+保序全扫驱动（8 workers spawn、断点续跑 jsonl、证书落盘）。 | 无参数 → `fast_scan_progress.jsonl` + `pocket2_onestep_order_certs.txt` |
| `fast_scan_31_45.py` | m≥31 扩扫驱动（agent-4）。同管线 + workers=2、`A4_SCAN_TIMEBOX=440s` 时间盒自退（8min 硬顶）、断点续跑。 | `python fast_scan_31_45.py M_LO M_HI` → 进度/证书 jsonl 追加 |
| `verify_certs.py` | 独立复核器（agent-4）。**不调 linprog**：重建矩阵 + 纯 Fraction 核对 Aᵀy=0、btᵀy=0、bcᵀy=−1、y≥0。支持三种格式：①fast jsonl `{'m','cnt','k','cert':[(名,权)]}`（重名装箱行用列平衡强制指派）；②遗留 jsonl（builder+参数+索引稀疏权重）；③口袋1 txt（头变体 nofs/jj=/S12/jj2=/h=）。分片：`A4_VERIFY_SLICE=N` 每片 N 条自退，sidecar `<file>.vprog` 断点。 | 证书文件 → PASS/FAIL 计数 |
| `pairing_feasible.py` | `bin_count_solutions(m)`：箱型计数 (a,b,c,d,e,f) 全枚举（冻结基线，全员只读）。 | m → cnt 列表 |
| `farkas_fixed.py` | 旧编码一步 LP（修正 firststep：`build_fixed(m,cnt,k)`）+ `float_cert`/`rationalize_verify`。遗留证书（pocket2_legacy_build_fixed.jsonl）重建用。 | (m,cnt,k) → (A,bc,bt,names,nv) |
| `second_step.py` | 旧编码二步 LP（`build_fixed2(m,cnt,k,jj2)`：q2 动态 S1/S2/S3）。遗留二步证书重建用。 | (m,cnt,k,jj2) → (A,bc,bt,names,nv) |

依赖关系：`fast_scan*.py` → `fast_lp.py` + `pairing_feasible.py`；
`verify_certs.py` → `fast_lp.py`（fast 格式）/ `farkas_fixed.py`+`second_step.py`（遗留 jsonl）。
口袋1 txt 复核需 agent-1 的 `pocket1_bins.py`（不在本包，其证据链归 agent-1）。

运行约定：脚本内部将自身所在目录插入 sys.path——从 `artifact/code/` 内运行即自足。
