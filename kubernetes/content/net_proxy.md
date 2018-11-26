#### 三种网络代理模式： userspace、iptables和ipvs

#### 官方文档： https://kubernetes.io/docs/concepts/services-networking/service

#### 三种网络代理模式原理图（从左到右依次为：userspace、iptables和ipvs）

![image](https://github.com/hdpingshao/ops/blob/master/kubernetes/images/6-1.jpg)

#### service-服务代理YAML配置文件详解

	apiVersion: v1
	kind: Service
	metadata:
	  name: nginx-svc
	  labels:
		app: nginx
	spec:
	  ports:
	  - name: http
		protocol: TCP
		port: 80
		targetPort: 80
	  - name: https
		protocol: TCP
		port: 443
		targetPort: 443
	  selector:
		app: nginx