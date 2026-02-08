---
title: "Understanding the Core Mechanisms of Prometheus in One Article"
Categories: ["Observability"]
Description: ''
DisableComments: false
Tags: []
date: 2026-02-08 21:44:06
summary: "I recently joined a NeoCloud company as an Observability Engineer
  and had the opportunity to participate in building a monitoring system from scratch.
  This led me to systematically learn about Prometheus. This article is aimed at those
  who have a foundational understanding of K8s but are encountering Prometheus for
  the first time. It explains core concepts such as the Pull model, time series storage,
  and the Exporter mechanism, helping you establish a complete cognitive framework
  before you start using it formally."

---

# Background

Recently, I joined a Finnish NeoCloud company as an observability engineer. As the business rapidly expands, building a comprehensive observability system (Logs / Metrics / Tracing) for the cloud service platform from scratch has become a priority, giving me the chance to be systematically involved.

In my previous work, I mainly acted as a user who directly consumed ready-made Grafana/Datadog dashboards, and my understanding of Prometheus was limited to "it collects metrics from nodes and applications." This time, by taking part in setting up the monitoring system, I gained a deeper understanding of Prometheus's core mechanisms and compiled this study log. I hope it can help fellow learners of Prometheus.

This article is aimed at those who **have a foundation in Kubernetes but are encountering Prometheus for the first time**. You might have pondered these questions during your study:

- How does Prometheus work?
- Why does Prometheus use pull instead of push?
- What is an exporter? When should `/metrics` be built in again?

I hope this article helps you establish a complete mental map before you officially "use Prometheus."

# Core Mechanics of Prometheus

If I had to describe the core operation of Prometheus in one sentence, it would be:

"Periodically scrape a snapshot of current metrics from targets and store them in its own time series database (TSDB)."

![architecture](images/architecture.png)

As shown in the diagram, the working principle of Prometheus is to periodically request the /metrics endpoint exposed by target services and store the specifically formatted data they retrieve into its own TSDB. It is noteworthy that Prometheus's pull behavior does not distinguish between static and dynamic metrics, which means even if a metric theoretically never changes, it will still be repeatedly scraped each time.

Once stored in the database, this data becomes individual "time series." What is a time series? Simply put:

> ***A metric + a set of labels = an independent time series***

For the same metric, if the composition of labels differs, then it will generate another time series.If you have a service `user-service` that exposes a metric `http_requests_total` to record the total number of HTTP requests, and this service has multiple endpoints (`/api/users`, `/api/orders`), with each endpoint having different request methods (GET, POST), Prometheus will create a separate time series for each combination:

```jsx
http_requests_total{method="GET", path="/api/users"}   → Time Series 1
http_requests_total{method="POST", path="/api/users"}  → Time Series 2
http_requests_total{method="GET", path="/api/orders"}  → Time Series 3
```

For example, for time series 1 `http_requests_total{method="GET", path="/api/users"}`, it will store a series of data points over time:

```text
┌─────────────┬───────┐
│  Timestamp   │  Value│
├─────────────┼───────┤
│ 10:00:00    │ 1523  │
│ 10:00:15    │ 1537  │  ← Reads the latest data from the /metrics endpoint every 15 seconds
│ 10:00:30    │ 1562  │
│ 10:00:45    │ 1580  │
└─────────────┴───────┘
```

So, how can you use these data points, which are metrics stored in Prometheus?

For metrics in time series databases, Prometheus provides **PromQL (Prometheus Query Language)** to query these time series data. PromQL is a functional query language specifically designed for time series data, and it is gradually becoming an industry standard, similar to the role of SQL in relational databases (such as MySQL).

Here's a simple example. If we want to check the CPU usage of a particular pod:

```jsx
rate(container_cpu_usage_seconds_total{pod="my-app"}[5m])
```

This query means: calculate the rate of...Calculate the CPU usage growth rate in `my-app` Pods over the past 5 minutes.

