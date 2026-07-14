# Benes 8×8 最短路径规划器

一个用于演示 Benes 光交换网络最短路径规划的 Windows 桌面软件。用户可以选择输入、输出端口，修改每条连线的路径长度，并使用 Dijkstra 算法计算和显示总长度最短的路径。

## 当前功能

- 固定建立 8×8 Benes 网络，包含5级、20个 2×2 交换单元。
- 选择 `I0–I7` 和 `O0–O7` 中任意一组端口。
- 启动时输入线和输出线的路径长度默认为 `1`，级间线随机生成 `1–10` 的路径长度。
- 鼠标悬停连线可查看端点与当前权重，双击连线可修改长度。
- 使用 Dijkstra 算法进行最短路径规划。
- 高亮路径，并在交换单元内部用平行线或交叉线显示 `Bar`、`Cross` 状态。
- 显示最短路径节点、总长度和跳数，并列出当前输入输出之间全部4条可行路径及各自总长度。

## 开发环境

项目要求 Windows 11 和 Python 3.11 64 位。在 PowerShell 中执行：

```powershell
py -3.11 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

启动软件：

```powershell
$env:PYTHONPATH = "src"
.\venv\Scripts\python.exe -m benes.app
```

运行测试：

```powershell
.\venv\Scripts\python.exe -m pytest
```

## 使用方法

1. 在顶部选择输入端口和输出端口。
2. 鼠标移到连线上可查看路径长度；双击连线可输入新的非负长度。
3. 点击“开始规划”。
4. 在拓扑图和右侧结果区查看最短路径、交换单元状态，以及按总长度排序的4条可行路径。
5. 点击“重新随机权重”可重置两侧连线为 `1`，并为级间线重新生成 `1–10` 的整数长度。

路径长度必须是大于或等于零的有限数字。

## 构建 Windows 软件

安装开发依赖后执行：

```powershell
.\scripts\build_exe.ps1
```

脚本先生成便于排查问题的目录版，再生成最终单文件版本：

```text
dist/onedir/BenesPathPlanner/BenesPathPlanner.exe
dist/BenesPathPlanner.exe
```

`build/`、`dist/`、`outputs/` 和本地虚拟环境不会提交到 Git。

## 协作说明

修改项目代码前请先阅读 `AGENTS.md`，并保持其中定义的公开接口、节点命名和模块边界。

建议阅读：

1. `AGENTS.md`：所有使用 Codex/Agent 写代码时必须遵守的总规则。
2. `docs/member-a-topology.md`：A 同学负责拓扑建模时读这个。
3. `docs/member-b-algorithm.md`：B 同学，也就是算法负责人，读这个。
4. `docs/beginner-guide.md`：零基础入门说明，解释未来每个文件是干什么的，以及最后怎么展示结果。
5. `docs/benes-8x8-learning-plan.md`：算法负责人第一阶段的 8x8 Benes、无权最短路径和 BFS 学习计划。

## 项目结构

```text
da_chuang/
|-- README.md
|-- AGENTS.md
|-- requirements.txt
|-- src/
|   `-- benes/
|       |-- __init__.py
|       |-- topology.py
|       |-- routing.py
|       |-- metrics.py
|       |-- layout.py
|       |-- visualize.py
|       |-- app.py
|       `-- ui/
|-- tests/
|   |-- test_topology.py
|   |-- test_routing.py
|   |-- test_metrics.py
|   |-- test_visualize.py
|   `-- test_ui.py
|-- scripts/
|   `-- build_exe.ps1
`-- docs/
    |-- member-a-topology.md
    |-- member-b-algorithm.md
    |-- benes-8x8-learning-plan.md
    `-- beginner-guide.md
```
