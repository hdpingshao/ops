### NFS网络数据集部署

#### 1、部署一台NFS服务器用于存储数据

    [root@localhost ~]# yum install -y nfs-utils
    [root@localhost data]# systemctl enable rpcbind
    [root@localhost data]# systemctl start rpcbind
    [root@localhost data]# systemctl enable nfs-server
    [root@localhost data]# systemctl start nfs-server
    [root@localhost data]# cat /etc/exports
    /opt/nfs/data 192.168.0.0/16(rw,no_root_squash)
    [root@localhost ~]# ls /opt/nfs/data/
    index.html  index.php
    [root@localhost ~]# cat /opt/nfs/data/index.html 
    hello NFS.html.
    [root@localhost ~]# 

- 记得关闭selinux以及iptables
- 在每个node节点上都需要安装nfs-utils（yum install -y nfs-utils）

#### 2、 启动Deployment控制器测试NFS网络数据卷的使用

	[root@localhost volume]# cat nfs-deploy.yaml 
	apiVersion: extensions/v1beta1
	kind: Deployment
	metadata:
	  name: nginx-deployment
	spec:
	  replicas: 3
	  template:
		metadata:
		  labels:
			app: nginx
		spec:
		  containers:
		  - name: nginx
			image: nginx
			volumeMounts:
			- name: wwwroot
			  mountPath: /usr/share/nginx/html
			ports:
			- containerPort: 80
		  volumes:
		  - name: wwwroot
			nfs:
			  server: 192.168.200.134
			  path: /opt/nfs/data
	[root@localhost volume]# kubectl apply -f nfs-deploy.yaml 
	deployment.extensions/nginx-deployment created
	[root@localhost volume]# kubectl get pods -o wide
	NAME                                READY   STATUS    RESTARTS   AGE   IP            NODE              NOMINATED NODE
	nginx-deployment-69f8b9b8cf-l6wvl   1/1     Running   0          12s   172.17.75.2   192.168.200.117   <none>
	nginx-deployment-69f8b9b8cf-lmk6l   1/1     Running   0          12s   172.17.65.2   192.168.200.118   <none>
	nginx-deployment-69f8b9b8cf-wk2pv   1/1     Running   0          12s   172.17.75.3   192.168.200.117   <none>
	[root@localhost volume]# 

#### 3、在node节点上测试

	[root@localhost ~]# curl 172.17.75.2
	hello NFS.html.
	[root@localhost ~]# curl 172.17.75.3
	hello NFS.html.
	[root@localhost ~]# curl 172.17.65.2
	hello NFS.html.
	[root@localhost ~]# 