---
title: "一文读懂 Prometheus 核心机制"
date: 2026-02-08T23:44:06+02:00
Description: ""
Tags: []
Categories: ["Observability"]
DisableComments: false
summary: "最近作为可观测性工程师加入了一家 NeoCloud 公司，有幸参与从 0 到 1 搭建监控体系，便系统性地学习了 Prometheus。本文面向有 K8s 基础但第一次接触 Prometheus 的同学，讲解 Pull 模式、时间序列存储、Exporter 机制等核心概念，帮助你在正式使用前建立完整的认知框架。"
---

# 背景

最近我作为可观测性工程师加入了芬兰一家 NeoCloud 公司开始工作。随着业务规模的快速增长，为云服务平台从 0 到 1 构建完整的可观测性体系（Logs / Metrics / Tracing）被提上了日程，而我也因此有机会系统性地参与其中。

在我以往的工作中，我更多的是作为使用者直接消费现成的Grafana/Datadog Dashboard，对Prometheus的理解也仅停留在“它会收集节点和应用的指标”这一层。这次借着需要参与搭建监控体系的机会，让我深入理解了 Prometheus 的核心机制，并总结出了这篇学习日志。希望可以帮助到同样在学习 Prometheus 的同学。

本文面向**有 Kubernetes 基础、但第一次接触 Prometheus** 的同学，相信你们在学习过程中也产生过这样的问题：

- Prometheus 是到底是怎么工作的？
- Prometheus 为什么选择 pull 而不是 push？
- exporter 到底是什么？什么时候又该内置 /metrics？

希望这篇文章能帮助你在正式“用 Prometheus 之前”，先在脑子里建立一张完整的结构图。

# Prometheus 核心机制

如果要用一句话来描述 Prometheus 的核心工作方式，那就是：

“定期去目标（targets）上拉取（scrape）一份当前指标快照，然后存进自己的时序数据库（TSDB）。”

![architecture](images/architecture.png)

正如图中所示, Prometheus的工作原理就是周期性的请求目标服务暴露的 /metrics 接口，并将他们拿到的特定格式的数据存入自身的 TSDB 当中。这里值得注意的是，Prometheus 本身的 Pull 行为是不区分静态/动态指标的，这也意味着即使某个指标理论上永远不改变，它也会在每次 scrape 时重复拉取。

在存入数据库之后，这些数据就会变成一条条“时间线（Time Series）”。什么是时间线？简单来说就是：

> ***一个指标 + 一组标签 = 一个独立的时间线***
> 

对于同一个指标，如果标签的组成不同，那它就会生成另一个时间线。例如，你有一个服务 `user-service` 暴露了一个指标 `http_requests_total`，用来记录 HTTP 请求总数。但这个服务有多个接口（`/api/users`、`/api/orders`），每个接口又有不同的请求方法（GET、POST），那么 Prometheus 实际上会为每一种组合创建一条独立的时间线：

```jsx
http_requests_total{method="GET", path="/api/users"}   → 时间线 1
http_requests_total{method="POST", path="/api/users"}  → 时间线 2
http_requests_total{method="GET", path="/api/orders"}  → 时间线 3
```

例如，对于时间线 1 `http_requests_total{method="GET", path="/api/users"}` ，它会随时间存入这样的一系列数据点：

```text
┌─────────────┬───────┐
│  时间戳      │  值   │
├─────────────┼───────┤
│ 10:00:00    │ 1523  │
│ 10:00:15    │ 1537  │  ← 每隔15秒读取一次/metrics接口最新的数据
│ 10:00:30    │ 1562  │
│ 10:00:45    │ 1580  │
└─────────────┴───────┘
```

那么，存入 Prometheus 的这些数据点，也就是 metrics，该怎么使用呢？

对于时序数据库中的 metrics，Prometheus 提供了 **PromQL（Prometheus Query Language）** 来查询这些时序数据。PromQL 是一种函数式查询语言，专门为时序数据设计，现在也逐渐成为行业标准，类似于 SQL 在关系型数据库（例如 MySQL）领域的生态位。

举个简单的例子，如果我们想查看某个 Pod 的 CPU 使用率：

```jsx
rate(container_cpu_usage_seconds_total{pod="my-app"}[5m])
```