In practice, we usually don't write PromQL directly. Instead, we use visualization tools like Grafana to connect with Prometheus as a data source, use PromQL to query data on the Dashboard, render it into various charts or dashboards, or set up alert rules (sending notifications when a metric exceeds a threshold).

# Why Prometheus Chooses Pull Instead of Push

As mentioned earlier, Prometheus "periodically pulls data," which might seem confusing to some. Most monitoring systems adopt a method where services actively push data to the monitoring center, which seems more intuitive. So why does Prometheus choose the opposite approach?

There are two main reasons for this:

## 1. The Monitoring System Retains Control

In a pull model, Prometheus controls all data collection activities:

- **When to pull**: All scrape intervals are managed collectively in the Prometheus configuration file.
- **What targets to pull from**: The operations team centrally decides which services to monitor.
- **Pull timeout**: Prevents being hindered by slow-responding services.

```jsx
scrape_configs:
  - job_name: 'user-service'
    scrape_interval: 15s
  - job_name: 'order-service'
    scrape_interval: 30s
```

This allows operations to flexibly adjust:
- Critical services are collected every 15 seconds.
- Peripheral services are collected every minute.
- Or temporarily increase the collection frequency of a particular service.

**More importantly, it avoids "flood attacks":**

No matter what happens with the target application (bugs, attacks, misconfigurations), Prometheus maintains its rhythm—for example, pulling once every 15 seconds and moving on. This eliminates the chance of applications crazily pushing metrics and overwhelming the monitoring system.

In contrast, a push model carries such risks:

- Collection frequencies are spread across the code of each application, requiring changes in numerous services to adjust them uniformly.
- If an application starts pushing 100,000 metrics per second, the monitoring server has to bear the load.

## 2. Clearer Failure Semantics

In a pull model, if pulling fails, the reason is straightforward:

- Either the target service is down.
- Or the network is unreachable.

In a push model, the reason for "not receiving data" is ambiguous:

- Is the service down?
- Is the service running normally but just has no new data?To Push or Not to Push?
- Did network issues cause the push to fail?

For example, consider an application that only sends `http_requests_total` when it receives an HTTP request. At 3 a.m., no one accesses it, so naturally, it doesn't send any data. How can the monitoring system differentiate between "no data due to normal conditions" and "service is down"?

The Pull model doesn't have this issue. Prometheus regularly asks, "Are you still alive? Give me the latest data," and if it can't retrieve anything, it knows there's a problem immediately.

# Two Methods of Exposing Metrics

At this point, you may wonder: Since Prometheus only recognizes the `/metrics` endpoint, who exactly provides this endpoint?
In my work experience, I've found that two distinct models exist in the world of Prometheus.

### Model A: Standalone Exporter (Sidecar / Daemon)

The first model involves deploying a **standalone Exporter process**. It works as follows:

```text
[ Monitored Object ]
       ↓ Query/Read
   [ Exporter ]
       ↓ /metrics
   [ Prometheus ]
```

The Exporter's role is straightforward:

1. Connect to the monitored object (MySQL, GPU, operating system, etc.)
2. Retrieve raw data (execute SQL, read system files, call driver APIs)
3. Translate it into Prometheus format
4. Expose the `/metrics` endpoint

**Typical Examples:**

- **node-exporter**: Collects operating system metrics (CPU, memory, disk)
- **dcgm-exporter**: Collects NVIDIA GPU metrics
- **mysql-exporter**: Collects MySQL database metrics
- **blackbox-exporter**: Proactively probes the availability of target services

These are essentially small Services, and while each Exporter might have a completely different implementation—node-exporter reads the `/proc` filesystem, mysql-exporter executes SQL queries, dcgm-exporter calls NVIDIA's C libraries—their goal is the same: **collect status and provide a `/metrics` endpoint**.

### Model B: Built-in /metrics in Application

The second model is to directly integrate metric exposure capabilities into the application's code:

