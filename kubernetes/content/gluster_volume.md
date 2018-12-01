#### 一、gluster集群部署

- 参考文档：https://docs.gluster.org/en/latest/Quick-Start-Guide/Quickstart/

##### 1、部署gluster数据卷最好单独存放到一个磁盘分区中，我们这边新添加一块分区用作数据卷（/dev/sdb1）
##### 将新分区格式化成xfs并挂载到指定目录，添加到开机自动挂载中

	mkfs.xfs -i size=512 /dev/sdb1 
	mkdir /data/brick1 -p
	echo '/dev/sdb1 /data/brick1 xfs defaults 1 2' >> /etc/fstab 
	mount -a && mount
	
##### 2、安装glusterfs-server

    yum install centos-release-gluster
    yum install -y glusterfs glusterfs-server glusterfs-fuse glusterfs-rdma
    
##### 3、启动glusterd并加入到开机启动中

    systemctl enable glusterd
    systemctl start glusterd
    systemctl status glusterd
    
##### 4、添加hosts绑定到集群所有节点上，方便gluster集群的部署

    192.168.200.134 gluster01
    192.168.200.135 gluster02

##### 5、这边把防火墙相关的先关了

    setenforce 0
    iptables -F
    systemctl stop firewalld
    
##### 6、在任一gluster节点上将其它gluster节点添加进集群中（在gluster01上操作），并查看添加后详细信息

    gluster peer probe gluster02
    gluster peer status
    

##### 7、删除节点

    gluster peer detach gluster02
    
##### 8、使用：需要在所有的k8s的node节点上安装gluster客户端工具

    yum install -y glusterfs glusterfs-fuse

##### 9、创建存储数据的目录并加入到gluster集群中(其中replica数量可以根据集群数来设定)

    mkdir -p /data/brick1/gv0
    gluster volume create gv0 replica 2 gluster01:/data/brick1/gv0 gluster02:/data/brick1/gv0
    gluster volume start gv0
    gluster volume info

- 接下来就可以使用gluster集群的存储功能了

#### 二、部署k8s集群使用gluster集群

- 参考文档： https://github.com/kubernetes/kubernetes/tree/8fd414537b5143ab039cb910590237cabf4af783/examples/volumes/glusterfs

##### 1、启动glusterfs-endpoints.json

	[root@localhost gluster]# cat glusterfs-endpoints.json 
	{
	  "kind": "Endpoints",
	  "apiVersion": "v1",
	  "metadata": {
		"name": "glusterfs-cluster"
	  },
	  "subsets": [
		{
		  "addresses": [
			{
			  "ip": "192.168.200.134"
			}
		  ],
		  "ports": [
			{
			  "port": 1
			}
		  ]
		},
		{
		  "addresses": [
			{
			  "ip": "192.168.200.135"
			}
		  ],
		  "ports": [
			{
			  "port": 1
			}
		  ]
		}
	  ]
	}
	[root@localhost gluster]# kubectl apply -f glusterfs-endpoints.json 
	endpoints/glusterfs-cluster created
	[root@localhost gluster]# kubectl get ep -o wide
	NAME                ENDPOINTS                                   AGE
	glusterfs-cluster   192.168.200.134:1,192.168.200.135:1         8s
	kubernetes          192.168.200.111:6443,192.168.200.116:6443   7d20h
	[root@localhost gluster]# 
	
##### 2、启动glusterfs-service.json

	[root@localhost gluster]# cat glusterfs-service.json 
	{
	  "kind": "Service",
	  "apiVersion": "v1",
	  "metadata": {
		"name": "glusterfs-cluster"
	  },
	  "spec": {
		"ports": [
		  {"port": 1}
		]
	  }
	}
	[root@localhost gluster]# kubectl apply -f glusterfs-service.json 
	service/glusterfs-cluster created
	[root@localhost gluster]# kubectl get svc -o wide
	NAME                TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE     SELECTOR
	glusterfs-cluster   ClusterIP   10.0.0.108   <none>        1/TCP     4s      <none>
	kubernetes          ClusterIP   10.0.0.1     <none>        443/TCP   7d20h   <none>
	[root@localhost gluster]# 

#### 三、测试k8s使用gluster集群做存储卷

##### 1、现在node节点做个简单的数据卷挂载测试

	[root@localhost ~]# mount -t glusterfs gluster01:/gv0 /mnt/
	[root@localhost ~]# cd /mnt/
	[root@localhost mnt]# echo "hello gluster." > index.html

- 测试观察在node挂载的mnt目录下创建的文件在gluster集群所有节点中都会同步过来，说明集群创建成功，并且k8s使用gluster集群做存储也是正常的

##### 2、创建k8s资源使用gluster集群挂载

	[root@localhost gluster]# cat deploy-gluster.yaml 
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
			- name: glusterfsvol
			  mountPath: /usr/share/nginx/html
			ports:
			- containerPort: 80
		  volumes:
		  - name: glusterfsvol
			glusterfs:
			  endpoints: glusterfs-cluster
			  path: gv0
			  readOnly: false
	---
	apiVersion: v1
	kind: Service
	metadata:
	  name: nginx-service
	spec:
	  selector:
		app: nginx
	  ports:
	  - name: http
		port: 80
		protocol: TCP
		targetPort: 80
	  type: NodePort
	[root@localhost gluster]# kubectl apply -f deploy-gluster.yaml 
	deployment.extensions/nginx-deployment created
	service/nginx-service created
	[root@localhost gluster]# kubectl get pods
	NAME                                READY   STATUS    RESTARTS   AGE
	nginx-deployment-7549cc478b-6qw55   1/1     Running   0          16s
	nginx-deployment-7549cc478b-g624m   1/1     Running   0          16s
	nginx-deployment-7549cc478b-rc8jh   1/1     Running   0          16s
	[root@localhost gluster]# kubectl get svc
	NAME                TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)        AGE
	glusterfs-cluster   ClusterIP   10.0.0.108   <none>        1/TCP          28m
	kubernetes          ClusterIP   10.0.0.1     <none>        443/TCP        7d21h
	nginx-service       NodePort    10.0.0.160   <none>        80:48438/TCP   20s
	[root@localhost gluster]# 
	
##### 3、测试集群挂载情况

    [root@localhost mnt]# curl 10.0.0.160
    hello gluster.
    [root@localhost mnt]# 
    
- 观察发现该index.html为我们上面再gluster集群添加进去的文件，测试k8s使用gluster集群正常