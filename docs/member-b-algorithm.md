# B 同学约束文件：路径算法

本文件给负责算法部分的同学使用。这里的 B 就是算法负责人。

## 你的目标

你负责在 A 同学生成的 Benes 网络上寻找路径，并计算路径质量。你的成果要能回答：

```text
从 I3 到 O6，应该走哪条路径？
这条路径有多长？
损耗、延迟、串扰和总代价是多少？
不同算法谁更快、谁代价更低？
```

## 你主要负责的文件

```text
src/benes/routing.py
src/benes/metrics.py
tests/test_routing.py
tests/test_metrics.py
```

后续如果做批量对比，可以参与：

```text
src/benes/experiments.py
```

## 你必须提供的函数

```python
def find_path(G, src: str, dst: str, method: str = "bfs", weight: str | None = None) -> list[str]:
    """从 src 到 dst 找路径，返回路径节点列表。"""
```

```python
def compute_path_metrics(G, path: list[str]) -> dict:
    """计算路径指标。"""
```

## 第一阶段先实现什么

先不要一上来写复杂算法。零基础最稳的顺序是：

1. BFS：先能找出一条最短跳数路径。
2. Dijkstra：再考虑边权重，找总代价最低路径。
3. 自定义权重算法：把损耗、延迟、串扰加进总代价。
4. Floyd：只用于 8x8、16x16 的小规模对比，不作为大规模主算法。
5. KNN：最后再做，用来筛选路径质量。

## 方法名必须统一

`find_path()` 的 `method` 参数只使用这些名字：

```text
bfs
dijkstra
floyd
weighted_benes
```

不要使用 `shortest`、`my_algorithm`、`best_path` 这类临时名字。

## 路径返回格式

必须返回节点列表：

```python
["I3", "S1_1", "S2_1", "S3_1", "S4_3", "S5_3", "O6"]
```

不要返回字符串：

```python
"I3 -> S1_1 -> O6"
```

字符串可以在展示时再转换，算法内部必须用列表。

## 指标返回格式

`compute_path_metrics()` 至少返回：

```python
{
    "length": 6,
    "loss": 1.2,
    "delay": 5.0,
    "crosstalk": 0.3,
    "cross_count": 2,
    "cost": 9.0,
}
```

字段名不要随便改，因为实验和可视化会读取这些名字。

## 默认代价公式

没有真实光芯片数据时，先用模拟公式：

```text
cost = length + loss + 0.5 * delay + crosstalk
```

以后如果老师给了真实参数，只替换每条边的 `loss`、`delay`、`crosstalk` 或公式系数，不要改函数接口。

## weighted_benes 的含义

`weighted_benes` 不是一个完全新发明的神秘算法。第一阶段可以理解为：

```text
weighted_benes = 使用 Benes 光网络代价模型的 Dijkstra
```

也就是说，它还是找最小总代价路径，但对交叉状态、损耗、延迟、串扰给更高惩罚。

## 你不要做的事

1. 不要修改 `build_benes_network()` 的函数名。
2. 不要在算法里重新生成拓扑。
3. 不要把路径画图逻辑写进 `routing.py`。
4. 不要为了某个例子写死 `I3 -> O6` 的答案。
5. 不要让 `find_path()` 返回不合法路径。

## 交付标准

至少要能跑通：

```python
G = build_benes_network(8)
path = find_path(G, "I3", "O6", method="bfs")
metrics = compute_path_metrics(G, path)
```

其中：

```text
path[0] == "I3"
path[-1] == "O6"
metrics 中包含 length、loss、delay、cost
```
