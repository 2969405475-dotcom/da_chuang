# 零基础入门指南

这份文档给刚开始做项目的同学看。你不需要一次性看懂所有内容，先知道每个文件负责什么，后面写代码时再回来查。

## 一、这个项目到底要做什么

一句话：

```text
在 Benes 光交换网络中，帮某个输入端口找到到某个输出端口的路径，并比较不同算法效果。
```

例子：

```text
输入：I3
输出：O6
目标：找到 I3 到 O6 的一条路径
```

最后我们希望能展示：

```text
1. 一张 Benes 网络拓扑图
2. 一条被高亮的路径
3. 不同算法的对比表格
4. 不同算法的运行时间、路径代价对比图
```

## 二、未来每个文件是干什么的

### README.md

项目首页说明。别人打开仓库，第一眼会看到它。

它应该说明：

```text
项目做什么
怎么安装
怎么运行
怎么查看结果
```

### AGENTS.md

给 Agent 看的规则文件。

以后你让 Codex 或其他 AI 写代码时，要先让它读这个文件。它的作用是防止 AI 乱改函数名、乱动别人负责的模块。

### requirements.txt

记录项目需要安装哪些 Python 包。

以后可能会写：

```text
networkx
numpy
pandas
matplotlib
pytest
```

安装命令通常是：

```bash
python -m pip install -r requirements.txt
```

### src/benes/topology.py

负责生成 Benes 网络。

你可以理解成：它负责画出“路网本身”，但不负责找路。

核心函数：

```python
build_benes_network(8)
```

它应该生成：

```text
I0 到 I7
O0 到 O7
S1_0 到 S5_3
```

### src/benes/routing.py

负责找路径。

比如：

```python
find_path(G, "I3", "O6", method="bfs")
```

它应该返回：

```python
["I3", "S1_1", "S2_1", "S3_1", "S4_3", "S5_3", "O6"]
```

注意：实际路径可能不完全一样，只要是合法路径即可。

### src/benes/metrics.py

负责算这条路径好不好。

比如一条路径可能有：

```text
路径长度：6
损耗：1.2
延迟：5.0
串扰风险：0.3
总代价：9.0
```

这些指标后面会用来画图和写报告。

### src/benes/visualize.py

负责画图。

它不负责找路径，只负责把已有网络和已有路径画出来。

最后它应该能生成：

```text
outputs/figures/benes_8x8.png
outputs/figures/path_I3_O6.png
```

### src/benes/experiments.py

负责批量实验。

例如一次性比较：

```text
BFS
Dijkstra
weighted_benes
```

然后输出 CSV 表格：

```text
outputs/reports/algorithm_comparison.csv
```

CSV 可以用 Excel 打开。

### tests/

测试文件夹。

它的作用是检查代码有没有写错。比如：

```text
8x8 是否真的有 5 级
I3 到 O6 是否能找到路径
返回的路径是否合法
metrics 里面是否包含 cost
```

运行命令：

```bash
python -m pytest
```

### examples/

示例文件夹。

里面放可以直接运行的小脚本。例如：

```text
demo_8x8.py
demo_batch_experiment.py
```

你以后可以把它理解为“演示按钮”。

### outputs/

输出结果文件夹。

建议分成：

```text
outputs/figures/   放图片
outputs/reports/   放 CSV 表格
```

这些通常不用提交到 GitHub，除非老师要求提交展示结果。

## 三、最后结果怎么可视化呈现

最终展示可以分三层。

### 1. 拓扑图

展示 Benes 网络结构：

```text
左边是输入 I0 到 I7
中间是交换单元 S1_0 到 S5_3
右边是输出 O0 到 O7
```

用途：让老师直观看到你们真的建出了 Benes 网络。

### 2. 路径高亮图

例如高亮：

```text
I3 -> S1_1 -> S2_1 -> S3_1 -> S4_3 -> S5_3 -> O6
```

普通边用灰色，路径边用红色或蓝色。

用途：展示算法找出来的路径。

### 3. 算法对比图

从 CSV 表格生成柱状图或折线图。

建议至少做三张：

```text
1. 不同算法运行时间对比
2. 不同算法路径总代价对比
3. 不同网络规模下算法运行时间变化
```

答辩时可以这样讲：

```text
BFS 只考虑跳数，所以快，但不考虑损耗。
Dijkstra 可以考虑权重，路径质量更好。
weighted_benes 在 Dijkstra 基础上加入光网络损耗、延迟、串扰等因素，更贴合题目。
```

## 四、你作为初学者应该按什么顺序做

推荐顺序：

1. 先看懂 `README.md` 和 `AGENTS.md`。
2. 让 A 先完成 `topology.py`。
3. 你再完成 `routing.py` 的 BFS。
4. 然后完成 `metrics.py`。
5. 再做 Dijkstra。
6. 最后做可视化和实验对比。

不要一开始就做 KNN。KNN 是后面的加分项，不是第一天必须完成的东西。

## 五、最小可展示成果

第一阶段只要做到下面这些，就已经可以演示：

```text
1. 运行 demo_8x8.py
2. 生成 8x8 Benes 网络图
3. 找到 I3 到 O6 的路径
4. 图中高亮这条路径
5. 输出 algorithm_comparison.csv
```

这就是项目的最小闭环。
