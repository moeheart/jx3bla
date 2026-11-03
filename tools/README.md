# tools

保留原有工具目录。`Functions.py`、`Attribute.py`、`LoadData.py`、`Names.py`、`ResourcePath.py` 等供客户端或服务端调用；独立分析、取证和校验入口也放在这里，沿用 PascalCase 文件名。

| 入口 | 用途 |
| --- | --- |
| `ValidateLuoyang`、`ValidateLuoyangRdps`、`ValidateWujie` | 日志解析、属性、rDPS 与窗口回归 |
| `ValidateLuoyangFirstThree`、`ValidateLuoyangLastTwo` | 洛阳首领机制校验 |
| `LuoyangFirstThreeEvidence`、`LuoyangLastTwoEvidence` | 洛阳日志取证 |
| `ValidateCangshengEquipment`、`ValidateCangshengNativeGem`、`ValidateCangshengRolePanel`、`ValidateLuoyangNpcDefense` | 装备和客户端原始证据复核 |
| `AnalyzeLingsuRdps`、`MineShiChaoyiCircles`、`PlotShiChaoyiCircles` | 专项分析和绘图 |

从仓库根目录运行，例如 `python -m tools.ValidateLuoyang --help`。输出放入 `build/`、`backups/` 或 `.tmp/`；需要长期保留的说明和证据放入 `docs/`。

生成装备或心法数据的脚本位于 `release/`，例如 `python -m release.FormalXinfa50Generator --help`。纯单元测试位于 `tests/`，统一用 `python -m unittest discover -s tests` 运行。
