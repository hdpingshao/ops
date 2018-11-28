#### emptyDir本地数据卷

	[root@localhost volume]# cat redis-pod.yaml 
	apiVersion: v1
	kind: Pod
	metadata:
	  name: redis-pod
	spec:
	  containers:
	  - image: redis
		name: redis
		volumeMounts:
		- mountPath: /cache
		  name: cache-volume
	  volumes:
	  - name: cache-volume
		emptyDir: {}
	[root@localhost volume]# kubectl create -f redis-pod.yaml 
	pod/redis-pod created
	[root@localhost volume]# kubectl get pods -o wide
	NAME                    READY   STATUS              RESTARTS   AGE   IP            NODE              NOMINATED NODE
	httpd-7db5849b8-hdswc   1/1     Running             0          20h   172.17.75.3   192.168.200.117   <none>
	nginx-dbddb74b8-kp5h2   1/1     Running             0          20h   172.17.75.2   192.168.200.117   <none>
	redis-pod               0/1     ContainerCreating   0          7s    <none>        192.168.200.117   <none>
	[root@localhost volume]# kubectl exec -it redis-pod -- /bin/bash
	root@redis-pod:/data# ls /cache/
	root@redis-pod:/data# mount | grep cache
    /dev/mapper/centos-root on /cache type xfs (rw,relatime,seclabel,attr2,inode64,noquota)
    root@redis-pod:/data# 
	
#### hostPath挂载本地数据卷

	[root@localhost volume]# cat test-pod.yaml 
	apiVersion: v1
	kind: Pod
	metadata:
	  name: test-pod
	spec:
	  containers:
	  - image: nginx
		name: test-container
		volumeMounts:
		- mountPath: /test-pod
		  name: test-volume
	  volumes:
	  - name: test-volume
		hostPath:
		  path: /tmp
		  type: Directory
	[root@localhost volume]# 
	[root@localhost volume]# kubectl apply -f test-pod.yaml 
	pod/test-pod created
	[root@localhost volume]# kubectl get pods -o wide
	NAME                    READY   STATUS    RESTARTS   AGE   IP            NODE              NOMINATED NODE
	httpd-7db5849b8-hdswc   1/1     Running   0          20h   172.17.75.3   192.168.200.117   <none>
	nginx-dbddb74b8-kp5h2   1/1     Running   0          20h   172.17.75.2   192.168.200.117   <none>
	redis-pod               1/1     Running   0          11m   172.17.75.5   192.168.200.117   <none>
	test-pod                1/1     Running   0          48s   172.17.65.2   192.168.200.118   <none>
	[root@localhost volume]# kubectl exec -it test-pod -- /bin/bash
	root@test-pod:/# ls /test-pod/
	ks-script-H1fWpo                                                         systemd-private-9c55ca95ba214c25b493e53ee801fa21-chronyd.service-Bu1zUV  yum.log
	systemd-private-839e4d32c9c640e790dab2537a42afc3-chronyd.service-vMsLjk  systemd-private-b94cf72c12e54a8f8d8e6e824edc14a0-chronyd.service-ITnbyw
	root@test-pod:/# mount | grep test-volume
	root@test-pod:/# mount | grep test-pod   
	/dev/mapper/centos-root on /test-pod type xfs (rw,relatime,seclabel,attr2,inode64,noquota)
	root@test-pod:/# 
	
##### 观察发现/test-pod目录下的内容即为192.168.200.118这台node节点上的/tmp下的内容，在该tmp目录下添加删除文件都会及时同步到容器中的/test-pod目录下