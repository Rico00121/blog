---
title: "Dissecting Docker: From Dockers to Container Sandboxes"
date: 2023-05-28
draft: false
description: "Guide to Thumbnails in Hugo"
---


### What is Docker?
If you've heard of Docker and used it, you probably know where the name comes from; Docker takes its name from the dockworkers who are responsible for moving containers and moving them from one place to another. In the computer world, Docker is also a mover, responsible for moving applications and their dependencies from one environment to another. This is a concrete implementation of containerisation technology, which enables lightweight packaging and deployment of applications through the concepts of images and containers that package an application into a portable container.

Image is an important concept in Docker, which is similar to the disc on which the operating system is installed. In Docker, an image is an executable image of the code, which consists of some initialisation data and the binary file of the code itself. A container is a virtual computer with an installed system that is booted from an image. With the docker run command, we can quickly start a container that runs the software corresponding to the image, thus enabling the application to run.

Containers are actually a sandboxing technology, and as the name suggests, a sandbox is a technology that "packs" your application like a container. In this way, applications and applications because there is a boundary and not to interfere with each other. The applications that are packed into the container can also be easily moved around. This sandboxing technique helps us to better isolate different applications from each other. At the same time, it also makes applications more portable and can be easily run in different environments.

### What's the difference from a traditional virtual machine？

Both Docker and virtual machines can be used to isolate applications and their dependencies, enabling lightweight packaging and deployment of applications. However, they are implemented differently.

![Comparing Virtual Machines and Docker](images/compare.png)

In a virtual machine, Hypervisor hardware virtualisation simulates the hardware needed to run an operating system and then installs a new operating system on that virtual hardware. In Docker, the Docker project helps users start the same application processes, but when creating them, Docker adds various Namespace parameters to achieve isolation and resource management between processes.
The advantage of Docker over virtual machines is that it starts faster and uses fewer resources. Container images are much smaller in size because they contain only all the files and directories of the operating system, not the kernel, which makes system calls through the Docker Engine (similar to how Java programs go through the JVM). It is usually only a few hundred megabytes, whereas a traditional virtual machine image is a "snapshot" of a disk, so the image is at least as big as the disk.
However, Docker has some limitations. For example, in the Linux kernel, there are many resources and objects that cannot be Namespaced, such as time. If you execute a system call that modifies time in a Docker container, the time of the entire host is also modified. Therefore, when deploying an application using Docker, you need to give more thought to which resources and objects can be Namespace-enabled, as well as their limitations and security concerns. Virtual machines, on the other hand, completely isolate the application and its dependencies and are relatively more secure, but they also require more resources and cost more to run.
In summary, both Docker and virtual machines have their advantages and limitations. When choosing which technology to use, you need to weigh them against specific application scenarios and requirements. For applications that require rapid deployment and lightweight isolation, Docker may be more suitable, while for applications with higher requirements for isolation and security, virtual machines may be more appropriate.

### What problem does Docker solve?

Imagine being able to easily package an application and all its dependencies and then run it smoothly in different development, testing and production environments. This is the goal of the open source Docker project.
The emergence of Docker as an open source containerisation platform has solved many of the application packaging and deployment challenges. Before the emergence of container technology, application packaging and deployment usually need to consider a lot of dependencies (all kinds of interdependencies caused by dependencies hell), environment and configuration issues, which makes the deployment of applications become complex and error-prone. Docker solves the fundamental problem of application packaging and deployment by packaging applications and their dependencies into a portable container through the concept of container images. By constraining and modifying the dynamic behaviour of processes, Docker creates a clear "boundary" for containers, making application deployment and management easier and more reliable.
In addition, Docker lays the foundation for container orchestration technologies like Kubernetes (k8s), which provides a set of foundational dependencies for building distributed systems based on containers. Using Docker and Kubernetes, developers can more easily build, deploy, and manage distributed applications, while also better enabling horizontal scaling and high availability of applications. As a result, Docker is widely used in cloud computing, DevOps, and microservices, and has become one of the key cornerstones of modern software development and deployment.

### The underlying technical principles of Docker

