#### 配置任意一台服务器当控制器来允许远程连入我们的k8s集群，允许通过apiserver操控整个集群（本例中以我平时常用的服务器为例：192.168.200.111）
#### 这样的话我们就无需登陆到k8s集群的服务器上去操作集群，而是可以通过远程操作的方式操作

##### 1、拷贝可执行文件以及相关的证书文件到该服务器中

	[root@localhost ~]# scp /opt/kubernetes/ssl/ca*pem root@192.168.200.111:/opt/kubernetes/ssl/
	root@192.168.200.111's password: 
	ca-key.pem                                                                                                                                                         100% 1675     3.3MB/s   00:00    
	ca.pem                                                                                                                                                             100% 1354     3.1MB/s   00:00    
	[root@localhost ~]# scp /opt/local/k8s/pki/apiserver/admin*pem root@192.168.200.111:/opt/kubernetes/ssl/
	root@192.168.200.111's password: 
	admin-key.pem                                                                                                                                                      100% 1675    59.2KB/s   00:00    
	admin.pem                                                                                                                                                          100% 1395   191.6KB/s   00:00    
	[root@localhost ~]# scp /opt/kubernetes/bin/kubectl root@192.168.200.111:/usr/local/bin
	root@192.168.200.111's password: 
	kubectl                                                                                                                                                            100%   55MB  56.1MB/s   00:00    
	[root@localhost ~]# 

##### 2、手动生成kubectl执行需要的配置文件（在192.168.200.111上执行操作）

	[root@localhost ~]# cd /opt/kubernetes/ssl/
	[root@localhost ssl]# kubectl config set-cluster kubernetes --server=https://192.168.200.142:6443 --certificate-authority=ca.pem 
	Cluster "kubernetes" set.
	[root@localhost ssl]# kubectl config set-credentials cluster-admin --certificate-authority=ca.pem --client-key=admin-key.pem --client-certificate=admin.pem 
	User "cluster-admin" set.
	[root@localhost ssl]# kubectl config set-context default --cluster=kubernetes --user=cluster-admin
	Context "default" created.
	[root@localhost ssl]# kubectl config use-context default
	Switched to context "default".
	[root@localhost ssl]# cat /root/.kube/config
	apiVersion: v1
	clusters:
	- cluster:
		certificate-authority: /opt/kubernetes/ssl/ca.pem
		server: https://192.168.200.142:6443
	  name: kubernetes
	contexts:
	- context:
		cluster: kubernetes
		user: cluster-admin
	  name: default
	current-context: default
	kind: Config
	preferences: {}
	users:
	- name: cluster-admin
	  user:
		client-certificate: /opt/kubernetes/ssl/admin.pem
		client-key: /opt/kubernetes/ssl/admin-key.pem
	[root@localhost ssl]# 

##### 3、在192.168.200.111这台远程服务器上测试kubectl的使用情况

	[root@localhost ssl]# kubectl get nodes
	NAME              STATUS   ROLES    AGE   VERSION
	192.168.200.117   Ready    <none>   2d    v1.12.2
	192.168.200.118   Ready    <none>   2d    v1.12.2
	[root@localhost ssl]# kubectl get pods
	NAME                    READY   STATUS    RESTARTS   AGE
	nginx-dbddb74b8-2rpt2   1/1     Running   0          21h
	nginx-dbddb74b8-2zl2m   1/1     Running   0          21h
	nginx-dbddb74b8-4n6sm   1/1     Running   0          21h
	[root@localhost ssl]# kubectl get secret -n kube-system
	NAME                               TYPE                                  DATA   AGE
	dashboard-admin-token-xlxdp        kubernetes.io/service-account-token   3      64m
	default-token-pjzwj                kubernetes.io/service-account-token   3      2d1h
	kubernetes-dashboard-certs         Opaque                                0      3h48m
	kubernetes-dashboard-key-holder    Opaque                                2      3h48m
	kubernetes-dashboard-token-kdlpb   kubernetes.io/service-account-token   3      3h45m
	[root@localhost ssl]# 

##### 5、接下来我们只需要将如下的这些文件打包拷贝到任意一台服务器上相应的目录下即可访问我们的k8s集群

	[root@localhost .kube]# ll /root/.kube/config 
	-rw------- 1 root root 430 Nov 23 15:29 /root/.kube/config
	[root@localhost .kube]# ll /opt/kubernetes/ssl/
	total 16
	-rw------- 1 root root 1675 Nov 23 15:22 admin-key.pem
	-rw-r--r-- 1 root root 1395 Nov 23 15:22 admin.pem
	-rw------- 1 root root 1675 Nov 23 15:21 ca-key.pem
	-rw-r--r-- 1 root root 1354 Nov 23 15:21 ca.pem
	[root@localhost .kube]# 
