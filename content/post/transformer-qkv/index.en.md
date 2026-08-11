---
title: "Understanding QKV in Transformers: Why Attention Separates Matching from Content"
date: 2026-08-11T14:15:00+08:00
Description: ""
Tags: []
Categories: ["Machine Learning"]
summary: "Why does attention need Queries and Keys if Values are what it ultimately reads? This article uses that question to explain the roles of Q, K, and V, then shows how representation dimensions, multiple attention heads, and stacked layers give Transformers their flexible context-matching ability."
DisableComments: false
draft: false
---

While studying the core equations behind Transformers, I found myself returning to a basic question about QKV—Query, Key, and Value. If the attention mechanism ultimately retrieves Values, why not match a Query directly against those Values? Why introduce Keys at all?

Following that question led me to a more useful mental model: QKV is not merely a sequence of extra vector operations. Its key idea is to separate how information is found from what that information contains.

## What Do Q, K, and V Actually Do?

In self-attention, the representation of every token is passed through three different learned linear projections to produce a Query, a Key, and a Value. A Query at one position is compared with the Keys at all positions. The resulting similarities are scaled and normalized with Softmax, then used as weights for a sum of the corresponding Values:

$$
\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

An intuitive way to think about the three roles is:

1. **Query** describes what I am looking for.
2. **Key** describes the features by which I can be found.
3. **Value** contains what I contribute if I receive attention.

The $QK^T$ term therefore determines how much attention should flow between token positions, while $V$ carries the content that will be aggregated.

## Why Not Match Queries Directly Against Values?

If Queries were matched directly against Values, one representation would need to serve two purposes: exposing features useful for retrieval and carrying the content passed to the next computation. That is not mathematically impossible, but it couples two learning objectives and gives the model less freedom to develop different representations for matching and content.

Separating Keys from Values allows the model to learn two distinct answers:

1. How should I match against other tokens to find the information needed here?
2. Once a token is selected, what information should it pass forward?

This decoupling is central to the QKV design. A word can play different roles in different contexts. Its Key can emphasize features useful for deciding whether it is relevant, while its Value can preserve a different set of features suitable for aggregation. In that sense, a Key resembles an index entry, while a Value resembles the content to which the index points.

Keys and Values are not hand-written tables of semantic attributes. Both are learned projections. A token's Q, K, and V originate from the same input representation, but their separate projection matrices allow them to specialize for different jobs.

## How Does the Model Match Multiple Attributes?

A word usually has many properties at once. A cat, for example, is an animal, a pet, a creature with teeth and limbs, and something associated with hunting. Some of those relationships may also operate at different levels of abstraction. How can a Transformer select the relationship that matters in the current context?

Several parts of the architecture contribute to this ability.

### 1. Vector Dimensions Provide Representational Space

Larger representations can generally encode richer features, giving Queries, Keys, and Values more room to express fine-grained distinctions. More dimensions are not free, however: they increase parameter counts, computation, and memory use.

During autoregressive inference, the model must also retain Keys and Values from earlier tokens in the KV Cache. The total K/V width, sequence length, number of layers, and numerical precision therefore all affect cache size. Model design has to balance representational capacity against compute and inference memory.

### 2. Multiple Attention Heads Provide Different Views

Multi-Head Attention projects representations into several subspaces and computes attention independently in each head. The same word can participate in very different relationships across heads. One head may respond to syntactic dependencies, another to coreference, and another to positional or semantic relationships.

Multi-head attention can therefore be understood as a form of multi-view querying. Rather than assigning a handcrafted Key to every possible attribute, it lets the heads learn useful matching strategies during training. The heads can also be computed in parallel, which maps well to modern GPU hardware.

### 3. Stacked Layers Build Increasingly Contextual Representations

A Transformer normally stacks many Blocks, each containing an attention module and a feed-forward network (FFN). Early representations tend to be closer to local or surface-level features. As information repeatedly passes through attention and nonlinear transformations, later layers can build more abstract and context-dependent representations on top of earlier results.

This does not mean that every layer corresponds to a fixed semantic level. Depth does, however, let the model update token representations repeatedly. The contextualized output of one layer becomes the input to the next, which then computes a fresh set of Queries, Keys, and Values. More complex relationships can emerge through this iterative process.

## Conclusion

The clearest way to understand QKV is to view attention as two stages: addressing and reading. Queries and Keys decide where to look; Values determine what is retrieved once attention has been assigned.

Representation dimensions provide capacity, multiple heads offer different views of token relationships, and stacked layers continually update those representations in context. Together, these mechanisms give Transformers their flexible semantic matching ability.

Keys are therefore not an unnecessary intermediate step. They allow the model to learn how to find information separately from what that information contains—and that separation is a major reason attention works so well across complex contexts.
