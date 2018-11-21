### 注意：在部署过程中一定要先部署apiserver组件，然后再部署另外两个组件

#### 1、github上下载二进制包（下载Server Binaries的二进制包就够了）

    https://github.com/kubernetes/kubernetes/releases
    wget https://dl.k8s.io/v1.12.2/kubernetes-server-linux-amd64.tar.gz
    
#### 2、将下载好的二进制包解压并拷贝所需要的二进制可执行文件

	[root@localhost soft]# tar zxf kubernetes-server-linux-amd64.tar.gz 
	[root@localhost soft]# cd kubernetes/server/bin/
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
	[root@localhost bin]# cp kube-apiserver kubectl kube-controller-manager kube-scheduler /opt/kubernetes/bin/
	[root@localhost bin]# ls /opt/kubernetes/bin/
	kube-apiserver  kube-controller-manager  kubectl  kube-scheduler
	[root@localhost bin]# 

#### 3、拷贝apiserver的ssl证书到指定目录

	[root@localhost bin]# cp /opt/local/k8s/pki/apiserver/ca*.pem /opt/kubernetes/ssl/
	[root@localhost bin]# cp /opt/local/k8s/pki/apiserver/server*.pem /opt/kubernetes/ssl/
	[root@localhost bin]# ls /opt/kubernetes/ssl/
	ca-key.pem  ca.pem  server-key.pem  server.pem
	[root@localhost bin]# ls /opt/etcd/ssl/
	ca.pem  server-key.pem  server.pem
	[root@localhost bin]# 

#### 4、因apiserver的配置文件需要用到token认证信息，故手动生成一个token配置文件

	[root@localhost soft]# head -c 16 /dev/urandom | od -An -t x | tr -d ' '
	a1f7e11eef3b7a83026f50fa6483ab80
	[root@localhost soft]# cat /opt/kubernetes/cfg/token.csv 
	a1f7e11eef3b7a83026f50fa6483ab80,kubelet-bootstrap,10001,"system:kubelet-bootstrap"
	[root@localhost soft]# 

#### 4、准备Master-apiserver组件生成配置文件的脚本

> * https://github.com/hdpingshao/ops/blob/master/kubernetes/content/apiserver.sh

#### 5、通过脚本启动apiserver组件

	[root@localhost soft]# ./apiserver.sh 192.168.200.111 https://192.168.200.111:2379,https://192.168.200.116:2379,https://192.168.200.117:2379
	Created symlink from /etc/systemd/system/multi-user.target.wants/kube-apiserver.service to /usr/lib/systemd/system/kube-apiserver.service.
	[root@localhost soft]# ps aux | grep apiserver
	root     11650 98.2  8.0 397824 313656 ?       Ssl  14:00   0:10 /opt/kubernetes/bin/kube-apiserver --logtostderr=true --v=4 --etcd-servers=https://192.168.200.111:2379,https://192.168.200.116:2379,https://192.168.200.117:2379 --bind-address=192.168.200.111 --secure-port=6443 --advertise-address=192.168.200.111 --allow-privileged=true --service-cluster-ip-range=10.0.0.0/24 --enable-admission-plugins=NamespaceLifecycle,LimitRanger,ServiceAccount,ResourceQuota,NodeRestriction --authorization-mode=RBAC,Node --kubelet-https=true --enable-bootstrap-token-auth --token-auth-file=/opt/kubernetes/cfg/token.csv --service-node-port-range=30000-50000 --tls-cert-file=/opt/kubernetes/ssl/server.pem --tls-private-key-file=/opt/kubernetes/ssl/server-key.pem --client-ca-file=/opt/kubernetes/ssl/ca.pem --service-account-key-file=/opt/kubernetes/ssl/ca-key.pem --etcd-cafile=/opt/etcd/ssl/ca.pem --etcd-certfile=/opt/etcd/ssl/server.pem --etcd-keyfile=/opt/etcd/ssl/server-key.pem
	root     11673  0.0  0.0 112720   984 pts/0    S+   14:01   0:00 grep --color=auto apiserver
	[root@localhost soft]# 
	
#### 6、准备Master-controller-manager组件生成配置文件的脚本

> * https://github.com/hdpingshao/ops/blob/master/kubernetes/content/controller-manager.sh

#### 7、通过脚本启动controller-manager组件

	[root@localhost soft]# ./controller-manager.sh 127.0.0.1
	Created symlink from /etc/systemd/system/multi-user.target.wants/kube-controller-manager.service to /usr/lib/systemd/system/kube-controller-manager.service.
	[root@localhost soft]# ps aux | grep controller
	root     11727 27.8  1.4 135184 58072 ?        Ssl  14:06   0:02 /opt/kubernetes/bin/kube-controller-manager --logtostderr=true --v=4 --master=127.0.0.1:8080 --leader-elect=true --address=127.0.0.1 --service-cluster-ip-range=10.0.0.0/24 --cluster-name=kubernetes --cluster-signing-cert-file=/opt/kubernetes/ssl/ca.pem --cluster-signing-key-file=/opt/kubernetes/ssl/ca-key.pem --root-ca-file=/opt/kubernetes/ssl/ca.pem --service-account-private-key-file=/opt/kubernetes/ssl/ca-key.pem --experimental-cluster-signing-duration=87600h0m0s
	root     11738  0.0  0.0 112720   984 pts/0    S+   14:06   0:00 grep --color=auto controller
	[root@localhost soft]# 
	
#### 8、准备Master-scheduler组件生成配置文件的脚本

> * https://github.com/hdpingshao/ops/blob/master/kubernetes/content/scheduler.sh

#### 9、通过脚本启动scheduler组件

	[root@localhost soft]# ./scheduler.sh 127.0.0.1
	Created symlink from /etc/systemd/system/multi-user.target.wants/kube-scheduler.service to /usr/lib/systemd/system/kube-scheduler.service.
	[root@localhost soft]# ps aux | grep scheduler
	root     11788  1.6  0.5  45616 20128 ?        Ssl  14:09   0:00 /opt/kubernetes/bin/kube-scheduler --logtostderr=true --v=4 --master=127.0.0.1:8080 --leader-elect
	root     11799  0.0  0.0 112720   980 pts/0    S+   14:09   0:00 grep --color=auto scheduler
	[root@localhost soft]# 
	
#### 10、验证Master三个组件的部署是否正常（能显示如下信息说明apiserver是正常的，另外两个组件可以直观查看其状态）

	[root@localhost soft]# /opt/kubernetes/bin/kubectl get cs
	NAME                 STATUS    MESSAGE             ERROR
	scheduler            Healthy   ok                  
	controller-manager   Healthy   ok                  
	etcd-1               Healthy   {"health":"true"}   
	etcd-0               Healthy   {"health":"true"}   
	etcd-2               Healthy   {"health":"true"}   
	[root@localhost soft]# 