#### PersistentVolumes介绍

- PersistentVolume(PV，持久卷)：对存储抽象实现，使得存储作为集群中的资源
- PersistentVolumeClaim(PVC，持久卷申请)：PVC消费PV的资源。
- Pod申请PVC作为卷来使用，集群通过PVC查找绑定的PV，并Mount给Pod。

PV支持的类型：

	GCEPersistentDisk
	AWSElasticBlockStore
	AzureFile
	AzureDisk
	FC (Fibre Channel)
	FlexVolume
	Flocker
	NFS
	iSCSI
	RBD (Ceph Block Device)
	CephFS
	Cinder (OpenStack block storage)
	Glusterfs
	VsphereVolume
	Quobyte Volumes
	HostPath
	VMware Photon
	Portworx Volumes
	ScaleIO Volumes
	StorageOS

##### 1、PV三种模式：

- ReadWriteOnce：针对Pod部署的node节点读写权限
- ReadOnlyMany：针对所有节点只读权限
- ReadWriteMany：针对所有节点读写权限

##### 2、PV回收策略

- Retain：保留PV，并保留PV里存储的数据（默认）
- Recyle：保留PV，并清除PV里存储的数据
- Delete：删除PV及PV里存储的数据

##### 3、PV的四种状态

- Available：可用状态
- Bound：已绑定PVC状态
- Released：释放状态
- Failed：不可用状态

#### PersistentVolumes使用

##### 1、创建类型为nfs的PV

	[root@localhost gluster]# cat nfs-pv.yaml 
	apiVersion: v1
	kind: PersistentVolume
	metadata:
	  name: nfs-pv
	spec:
	  capacity:
		storage: 5Gi
	  accessModes:
	  - ReadWriteMany
	  persistentVolumeReclaimPolicy: Recycle
	  nfs:
		path: /opt/nfs/data
		server: 192.168.200.134
	[root@localhost gluster]# kubectl apply -f nfs-pv.yaml 
	persistentvolume/nfs-pv created
	[root@localhost gluster]# kubectl get pv
	NAME     CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS   REASON   AGE
	nfs-pv   5Gi        RWX            Recycle          Available                                   7s
	[root@localhost gluster]# 

##### 2、创建类型为gluster的PV

	[root@localhost gluster]# cat gluster-pv.yaml 
	apiVersion: v1
	kind: PersistentVolume
	metadata:
	  name: gluster-pv01
	spec:
	  capacity:
		storage: 10Gi
	  accessModes:
	  - ReadWriteMany
	  glusterfs:
		endpoints: "glusterfs-cluster"
		path: "gv0"
		readOnly: false
	[root@localhost gluster]# kubectl apply -f gluster-pv.yaml 
	persistentvolume/gluster-pv01 created
	[root@localhost gluster]# kubectl get pv
	NAME           CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS   REASON   AGE
	gluster-pv01   10Gi       RWX            Retain           Available                                   7s
	nfs-pv         5Gi        RWX            Recycle          Available                                   5m21s
	[root@localhost gluster]# 
	
##### 3、创建PVC自动分配绑定PV（消费PV）

	[root@localhost gluster]# cat nfs-pvc.yaml 
	apiVersion: v1
	kind: PersistentVolumeClaim
	metadata:
	  name: nginx-pvc001
	spec:
	  accessModes:
	  - ReadWriteMany
	  resources:
		requests:
		  storage: 5Gi
	[root@localhost gluster]# kubectl apply -f nfs-pvc.yaml 
	persistentvolumeclaim/nginx-pvc001 created
	[root@localhost gluster]# kubectl get pv,pvc
	NAME                            CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM                  STORAGECLASS   REASON   AGE
	persistentvolume/gluster-pv01   10Gi       RWX            Retain           Available                                                  8m22s
	persistentvolume/gluster-pv02   20Gi       RWX            Retain           Available                                                  7m16s
	persistentvolume/nfs-pv         5Gi        RWX            Recycle          Bound       default/nginx-pvc001                           13m

	NAME                                 STATUS   VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
	persistentvolumeclaim/nginx-pvc001   Bound    nfs-pv   5Gi        RWX                           4s
	[root@localhost gluster]# 
	
##### 4、创建Pod测试绑定刚刚PVC申请的NFS存储

	[root@localhost gluster]# cat nginx-pv.yaml 
	apiVersion: v1
	kind: Pod
	metadata:
	  name: mypod
	spec:
	  containers:
	  - name: nginx
		image: nginx
		volumeMounts:
		- mountPath: "/usr/share/nginx/html"
		  name: wwwroot
	  volumes:
	  - name: wwwroot
		persistentVolumeClaim:
		  claimName: nginx-pvc001
	[root@localhost gluster]# kubectl apply -f nginx-pv.yaml 
	pod/mypod created
	[root@localhost gluster]# kubectl get pods -o wide
	NAME    READY   STATUS    RESTARTS   AGE   IP            NODE              NOMINATED NODE
	mypod   1/1     Running   0          22s   172.17.75.2   192.168.200.117   <none>
	[root@localhost gluster]# 
	
	在node节点上测试数据是否挂载上来
	[root@localhost ~]# curl 172.17.75.2
	hello NFS.html.
	[root@localhost ~]# 
	
