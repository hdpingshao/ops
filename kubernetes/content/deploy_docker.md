### docker结合k8s的容器管理平台架构图

![image](https://github.com/hdpingshao/ops/blob/master/kubernetes/images/2-4-1.jpg)

### 在Node节点上安装部署docker最新版本（这边使用的是官网下载的，也可以使用阿里云的rpm包来下载安装）

#### 安装所需的依赖包

    yum install -y yum-utils device-mapper-persistent-data lvm2
    
#### 配置仓库

    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    
#### 安装docker-ce

    yum install -y docker-ce
    
#### 配置daocloud加速器

    curl -sSL https://get.daocloud.io/daotools/set_mirror.sh | sh -s http://f1361db2.m.daocloud.io