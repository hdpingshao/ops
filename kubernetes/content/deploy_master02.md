#### 1、将部署Master组件所需的配置文件从Master01拷贝到Master02上，做相关IP地址的修改

	[root@localhost ~]# scp -r /opt/kubernetes root@192.168.200.116:/opt/
	root@192.168.200.116's password: 
	kube-apiserver                                                                                                                                                     100%  184MB 127.2MB/s   00:01    
	kubectl                                                                                                                                                            100%   55MB 141.4MB/s   00:00    
	kube-controller-manager                                                                                                                                            100%  155MB  38.9MB/s   00:04    
	kube-scheduler                                                                                                                                                     100%   55MB  54.5MB/s   00:01    
	token.csv                                                                                                                                                          100%   84   235.3KB/s   00:00    
	kube-apiserver                                                                                                                                                     100%  939     2.5MB/s   00:00    
	kube-controller-manager                                                                                                                                            100%  483     1.2MB/s   00:00    
	kube-scheduler                                                                                                                                                     100%   94   324.7KB/s   00:00    
	ca-key.pem                                                                                                                                                         100% 1675     4.9MB/s   00:00    
	ca.pem                                                                                                                                                             100% 1354     4.2MB/s   00:00    
	server-key.pem                                                                                                                                                     100% 1675     5.0MB/s   00:00    
	server.pem                                                                                                                                                         100% 1639     4.9MB/s   00:00    
	[root@localhost ~]# scp /usr/lib/systemd/system/{kube-apiserver,kube-scheduler,kube-controller-manager}.service root@192.168.200.116:/usr/lib/systemd/system
	root@192.168.200.116's password: 
	kube-apiserver.service                                                                                                                                             100%  282   524.1KB/s   00:00    
	kube-scheduler.service                                                                                                                                             100%  281   263.2KB/s   00:00    
	kube-controller-manager.service                                                                                                                                    100%  317   889.1KB/s   00:00    
	[root@localhost ~]# 

#### 2、配置文件修改完成即可启动Master02相关组件，并检查启动是否正常

	[root@localhost cfg]# systemctl start kube-apiserver
	[root@localhost cfg]# ps aux | grep apiserver
	root     11830  110  6.8 353792 264880 ?       Ssl  11:08   0:07 /opt/kubernetes/bin/kube-apiserver --logtostderr=true --v=4 --etcd-servers=https://192.168.200.111:2379,https://192.168.200.116:2379,https://192.168.200.117:2379 --bind-address=192.168.200.116 --secure-port=6443 --advertise-address=192.168.200.116 --allow-privileged=true --service-cluster-ip-range=10.0.0.0/24 --enable-admission-plugins=NamespaceLifecycle,LimitRanger,ServiceAccount,ResourceQuota,NodeRestriction --authorization-mode=RBAC,Node --kubelet-https=true --enable-bootstrap-token-auth --token-auth-file=/opt/kubernetes/cfg/token.csv --service-node-port-range=30000-50000 --tls-cert-file=/opt/kubernetes/ssl/server.pem --tls-private-key-file=/opt/kubernetes/ssl/server-key.pem --client-ca-file=/opt/kubernetes/ssl/ca.pem --service-account-key-file=/opt/kubernetes/ssl/ca-key.pem --etcd-cafile=/opt/etcd/ssl/ca.pem --etcd-certfile=/opt/etcd/ssl/server.pem --etcd-keyfile=/opt/etcd/ssl/server-key.pem
	root     11840  0.0  0.0 112720   984 pts/0    R+   11:08   0:00 grep --color=auto apiserver
	[root@localhost cfg]# systemctl start kube-controller-manager
	[root@localhost cfg]# ps aux | grep controller
	root     11847 23.5  1.1 109560 43676 ?        Ssl  11:09   0:01 /opt/kubernetes/bin/kube-controller-manager --logtostderr=true --v=4 --master=127.0.0.1:8080 --leader-elect=true --address=127.0.0.1 --service-cluster-ip-range=10.0.0.0/24 --cluster-name=kubernetes --cluster-signing-cert-file=/opt/kubernetes/ssl/ca.pem --cluster-signing-key-file=/opt/kubernetes/ssl/ca-key.pem --root-ca-file=/opt/kubernetes/ssl/ca.pem --service-account-private-key-file=/opt/kubernetes/ssl/ca-key.pem --experimental-cluster-signing-duration=87600h0m0s
	root     11855  0.0  0.0 112720   988 pts/0    S+   11:09   0:00 grep --color=auto controller
	[root@localhost cfg]# systemctl start kube-scheduler
	[root@localhost cfg]# ps aux | grep scheduler
	root     11862  1.3  0.5  45616 19828 ?        Ssl  11:09   0:00 /opt/kubernetes/bin/kube-scheduler --logtostderr=true --v=4 --master=127.0.0.1:8080 --leader-elect
	root     11872  0.0  0.0 112720   984 pts/0    S+   11:09   0:00 grep --color=auto scheduler
	[root@localhost cfg]# 
	
#### 3、检查Master02启动的集群状态

	[root@localhost cfg]# /opt/kubernetes/bin/kubectl get cs
	NAME                 STATUS    MESSAGE             ERROR
	scheduler            Healthy   ok                  
	controller-manager   Healthy   ok                  
	etcd-0               Healthy   {"health":"true"}   
	etcd-2               Healthy   {"health":"true"}   
	etcd-1               Healthy   {"health":"true"}   
	[root@localhost cfg]# /opt/kubernetes/bin/kubectl get nodes
	NAME              STATUS   ROLES    AGE   VERSION
	192.168.200.117   Ready    <none>   19h   v1.12.2
	192.168.200.118   Ready    <none>   19h   v1.12.2
	[root@localhost cfg]# 
	
#### 补充：K8S所有的集群状态都是保存在etcd数据库中的，所以说只要能连到etcd数据库集群就能获取到整个集群的所有信息（比如在本例中的两个node节点我们都只配置了指向连接到Master01的节点，没有指向到Master02节点，但是Master02节点只要组件启动成功，能连接到etcd数据库集群仍然可以直接获取node的节点信息，就是因为可以从etcd数据库集群中获取到这些保存的信息）。