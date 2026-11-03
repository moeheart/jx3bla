# 苍生铸世开发证据

本目录保存客户端原件、反编译副本和审计输出，供属性与机制复核。运行表、名称表生成输入及其来源清单仍在 `equip/resources/cangshengtf/`，本目录不随客户端构建发布。

- `xinfa_evidence/`：普通心法的 9503 原件、可读副本和提取清单。
- `wujie_evidence/`：无界与幽罗的 9517 原件、可读副本和提取清单。
- `xinfa10009_evidence/`：当前正式服 10009 的 114 份原件、选择清单及临时增益证据。
- `legacy9506/`：体服时期的心法、NPC 派生 JSON 及旧来源清单；目录名沿用当时核心表版本，心法实际来源为 9503/9517。仅用于历史审计，不参与运行。
- `*.luac`：参数及角色面板的 Lua 字节码原件。
- `*_evidence.json`：镶嵌、角色面板和临时心法转换的审计结果。
- [RDPS_EVIDENCE.md](RDPS_EVIDENCE.md)：参数、原生公式及证据边界。

`equip/resources/cangshengtf/source_manifest.json` 中的文件路径以该清单所在目录为起点；`evidence_root` 指向本目录。当前 `xinfa50.json` 内的 `source.evidence_root`、`evidence_manifest` 使用本目录内的相对路径，例如 `xinfa10009_evidence/source_manifest.json`。它们是来源标识，不是运行时文件查找路径。原始提取路径、版本、大小及 SHA256 保留不变。

`legacy9506/source_manifest.json` 保留原字节，其路径描述迁移前的资源布局；旧核心表可在 Git 基线 `ae046c3` 查阅。`Xinfa50Generator`、`WujieXinfa50Generator` 的默认输出属于此历史目录；当前运行数据使用 `FormalXinfa50Generator`。

从仓库根目录运行以下只读检查：

```powershell
python -m tools.ValidateCangshengRolePanel
python -m tools.ValidateCangshengNativeGem
python -m release.FormalXinfa50Generator --deps backups/luoyang-20260915/attribute-verification/python-deps --check
python -m release.XinfaBuffEvidenceGenerator --check
python -m release.WujieXinfa50Generator --deps backups/luoyang-20260915/attribute-verification/python-deps --check
python -m unittest tests.test_cangsheng_xinfa tests.test_cangsheng_wujie tests.test_buff_tables
```

`XinfaBuffEvidenceGenerator --check` 比较当前正式输入表和 `xinfa10009_evidence/xinfa_buff_evidence.json`。根目录中的同名证据保留 9503 来源，不作为当前整表哈希的通过条件。
