#### 1、k8s Web UI地址

> * https://github.com/kubernetes/kubernetes/tree/master/cluster/addons/dashboard

#### 2、下载dashboard部署所需要的yaml文件（之前下载的apiserver包里面就包含dashboard所需要的yaml文件，直接部署使用即可）

	[root@localhost kubernetes]# cd /opt/local/k8s/soft/kubernetes
	[root@localhost kubernetes]# ls
	addons  kubernetes-src.tar.gz  LICENSES  server
	[root@localhost kubernetes]# tar zxf kubernetes-src.tar.gz 
	[root@localhost kubernetes]# cd cluster/addons/dashboard/
	[root@localhost dashboard]# ls
	dashboard-configmap.yaml  dashboard-controller.yaml  dashboard-rbac.yaml  dashboard-secret.yaml  dashboard-service.yaml  MAINTAINERS.md  OWNERS  README.md
	[root@localhost dashboard]# 
	
##### 下载的时官方的yaml配置文件，所以里面使用的镜像源都是国外的镜像源，国内是无法拉下来的，所以我们需要自己去找国内的镜像源

> * https://dev.aliyun.com/search.html
> * 搜索：kubernetes-dashboard-amd64
> * 镜像仓库地址：registry.cn-hangzhou.aliyuncs.com/google_containers/kubernetes-dashboard-amd64:v1.10.0

#### 3、通过yaml文件部署启动dashboard控制台（按顺序一个个创建）

	[root@localhost kubernetes]# cd /opt/local/k8s/soft/kubernetes
	[root@localhost kubernetes]# ls
	addons  kubernetes-src.tar.gz  LICENSES  server
	[root@localhost kubernetes]# tar zxf kubernetes-src.tar.gz 
	[root@localhost kubernetes]# cd cluster/addons/dashboard/
	[root@localhost dashboard]# ls
	dashboard-configmap.yaml  dashboard-controller.yaml  dashboard-rbac.yaml  dashboard-secret.yaml  dashboard-service.yaml  MAINTAINERS.md  OWNERS  README.md
	[root@localhost dashboard]# kubectl get pods -n kube-system
	NAME                                    READY   STATUS    RESTARTS   AGE
	kubernetes-dashboard-6bff7dc67d-qbhgd   1/1     Running   0          4m10s
	[root@localhost dashboard]# kubectl logs kubernetes-dashboard-6bff7dc67d-qbhgd -n kube-system
	2018/11/23 03:48:51 Using in-cluster config to connect to apiserver
	2018/11/23 03:48:51 Using service account token for csrf signing
	2018/11/23 03:48:51 No request provided. Skipping authorization
	2018/11/23 03:48:51 Starting overwatch
	2018/11/23 03:48:51 Successful initial request to the apiserver, version: v1.12.2
	2018/11/23 03:48:51 Generating JWE encryption key
	2018/11/23 03:48:51 New synchronizer has been registered: kubernetes-dashboard-key-holder-kube-system. Starting
	2018/11/23 03:48:51 Starting secret synchronizer for kubernetes-dashboard-key-holder in namespace kube-system
	2018/11/23 03:48:56 Initializing JWE encryption key from synchronized object
	2018/11/23 03:48:56 Creating in-cluster Heapster client
	2018/11/23 03:48:56 Metric client health check failed: the server could not find the requested resource (get services heapster). Retrying in 30 seconds.
	2018/11/23 03:48:56 Auto-generating certificates
	2018/11/23 03:48:56 Successfully created certificates
	2018/11/23 03:48:56 Serving securely on HTTPS port: 8443

##### github上下载的dashboard的service的yaml配置文件未开启NodePort，我们这边手动修改下，这样才能让外部网络访问到我们的dashboard

	[root@localhost dashboard]# cat dashboard-service.yaml 
	apiVersion: v1
	kind: Service
	metadata:
	  name: kubernetes-dashboard
	  namespace: kube-system
	  labels:
		k8s-app: kubernetes-dashboard
		kubernetes.io/cluster-service: "true"
		addonmanager.kubernetes.io/mode: Reconcile
	spec:
	  type: NodePort
	  selector:
		k8s-app: kubernetes-dashboard
	  ports:
	  - port: 443
		targetPort: 8443
	[root@localhost dashboard]# 
	[root@localhost dashboard]# kubectl create -f dashboard-service.yaml 
	service/kubernetes-dashboard created
	[root@localhost dashboard]# kubectl get svc -n kube-system
	NAME                   TYPE       CLUSTER-IP   EXTERNAL-IP   PORT(S)         AGE
	kubernetes-dashboard   NodePort   10.0.0.231   <none>        443:33592/TCP   13s
	[root@localhost dashboard]# 

