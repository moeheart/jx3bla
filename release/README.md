发布构建说明。

## 正式版构建

正式版保持轻量，不打包离线属性分析所需的大型本地静态表。

构建命令：

```powershell
./release/Release.ps1
```

对应配置：

- `release/Release.ps1`
- `MainWindow.spec`

产物：

- `dist/j3jz.exe`

注意事项：

- 正式版不要改用 `MainWindow.beta.spec`，否则会显著增大发布体积。
- 不要再直接运行 `pyinstaller -F -i jx3bla.ico MainWindow.py`，这样会绕过 spec 和后续维护约定。

## Beta 离线版构建

`EDITION` 含 `beta` 时，会走本地属性分析逻辑，因此必须把离线所需静态资源一起打进 onefile。

构建命令：

```powershell
./release/ReleaseBeta.ps1
```

对应配置：

- `release/ReleaseBeta.ps1`
- `MainWindow.beta.spec`

产物：

- `dist/j3jz-beta.exe`

Beta 离线版额外打包的资源：

- `equip/resources/Custom_Trinket.tab`
- `equip/resources/Custom_Armor.tab`
- `equip/resources/Custom_Weapon.tab`
- `equip/resources/attrib.tab`
- `equip/resources/enchant.tab`
- `equip/resources/item.txt`
- `equip/resources/other.tab`
- `equip/resources/Set.tab`
- `icons/`

说明：

- 这些资源只给 beta 离线版使用，不应并入正式版。
- 运行时资源路径已经兼容源码目录、exe 同目录资源，以及 PyInstaller onefile 解包目录。
- `icons/rate.dat` 属于运行时缓存，程序会优先写到 exe 同目录，而不是 `_MEIPASS`。
