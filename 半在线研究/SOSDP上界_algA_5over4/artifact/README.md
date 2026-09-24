# Artifact：口袋2 计算闭合证据链（m=4..50）

半在线调度证明项目（Algorithm A 竞争比 5/4）的计算证据包：**口袋2（最闲机为单子机）角落
在修正版 LP + 保序约束下 m=4..50 全闭（零洞）**，证书经独立纯 Fraction 复核。

打包时间：2026-09-22（agent-4）。来源目录：`/Users/a123456/math/research/2026-09-19_algA_5over4/`。

## 1. 结论与规模

| 范围 | 情形数 (m,cnt,k) | 洞 | 证书 | 独立复核 |
|---|---|---|---|---|
| m=4..30 | 43981 | 0 | 43981 份 | PASS 43981 / FAIL 0 |
| m=31..45 | 263575 | 0 | 263575 份 | PASS 263575 / FAIL 0 |
| m=46..50 | 204312 | 0 | 204312 份（+97 重复行） | 部分（123425 行 PASS，其余 80984 行未验，见 §4） |
| **合计 m=4..50** | **511868** | **0** | | |

另含遗留编码（build_fixed 无保序 / build_fixed2 二步）证书：419 + 3021 份，均全量复核 PASS
（m=4..11 一步全闭；二步闭合 3021 个 (m,cnt,k,jj2)，m=12..30 残留 304 个由保序引理杀死——
见主项目 BOARD.md/SEMANTICS.md）。

## 2. 目录结构

```
artifact/
├── README.md                      ← 本文件
├── manifest.sha256                ← 全部文件 sha256 校验和
├── certs/
│   ├── pocket2_onestep_order_certs.txt            43981 份（m=4..30，全验）
│   ├── pocket2_onestep_order_certs_31_45.txt      263575 份（m=31..45，全验）
│   ├── pocket2_legacy_build_fixed.jsonl           419 份（旧编码一步，全验）
│   ├── pocket2_legacy_build_fixed2_2step.jsonl    3021 份（旧编码二步，全验）
│   └── unverified/
│       ├── pocket2_onestep_order_certs_46_50.partial.txt   m=46..50 证书（前 123425 行已验 PASS，
│       │                                                   后 80984 行未验——按"只打包已验部分"
│       │                                                   原则单列于此，勿当作已验证据引用）
│       └── ...partial.txt.vprog.note                       断点对应关系说明
└── code/
    ├── README.md                  ← 逐文件说明
    ├── fast_lp.py                 ← 快管线核心（rows_fixed/float_cert_rows/exact_verify_support）
    ├── fast_scan.py               ← m=4..30 扫描驱动（main）
    ├── fast_scan_31_45.py         ← m≥31 扫描驱动（workers=2、440s 时间盒自退、断点续跑）
    ├── verify_certs.py            ← 独立复核器（纯 Fraction、不调 linprog）
    ├── pairing_feasible.py        ← bin_count_solutions 箱型枚举（冻结基线）
    ├── farkas_fixed.py            ← 旧编码一步 LP（遗留证书重建用）
    └── second_step.py             ← 旧编码二步 LP（遗留证书重建用）
```

## 3. 复现步骤

环境：macOS + Python 3.12 venv（`/Users/a123456/math/.venv`，依赖 numpy/scipy/sympy）。
通用 python 一律用 `/Users/a123456/math/.venv/bin/python`。

### 3.1 复核已验证书（最核心）

```bash
cd <项目根>   # research/2026-09-19_algA_5over4/
# m=4..30（约 5-8 min，2 workers）：
nice -n 15 .venv/bin/python artifact/code/verify_certs.py artifact/certs/pocket2_onestep_order_certs.txt
# m=31..45（约 40-60 min 于负载机；分片自退+断点续跑，每片 ≤8min）：
A4_VERIFY_SLICE=24000 nice -n 15 .venv/bin/python artifact/code/verify_certs.py \
    artifact/certs/pocket2_onestep_order_certs_31_45.txt   # 重复执行至 EOF（sidecar .vprog 自动续）
# 遗留编码（秒级）：
.venv/bin/python artifact/code/verify_certs.py artifact/certs/pocket2_legacy_build_fixed.jsonl
.venv/bin/python artifact/code/verify_certs.py artifact/certs/pocket2_legacy_build_fixed2_2step.jsonl
```

预期输出：`PASS <份数>, FAIL 0`。复核器不调用 linprog：用 `rows_fixed`/`build_fixed`/`build_fixed2`
重建约束矩阵（Fraction 精确），纯 Fraction 核对 Aᵀy=0、btᵀy=0、bcᵀy=−1、y≥0。
重名装箱行（SS/SJ/JJJ/JJ）由"列平衡强制指派"完备对齐（opt_db.json P02 坑）。

注意：verify_certs.py 与 fast_scan 脚本内部按 `code/` 目录布局解析模块路径（sys.path 插入
脚本所在目录），从 artifact/code/ 运行即可自足（不依赖项目其他文件）。

### 3.2 重跑扫描（重新生成证书）

```bash
# m=4..30（8 workers 基线 102s；CPU 条款下请先改 workers≤2 或设 nice）：
.venv/bin/python artifact/code/fast_scan.py            # 自带断点 fast_scan_progress.jsonl
# m≥31（workers=2、nice15、440s 时间盒自退，被杀/超时后直接重跑同一命令续）：
nice -n 15 .venv/bin/python artifact/code/fast_scan_31_45.py 31 50
```

预期：每个 m 打印 `洞 0 个`；全部情形输出精确常数证书（float 定位 + 支撑行 Fraction 验证）。
实测耗时基线（M 系 Mac，负载中等）：m=46..50 单 m 各 3.5/4.7/5.8/≈8/≈11.5 min（2 workers）；
复核 ~60-90 份/s（2 workers, nice 15）。

### 3.3 m=46..50 未验部分续验

`certs/unverified/pocket2_onestep_order_certs_46_50.partial.txt`：前 123425 行已验 PASS；
续验剩余 80984 行：对该文件新建 sidecar 并跳过前缀（或直接用整文件断点见
`pocket2_onestep_order_certs_31_45.txt.vprog.note` 说明），命令同 §3.1 分片式。

## 4. 诚实声明（已知边界）

- 复核是**快照语义**：certs/ 内文件与复核时内容逐字节一致（manifest.sha256 锁定）。
- m=46..50 证书**未全验**：已验部分全 PASS，未验部分按规则不进 certs/ 主目录。
- 本证据链仅覆盖口袋2；口袋1（agent-1）/口袋3（agent-3 重建中）证据链不在本包。
  口袋3 曾有一版"统一体积证书"（agent-4 会话22）建于已判 INVALID 的约束 `y>=1-2t`，
  **已作废，不在本包**（见 SEMANTICS.md）。
- LP 语义合法性依赖：修正 firststep 编码、保序引理、装箱固定分组 w.l.o.g.（最后一项
  SEMANTICS 标注"字面为假/角落语境可接受"，严格化未完成——为本证据链的唯一 SUSPECT 依赖）。