##### 此时我们可以通过web使用33592端口从外部网络来访问了（任意一台node节点IP:33592，需要使用https协议访问）

![image](https://github.com/hdpingshao/ops/blob/master/kubernetes/images/2-1.jpg)

#### 4、创建token令牌来进行WEB UI的登陆认证

##### 首先创建一个ServiceAccount并绑定角色组的yaml文件

	[root@localhost dashboard]# cat k8s-admin.yaml 
	apiVersion: v1
	kind: ServiceAccount
	metadata:
	  name: dashboard-admin
	  namespace: kube-system
	---
	kind: ClusterRoleBinding
	apiVersion: rbac.authorization.k8s.io/v1beta1
	metadata:
	  name: dashboard-admin
	subjects:
	  - kind: ServiceAccount
		name: dashboard-admin
		namespace: kube-system
	roleRef:
	  kind: ClusterRole
	  name: cluster-admin
	  apiGroup: rbac.authorization.k8s.io
	[root@localhost dashboard]# 
	
##### 创建sa资源

	[root@localhost dashboard]# kubectl create -f k8s-admin.yaml 
	serviceaccount/dashboard-admin created
	clusterrolebinding.rbac.authorization.k8s.io/dashboard-admin created
	[root@localhost dashboard]# kubectl get secret -n kube-system
	NAME                               TYPE                                  DATA   AGE
	dashboard-admin-token-xlxdp        kubernetes.io/service-account-token   3      14s
	default-token-pjzwj                kubernetes.io/service-account-token   3      2d
	kubernetes-dashboard-certs         Opaque                                0      164m
	kubernetes-dashboard-key-holder    Opaque                                2      164m
	kubernetes-dashboard-token-kdlpb   kubernetes.io/service-account-token   3      161m
	[root@localhost dashboard]# 
	[root@localhost dashboard]# kubectl get sa -n kube-system
	NAME                   SECRETS   AGE
	dashboard-admin        1         91s
	default                1         2d
	kubernetes-dashboard   1         162m
	[root@localhost dashboard]# 

##### 获取用户的token值并复制到WEB UI当作登陆凭证用

	[root@localhost dashboard]# kubectl describe secret dashboard-admin-token-xlxdp -n kube-system
	Name:         dashboard-admin-token-xlxdp
	Namespace:    kube-system
	Labels:       <none>
	Annotations:  kubernetes.io/service-account.name: dashboard-admin
				  kubernetes.io/service-account.uid: 11f19aef-eee9-11e8-8ada-0050568b5e20

	Type:  kubernetes.io/service-account-token

	Data
	====
	token:      eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJkYXNoYm9hcmQtYWRtaW4tdG9rZW4teGx4ZHAiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGFzaGJvYXJkLWFkbWluIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiMTFmMTlhZWYtZWVlOS0xMWU4LThhZGEtMDA1MDU2OGI1ZTIwIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Omt1YmUtc3lzdGVtOmRhc2hib2FyZC1hZG1pbiJ9.HWe-70KeWE6H40nK06CT5GmCAvxaP7Iv7bAjzYu--fzcJQ9GiYAQ7afs62iQjKQSg1KhHENssUNNXiLjiAInWegeMJ6T6NFPKWAFbRx53zglTkbfecKezhJjVQNYmK7E-Cg96GHNEKCKlb8N_lE43VV5tZ2x5Bg3taTWWF5S5qQWy4vY2Wq8kXTx4AaVwMc_nBQpJ6HcFF0XYx_LcoZFtJSeB__uB7ybFbYGQxHDlQw-6I26XEnfk0np8fJMzSSwAEtjH91HCRGWrF_OxTyZuywCyffPz118umh0p4igOCoobuEgq28CyFHx8T_nG1uxk_aPTC01W-WlGbSWHdX2qg
	ca.crt:     1354 bytes
	namespace:  11 bytes
	[root@localhost dashboard]# 
	
##### 登陆认证成功

![image](https://github.com/hdpingshao/ops/blob/master/kubernetes/images/2-2.jpg)