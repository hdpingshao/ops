#### 1、在Master01上将kubelet-bootstrap用户绑定到系统集群角色

	[root@localhost bin]# kubectl create clusterrolebinding kubelet-bootstrap --clusterrole=system:node-bootstrapper --user=kubelet-bootstrap
	clusterrolebinding.rbac.authorization.k8s.io/kubelet-bootstrap created
    
#### 2、创建kubeconfig文件

##### 2.1、生成kubeconfig配置文件的脚本供Node节点使用

> * https://github.com/hdpingshao/ops/blob/master/kubernetes/content/kubeconfig.sh

##### 2.2、在Master01上执行该脚本（因为SSL证书都是在该台服务器上生成的，执行脚本过程有用到相应的SSL证书，所以我们在Master01脚本执行，然后再把执行得到的配置文件拷贝到Node节点上）

	[root@localhost soft]# ./kubeconfig.sh 192.168.200.111 /opt/local/k8s/pki/apiserver
	Cluster "kubernetes" set.
	User "kubelet-bootstrap" set.
	Context "default" created.
	Switched to context "default".
	Cluster "kubernetes" set.
	User "kube-proxy" set.
	Context "default" created.
	Switched to context "default".
	[root@localhost soft]# ll *kubeconfig*
	-rw-------. 1 root root 2165 11月 21 14:50 bootstrap.kubeconfig
	-rwxr-xr-x. 1 root root 1611 11月 21 14:40 kubeconfig.sh
	-rw-------. 1 root root 6259 11月 21 14:50 kube-proxy.kubeconfig
	[root@localhost soft]# 
	
#### 3、将可执行文件以及kubeconfig配置文件拷贝到Node节点上准备部署Node节点所需的组件

	[root@localhost soft]# cd /opt/kubernetes/soft/kubernetes/server/bin/
	[root@localhost bin]# ll
	总用量 1821524
	-rwxr-xr-x. 1 root root  60859975 10月 24 15:49 apiextensions-apiserver
	-rwxr-xr-x. 1 root root 142923436 10月 24 15:49 cloud-controller-manager
	-rw-r--r--. 1 root root         8 10月 24 15:44 cloud-controller-manager.docker_tag
	-rw-r--r--. 1 root root 144309760 10月 24 15:44 cloud-controller-manager.tar
	-rwxr-xr-x. 1 root root 248021112 10月 24 15:49 hyperkube
	-rwxr-xr-x. 1 root root  54042644 10月 24 15:49 kubeadm
	-rwxr-xr-x. 1 root root 192781649 10月 24 15:49 kube-apiserver
	-rw-r--r--. 1 root root         8 10月 24 15:44 kube-apiserver.docker_tag
	-rw-r--r--. 1 root root 194167808 10月 24 15:44 kube-apiserver.tar
	-rwxr-xr-x. 1 root root 162961401 10月 24 15:49 kube-controller-manager
	-rw-r--r--. 1 root root         8 10月 24 15:44 kube-controller-manager.docker_tag
	-rw-r--r--. 1 root root 164347392 10月 24 15:44 kube-controller-manager.tar
	-rwxr-xr-x. 1 root root  57352138 10月 24 15:49 kubectl
	-rwxr-xr-x. 1 root root 176648680 10月 24 15:49 kubelet
	-rwxr-xr-x. 1 root root  50330867 10月 24 15:49 kube-proxy
	-rw-r--r--. 1 root root         8 10月 24 15:44 kube-proxy.docker_tag
	-rw-r--r--. 1 root root  98355200 10月 24 15:44 kube-proxy.tar
	-rwxr-xr-x. 1 root root  57184656 10月 24 15:49 kube-scheduler
	-rw-r--r--. 1 root root         8 10月 24 15:44 kube-scheduler.docker_tag
	-rw-r--r--. 1 root root  58570752 10月 24 15:44 kube-scheduler.tar
	-rwxr-xr-x. 1 root root   2330265 10月 24 15:49 mounter
	[root@localhost bin]# scp kubelet kube-proxy root@192.168.200.117:/opt/kubernetes/bin/
	root@192.168.200.117's password: 
	kubelet                                                                                                                                                            100%  168MB 128.5MB/s   00:01    
	kube-proxy                                                                                                                                                         100%   48MB 132.0MB/s   00:00    
	[root@localhost bin]# scp kubelet kube-proxy root@192.168.200.118:/opt/kubernetes/bin/
	The authenticity of host '192.168.200.118 (192.168.200.118)' can't be established.
	ECDSA key fingerprint is SHA256:dw3jNDecw5foFCELxhdiyBJoYd0rOwrvlIJjrWdgev8.
	ECDSA key fingerprint is MD5:3c:d7:ba:9c:ea:86:d3:f3:ee:a7:42:03:a4:b7:2a:97.
	Are you sure you want to continue connecting (yes/no)? yes
	Warning: Permanently added '192.168.200.118' (ECDSA) to the list of known hosts.
	root@192.168.200.118's password: 
	kubelet                                                                                                                                                            100%  168MB 118.9MB/s   00:01    
	kube-proxy                                                                                                                                                         100%   48MB  48.0MB/s   00:01    
	[root@localhost bin]# scp /opt/kubernetes/soft/*kubeconfig root@192.168.200.117:/opt/kubernetes/cfg/
	root@192.168.200.117's password: 
	bootstrap.kubeconfig                                                                                                                                               100% 2165     4.5MB/s   00:00    
	kube-proxy.kubeconfig                                                                                                                                              100% 6259    12.9MB/s   00:00    
	[root@localhost bin]# scp /opt/kubernetes/soft/*kubeconfig root@192.168.200.118:/opt/kubernetes/cfg/
	root@192.168.200.118's password: 
	bootstrap.kubeconfig                                                                                                                                               100% 2165     3.7MB/s   00:00    
	kube-proxy.kubeconfig                                                                                                                                              100% 6259    13.2MB/s   00:00    
	
