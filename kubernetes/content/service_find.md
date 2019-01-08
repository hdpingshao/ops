### 服务发现支持Service环境变量和DNS两种模式：

#### 1、环境变量

    当一个Pod运行到Pod，kubelet会为每个容器添加一组环境变量，Pod容器中程序就可以使用这些环境变量发现Service。
    环境变量名格式如下：
    {SVC_NAME}_SERVICE_HOST
    {SVC_NAME}_SERVICE_PORT
    其中服务名和端口名转为大写，连字符转换为下划线。
    限制：
    （1）Pod和Service的创建顺序是有要求的，Service必须在Pod创建之前被创建，否则环境变量不会被设置到Pod中。
    （2）Pod只能获取同Namespace中的Service环境变量。
    
#### 2、DNS

    DNS服务监视Kubernetes API，为每一个Service创建DNS记录用于域名解析。这样Pod中就可以通过DNS域名获取Service的访问地址。
    
    ClusterIP A记录格式： <service-name>.<namespace-name>.svc.cluster.local
    示例：my-svc.my-namespace.svc.cluster.local
    
### 进入pod查看环境变量配置（env指令的使用）

	[root@localhost service]# kubectl exec -it nginx-pod bash
	root@nginx-pod:/# env
	NGINX_SVC_PORT_443_TCP_ADDR=10.0.0.132
	HOSTNAME=nginx-pod
	NJS_VERSION=1.13.12.0.2.0-1~stretch
	NGINX_VERSION=1.13.12-1~stretch
	KUBERNETES_PORT_443_TCP_PROTO=tcp
	KUBERNETES_PORT_443_TCP_ADDR=10.0.0.1
	NGINX_SVC_PORT_80_TCP_PORT=80
	NGINX_SVC_PORT_80_TCP_ADDR=10.0.0.132
	KUBERNETES_PORT=tcp://10.0.0.1:443
	PWD=/
	NGINX_SVC_SERVICE_PORT=80
	HOME=/root
	NGINX_SVC_PORT_80_TCP_PROTO=tcp
	KUBERNETES_SERVICE_PORT_HTTPS=443
	KUBERNETES_PORT_443_TCP_PORT=443
	NGINX_SVC_PORT_443_TCP=tcp://10.0.0.132:443
	KUBERNETES_PORT_443_TCP=tcp://10.0.0.1:443
	NGINX_SVC_SERVICE_HOST=10.0.0.132
	NGINX_SVC_PORT_443_TCP_PROTO=tcp
	TERM=xterm
	NGINX_SVC_SERVICE_PORT_HTTPS=443
	NGINX_SVC_PORT_443_TCP_PORT=443
	NGINX_SVC_PORT=tcp://10.0.0.132:80
	NGINX_SVC_SERVICE_PORT_HTTP=80
	SHLVL=1
	KUBERNETES_SERVICE_PORT=443
	PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
	NGINX_SVC_PORT_80_TCP=tcp://10.0.0.132:80
	KUBERNETES_SERVICE_HOST=10.0.0.1
	_=/usr/bin/env
	root@nginx-pod:/# 

#### 可以查看到nginx-svc这个service对应的IP地址，所以他可以通过nginx-svc来访问该service

### kube-dns组件的部署

#### kube-dns原理图

