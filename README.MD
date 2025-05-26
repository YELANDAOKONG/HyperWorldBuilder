# HyperWorld Builder

[Script/Minecraft] 用于制作 Hyper World 整合包核心数据包的工具集及数据包源代码

---

### **目录结构：**

- `Imports`：从相关模组中提取的部分文件、用于可视化决策树及代码引用
- `Sources`：源代码
- `Basic`：引用的基础兼容数据包（**非Git子模块**）
- `Templates`：模版文件
- `Temporary`：临时文件
- `Script`：工具脚本
- `OutPut`：构建输出的文件

> 作者计划通过一种程序化的方式使用生成器来构建数据包，而非手动修改 JSON 格式的决策树。


### **脚本说明：**

- `BuildDocs.py`：用于构建生成决策树文档网页
- `DisplayX.py`：用于可视化 Big Globe 原版决策树，生成图片文件
- `DisplayTextX.py`：用于可视化 Big Globe 原版决策树，生成 HTML 和 MD 文件
- `Build.py`：用于构建数据包（制作中）
- `Debug.py`：用于快速调试数据包（制作中）

> 运`Build/Debug`时使用 `--debug` 参数将执行`Sources\Main.py`中的`build_debug`函数；
> 
> 此函数主要用于构建一些可以快速看到效果的东西（检查是否正确生成），**数据包数值极端、无法正常游玩**。
