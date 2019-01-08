### 一、部署的项目情况

- 1、业务架构及服务（dubbo，spring cloud）
- 2、第三方服务，例如mysql，redis，zookeeper，eruka，mq
- 3、服务之间如何通信要规划好。
- 4、资源消耗：硬件资源，带宽。
- ......

### 二、部署项目时用到的k8s资源

- 1、使用namespace进行不同项目隔离，或者隔离不同环境（dev，test，prod）
- 2、无状态应用（deployment）
- 3、有状态应用（statefulset，pv，pvc）
- 4、暴露给外部访问（Service，Ingress）
- 5、secret以及configmap
- ......

### 三、项目基础镜像如何生成使用

### 四、编排部署（镜像为交付物）

- 1、项目构建（java）。CI/CD环境这个阶段自动完成（代码拉取->代码编译构建->镜像打包->推送到镜像仓库）。
- 2、编写yaml文件，使用这个镜像
- ......

### 五、工作流程

- kubectl->yaml->镜像仓库拉取镜像->Service（集群内部访问）/Ingress 暴露给外部用户