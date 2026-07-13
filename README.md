# da_chuang

基于 Benes 光交换网络的最短路径与连接规划算法。

## 当前阶段

项目刚起步，当前仓库先放协作约束和接口约定，避免后续 A、B、Agent 同时开发时出现函数名不一致、互相改文件、代码冲突等问题。

## 先读哪些文件

1. `AGENTS.md`：所有使用 Codex/Agent 写代码时必须遵守的总规则。
2. `docs/member-a-topology.md`：A 同学负责拓扑建模时读这个。
3. `docs/member-b-algorithm.md`：B 同学，也就是算法负责人，读这个。
4. `docs/beginner-guide.md`：零基础入门说明，解释未来每个文件是干什么的，以及最后怎么展示结果。
5. `docs/benes-8x8-learning-plan.md`：算法负责人第一阶段的 8x8 Benes、无权最短路径和 BFS 学习计划。

## 暂定项目结构

后续真正开始写代码时，建议按下面结构创建：

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
|       |-- visualize.py
|       `-- experiments.py
|-- tests/
|   |-- test_topology.py
|   |-- test_routing.py
|   `-- test_metrics.py
|-- examples/
|   |-- demo_8x8.py
|   `-- demo_batch_experiment.py
|-- outputs/
|   |-- figures/
|   `-- reports/
`-- docs/
    |-- member-a-topology.md
    |-- member-b-algorithm.md
    |-- benes-8x8-learning-plan.md
    `-- beginner-guide.md
```

## 最小目标

第一阶段不要追求复杂论文复现，先完成最小闭环：

1. 能生成 8x8 Benes 网络。
2. 能从 `I3` 找到 `O6` 的路径。
3. 能计算路径长度、损耗、延迟、总代价。
4. 能画出拓扑图，并高亮这条路径。
5. 能输出一份 CSV 表格，比较 BFS、Dijkstra、自定义权重算法。
