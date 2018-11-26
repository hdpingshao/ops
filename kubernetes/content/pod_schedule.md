#### Pod.spec.nodeName      强制约束Pod调度到指定Node节点上

#### Pod.spec.nodeSelector  通过label-selector机制选择节点

#### 创建Pod使用调度约束的配置文件

	[root@localhost pod]# kubectl get nodes
	NAME              STATUS   ROLES    AGE     VERSION
	192.168.200.117   Ready    <none>   4d19h   v1.12.2
	192.168.200.118   Ready    <none>   4d19h   v1.12.2
	[root@localhost pod]# cat nginx-pod.yml 
	apiVersion: v1
	kind: Pod
	metadata:
	  name: nginx-pod
	  namespace: default
	  labels:
		app: nginx
	spec:
	  nodeName: 192.168.200.118
	  # nodeSelector:
	  #   env_role: dev
	  containers:
	  - name: nginx-container
		image: nginx:1.13
	[root@localhost pod]# kubectl create -f nginx-pod.yml 
	pod/nginx-pod created
	[root@localhost pod]# kubectl get pods -o wide
	NAME        READY   STATUS    RESTARTS   AGE   IP            NODE              NOMINATED NODE
	nginx-pod   1/1     Running   0          5s    172.17.65.2   192.168.200.118   <none>
	[root@localhost pod]# 
	
- 指定nodeName会自动将pod部署在指定的node节点上
- 指定nodeSelector会自动将pod部署在具有env_role=dev标签的节点上，如果所有节点都不具有env_role=dev标签，则pod会一直处于Pending状态，直至出现具有env_role=dev标签的节点（在不配置其它属性的情况下）
