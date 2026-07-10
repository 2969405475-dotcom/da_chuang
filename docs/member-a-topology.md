# A 同学约束文件：拓扑建模

本文件给负责 Benes 网络拓扑建模的同学使用。

## 你的目标

实现 Benes 光交换网络的结构生成。你只负责“网络长什么样”，不负责“怎么找路径”和“怎么画图”。

## 你主要负责的文件

```text
src/benes/topology.py
tests/test_topology.py
```

## 你必须提供的函数

```python
def build_benes_network(N: int):
    """生成 N x N Benes 网络，返回 NetworkX DiGraph。"""
```

## 必须支持的规模

第一阶段：

```text
N = 8
```

第二阶段：

```text
N = 16, 32, 64, 128
```

## 8x8 Benes 的基本要求

8x8 Benes 网络必须满足：

```text
级数：5
每级交换单元数：4
交换单元总数：20
输入端口：I0 到 I7
输出端口：O0 到 O7
交换单元：S1_0 到 S5_3
```

## 节点命名必须统一

不要自己发明别的名字，例如 `input_0`、`switch1`、`out0` 都不要用。

统一使用：

```text
输入端口：I0, I1, I2 ...
输出端口：O0, O1, O2 ...
交换单元：S{stage}_{index}
```

例如：

```text
S1_0 表示第 1 级第 0 个交换单元
S5_3 表示第 5 级第 3 个交换单元
```

## 图结构建议

建议使用：

```python
networkx.DiGraph
```

每个节点建议保存这些属性：

```python
kind: "input" | "switch" | "output"
stage: int
index: int
```

每条边建议保存这些属性：

```python
loss: float
delay: float
cost: float
action: "straight" | "cross" | "terminal"
```

这些边属性给 B 同学的算法模块使用，所以尽量不要改字段名。

## 你不要做的事

1. 不要实现 BFS、Dijkstra、KNN。
2. 不要写可视化代码。
3. 不要修改 `routing.py`、`metrics.py` 的函数名。
4. 不要为了某个路径强行写死连接结果。

## 交付标准

你完成后，至少应该能让下面事情成立：

```python
G = build_benes_network(8)
```

并且：

```text
G 中有 8 个输入端口
G 中有 8 个输出端口
G 中有 20 个交换单元
从任意 I 输入端口，理论上能连到若干后续交换单元
```
