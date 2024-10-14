---
title: "Universal Guide to Debugging User-data on Linux Cloud Instances"
date: 2024-10-14T22:46:53+02:00
Description: ""
Tags: []
Categories: []
DisableComments: false
---
## Introduction
In the cloud computing environment, Cloud-init is a powerful tool that can automatically configure instances when a virtual machine or container is first started. It is used in almost all cloud computing products on the market. User data is an important function in Cloud-init. Through the user-data file, we can define the configuration of the instance, such as setting SSH keys, installing software packages, configuring the network, etc. However, when the configuration in the user-data file does not take effect or there is a problem, how to debug becomes particularly important.

This article will introduce how to debug the user-data file of Cloud-init to help you quickly find problems and solve them.

## User-data File
Before learning how to debug, it is necessary to understand the composition of the user-data file. The user-data file is a configuration file for Cloud-init, usually in YAML format, which defines the initial configuration of the instance. A typical user-data file may include the following:
```shell
#cloud-config
hostname: my-cloud-instance
users:
  - name: ubuntu
    ssh-authorized-keys:
      - ssh-rsa AAAAB3...example-key...
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    shell: /bin/bash
packages:
  - nginx
  - git
```
- #cloud-config: Indicates that this is a cloud-config file.
- hostname: Set the hostname of the instance.
- users: Create users and configure SSH keys.
- packages: Specify a list of packages to install.

In addition to YAML-formatted cloud-config configuration files, we also support using shell scripts to do some initialization configuration, but there are a few points worth noting⚠️:

- User data shell scripts must start with the #! character and the path to the interpreter to read the script (usually `#!/bin/bash`).
- Scripts entered as user data are run as the root user, so the sudo command is **not** required in the script.
- In addition, because the script does not run interactively, it cannot contain commands that require user feedback (such as using the `yum updates` command, you need to add the `-y` flag to skip user interaction).

So how do we ensure that our scripts have no syntax errors? We can use `sudo cloud-init schema --system --annotate` to verify whether the current user-data configuration conforms to the Cloud-init schema standard, helping us find potential syntax or configuration errors.

Through the user-data file, users can automatically complete common configuration tasks when the instance is started, which greatly reduces the duplication of cloud engineers. Our user-data scripts are usually stored in the `/var/lib/cloud/instances/` directory. When we check this directory, we will find our instance information files below:
```shell
ls
i-0e738afccf03a26ab  i-0f352a615063e5912
```
We found that there are two folders here. This is because my current instance is built based on my self-built AMI, so it saves the information of its source instance, including the original file of its user script file. Cloud-init will convert the original file into an executable file and place it in the `/scripts` directory. One thing to note here is that /var/lib/cloud/instances stores the cloud-init information of all source instances. Although after repeated tests by me, Cloud-init does not execute the User data scripts of all source instances. But in any case, when building a new AMI, it is best to delete all User data scripts that exist in the original image in advance to avoid unnecessary risks, such as causing some security information of the base image to be leaked.

## Simplify debugging of user-data scripts
When debugging the user-data configuration of Cloud-init, many users may face the challenges of complex configuration and multiple attempts, which I believe is annoying for everyone. To simplify this process, we can adopt some effective strategies to improve debugging efficiency.

Some ideas for debugging:

1. **Debugging and logging**: We can view the output log of our user-data script in `/var/log/cloud-init-output.log` of the instance. In addition, we can also add detailed logging to the user data script, which helps us find problems faster after the instance is started. Make sure the script outputs logs to `/var/log` or other log files for subsequent analysis.
2. **Use temporary startup scripts for EC2 instances**: You can run your script on a test instance first, modify, debug, and call the run script directly instead of creating a new instance each time, which can greatly save time.
- For Shell scripts, we can run directly.
- For cloud-config scripts, we can run through the `cloud-init modules --mode=final` command.
3. **Test using automated scripts**: Write some automated scripts to start and destroy instances to simplify the instance creation and destruction process.

```shell
#!/bin/bash

AMI_ID="ami-00f87382f90261efc"
INSTANCE_TYPE="t2.micro"
TAGS="ResourceType=instance,Tags=[{Key=Name,Value=TestInstance}]"
KEY_NAME="RT-key"
SECURITY_GROUP="sg-07d979f09443f6cf0"
#SUBNET_ID="subnet-0123456789abcdef0"

aws ec2 run-instances \
    --image-id $AMI_ID \
    --count 1 \
    --instance-type $INSTANCE_TYPE \
    --tag-specifications $TAGS \
    --key-name $KEY_NAME \
    --security-group-ids $SECURITY_GROUP \
    --user-data file://user-data.sh
#    --subnet-id $SUBNET_ID \
```

4. **Manage infrastructure through AWS CloudFormation or Terraform**: This is an extension of the third point. These tools allow you to define and modify infrastructure configurations, including user data scripts. You can quickly redeploy test instances without manually creating them. I prefer to use **Terraform**. Because Terraform allows you to quickly switch to other cloud service providers, while **AWS CloudFormation** only supports AWS's own services.
5. **Use QEMU to simulate cloud instance environment**: Use QEMU to start the virtual machine and tell it that it is in a nocloud environment, specify the data source (user-data, meta-data and vendor data) from the local machine, so as to achieve rapid debugging of the simulated cloud environment. The principle of this method is similar to using LXD containers, but the method based on LXD containers is more lightweight.
6. **Use LXD containers to simulate the environment of cloud instances**

Of course, most of the time we have to go to the cloud computing platform to create instances with a big fuss if we only make slight modifications. Rebooting again and again just to test whether User data is executed correctly and enter it to view the log is too slow. In fact, we can also use containerization technology to simulate the environment of cloud service instances, so as to quickly start testing locally.

In our Linux system (there is no Ubuntu virtual machine to replace it), we can use the following command to install the lxd container service and the supporting tool lxc.

```shell
//Install lxd
sudo snap install lxd

//Perform minimal configuration for lxd startup
sudo lxd init --minimal
```

Next, we can create a my-user-data file locally, for example, its content is:

```shell
#cloud-config
runcmd:
  - echo 'Hello, World!' > /var/tmp/hello-world.txt
```

We can then run our instance with `lxc launch ubuntu:focal my-test --config=user.user-data="$(cat /tmp/my-user-data)”`. ubuntu:focal has the Cloud-init tool pre-installed, so the instance will try to automatically execute our user data script after startup. After each test, you can quickly terminate the container with `sudo lxc delete my-test --force`.