#### Pod管理-资源限制YAML配置文件

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
		resources:
		  requests:
			memory: "64Mi"
			cpu: "250m"
		  limits:
			memory: "256Mi"
			cpu: "500m"
			
- memory： 64Mi表示使用64M的内存
- cpu： 正常情况下1核=1000m，也就是说500m就代表0.5核

