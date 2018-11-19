### k8s部署方式与ing太规划

#### 官方提供的三种部署方式：

> * 1、minikube
> * Minikube是一个工具，可以在本地快速运行一个单点的kubernetes，仅用于尝试kubernetes或日常开发的用户使用。
> * 部署地址：https://kubernetes.io/docs/setup/minikube
> * 2、kubeadm
> * kubeadm也是一个工具，提供kubeadm init和kubeadm join，用于快速部署kubernetes集群
> * 部署地址：https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm
> * 3、二进制包
> * 推荐，从官方下载发行版的二进制包，手动部署每个组件，组成kubernetes集群
> * 下载地址：https://github.com/kubernetes/kubernetes/releases

#### kubernetes平台环境规划

|软件|版本|
|------|------|
|Linux操作系统|CentOS7.5_x64|
|Kubernetes|1.12|
|Docker|18.xx-ce|
|Etcd|3.x|
|Flannel|0.10|

|角色|IP|组件|推荐配置|
|------|------|------|------|
|master01|192.168.200.111|kube-apiserver<br>kube-controller-manager<br>kube-scheduler<br>etcd|CPU:2C+<br>内存:4G|
|master02|192.168.200.116|kube-apiserver<br>kube-controller-manager<br>kube-scheduler<br>etcd|CPU:2C+<br>内存:4G|
|node01|192.168.200.117|kubelet<br>kube-proxy<br>docker<br>flannel<br>etcd|CPU:2C+<br>内存:4G|
|node02|192.168.200.118|kubelet<br>kube-proxy<br>docker<br>flannel|CPU:2C+<br>内存:4G|


#### k8s单Master集群架构图

![iamge](https://github.com/hdpingshao/ops/blob/master/kubernetes/images/2-1-1.jpg)

#### k8s多Master集群架构图

![image](https://github.com/hdpingshao/ops/blob/master/kubernetes/images/2-1-2.jpg)

#### 自签etcd的ssl证书

> * https://github.com/hdpingshao/ops/blob/master/kubernetes/content/ssl_etcd.md

#### etcd数据库集群部署

> * 