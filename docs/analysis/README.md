# 洛阳之战历史研究

| 版本与范围 | 样本与结果 |
| --- | --- |
| [9 月 15 日体验服史朝义](shichaoyi-circles-20260915/研究报告.md) | 46 场，13 轮，438 个圈。9 个满轮均为 20 红 20 白，同轮所有点对距离都超过 4 尺。 |
| [11 月 2–3 日正式服史朝义](shichaoyi-circles-live-20261104/研究报告.md) | 5 份去重战斗，11 轮，416 个圈。全部符合内外各四象限的八圈周期，已消失圈附近可以再次生成。 |
| [10 月 6 日体服心法统计](luoyang-xinfa-20261006/洛阳之战心法表现与推荐.md) | 43 场通关、1,071 份个人复盘。按角色聚合后提供 64 个心法与五个首领的样本量和分位数。 |
| [10 月 7–8 日体服失误统计](luoyang-mistakes-20261007-08/README.md) | 70 份战斗日志的规则和汇总。 |

## 复核红白圈

两份 `evidence.json` 包含匿名战斗编号、输入字节数及 SHA256、轮次、坐标和机制时间。正式服样本的 `discovery_set` 标识发现规律时已使用的两场，供复算追加验证。个人战报、角色别名、系统喊话和原始日志路径保存在本地原始资料中。研究比较以各自当时的地图、难度和版本为限。

从仓库根目录运行下列命令。颜色统计仅依赖 Python，绘图需要 Matplotlib 和 NumPy，正式服模型模拟需要 NumPy。输出位于 `build/research/` 下的同名研究目录。正式服模拟每种模型使用 10,000 次重复。

```powershell
python docs/analysis/shichaoyi-circles-20260915/stats_analysis.py
python -m tools.PlotShiChaoyiCircles
python docs/analysis/shichaoyi-circles-live-20261104/describe_and_plot.py
python docs/analysis/shichaoyi-circles-live-20261104/candidate_models.py
```

持有原始 JCL 时可从输入日志核对公开样本，例如将正式服五场日志置于同一目录后运行下列命令。日志以内容哈希匹配，包括一场文件名标作其他 NPC 的零圈战斗。也可将 `--logs` 换成 `--manifest 清单.json`，清单为含 `source` 和 `sha256` 的对象数组，相对路径以清单所在目录为准。

```powershell
python -m tools.MineShiChaoyiCircles --logs 游戏日志目录 --check-sample docs/analysis/shichaoyi-circles-live-20261104/evidence.json
```

`MineShiChaoyiCircles --logs 游戏日志目录` 单独运行时，按史朝义文件名提取体验服研究用的逐事件表，默认写入本地构建目录。完整历史研究的长模拟、审阅底稿和私有审计结果可由维护者从清理前原件恢复。

## 旧版通关算法

8.16.3 草稿同时要求祈愿、历练值、伤害封顶及同一本体脱战，其测试还覆盖 5 秒窗口端点、同名分身、续战、截断和长威压。当前测试保留同一本体、近期有效伤害、续战否决、失败截止和长威压等边界。普通掉落或通用奖励可出现在未完成的战斗中。新版以原生全胜完成、精确赛季荣誉及各自的匹配条件判断通关。历史草稿、五个源文件和当时的实录已按 8.16.3 基线保留。[完成和威压用例](../../tests/test_luoyang_completion.py) · [赛季荣誉及通用奖励反例](../../tests/test_luoyang_seasonal_victory.py)