#### 4、准备kubelet配置文件的脚本

> * https://github.com/hdpingshao/ops/blob/master/kubernetes/content/kubelet.sh

#### 5、准备kube-proxy配置文件的脚本

> * https://github.com/hdpingshao/ops/blob/master/kubernetes/content/kube-proxy.sh

#### 6、执行kubelet.sh脚本文件部署启动kubelet

	[root@localhost k8s]# ./kubelet.sh 192.168.200.117 10.0.0.2
	[root@localhost k8s]# ps aux | grep kubelet
	root      7974  1.5  1.1 321836 43924 ?        Ssl  15:11   0:00 /opt/kubernetes/bin/kubelet --logtostderr=true --v=4 --address=192.168.200.117 --hostname-override=192.168.200.117 --kubeconfig=/opt/kubernetes/cfg/kubelet.kubeconfig --experimental-bootstrap-kubeconfig=/opt/kubernetes/cfg/bootstrap.kubeconfig --config=/opt/kubernetes/cfg/kubelet.config --cert-dir=/opt/kubernetes/ssl --pod-infra-container-image=registry.cn-hangzhou.aliyuncs.com/google-containers/pause-amd64:3.0
	root      7998  0.0  0.0 112720   980 pts/0    S+   15:11   0:00 grep --color=auto kubelet
	[root@localhost k8s]# 
	
#### 7、执行kube-proxy.sh脚本文件部署启动kube-proxy

	[root@localhost k8s]# ./kube-proxy.sh 192.168.200.117
	Created symlink from /etc/systemd/system/multi-user.target.wants/kube-proxy.service to /usr/lib/systemd/system/kube-proxy.service.
	[root@localhost k8s]# ps aux | grep proxy
	root      8204  1.1  0.5  41780 19740 ?        Ssl  15:14   0:00 /opt/kubernetes/bin/kube-proxy --logtostderr=true --v=4 --hostname-override=192.168.200.117 --cluster-cidr=10.0.0.0/24 --proxy-mode=ipvs --kubeconfig=/opt/kubernetes/cfg/kube-proxy.kubeconfig
	root      8340  0.0  0.0 112720   984 pts/0    S+   15:14   0:00 grep --color=auto proxy
	[root@localhost k8s]# 
	
#### 8、在Master01上查看是否生成Node节点的证书请求

	[root@localhost bin]# kubectl get csr
	NAME                                                   AGE    REQUESTOR           CONDITION
	node-csr-YDJxuiTHd3077fduLdpyE8YNPKF8QW4VkNPv-owD-vg   4m4s   kubelet-bootstrap   Pending
	
#### 9、授权Node证书请求，允许该Node加入到k8s集群中

	[root@localhost bin]# kubectl certificate approve node-csr-YDJxuiTHd3077fduLdpyE8YNPKF8QW4VkNPv-owD-vg
	certificatesigningrequest.certificates.k8s.io/node-csr-YDJxuiTHd3077fduLdpyE8YNPKF8QW4VkNPv-owD-vg approved

#### 10、查看集群节点状态（发现证书请求以及通过，观察状态已经变化，查看该node节点状态已经是Ready可用状态）

	[root@localhost bin]# kubectl get csr
	NAME                                                   AGE     REQUESTOR           CONDITION
	node-csr-YDJxuiTHd3077fduLdpyE8YNPKF8QW4VkNPv-owD-vg   5m40s   kubelet-bootstrap   Approved,Issued
	[root@localhost bin]# kubectl get nodes
	NAME              STATUS   ROLES    AGE   VERSION
	192.168.200.117   Ready    <none>   31s   v1.12.2
	[root@localhost bin]# 

### 继续部署Node02节点，并且将Node02节点也加入到该集群中来（操作同Node01节点）

    [root@localhost bin]# kubectl get nodes
    NAME              STATUS   ROLES    AGE     VERSION
    192.168.200.117   Ready    <none>   9m56s   v1.12.2
    192.168.200.118   Ready    <none>   14s     v1.12.2