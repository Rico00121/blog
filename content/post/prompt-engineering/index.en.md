---
title: "Prompt Engineering: a scientific guide to using generative AI"
date: 2023-10-29
draft: false
---

## Preface
The field of Artificial Intelligence is full of big models, combined with the use of various AI tools in the last six months (ChatGPT, Claude-Instant, PaLM, Midjourney).Each of us should keep an eye on developments in the field of AI, as AI can be used to automate tasks that you are spending countless hours doing right now.

## What is prompt engineering
The prompt engineering is an input style guide for interacting with generative AI tools. Prompt engineering is to develop a series of style guides and input templates for interacting with generative AI to influence and derive its output. Through appropriate prompts and constraints, the perceptions and "desires" of the generative AI can be altered to influence and derive its ideas and outputs.

Through prompt engineering techniques, we can control the scope of the AI tool's output so that it focuses on a particular topic or idea, and at the same time improve the quality of the output, reduce bias and errors, enhance the accuracy of the answers, and ultimately the output meets our expectations and goals. Overall, prompt engineering is the use of input styles and constraints to guide the process of interacting with a generative AI, facilitating effective and desirable output.

## Understanding the mindset of generative AI 
Before learning about how to write good prompts, I think it's necessary for us to have some understanding of how generative AI works. Here, let's take the popular generative text AI as an example. Its brain consists of billions of artificial neurons. The structure of these neurons is called a transformer architecture, which is a fairly complex type of neural network. We understand it as an Encoder-Decoder (ED) model, where the encoder part is used to transform the user input (natural language sentences) into a form understandable by the processing unit (contextual information), and the decoder transforms the combination of outputs from the processing unit into a form understandable by the user (translated target language sentences).

What we need to know is that AI is essentially just some mathematical function. Of course, they're more like `f(thousands of variables) = thousands of possible outputs` than simple functions like `f(x) = 2x+1` that we learnt in primary school. It understands sentences by breaking them down into tokens, e.g. if I type "I prefer coffee to tea.", the AI might slice it up into "I", "prefer", "coffee", "to", "tea", and vectorise (convert to a set of cryptic numbers) each of these words to help them understand the sentence. The AI will predict the next word based on the previous word, so they are not really thinking, but rather a speculation of possibilities, generating answers by way of emergence (which is why we occasionally get logically confusing answers), and this is why we need to learn about prompt engineering, we need to pass certain statutes that allow the AI to be able to give us as much as possible the way we want to us a reply.

## Guidance on writing prompts (using Claude-instant as an example)
In order to interact textually with generative AI, we inevitably need to learn to provide appropriate prompt words.
Some guidelines for prompt words are given below.

### Give direct instructions
This is the way we often use, provide context + give instructions, this way is straightforward.

```
Q: Tell me a joke about coffee please.

A: Sure, here's a coffee-related joke for you:

Why did the coffee file a police report?

Because it got mugged!
```

### Character hints
We can try to go further than just giving direct instructions. In general, assigning a role to the AI is usually helpful to you in solving problems because it helps it to limit the scope of the domain in which it can answer the question without it having to speculate on its own, reducing the likelihood of error.
```
Q: You are an exceptional computer scientist and have extensive engineering practice. Please help me with the following question:
I am currently using the Springboot framework for Java and I want the web application I build to be able to withstand 100 million requests per second concurrently, please help me come up with some solutions.

A: When dealing with such a large amount of traffic as 100 million requests per second, there are several points to consider.

  1. scale horizontally: add more application server instances to share the load. You can use a load balancer such as Nginx or Apache to distribute the incoming requests to different application instances.
  
  2. Use a distributed cache, such as Redis or Memcached, to reduce the pressure on the database by caching non-critical and infrequently changing data.
  
  3. Optimise the database. Use quasi-real-time read-write separation to extend database throughput, i.e., read operations are assigned to the slave and write operations are assigned to the master. Sharding can also help with horizontal scaling.
  
  4. Use asynchronous and message queues. Set some long-running background tasks, such as mail sending and image processing as asynchronous tasks. Use message queues to decouple background tasks from the web application.
  
  5. Use CDN to cache static resources. JS, CSS, images and other static resources cached on the CDN to reduce application server pressure.
  
  6. Monitoring and logging. Use monitoring frameworks such as Prometheus to monitor system metrics in real time. Log analysis framework such as ELK Stack to analyse and diagnose exceptions.
  
  7. Optimise code. Avoid IO-intensive operations, reasonable settings for database connection pooling, the use of object pooling and other techniques to improve code performance.
  
  8. Use cloud services. If internal resources are limited, you can consider using AWS or AliCloud and other cloud service providers hosting servers, caching, message queues and CDN services.
  
  The above considerations of horizontal scaling, caching, database expansion, asynchronous and other aspects, I believe that the application can carry such a huge amount of traffic to provide reference. I hope to provide you with some valuable ideas.
```