##### 5、测试Recycle回收策略

	[root@localhost ~]# kubectl get pv,pvc
	NAME                            CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM                  STORAGECLASS   REASON   AGE
	persistentvolume/gluster-pv01   10Gi       RWX            Retain           Available                                                  127m
	persistentvolume/gluster-pv02   20Gi       RWX            Retain           Available                                                  126m
	persistentvolume/nfs-pv         5Gi        RWX            Recycle          Bound       default/nginx-pvc001                           132m

	NAME                                 STATUS   VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
	persistentvolumeclaim/nginx-pvc001   Bound    nfs-pv   5Gi        RWX                           119m
	[root@localhost ~]# kubectl get pods
	NAME    READY   STATUS    RESTARTS   AGE
	mypod   1/1     Running   0          13s
	[root@localhost ~]# kubectl get pods -o wide
	NAME    READY   STATUS    RESTARTS   AGE   IP            NODE              NOMINATED NODE
	mypod   1/1     Running   0          17s   172.17.75.2   192.168.200.117   <none>
	[root@localhost ~]# kubectl get pv,pvc
	NAME                            CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS   REASON   AGE
	persistentvolume/gluster-pv01   10Gi       RWX            Retain           Available                                   138m
	persistentvolume/gluster-pv02   20Gi       RWX            Retain           Available                                   137m
	persistentvolume/nfs-pv         5Gi        RWX            Recycle          Available                                   143m
	[root@localhost ~]# 

- 进入到nfs存储目录发现目录下的文件全被删除了，也就是说Recycle回收是会删除目录下的文件使得该PV又重新变成新的可用PV（Available）

##### 6、创建pvc

	[root@localhost gluster]# cat gluster-pvc.yaml 
	apiVersion: v1
	kind: PersistentVolumeClaim
	metadata:
	  name: nginx-pvc002
	spec:
	  accessModes:
	  - ReadWriteMany
	  resources:
		requests:
		  storage: 11Gi
	[root@localhost gluster]# kubectl apply -f gluster-pvc.yaml 
	persistentvolumeclaim/nginx-pvc002 created
	[root@localhost gluster]# kubectl get pv,pvc
	NAME                            CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM                  STORAGECLASS   REASON   AGE
	persistentvolume/gluster-pv01   10Gi       RWX            Retain           Available                                                  143m
	persistentvolume/gluster-pv02   20Gi       RWX            Retain           Bound       default/nginx-pvc002                           142m
	persistentvolume/nfs-pv         5Gi        RWX            Recycle          Available                                                  149m

	NAME                                 STATUS   VOLUME         CAPACITY   ACCESS MODES   STORAGECLASS   AGE
	persistentvolumeclaim/nginx-pvc002   Bound    gluster-pv02   20Gi       RWX                           4s
	[root@localhost gluster]# 
	
##### 7、创建Pod测试绑定刚刚PVC申请的gluster存储

	[root@localhost gluster]# cat nginx-gluster-pv.yaml 
	apiVersion: v1
	kind: Pod
	metadata:
	  name: mypod
	spec:
	  containers:
	  - name: nginx
		image: nginx
		volumeMounts:
		- mountPath: "/usr/share/nginx/html"
		  name: wwwroot
	  volumes:
	  - name: wwwroot
		persistentVolumeClaim:
		  claimName: nginx-pvc002
	[root@localhost gluster]# kubectl apply -f nginx-gluster-pv.yaml 
	pod/mypod created
	[root@localhost gluster]# kubectl get pods -o wide
	NAME    READY   STATUS    RESTARTS   AGE   IP            NODE              NOMINATED NODE
	mypod   1/1     Running   0          14s   172.17.75.2   192.168.200.117   <none>
	[root@localhost gluster]# 
	
	测试挂载的数据卷是否正确
	[root@localhost ~]# curl 172.17.75.2
    hello gluster.> 2018/11/29 > 11111111111 > 222222222 > 333333
    [root@localhost ~]# 
    
##### 8、进入Pod容器可以查看挂载情况

	[root@localhost gluster]# kubectl get pods
	NAME    READY   STATUS    RESTARTS   AGE
	mypod   1/1     Running   0          93s
	[root@localhost gluster]# kubectl exec -it mypod -- bash
	root@mypod:/# mount | grep gluster
	192.168.200.134:gv0 on /usr/share/nginx/html type fuse.glusterfs (rw,relatime,user_id=0,group_id=0,default_permissions,allow_other,max_read=131072)
	root@mypod:/# 

#### PV持久卷部署完成