Before we talk about the technical implementation of Docker, it's important to understand what a process is so that we can better understand the Docker container. What is a process? Simply put, a process is an entry with a port that we see when we open the task manager or type ps in cmd, it is a process, it is a programme that runs when we write code. To put it more professionally, a process is the sum total of the execution environment of a computer after a programme has been run. For a process, its static representation is the programme, once it is running, it becomes the sum of the data and state in the computer (dynamic representation). Containers, on the other hand, are essentially a special kind of process.
Docker uses Namespace technology and Cgroups technology in the Linux operating system to implement containerisation, enabling isolation and resource management between containers and hosts.

**Namespace**

Namespace is one of the cores of Linux container technology, which is responsible for encapsulating, abstracting, restricting, and isolating processes within a container so that they appear to have their own global resources. It is an isolation mechanism provided by the Linux kernel that isolates global system resources, such as process IDs, network, filesystems, users, etc., into separate namespaces to achieve isolation between processes.Docker provides containers with separate isolation environments such as process space, network space, and filesystem space through the use of the Namespace technology to achieve isolation between containers.

**Cgroups**

Cgroups (short for control groups) is another key Linux kernel feature that limits, describes, and isolates the resource usage of a group of processes. It is also a resource management mechanism provided by the Linux kernel, which enables resource control of processes by limiting their resource usage, such as CPU, memory, disk IO, etc. Docker provides resource limitation and control for containers through the use of the Cgroups technology, for example, it can limit the container's CPU usage, memory usage, and so on.

So, a running Docker container is actually an application process with multiple Linux Namespaces enabled, and the amount of resources this process can use is limited by the Cgroups configuration.
We can access the bash shells inside a running Docker container with the following command:

```bash
docker exec -it my_container bash
```

When we enter a container, and use the ls command to view the current file directory, we see that the container has a full Linux system directory inside (using the mysql:8.0 image as an example):

```shell
bash-4.4# ls
bin   dev                         entrypoint.sh  home  lib64  mnt  proc  run   srv  tmp  var
boot  docker-entrypoint-initdb.d  etc            lib   media  opt  root  sbin  sys  usr
```

This is actually based on Mount Namespace in Namespace technology. Mount Namespace plays an important role in container technology. It allows applications in the container to see a completely separate filesystem, providing isolation between the container and the host. However, it is important to note that Mount Namespace only isolates increments, not stocks. Specifically:

- When the container is created, it will inherit the file system mount points that already exist on the host, this part is "stock".

- Subsequently, if a container creates or modifies a file system mount point, this part is isolated in the Namespace, and this part is "incremental".

This means that until the container is started, newly created containers inherit directly from the host's mount points. Therefore, to make the container's root directory look more realistic, we can mount a complete operating system filesystem, such as the ISO of Ubuntu 16.04, in the root directory where the container is started. after isolating it through the Mount Namespace, execute the ls / command after the container is started to view the container's root directory, and you can see all the files and directories of Ubuntu, which are mounted on the root directory. The filesystem mounted on the root of the container is known as the "container image", also known as rootfs.

Smart guys will certainly think of a problem when they see this, we have thousands of images in container repositories like Docker Hub, and most of the images are similar to the underlying Linux OS parts except for the encapsulation of the program code itself, and the dependencies needed to run the program, so wouldn't Docker Hub have to spend a lot of space to store these duplicates? On the other hand, when we change our application code and want to rebuild the image, won't we have to rebuild all the dependencies again? To solve these problems, based on rootfs, Docker innovatively proposes to use multiple incremental rootfs to jointly mount a complete rootfs (called AuFS, Advanced Multi-Layered Unification Filesystem), which introduces a "layer" in container images. This introduces the concept of "layers" in container images.
Let's take the mysql image as an example:

