#### Ingress部署步骤

- 部署Default Backend
- 部署Ingress Controller
- 部署Ingress
- 部署Ingress TLS

#### Ingress介绍图

![image](https://github.com/hdpingshao/ops/blob/master/kubernetes/images/7-1.jpg)

#### Ingress部署

##### 部署Ingress组件的配置文件准备

    wget https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/mandatory.yaml
    wget https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/provider/baremetal/service-nodeport.yaml
    
- 注意：需修改国内镜像下载地址(registry.cn-hangzhou.aliyuncs.com/google_containers/nginx-ingress-controller:0.21.0)
- 官方文档：https://github.com/kubernetes/ingress-nginx/tree/master/deploy

##### 部署

	[root@localhost deploy]# kubectl apply -f mandatory.yaml 
	namespace/ingress-nginx created
	configmap/nginx-configuration created
	serviceaccount/nginx-ingress-serviceaccount created
	clusterrole.rbac.authorization.k8s.io/nginx-ingress-clusterrole created
	role.rbac.authorization.k8s.io/nginx-ingress-role created
	rolebinding.rbac.authorization.k8s.io/nginx-ingress-role-nisa-binding created
	clusterrolebinding.rbac.authorization.k8s.io/nginx-ingress-clusterrole-nisa-binding created
	deployment.extensions/nginx-ingress-controller created
	[root@localhost deploy]# 
	[root@localhost deploy]# kubectl apply -f ../../service-nodeport.yaml 
	service/ingress-nginx created
	[root@localhost deploy]# kubectl get svc -n ingress-nginx
	NAME            TYPE       CLUSTER-IP   EXTERNAL-IP   PORT(S)                      AGE
	ingress-nginx   NodePort   10.0.0.185   <none>        80:35621/TCP,443:47037/TCP   10s
	[root@localhost deploy]# kubectl get deploy -n ingress-nginx
	NAME                       DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
	nginx-ingress-controller   1         1         1            1           38s
	[root@localhost deploy]# kubectl get pods -n ingress-nginx
	NAME                                        READY   STATUS    RESTARTS   AGE
	nginx-ingress-controller-6b66d9cb7d-whhc4   1/1     Running   0          43s
	[root@localhost deploy]# 

#### 部署完成
