## service-发布服务

### 服务类型

#### 1、ClusterIP

- 分配一个内部集群IP地址，只能在集群内部访问（同namespace内的Pod），默认ServiceType。

#### 2、NodePort

- 分配一个内部集群IP地址，并在每个节点上启用一个端口来暴露服务，可以在集群外部访问。
- 访问地址：<NodeIP>:<NodePort>

#### 3、LoadBalancer

- 分配一个内部集群IP地址，并在每个节点上启用一个端口来暴露服务。
- 除此之外，kubernetes会请求底层云平台上的负载均衡器，将每个Node([NodeIP]:[NodePort])作为后端添加进去。

### Service功能

- 防止Pod失联
- 定义一组Pod的访问策略
- 支持ClusterIP、NodePort以及LoadBalancer三种类型
- Service的底层实现主要又iptables和ipvs两种网络模型

### Pod与Service的关系

- 通过label-selector相关联
- 通过Service实现Pod的负载均衡（TCP/UDP 4层负载均衡）

### NodePort示例（最常用的服务类型）

	apiVersion: extensions/v1beta1
	kind: Deployment
	metadata:
	  name: nginx-deployment
	spec:
	  replicas: 3
	  template:
		metadata:
		  labels:
			app: nginx
			role: web
		spec:
		  containers:
		  - name: nginx
			image: nginx:1.13
			ports:
			- containerPort: 80
	---
	apiVersion: v1
	kind: Service
	metadata:
	  name: nginx-service
	  labels:
		app: nginx
	spec:
	  selector:
		app: nginx
		role: web
	  ports:
	  - name: http
		port: 8080
		protocol: TCP
		targetPort: 80
	  type: NodePort