![image](https://github.com/hdpingshao/ops/blob/master/kubernetes/images/6-2.jpg)

#### 部署kube-dns所需的配置文件

	# Copyright 2016 The Kubernetes Authors.
	#
	# Licensed under the Apache License, Version 2.0 (the "License");
	# you may not use this file except in compliance with the License.
	# You may obtain a copy of the License at
	#
	#     http://www.apache.org/licenses/LICENSE-2.0
	#
	# Unless required by applicable law or agreed to in writing, software
	# distributed under the License is distributed on an "AS IS" BASIS,
	# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
	# See the License for the specific language governing permissions and
	# limitations under the License.

	# Should keep target in cluster/addons/dns-horizontal-autoscaler/dns-horizontal-autoscaler.yaml
	# in sync with this file.

	# Warning: This is a file generated from the base underscore template file: kube-dns.yaml.base

	apiVersion: v1
	kind: Service
	metadata:
	  name: kube-dns
	  namespace: kube-system
	  labels:
		k8s-app: kube-dns
		kubernetes.io/cluster-service: "true"
		addonmanager.kubernetes.io/mode: Reconcile
		kubernetes.io/name: "KubeDNS"
	spec:
	  selector:
		k8s-app: kube-dns
	  clusterIP: 10.0.0.2
	  ports:
	  - name: dns
		port: 53
		protocol: UDP
	  - name: dns-tcp
		port: 53
		protocol: TCP
	---
	apiVersion: v1
	kind: ServiceAccount
	metadata:
	  name: kube-dns
	  namespace: kube-system
	  labels:
		kubernetes.io/cluster-service: "true"
		addonmanager.kubernetes.io/mode: Reconcile
	---
	apiVersion: v1
	kind: ConfigMap
	metadata:
	  name: kube-dns
	  namespace: kube-system
	  labels:
		addonmanager.kubernetes.io/mode: EnsureExists
	---
	apiVersion: extensions/v1beta1
	kind: Deployment
	metadata:
	  name: kube-dns
	  namespace: kube-system
	  labels:
		k8s-app: kube-dns
		kubernetes.io/cluster-service: "true"
		addonmanager.kubernetes.io/mode: Reconcile
	spec:
	  # replicas: not specified here:
	  # 1. In order to make Addon Manager do not reconcile this replicas parameter.
	  # 2. Default is 1.
	  # 3. Will be tuned in real time if DNS horizontal auto-scaling is turned on.
	  strategy:
		rollingUpdate:
		  maxSurge: 10%
		  maxUnavailable: 0
	  selector:
		matchLabels:
		  k8s-app: kube-dns
	  template:
		metadata:
		  labels:
			k8s-app: kube-dns
		  annotations:
			scheduler.alpha.kubernetes.io/critical-pod: ''
		spec:
		  tolerations:
		  - key: "CriticalAddonsOnly"
			operator: "Exists"
		  volumes:
		  - name: kube-dns-config
			configMap:
			  name: kube-dns
			  optional: true
		  containers:
		  - name: kubedns
			image: registry.cn-hangzhou.aliyuncs.com/google_containers/k8s-dns-kube-dns-amd64:1.14.7
			resources:
			  # TODO: Set memory limits when we've profiled the container for large
			  # clusters, then set request = limit to keep this container in
			  # guaranteed class. Currently, this container falls into the
			  # "burstable" category so the kubelet doesn't backoff from restarting it.
			  limits:
				memory: 170Mi
			  requests:
				cpu: 100m
				memory: 70Mi
			livenessProbe:
			  httpGet:
				path: /healthcheck/kubedns
				port: 10054
				scheme: HTTP
			  initialDelaySeconds: 60
			  timeoutSeconds: 5
			  successThreshold: 1
			  failureThreshold: 5
			readinessProbe:
			  httpGet:
				path: /readiness
				port: 8081
				scheme: HTTP
			  # we poll on pod startup for the Kubernetes master service and
			  # only setup the /readiness HTTP server once that's available.
			  initialDelaySeconds: 3
			  timeoutSeconds: 5
			args:
			- --domain=cluster.local.
			- --dns-port=10053
			- --config-dir=/kube-dns-config
			- --v=2
			env:
			- name: PROMETHEUS_PORT
			  value: "10055"
			ports:
			- containerPort: 10053
			  name: dns-local
			  protocol: UDP
			- containerPort: 10053
			  name: dns-tcp-local
			  protocol: TCP
			- containerPort: 10055
			  name: metrics
			  protocol: TCP
			volumeMounts:
			- name: kube-dns-config
			  mountPath: /kube-dns-config
		  - name: dnsmasq
			image: registry.cn-hangzhou.aliyuncs.com/google_containers/k8s-dns-dnsmasq-nanny-amd64:1.14.7
			livenessProbe:
			  httpGet:
				path: /healthcheck/dnsmasq
				port: 10054
				scheme: HTTP
			  initialDelaySeconds: 60
			  timeoutSeconds: 5
			  successThreshold: 1
			  failureThreshold: 5
			args:
			- -v=2
			- -logtostderr
			- -configDir=/etc/k8s/dns/dnsmasq-nanny
			- -restartDnsmasq=true
			- --
			- -k
			- --cache-size=1000
			- --no-negcache
			- --log-facility=-
			- --server=/cluster.local/127.0.0.1#10053
			- --server=/in-addr.arpa/127.0.0.1#10053
			- --server=/ip6.arpa/127.0.0.1#10053
			ports:
			- containerPort: 53
			  name: dns
			  protocol: UDP
			- containerPort: 53
			  name: dns-tcp
			  protocol: TCP
			# see: https://github.com/kubernetes/kubernetes/issues/29055 for details
			resources:
			  requests:
				cpu: 150m
				memory: 20Mi
			volumeMounts:
			- name: kube-dns-config
			  mountPath: /etc/k8s/dns/dnsmasq-nanny
		  - name: sidecar
			image: registry.cn-hangzhou.aliyuncs.com/google_containers/k8s-dns-sidecar-amd64:1.14.7
			livenessProbe:
			  httpGet:
				path: /metrics
				port: 10054
				scheme: HTTP
			  initialDelaySeconds: 60
			  timeoutSeconds: 5
			  successThreshold: 1
			  failureThreshold: 5
			args:
			- --v=2
			- --logtostderr
			- --probe=kubedns,127.0.0.1:10053,kubernetes.default.svc.cluster.local,5,SRV
			- --probe=dnsmasq,127.0.0.1:53,kubernetes.default.svc.cluster.local,5,SRV
			ports:
			- containerPort: 10054
			  name: metrics
			  protocol: TCP
			resources:
			  requests:
				memory: 20Mi
				cpu: 10m
		  dnsPolicy: Default  # Don't use cluster DNS.
		  serviceAccountName: kube-dns

### 启动一个测试的Pod资源用于测试DNS解析（busybox容器，用低于1.29版本的busybox测试，高于1.29版本的使用nslookup无法解析获取ip地址）

	[root@localhost pod]# kubectl exec -it busybox -- nslookup kubernetes.default
	Server:    10.0.0.2
	Address 1: 10.0.0.2 kube-dns.kube-system.svc.cluster.local

	Name:      kubernetes.default
	Address 1: 10.0.0.1 kubernetes.default.svc.cluster.local
	[root@localhost pod]# kubectl exec -it busybox -- nslookup nginx-svc.default
	Server:    10.0.0.2
	Address 1: 10.0.0.2 kube-dns.kube-system.svc.cluster.local

	Name:      nginx-svc.default
	Address 1: 10.0.0.132 nginx-svc.default.svc.cluster.local
	[root@localhost pod]# kubectl exec -it busybox -- nslookup nginx-svc
	Server:    10.0.0.2
	Address 1: 10.0.0.2 kube-dns.kube-system.svc.cluster.local

	Name:      nginx-svc
	Address 1: 10.0.0.132 nginx-svc.default.svc.cluster.local
	[root@localhost pod]# 