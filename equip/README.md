# equip

装备识别类，主要实现装备 ID 到属性的转化。计算和导出模块留在本目录，数据沿用 `resources/` 下按赛季分目录的方式。

`resources/cangshengtf/` 保留苍生铸世 50 级正式服运行表、名称/增益生成输入及 `source_manifest.json`。目录名称沿用既有方式，内容统一为 2026-10-29 的 10009 正式服数据。客户端实际打包的资源由 `release/ReleaseResources.py` 明确列出；不要递归打包整个资源目录。

客户端原始 Lua、反编译文本、原生指令和取证报告集中在 [docs/160/evidence](../docs/160/evidence/)。移动原件不改变其字节或 SHA256；`source_manifest.json` 中的文件路径仍相对于该清单所在目录。正式心法的 `evidence_manifest` 是证据目录内部的逻辑路径。`legacy9506/` 为历史取证，运行时不再读取。

运行表和取证原件均需保留，更新数据后应通过 `tests/test_buff_tables.py` 的来源哈希校验及对应属性回归，再构建安装包。