```text
[ Application Process ]
   ├── Business Logic
   ├── Metrics Collection Logic
   └── /metrics Endpoint
```

In this model, the application records metrics while processing business logic, and then exposes a **`/metrics`** HTTP endpoint for Prometheus to scrape. Modern programming languages have official Prometheus client libraries (Go, Java, Python), which make integration very simple.

Typical examples include:

- **Kubernetes apiserver**: Built-in performance metrics for all API calls
- **etcd**: Logs various metrics related to Raft consensus and storage
- **Prometheus itself**: Monitors its own scraping performance and storage usage
- **Most cloud-native microservices**

For these applications, **the application itself is the exporter**.

### Why Do We Still Need Independent Exporters?

This might lead you to another question: if built-in `/metrics` is so convenient, why deploy an exporter separately?

I also wondered about this when I first encountered Prometheus, and the answer is quite simple:

**Because some monitoring targets are applications you cannot modify.**

| Monitoring Target | Why Can't It Be Built-in? |
| --- | --- |
| Operating System (Linux) | You can't modify the kernel code |
| GPU Hardware | You can't modify NVIDIA drivers |
| Network Equipment | You can't modify switch firmware |
| MySQL / Redis | You don't want to intrude into third-party software code |
| Legacy Systems | Old projects from 5 years ago, no one dares to touch them |

In these scenarios, an exporter becomes the bridge between you and those "unmodifiable" objects.

### How Do You Decide Which Mode to Use?

In practice, I've summarized two criteria for deciding:

**Q1: Can I modify the code of the target being monitored?**

If you can modify it, then you can directly integrate `/metrics` because it is the lowest cost option, the easiest to maintain, and highly customizable. If you can't modify it, then you can look into whether there is an existing open-source exporter tool that fits your needs, or you can customize your own exporter.

**Q2: Is the collection logic highly general?**

If the collection logic is general, for example, performance monitoring for nodes where all Linux machines need CPU/memory monitoring, then we can prioritize using an existing exporter, like node-exporter, which is a more mature and stable solution.However, if metrics are specific to the business, such as "user payment success rate," we need to customize and embed them into the application.

In summary, **embed whenever possible, externalize only if not possible**. If you're developing a new microservice, the optimal solution is to expose metrics directly in the code using the Prometheus client library. On the other hand, if you need to monitor MySQL, GPU, or the operating system, deploying the corresponding Exporter is the correct choice.

For Prometheus, it doesn't matter who provides the `/metrics`, as long as it can retrieve data in the correct format. This design allows Prometheus to monitor both modern cloud-native applications and traditional infrastructure, demonstrating its robust adaptability. This adaptability is why it remains the de facto standard in the monitoring field even after many years.

# Summary

In this article, we explored the core working mechanisms of Prometheus, understanding how it periodically collects data from `/metrics` interfaces using a Pull model, stores this data as time series, and offers query capabilities through PromQL.

We also grasped why Prometheus prefers Pull over Push—it allows the monitoring system to maintain control, preventing it from being overwhelmed by problematic applications; failure semantics are clearer, allowing immediate assessment of service status. These design choices may seem "counterintuitive," but they are grounded in solid engineering considerations.

Finally, we understood the two approaches to exposing metrics: embedding `/metrics` if you can modify the code, or using an Exporter as a bridge if you cannot. This flexible design enables Prometheus to monitor both modern cloud-native applications and traditional infrastructure.

Returning to the issue mentioned at the beginning: before officially using Prometheus, I hope you can construct a comprehensive mental map of its structure. By understanding these core mechanisms, you won't treat Prometheus as a "black box" but will know what it's doing, why it does it, and how to leverage it effectively.

As engineers, we must always remember: **tools exist to solve real business problems**. Prometheus is not perfect; it has its suitable scenarios and limitations. However, by understanding its principles, we can make correct technical choices and build a monitoring system truly fit for business needs.

I hope this article helps you avoid some pitfalls when setting up a monitoring system.