#### 三种重启策略

Always：当容器停止，总是重建容器，默认策略。
OnFailure：当容器异常退出（退出状态码非0）时，才重启容器。
Never： 当容器终止退出，从不重启容器。

#### Pod管理-重启策略YAML配置文件

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
	  restartPolicy: OnFailure