这条查询的意思是：计算过去 5 分钟内，名为 `my-app` 的 Pod 的 CPU 使用秒数的增长率。

而在实际工作中，我们通常不会直接写 PromQL，而是通过 Grafana 这样的可视化工具来接入Prometheus作为数据源，在Dashboard 上用 PromQL查询数据，将数据渲染成各种图表，仪表盘，或者配置告警规则（当某个指标超过阈值时发送通知）。

# 为什么 Prometheus 选择 Pull 而不是 Push

前面提到 Prometheus 会"周期性地去拉取数据"，这可能让你有些疑惑——大多数监控系统会使用服务主动推送数据给监控中心方式，这也更符合直觉，但为什么 Prometheus 反其道而行？

这里主要是有两个核心考虑：

## 1. 监控系统掌握主动权

Pull 模式下，Prometheus 控制着所有采集行为：

- **什么时候拉取**：所有 scrape interval 都在 Prometheus 配置文件里统一管理
- **拉取哪些目标**：运维团队集中决定监控哪些服务
- **拉取超时时间**：避免被慢响应的服务拖垮

```jsx
scrape_configs:
  - job_name: 'user-service'
    scrape_interval: 15s
  - job_name: 'order-service'
    scrape_interval: 30s
```

运维可以灵活调整：
- 核心服务 15 秒采集一次
- 边缘服务 1 分钟采集一次
- 或者临时提高某个服务的采集频率

**更重要的是，这避免了被"洪水攻击"**：

无论目标应用发生什么（bug、被攻击、配置错误），Prometheus 永远按自己的节奏来——例如每 15 秒拉一次，拉完就走。杜绝了应用程序疯狂推送指标打爆监控系统的可能性。

对比而言，Push 模式下就会存在这样的风险：

- 采集频率分散在每个应用的代码里，想统一调整得改几十个服务
- 如果某个应用开始每秒推送 10 万条指标，监控服务器就得硬扛着

## 2. 失败语义更清晰

Pull 模式下，如果拉取失败，原因很明确：

- 要么目标服务挂了
- 要么网络不通

而 Push 模式下，"没收到数据"的原因是模糊的：

- 服务挂了？
- 服务正常运行，但刚好没有新数据要推送？
- 网络问题导致推送失败？

举个例子：一个只在收到 HTTP 请求时才推送 `http_requests_total` 的应用，凌晨 3 点没人访问，自然就不推送数据。监控系统怎么区分这是"正常的没数据"还是"服务挂了"？

而 Pull 模式就不存在这个问题，Prometheus 会定期去问"你还活着吗？给我最新数据"，拉不到立刻就知道有问题。

# 两种 metrics 暴露方式

到这里，细心的你可能会产生一个疑问：既然 Prometheus 只认 `/metrics` 接口，那这个接口到底由谁来提供？
在实际工作中，我发现 Prometheus 的世界里存在着两种截然不同的模式。

### 模式 A：独立 Exporter（边车 / 守护进程）

第一种模式是部署一个**独立运行的 Exporter 进程**。它的工作流程是这样的：

```text
[ 被监控对象 ]
       ↓ 查询/读取
   [ Exporter ]
       ↓ /metrics
   [ Prometheus ]
```

Exporter 做的事情很简单：

1. 连接到被监控对象（MySQL、GPU、操作系统...）
2. 获取原始数据（执行 SQL、读取系统文件、调用驱动 API）
3. 翻译成 Prometheus 格式
4. 暴露 `/metrics` 接口

**典型例子：**

- **node-exporter**：采集操作系统指标（CPU、内存、磁盘）
- **dcgm-exporter**：采集 NVIDIA GPU 指标
- **mysql-exporter**：采集 MySQL 数据库指标
- **blackbox-exporter**：主动探测目标服务的可用性

他们本质上就是一个小型的 Service，每个 Exporter 的实现逻辑可能完全不同——node-exporter 读 `/proc` 文件系统，mysql-exporter 执行 SQL 查询，dcgm-exporter 调用 NVIDIA 的 C 库——但它们的目标一致：**收集状态，提供 `/metrics` 接口**。

### 模式 B：应用内置 /metrics

第二种模式是在应用代码里直接集成指标暴露能力：

