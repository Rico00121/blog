---
title: "When Two Health Checks See Different GPU States: An Investigation, Fix, and Reflection on an Architecture Problem"
date: 2026-03-31T00:00:00+03:00
Description: ""
Tags: []
Categories: ["GPU Cluster"]
summary: "This article records a GPU health-check inconsistency in which the Passive Health Check and `dcgm-exporter` saw different GPU states on the same node. The root cause was that the two containers each ran their own embedded `nv-hostengine`, and the fix was to deploy a node-level Host Engine with `internalTrafficPolicy: Local` so every component shared the same state view and control entry point."
DisableComments: false
draft: false
---

## Background

For some time recently, I have been responsible for building the health check mechanism for our company's GPU cluster. Because we use Kubernetes to manage the GPU cluster in a unified way, we designed a **Passive Health Check Pod** that runs as a DaemonSet. It is deployed on every GPU node and actively probes node availability at a high frequency.

At the same time, we also introduced NVIDIA's official `dcgm-exporter` as the node-level GPU monitoring component, exposing GPU metrics to Prometheus.

For the working principles of DCGM, what `nv-hostengine` is, and the relationships between the components, you can refer to [the article I wrote earlier](https://rico00121.github.io/blog/en/post/dcgm/).

## What Triggered It: A Brief Alert State Mismatch

The trigger for the problem was a brief false alert event.

When our passive health check container executed a DCGM health check, it found an unstable current anomaly on a GPU of one node. However, when we checked the data from `dcgm-exporter` at the same time, the GPU on that node still appeared healthy.

Two components, the same node, but completely opposite conclusions. We quickly realized that this was **a problem of inconsistent container views**, not just an ordinary false positive.

After restarting the health check container, the anomaly disappeared. Obviously, we could solve it by resetting the DCGM instance used in the health check each time so the cache would be refreshed. But I realized that this would only treat the symptom. The real root cause had to be deeper.

## Deeper Investigation: The Root Cause

I spent some time studying the underlying working principles of DCGM in more depth, and eventually found the root cause of the problem.

The core issue was this: **the two Pods were each running their own `nv-hostengine` instance**.

Under its default configuration, `dcgm-exporter` starts an Embedded Host Engine inside the container rather than connecting to a node-level Host Engine. Our own Passive Health Check container did the same thing. It also embedded its own `nv-hostengine`.

This meant that there were **two separate data collection processes** on the same node. Each one maintained its own GPU state cache, their sampling times were different, their cache contents were different, and naturally the conclusions they produced could also be different.

As shown below (Current Architecture):

![Current Architecture](images/current-architecture.png)

This architecture had the following concrete problems:

**1. Internal Engine Conflict**  
Each container started its own embedded `nv-hostengine` instead of sharing a unified instance at the node layer. This meant redundant resource waste and multiple GPU control points.

**2. Inaccurate Reporting**  
The GPU state each container saw depended on its **own internal** Host Engine instance rather than the real state of the node. Once the sampling timeline or cache state of the two instances diverged, the reported results could conflict with each other.

This point is also mentioned in the official Nvidia documentation for `dcgm-exporter`:

> Since dcgm-exporter starts nv-hostengine as an embedded process (for collecting metrics), appropriate configuration options should be used if dcgm-exporter is run on systems (such as NVIDIA DGX) that have DCGM (or rather nv-hostengine) running.

Obviously, we needed to make some changes to the current deployment architecture. We needed to use one independent `nv-hostengine` to ensure a unified state view and a unified control entry point.

![Target Architecture](images/shared-hostengine-target.png)

## Improvement Strategy and Technical Choices

### Why not simply merge everything into one container?

The most intuitive solution would be to merge the two containers into one and let them share the same Host Engine. But that would not work, for two reasons:

- `dcgm-exporter` is an upstream open-source project, and we should not modify its internal implementation
- coupling the monitoring collection logic and the business health check logic into one container would make responsibilities unclear and lifecycle management more complex

### How should `nv-hostengine` be deployed independently?

Once it was clear that `nv-hostengine` needed to be separated out, there were two concrete ways to do it.

**Option 1: Run the `nv-hostengine` process directly at the VM / Bare Metal layer**

This is the approach mentioned in the NVIDIA documentation: start an `nv-hostengine` daemon directly at the node operating system level, and let all clients inside containers connect to it over the network. This is the closest to a “node-native” approach, and in theory also the most stable.

**Option 2: Package `nv-hostengine` as an independent container (DaemonSet)**

We eventually chose this option. The reasons were:

- **Unified management**: consistent with the other components, with lifecycle, configuration, and logs all managed through Kubernetes
- **Less invasive**: no need to manually install and configure `nv-hostengine` on the operating system of every GPU node
- **Better troubleshooting**: future engineers can directly `kubectl exec` into the container for debugging, using the familiar cloud-native toolchain instead of logging into the host machine

### Design discussion: three containers in one Pod, or three separate Pods?

We considered two solutions.

**Solution A: Put three containers in the same Pod (`nv-hostengine` + `dcgm-exporter` + Passive Health Check)**

The advantage is that the containers can communicate through `localhost`, which naturally guarantees that the traffic does not cross nodes. But the downside is that the Pod becomes coarse-grained and the lifecycle becomes tightly coupled. Restarting any one component affects the whole Pod. For example, if we keep maintaining and updating our own health check component in the future, every update would affect the other components too.

**Solution B: Three separate Pods communicating through a Service**

This gives much clearer separation of responsibilities and independent lifecycles. But it introduces a key problem: **sticky sessions for Service communication**.

We needed to ensure that each Passive Health Check Pod and each `dcgm-exporter` Pod could only connect to the `nv-hostengine` running on the **same node**, rather than being load-balanced by a Kubernetes Service to an instance on another node.

We ultimately chose **Solution B**, and solved the stickiness problem in the following way.

### How to implement node-local Service stickiness?

The key to solving cross-node routing was a Kubernetes Service field: `internalTrafficPolicy: Local`.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nvidia-dcgm
  namespace: monitoring
  labels:
    app.kubernetes.io/name: nvidia-dcgm
    app.kubernetes.io/component: dcgm
spec:
  internalTrafficPolicy: Local
  selector:
    app.kubernetes.io/name: nvidia-dcgm
    app.kubernetes.io/component: dcgm
  ports:
    - name: dcgm
      port: 5555
      protocol: TCP
  type: ClusterIP
```

The meaning of `internalTrafficPolicy: Local` is that when a Pod inside the cluster accesses this Service, `kube-proxy` only forwards the traffic to backend Pods that are on the **same node as the caller**. If there is no matching backend Pod on that node, the request fails directly instead of being load-balanced to another node.

This behavior is ideal for our case. We already ensure through DaemonSet that every node has one `nv-hostengine` Pod, so the “no backend on this node” case does not happen. When `dcgm-exporter` and the Passive Health Check Pod access the `nvidia-dcgm` Service, they naturally connect only to the Host Engine on the same node.

Compared with a Headless Service, the advantage of this solution is that the client does not need to be aware of specific Pod IPs. It can simply use the Service DNS name, `nvidia-dcgm.monitoring.svc.cluster.local:5555`, and the whole mechanism remains transparent to upper-layer applications.

## The Final Architecture

As shown in the architecture diagram (Final Architecture), the target architecture after the change is as follows:

![Final Architecture](images/final-architecture.png)

1. Run **one unified `nv-hostengine` (DCGM Host Engine)** on every GPU node as an independent DaemonSet Pod, acting as the node-level server.
2. Run `dcgm-exporter` and Passive Health Check as independent DaemonSet Pods as well, acting as clients that connect to the node-local Host Engine through the `nvidia-dcgm` Service.
3. All components derive their GPU state view from the same data entry point.

## The Value of This Change

On the surface, this architecture adjustment looks like a “split”: taking previously embedded pieces and separating them out. But the value it brings is much greater than that.

**First, it solved the most fundamental problem: the data view became unified.** All components share the same Host Engine instance, and their sampling time and cache content are completely aligned. The conflicting alerts in which “the health check says there is a problem, but the exporter says there is not” disappeared at the root. On-call engineers could finally trust the monitoring data with confidence.

**At the same time, duplicated resource overhead was also optimized.** In the old design, the two embedded Host Engines each polled the GPU independently, which was a kind of hidden resource waste. Now the system converges to a single instance, making the collection path clearer and the overhead lower.

**From a best-practice perspective, this is also the deployment model explicitly recommended by NVIDIA.** The official documentation points out that in Kubernetes scenarios, `nv-hostengine` should be deployed independently rather than embedded inside each container. Our new architecture is fully aligned with that recommendation.

**From an engineering-efficiency perspective, the independent container also brought unexpected convenience.** The `nvidia-dcgm` container naturally became a debugging entry point that engineers can enter at any time. They can directly `kubectl exec` into it to investigate problems, without needing to log into the host. This is both convenient and better from a security-boundary perspective because it reduces unnecessary VM-level access.

**Finally, and this is the point I consider most valuable, we unlocked error injection capability.** Thanks to Rodri for the support and insight on this part. `dcgm-exporter` is essentially only a metrics exporter and cannot inject forged error states into the Host Engine. But an independently deployed `nvidia-dcgm` Pod can do that, which is exactly the Error Injection capability described in the NVIDIA documentation. With it, we can actively simulate different GPU fault scenarios, verify whether the alerting path is triggered as expected, and also lay the testing foundation for future end-to-end automation around node detection, eviction, and recovery.
