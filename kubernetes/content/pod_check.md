#### 提供Probe机制，有以下两种类型：

- livenessProbe：如果检查失败，将杀死容器，根据Pod的restartPolicy来操作。
- readinessProbe：如果检查失败，Kubernetes会把Pod从service endpoints中剔除。

#### Probe支持以下三种检查方法：

- httpGet：发送HTTP请求，返回200-400范围状态码为成功
- exec： 执行Shell命令返回状态码是0为成功
- tcpSocket： 发起TCP Socket建立成功

#### 使用httpGet为例演示的YAML配置文件

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
		ports:
		- containerPort: 80
		livenessProbe:
		  httpGet:
			path: /index.html
			port: 80