```text
[ 应用进程 ]
   ├── 业务逻辑
   ├── 指标采集逻辑
   └── /metrics 端点
```

这种模式下，应用在处理业务逻辑的同时记录指标，然后暴露一个 **`/metrics`** HTTP 端点供 Prometheus 拉取。现代编程语言都有官方的 Prometheus client library（Go、Java、Python），集成起来非常简单。

典型的例子：

- **Kubernetes apiserver**：内置了所有 API 调用的性能指标
- **etcd**：记录了 Raft 共识和存储的各项指标
- **Prometheus 自身**：监控自己的抓取性能和存储使用情况
- **大多数云原生微服务**

对于这些应用来说，**应用本身就是 exporter**。

### 为什么还需要独立的 Exporter？

在这里，你可能又会产生新的疑问了，既然内置 `/metrics` 这么方便，为什么还要单独部署 Exporter 呢？

这个问题在我刚接触 Prometheus 时也困扰过我，而其实答案很简单：

**因为有些监控对象根本不是你能改代码的应用**。

| 被监控对象 | 为什么不能内置 |
| --- | --- |
| 操作系统（Linux） | 你不能改内核代码 |
| GPU 硬件 | 你不能改 NVIDIA 驱动 |
| 网络设备 | 你不能改交换机固件 |
| MySQL / Redis | 不想侵入第三方软件的代码 |
| 遗留系统 | 5 年前的老项目，没人敢动 |

这些场景下，Exporter 就成了你和这些"不可改"对象之间的桥梁。

### 怎么判断该用哪种模式？

在实际工作中，我总结了两个判断标准，

**Q1：我能改被监控对象的代码吗？**

如果能改，那么我们就可以直接内置 `/metrics` ，因为它成本最低，且维护最简单，可定制化程度也高。如果不能改，我们就可以选择看看针对你的需求有没有成熟的 exporter 开源工具，或者是自己定制化 exporter。

**Q2：采集逻辑是否高度通用？**

如果采集逻辑通用例如对于 node 的性能监控，所有 Linux 机器都需要 CPU/内存监控，所以我们可以优先考虑使用现成的 Exporter，如 node-exporter，更加成熟稳定的解决方案。但是如果属于业务私有的指标，比如"用户支付成功率"这种，我们就需要将它定制化内置到应用里。

所以总得来说，**能内置就内置，不能内置才外置**。如果你在开发一个新的微服务，直接用 Prometheus client library 在代码里暴露指标是最优解。而如果你要监控 MySQL、GPU、或者操作系统，部署对应的 Exporter 才是正确的选择。

对 Prometheus 来说，它并不关心 `/metrics` 是谁提供的——只要能拉到符合格式的数据就行。这种设计让 Prometheus 既能监控现代云原生应用，也能监控传统基础设施，展现了极强的适应性。这也是为什么它能在这么多年后依然是监控领域的事实标准。

# 总结

在这篇文章里，我们从 Prometheus 的核心工作机制出发，理解了它是如何通过 Pull 模式定期抓取 `/metrics` 接口，将数据存储为时间序列，并通过 PromQL 提供查询能力的。

我们也明白了 Prometheus 为什么选择 Pull 而不是 Push——监控系统掌握主动权，避免被异常应用拖垮；失败语义更清晰，能立刻判断服务状态。这些设计选择看似"反直觉"，但背后都有扎实的工程考量。

最后，我们也理解了指标暴露的两种方式：如果能改代码就内置 `/metrics`，如果不能改就用 Exporter 做桥梁。这种灵活的设计让 Prometheus 既能监控现代云原生应用，也能监控传统基础设施。

回到开头提到的问题：在正式使用 Prometheus 之前，我希望你能先在脑子里建立一张完整的结构图。理解了这些核心机制，你就不会把 Prometheus 当成一个"黑盒"，而是知道它在做什么、为什么这么做、以及该怎么用好它。

我认为作为工程师，我们要时刻记住：**工具是为了解决实际业务问题而存在的**。Prometheus 并不完美，它有自己的适用场景和局限性。但正是因为理解了它的工作原理，我们才能在实际工作中做出正确的技术选型，构建出真正适合业务需求的监控体系。

希望这篇文章能帮助你在搭建监控系统时，少走一些弯路。
