#### 三种网络代理模式： userspace、iptables和ipvs

###### iptables:

- 灵活，功能强大（可以在数据包不同阶段对包进行操作）
- 规则遍历匹配和更新，呈线性时延

###### ipvs：

- 工作在内核态，有更好的性能
- 调度算法丰富：rr, wrr, lc, wlc, ip hash...(修改调度算法方法：--ipvs-scheduler=wrr)

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