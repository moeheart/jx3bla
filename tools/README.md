# tools

保留原有工具目录。`Functions.py`、`Attribute.py`、`LoadData.py`、`Names.py`、`ResourcePath.py` 等供客户端或服务端调用；独立分析、取证和校验入口也放在这里，沿用 PascalCase 文件名。

| 入口 | 用途 |
| --- | --- |
| `ValidateLuoyang`、`ValidateLuoyangRdps`、`ValidateWujie` | 日志解析、属性、rDPS 与窗口回归 |
| `ValidateLuoyangFirstThree`、`ValidateLuoyangLastTwo` | 洛阳首领机制校验 |
| `LuoyangFirstThreeEvidence`、`LuoyangLastTwoEvidence` | 洛阳日志取证 |
| `LuoyangHeroicLastTwoEvidence` | 英雄洛阳后两首领日志与阶段、技能轴边界核验 |
| `ValidateCangshengEquipment`、`ValidateCangshengNativeGem`、`ValidateCangshengRolePanel`、`ValidateLuoyangNpcDefense` | 装备和客户端原始证据复核 |
| `AnalyzeLingsuRdps`、`MineShiChaoyiCircles`、`PlotShiChaoyiCircles` | 专项分析和绘图 |

从仓库根目录运行，例如 `python -m tools.ValidateLuoyang --help`。输出放入 `build/`、`backups/` 或 `.tmp/`；需要长期保留的说明和证据放入 `docs/`。

史朝义红白圈的体验服与正式服样本、源日志哈希、复核及绘图命令见[历史研究索引](../docs/analysis/README.md)。`MineShiChaoyiCircles` 支持用本地 JCL 逐项校验公开样本，`PlotShiChaoyiCircles` 可直接使用仓库中的体验服样本绘图。

大版本清理使用 `531aa11` 的[实录基线](../docs/160/cleanup-replay-baseline.json)。`normal` 为普通五场，`heroic13` 按顺序包含一场失败和五场通关，`heroic14` 为三个曾经漏判的英雄首领。每组共用装备上下文，比较通关、结束边界、有效时间、伤害守恒、全团表、个人技能数值、时间轴和待上传数量。个人数据只输出摘要。分别将组名和路径代入下列命令。

```powershell
$env:PYTHONHASHSEED = '0'
python -m tools.ValidateCleanupReplays --baseline docs/160/cleanup-replay-baseline.json --group heroic13 --log-dir C:/验证资料/英雄日志 --output build/validation/cleanup-heroic13.json
```

生成装备或心法数据的脚本位于 `release/`，例如 `python -m release.FormalXinfa50Generator --help`。纯单元测试位于 `tests/`，统一用 `python -m unittest discover -s tests` 运行。