Assigning a role to AI can often provide us with some constructive guidance in the field of expertise when we are at a loss, helping us to broaden the ideas that can solve the problem and conduct in-depth research into the possible directions.

### Multi-example Hints
Multi-example hinting is a powerful technique for allowing models to generate accurate and correctly formatted output.When using generative AI, we usually use examples to guide the AI to generate answers in the format we want.

```
Ask:
Birds, eggs: birds can lay eggs
Sheep, grass: sheep can eat grass
Man, coffee:
Output only the last line

Answer:
Man, coffee: man can drink coffee
```
We can see with the example above that we managed to get the AI to add the right verb between the two nouns, the output we want it to produce, by way of example. This is actually a very simple example, and by expanding on it, we can achieve some more complex tasks. For example, we can give it some test and implementation code samples and specify the language and framework to be used, in order to achieve the ability to generate business code given the test code, thus enabling TDD where only tests need to be written (with human double checking, of course). Or, we can also give it some actual business requirements and some task splitting cases, so that it can help us split the right task to help us clear our mind faster.


### Combining hints
Some of the above tips can be used in combination. By combining different tips, we will be able to get more powerful cues to help us do our tasks better.

For a good cue word, here I provide a sample, i.e.: Character + Instruction + Example 1 + Example 2 + Example 3.

In addition, by adding rich contextual information and further clarifying what our problem is, we can also make our generative AI perform better. For example, we can try to write our prompt like this: Role + Instruction + Example 1 + Example 2 + Example 3 + Context + Problem.

## Applied Scenarios
### Code
This goes without saying, copying the code to allow the big language model to analyse the problem, which I believe is commonly done by programmers nowadays.

### Structured data generation
This is one of the most interesting parts for me, you can implement structured text output through some LLMs, such as the statute that it outputs json, or the special syntax rules you define for him. There is a practical application of this in our team's project, in order to give some usage samples to our users, we would like to add some item templates for our new feature module, which was originally a BA's job. Since the data for the project templates is a structured data, I came up with the idea of using OpenAI's interface to implement and statute it to output the json format I specified. After teaching the BA some Prompts writing skills, the BA's work hours were greatly reduced.

Another more general example is when you want to summarise brief data information from a large piece of text, such as summarising financial reports from a speech, by specifying that it outputs data similar to a list presentation 📊.

### Output text
AIs such as ChatGPT are known for being able to write papers and blog posts quickly. There are many places in our daily lives where we need to produce text, such as writing emails or this blog post I'm writing right now. We can use the right LLMs to help us quickly output what we want to say, or we can ask them to help us polish the article.

We can tell the LLMs something about the context and formatting requirements of the content we need to write and it will help us output the right content. For example, when we want to write an email to our work leader, we can specify it to output formal email style text.

## Possible trouble

### Hallucination
When the model generates text that does not follow the original text (Faithfulness) or is not factual (Factualness), we can assume that the model has a hallucination problem. In the case of LLMs, the hallucination we usually consider is Factualness. Therefore, it is not currently feasible to use large language models to solve problems where we are not familiar with the context, for example, when LLMs are asked to generate code, it often outputs package or function names that do not exist. At this stage, LLMs can still only be used as an aid, requiring confirmation of the results of the problem by an expert with some experience.

### Advertisement implantation
Advertisement implantation is also a risk we need to consider when using LLMs. Currently, Microsoft has initiated a programme of ad implantation in responses to the ChatGPT version of Bing. For example, when we ask a question about the cheapest Honda car, it will not only tell the answer, but also display a purchase link to direct the user to make a purchase. In the future, when people rely more and more on large language model applications like ChatGPT, the main battleground for advertising will shift from major search engine sites and short video apps to large language models. LLMs can generate user profiles from the user's questions and implant hidden advertisements in replies to guide consumers to develop specific buying habits.



