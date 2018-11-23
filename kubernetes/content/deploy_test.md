#### 创建一个deployment以及为这个deployment创建service

    # kubectl run nginx --image=nginx --replicas=3
    # kubectl get pods
    # kubectl expose deployment nginx --port=88 --target-port=80 --type=NodePort
    # kubectl get svc nginx

#### 当使用logs查看每个pod的日志时会提示你登陆，这是因为我们kubelet未开启匿名用户（node节点上的kubelet除了管理控制pod之外还会收集pod的信息提供给apiserver）

    [root@localhost ~]# kubectl logs nginx-dbddb74b8-2rpt2
    error: You must be logged in to the server (the server has asked for the client to provide credentials ( pods/log nginx-dbddb74b8-2rpt2))
    [root@localhost ~]# 
    
#### 在node节点上开启kubelet允许匿名用户获取信息，修改kubelet.config配置文件，然后重启kubelet组件

	[root@localhost ~]# cat /opt/kubernetes/cfg/kubelet.config 
	kind: KubeletConfiguration
	apiVersion: kubelet.config.k8s.io/v1beta1
	address: 192.168.200.117
	port: 10250
	cgroupDriver: cgroupfs
	clusterDNS:
	- 10.0.0.2 
	clusterDomain: cluster.local.
	failSwapOn: false
	authentication:
	  anonymous:
		enabled: true
	[root@localhost ~]# 
	[root@localhost ~]# systemctl restart kubelet
	[root@localhost ~]# ps axu | grep kubelet
	root      8631  8.8  1.5 631816 61516 ?        Ssl  10:59   0:00 /opt/kubernetes/bin/kubelet --logtostderr=true --v=4 --address=192.168.200.117 --hostname-override=192.168.200.117 --kubeconfig=/opt/kubernetes/cfg/kubelet.kubeconfig --experimental-bootstrap-kubeconfig=/opt/kubernetes/cfg/bootstrap.kubeconfig --config=/opt/kubernetes/cfg/kubelet.config --cert-dir=/opt/kubernetes/ssl --pod-infra-container-image=registry.cn-hangzhou.aliyuncs.com/google-containers/pause-amd64:3.0
	root      8753  0.0  0.0 112720   980 pts/0    S+   10:59   0:00 grep --color=auto kubelet
	[root@localhost ~]# 

#### 在master节点上再次查看pod的日志信息时提示权限不够，因为我们未给anonymous这个用户绑定权限组，所以权限不够

	[root@localhost ~]# kubectl logs nginx-dbddb74b8-2rpt2
	Error from server (Forbidden): Forbidden (user=system:anonymous, verb=get, resource=nodes, subresource=proxy) ( pods/log nginx-dbddb74b8-2rpt2)
	[root@localhost ~]# 

#### 给anonymous匿名用户赋予相应的权限，将anonymous匿名用户绑定到系统已有角色权限上去

	[root@localhost ~]# kubectl create clusterrolebinding cluster-system-anonymous --clusterrole=cluster-admin --user=system:anonymous
	clusterrolebinding.rbac.authorization.k8s.io/cluster-system-anonymous created
	[root@localhost ~]# 

#### 再次查看pod的日志信息（正常显示日志信息）

	[root@localhost ~]# kubectl get pods
	NAME                    READY   STATUS    RESTARTS   AGE
	nginx-dbddb74b8-2rpt2   1/1     Running   0          17h
	nginx-dbddb74b8-2zl2m   1/1     Running   0          17h
	nginx-dbddb74b8-4n6sm   1/1     Running   0          17h
	[root@localhost ~]# kubectl logs nginx-dbddb74b8-2rpt2
	172.17.75.1 - - [22/Nov/2018:09:56:44 +0000] "GET / HTTP/1.1" 200 612 "-" "curl/7.29.0" "-"
	172.17.75.1 - - [22/Nov/2018:09:56:55 +0000] "GET / HTTP/1.1" 200 612 "-" "curl/7.29.0" "-"
	[root@localhost ~]# 