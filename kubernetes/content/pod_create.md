#### 使用YAML配置文件创建Pod对象

	apiVersion: v1
	kind: Pod
	metadata:
	  name: nginx-pod
	  namespace: default
	  labels:
		app: nginx
	spec:
	  containers:
	  - name: nginx-container
		image: nginx:1.13
		
#### Pod基本管理

##### 1、创建pod资源

    kubectl create -f nginx-pod.yaml
    
##### 2、查看pods

    kubectl get pods nginx-pod

##### 3、查看pod详细信息

    kubectl describe pods nginx-pod

##### 4、更新pod资源

    kubectl apply -f nginx-pod.yaml
    
##### 5、删除资源

    kubectl delete pod nginx-pod
    or
    kubectl delete -f nginx-pod.yaml