---
title: "What is Test Double"
date: 2022-05-25
draft: false
---

## Preface
In order to pursue engineering excellence, I recently started to learn about TDD (Test-Driven Development). Therefore, it is inevitable to come across the concept of Test Double. As a non-native English speaker, when I saw this word, I really thought it meant test twice. With deeper understanding, I gradually learnt about Dummy, Fake, Stub and other Test Double terms. I'm sure you're like me and were confused when you were first introduced to these concepts. In order to reflect on my recent learning, I have summarised the definitions and usefulness of various Test Doubles based on my own understanding.

## Various Test Doubles
> Since the implementation of Test Double related code and the API provided by each language is different, we will not give a code demonstration here, but only provide business examples.

### Dummy
Dummy stands for never used, used only to fill out a list of parameters. It's like a tasty little snack that's just there to satisfy the taste buds and serves no real purpose. For example, when we're testing a method where the passing of a parameter doesn't affect the scope of what we're trying to test, we'll often use null for a quick fill.

### Fake
Fake can be a memory-based implementation of a Data Access Object or Repository. The implementation doesn't really do database operations, but uses a simple HashMap or some test-specific in-memory database to store the data. It is possible to quickly prototype a system and run the entire system based on an in-memory repository, deferring some of the decisions used in database design. For example, we often use Fake to ensure that payments in a test environment always return successful results.

### Stub
Stub stands for objects that contain predefined data and are returned to the caller at test time. It is often used in scenarios where we don't want to return real data or cause other side effects. For example, when an object needs to fetch data from a database, we don't need to actually interact with the database or fetch the data from memory like Fake does, but rather just return the predefined data.

### Spy
Spy is a specially processed Stub, which in addition to having the ability of Stub, will record some information according to the call method. It is like a communication spy that secretly records the information you want to know during the function call and reacts in a certain way. For example, we may need it when we want to know how many emails have been sent by a certain method during its execution.

### Mock
Mocks are objects that only have their invocation information and corresponding triggered behaviour predefined, and can be verified with verify(mockInstanceName) to see if the behaviour (method) occurs. Mocks are used in place of real objects when we don't want to actually call the code in production or when it's difficult to verify real code execution in tests. For example, if you're testing an email service, you don't want to send an email every time you run a test, because it's hard to verify that the email was actually sent or received.Instead, we focus on whether the mail service is called in the appropriate business flow as we expect. In this case, we use a Mock to completely simulate the behaviour of the mail service, defining the return values of the methods under different calls, and simulating a real-looking mail service.

## Reality-based mapping
Read a variety of articles on the Internet, the feeling that the talk are dizzy, a sudden flash of light, think of an example of my own, I hope to be able to help you understand the partners. (If there is any error welcome to correct)

First of all, establish a context: our factory needs to make a customised pipe, the function is to automatically open the filter when monitoring the sand and water passing through, to filter the sand and water into clear water (please bring yourself into this context). Based on this, we, as inspection workers in the factory, of course need to perform a series of inspections on the pipe before it leaves the factory and tag it out at the end. For this, we did the following test to help us with our task.

![Water Pipe](images/water-pipe.jpg)

- Putting it into the whole or part of a pipework system, draining it of water (or various other fluids), and testing whether it works properly (integration testing);
- Through a variety of other well-done moulds, that is, "test double" (or test pipe with the machine, spray water machine, spray sand water machine, identify the water quality machine such as) assembled to test its function (unit testing);
- The inlet is connected to a Fake water sprayer or sand blaster to see if it can produce fresh water;
- Outlet simulation out of the liquid (Stub), to see if the water can go in (a little far-fetched.);
- When the sand water goes through the pipe, the filter clasp inside the pipe opens, at which point the filter falls out.I gave it sandy water, want to observe the filter buckle open (Mock), at this time do not need to care whether there is no filter, just want to observe the behaviour of the filter buckle;
- In order to find out if this strainer could be opened ten times in a row in an hour, I added a counter on the outside to monitor the number of times it opened over time (Spy);
- Each pipe has to be labelled before it can be used (it can be used without a label, but it's a hard and fast rule, so we put an irrelevant label on it first (Dummy)).