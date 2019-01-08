#### Pod简介

- 最小部署单元
- 一组容器的集合
- 一个Pod中的容器共享网络命名空间
- Pod是短暂的

#### Pod容器分类

- Infrastructure Container：基础容器，维护整个Pod网络空间
- InitContainers： 初始化容器，先于业务容器开始执行
- Containers：业务容器，并行启动

#### 镜像拉取策略（imagePullPolicy）

- IfNotPresent：默认值，镜像在宿主机上不存在时才拉取
- Always： 每次创建Pod都会重新拉取一次镜像
- Never： Pod永远不会主动拉取这个镜像