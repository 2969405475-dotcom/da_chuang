# Agent 协作约束

本文件是给 Codex、ChatGPT、Copilot 或其他 Agent 使用的总规则。任何 Agent 修改本仓库前，必须先阅读本文件。

## 项目目标

本项目研究 Benes 光交换网络中的最短路径与连接规划算法。近期目标是做一个可运行、可解释、可展示的 Python 仿真项目，而不是一次性复现完整光芯片物理实验。

## 禁止事项

1. 不要把所有代码写进一个 `main.py`。
2. 不要随意修改别人负责模块的公开函数名。
3. 不要在没有说明原因的情况下删除已有文件。
4. 不要把实验输出图片、CSV、大型缓存提交到核心代码目录。
5. 不要在未沟通的情况下修改 `AGENTS.md`、`README.md` 中的接口约定。
6. 不要为了让测试通过而降低测试要求。

## 模块边界

A 同学负责拓扑建模：

- 可以修改：`src/benes/topology.py`、`tests/test_topology.py`
- 不应修改：`src/benes/routing.py`、`src/benes/metrics.py` 的公开接口

B 同学负责路径算法：

- 可以修改：`src/benes/routing.py`、`src/benes/metrics.py`、`tests/test_routing.py`、`tests/test_metrics.py`
- 不应修改：`src/benes/topology.py` 的公开接口

C 同学负责可视化和实验：

- 可以修改：`src/benes/visualize.py`、`src/benes/experiments.py`、`examples/`
- 不应修改：`topology.py`、`routing.py`、`metrics.py` 的核心函数名

## 必须保持稳定的接口

后续代码必须优先兼容这些函数：

```python
def build_benes_network(N: int):
    """生成 N x N Benes 网络，返回 NetworkX 图。"""
```

```python
def find_path(G, src: str, dst: str, method: str = "bfs", weight: str | None = None) -> list[str]:
    """从 src 到 dst 找路径，返回节点名称列表。"""
```

```python
def compute_path_metrics(G, path: list[str]) -> dict:
    """计算路径长度、损耗、延迟、串扰、总代价等指标。"""
```

```python
def draw_benes_network(G, path: list[str] | None = None, save_path: str | None = None) -> None:
    """绘制 Benes 网络，可选高亮路径。"""
```

## 节点命名规则

必须统一使用以下命名：

- 输入端口：`I0`, `I1`, ..., `I{N-1}`
- 输出端口：`O0`, `O1`, ..., `O{N-1}`
- 交换单元：`S{stage}_{index}`

示例：

```text
I3 -> S1_1 -> S2_1 -> S3_1 -> S4_3 -> S5_3 -> O6
```

## 推荐开发流程

1. 先写或更新对应测试。
2. 再实现代码。
3. 本地运行 `pytest`。
4. 生成必要的示例结果。
5. 在 Pull Request 中说明改了哪些文件、如何验证。

## Agent 提示词建议

给 Agent 派任务时，建议这样写：

```text
请先阅读 AGENTS.md，只修改你负责的文件。
不要修改其他模块的公开函数名。
实现后运行 pytest，并说明通过了哪些测试。
```

## 当前默认技术栈

- Python
- NetworkX
- NumPy
- Pandas
- Matplotlib
- pytest

KNN 或机器学习部分后续可以加入 scikit-learn，但第一阶段不强制。