```shell
PS C:\Users\rico0> docker image inspect mysql:8.0
[
    {
        //...
        "RootFS": {
            "Type": "layers",
            "Layers": [
                "sha256:caefa4e45110eab274ebbdbc781f9227229f947f8718cee62ebeff1aac8f1d5b",
                "sha256:5ed69eb31cd773570fc2cdad9c6224f65db7475b3ca8d22e70c8ab24f7c5005c",
                "sha256:a9805d41c46adbdef5a8b43096d0928f57c30687950ad0a80ce317190abd1c05",
                "sha256:3f772020efc1dbae8c80a4bb7597c3952991b73cc8c7c9cd1467ba5a323684a3",
                "sha256:08745f0c18ca985883f4099696bd2499179aeb221275647d0bf5ed8c475b7bbb",
                "sha256:1c585189e67fdc2030c09ab748ad5fab930ca32eade2a28a290f3b17b35e32f7",
                "sha256:bd6b6a89e10a7cdc0eef1d4a90db1afd39a647aa075c92f595164eaf2069935f",
                "sha256:82a375517098b527686d74ce3e158e77deb7accde153ca19dd2207d9b14b5058",
                "sha256:44eaf2264b913c20d7732546a815a86f802a8be8ab2bcb357962f70798f65fc9",
                "sha256:ac2f3d433b8e30367e3bed5c72cd5fdd0422b2a5bcff0f0a95571459ce9b425a",
                "sha256:a4f094a199131314e86227d611298d820819bea9c70c8c78166c0f3bf147e212"
            ]
        },
        "Metadata": {
            "LastTagTime": "0001-01-01T00:00:00Z"
        }
    }
]
```

We can see that it has a lot of "Layers", they are a cumulative state of the file, these layers from the bottom up is divided into three categories: read-only layer, Init layer and read-write layer (the following image is only used for example, and do not represent the real layer situation). 

![image structure](images/image_structure.PNG)

First is the read-only layer, the bottom layer, which contains some basic system components, or common parts. By placing these common parts in the read-only layer, you can reduce the number of duplicate files that need to be uploaded to the Docker Hub and increase the speed of image downloads.

The next layer is the Init layer, which is similar to the .gitignore file in Git. The Init layer is a separate internal layer generated by the Docker project to hold information such as /etc/hosts, /etc/resolv.conf, etc. Users often need to write to this layer when they start a container. Users often need to write some specified values, such as the hostname, when they start the container, but when they execute the docker commit command, they will only commit the read/write layer, which does not contain this information.

Finally, there is the read-write layer, which is empty until a file is written. Once a write operation is performed in the container, the modifications appear in the read-write layer in increments. In addition, AuFS creates a whiteout file in the read-write layer to "mask" the files in the read-only layer that need to be deleted, thus enabling soft deletion (since the read-only layer is not writable).

Corresponding to a specific mysql: 8.0 image, that is:

- Read-only tier: Contains the underlying operating system running MySQL, the MySQL program itself, configuration files, and database base files. These will remain unchanged.

- Init Layer: Contains the MySQL service startup scripts and configurations that are run when the container starts.

- Read/Write Layer: Log files, temporary files, port mappings, etc., generated when the container is running, all exist here.

Through this layered approach, container images can be more flexible and efficient management and use. When the container is started, Docker will mount multiple layers together to form a complete root file system. This is one of the reasons Docker is able to start containers quickly. At the same time, because each layer is relatively independent, we can more easily manage and update the container image, just need to modify the corresponding layer, rather than having to rebuild the entire image. This is also in line with Docker's philosophy of "build once, run everywhere".

### Summary

In this article, we first compare the similarities and differences between Docker and traditional virtual machines. We then introduce the isolation environment consisting of various Namespaces and Cgroups, which we call the Container Runtime, the dynamic part of the Docker container. Next, we introduce the concept of the container image hierarchy, introducing a set of rootfs mounted on a filesystem directory, the "container image" part, which is the static part of the container. They are the static part of the container. The container image part is more important than the runtime part of the container, because they are the part that actually carries the information.

I think the core value of Docker technology is to layer, isolate, and simplify deployment. This allows developers to focus more on product coding, which greatly improves work efficiency. At the same time, the emergence of Docker technology has also laid a solid foundation for the emergence of container orchestration technologies like Docker Swarm, Kubernetes and Amazon ECS.

### References

1.  Merkel, D. (2014). Docker: lightweight linux containers for consistent development and deployment. Linux j, 239(2), 2.
2.  Chen, Hao. (2015, April 16). Docker Basic Techology: Linux Namespace (Part I). Coolshell. https://coolshell.cn/articles/17010.html
3.  Zhang, Lei. (2018, August 27). _A deep dive into Kubernetes_. Coolshell. https://time.geekbang.org/column/intro/100015201?tab=catalog