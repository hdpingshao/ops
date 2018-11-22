#### 1、分别在两台服务器上安装Nginx以及Keepalived服务

##### 配置nginx源

	[root@localhost ~]# cat /etc/yum.repos.d/nginx.repo 
	[nginx]
	name=nginx repo
	baseurl=http://nginx.org/packages/centos/7/$basearch/
	gpgcheck=0
	enabled=1
	
##### 安装Nginx以及Keepalived

    yum install -y nginx
    yum install -y keepalived
    
#### 2、配置Nginx四层负载均衡

	[root@localhost ~]# cat /etc/nginx/nginx.conf 

	user  nginx;
	worker_processes  4;

	error_log  /var/log/nginx/error.log warn;
	pid        /var/run/nginx.pid;


	events {
		worker_connections  1024;
	}

	# 配置nginx四层负载均衡

	stream {

		log_format k8s "$remote_addr $upstream_addr $time_local $status";
		access_log /var/log/nginx/k8s-access.log k8s;
		upstream k8s-apiserver {
			server 192.168.200.111:6443;
			server 192.168.200.116:6443;
		}
		server {
			listen 0.0.0.0:6443;
			proxy_pass k8s-apiserver;
		}

	}


	http {
		include       /etc/nginx/mime.types;
		default_type  application/octet-stream;

		log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
						  '$status $body_bytes_sent "$http_referer" '
						  '"$http_user_agent" "$http_x_forwarded_for"';

		access_log  /var/log/nginx/access.log  main;

		sendfile        on;
		#tcp_nopush     on;

		keepalive_timeout  65;

		#gzip  on;

		include /etc/nginx/conf.d/*.conf;
	}
	
#### 3、修改Node节点组件的配置信息，将指向apiserver的地址修改成指向刚刚部署的Nginx地址，然后重启Node组件，再检查Node运行状态（一步一步来，我们先使用单lb来进行操作）

	[root@localhost ~]# grep 200.111 /opt/kubernetes/cfg/*
	/opt/kubernetes/cfg/bootstrap.kubeconfig:    server: https://192.168.200.111:6443
	/opt/kubernetes/cfg/flanneld:FLANNEL_OPTIONS="--etcd-endpoints=https://192.168.200.111:2379,https://192.168.200.116:2379,https://192.168.200.117:2379 -etcd-cafile=/opt/etcd/ssl/ca.pem -etcd-certfile=/opt/etcd/ssl/server.pem -etcd-keyfile=/opt/etcd/ssl/server-key.pem"
	/opt/kubernetes/cfg/kubelet.kubeconfig:    server: https://192.168.200.111:6443
	/opt/kubernetes/cfg/kube-proxy.kubeconfig:    server: https://192.168.200.111:6443
	[root@localhost ~]# 

##### 将过滤出来的含有master ip的文件内容修改过来，flanneld文件不动

##### 重启相关组件

	[root@localhost cfg]# systemctl restart kubelet
	[root@localhost cfg]# ps axu | grep kubelet
	root      7576 11.7  1.5 499688 61736 ?        Ssl  16:53   0:00 /opt/kubernetes/bin/kubelet --logtostderr=true --v=4 --address=192.168.200.117 --hostname-override=192.168.200.117 --kubeconfig=/opt/kubernetes/cfg/kubelet.kubeconfig --experimental-bootstrap-kubeconfig=/opt/kubernetes/cfg/bootstrap.kubeconfig --config=/opt/kubernetes/cfg/kubelet.config --cert-dir=/opt/kubernetes/ssl --pod-infra-container-image=registry.cn-hangzhou.aliyuncs.com/google-containers/pause-amd64:3.0
	root      7644  0.0  0.0 112720   984 pts/0    S+   16:53   0:00 grep --color=auto kubelet
	[root@localhost cfg]# 
	[root@localhost cfg]# systemctl restart kube-proxy
	[root@localhost cfg]# ps axu | grep kube-proxy
	root      7708  1.6  0.5  42836 20452 ?        Ssl  16:53   0:00 /opt/kubernetes/bin/kube-proxy --logtostderr=true --v=4 --hostname-override=192.168.200.117 --cluster-cidr=10.0.0.0/24 --proxy-mode=ipvs --kubeconfig=/opt/kubernetes/cfg/kube-proxy.kubeconfig
	root      7817  0.0  0.0 112720   988 pts/0    S+   16:53   0:00 grep --color=auto kube-proxy
	[root@localhost cfg]#
	
##### 在Master01或者Master02上测试k8s集群是否正常运行

	[root@localhost ~]# kubectl get nodes
	NAME              STATUS   ROLES    AGE   VERSION
	192.168.200.117   Ready    <none>   25h   v1.12.2
	192.168.200.118   Ready    <none>   25h   v1.12.2
	
##### 重启node节点的kubelet组件，观察Nginx上的日志信息，观察是否由我们部署的Nginx上分发出去

	[root@localhost ~]# tail -f /var/log/nginx/k8s-access.log 
	192.168.200.117 192.168.200.111:6443 22/Nov/2018:16:53:06 +0800 200
	192.168.200.117 192.168.200.116:6443 22/Nov/2018:16:53:06 +0800 200
	192.168.200.117 192.168.200.111:6443 22/Nov/2018:16:53:36 +0800 200
	192.168.200.117 192.168.200.116:6443 22/Nov/2018:16:53:36 +0800 200
	192.168.200.117 192.168.200.116:6443 22/Nov/2018:16:53:36 +0800 200
	192.168.200.117 192.168.200.111:6443 22/Nov/2018:16:53:51 +0800 200
	192.168.200.118 192.168.200.111:6443 22/Nov/2018:16:55:38 +0800 200
	192.168.200.118 192.168.200.116:6443 22/Nov/2018:16:55:38 +0800 200
	192.168.200.117 192.168.200.111:6443 22/Nov/2018:17:04:51 +0800 200
	192.168.200.117 192.168.200.116:6443 22/Nov/2018:17:04:51 +0800 200
	192.168.200.117 192.168.200.111:6443 22/Nov/2018:17:04:51 +0800 200
	
##### 发现node节点与apiserver的通信地址修改后还是可以正常获取信息的，说明负载均衡代理正常，观察日志可以发现确实是负载均衡分发到后端两台Master节点上

#### 4、继续配置另外一台Nginx，实现两台nginx+Keepalived高可用

##### 主keepalived配置文件信息（从keepalived配置文件中要注意priority设置的要比主的小，设置成90即可）

	[root@localhost ~]# cat /etc/keepalived/keepalived.conf 
	! Configuration File for keepalived 
	 
	global_defs { 
	   # 接收邮件地址 
	   notification_email { 
		 acassen@firewall.loc 
		 failover@firewall.loc 
		 sysadmin@firewall.loc 
	   } 
	   # 邮件发送地址 
	   notification_email_from Alexandre.Cassen@firewall.loc  
	   smtp_server 127.0.0.1 
	   smtp_connect_timeout 30 
	   router_id NGINX_MASTER 
	} 

	# 配置nginx存活性检查脚本位置
	vrrp_script check_nginx {
		script "/opt/local/k8s/sbin/check_nginx.sh"
	}

	vrrp_instance VI_1 { 
		state MASTER 
		interface ens160
		virtual_router_id 51 # VRRP 路由 ID实例，每个实例是唯一的 
		priority 100    # 优先级，备服务器设置 90 
		advert_int 1    # 指定VRRP 心跳包通告间隔时间，默认1秒 
		authentication { 
			auth_type PASS      
			auth_pass 1111 
		}  
		virtual_ipaddress { 
			192.168.200.142/24 
		} 
		# 使用上面配置的nginx监测脚本
		track_script {
			check_nginx
		} 
	}
	
##### 配置check_nginx脚本文件（两台lb上都配置），并且给该脚本文件添加可执行权限

	[root@localhost ~]# cat /opt/local/k8s/sbin/check_nginx.sh 
	#!/bin/bash
	count=$(ps -ef |grep nginx |egrep -cv "grep|$$")

	if [ "$count" -eq 0 ]
	then
	  systemctl stop keepalived.service
	fi
	[root@localhost ~]# chmod +x /opt/local/k8s/sbin/check_nginx.sh
	
##### 启动keepalived服务，观察主keepalived节点的ens160网卡会多绑定一个VIP：192.168.200.142

	[root@localhost ~]# systemctl start keepalived.service
	[root@localhost ~]# ip addr
	1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
		link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
		inet 127.0.0.1/8 scope host lo
		   valid_lft forever preferred_lft forever
		inet6 ::1/128 scope host 
		   valid_lft forever preferred_lft forever
	2: ens160: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
		link/ether 00:50:56:8b:7b:ae brd ff:ff:ff:ff:ff:ff
		inet 192.168.200.172/24 brd 192.168.200.255 scope global noprefixroute ens160
		   valid_lft forever preferred_lft forever
		inet 192.168.200.142/24 scope global secondary ens160
		   valid_lft forever preferred_lft forever
		inet6 fe80::ddd1:ea5f:75ff:d153/64 scope link noprefixroute 
		   valid_lft forever preferred_lft forever
	[root@localhost ~]# 
	
#### 5、测试nginx+keepalived高可用是否部署成功

##### 测试方法：手动停止或杀死主上面的nginx服务，观察VIP会漂移到从服务上，当再次启动master上的nginx和keepalived服务时观察VIP又会漂移回主上去

#### 测试成功即表示我们的nginx+keepalived高可用集群部署成功

#### 6、高可用集群部署成功后，即可将我们Node节点上的配置apiserver的地址切换到我们的VIP（192.168.200.142）上来了，记得重启Node的组件

	[root@localhost cfg]# grep 200.172 /opt/kubernetes/cfg/*
	/opt/kubernetes/cfg/bootstrap.kubeconfig:    server: https://192.168.200.172:6443
	/opt/kubernetes/cfg/kubelet.kubeconfig:    server: https://192.168.200.172:6443
	/opt/kubernetes/cfg/kube-proxy.kubeconfig:    server: https://192.168.200.172:6443
	[root@localhost cfg]# 

##### 修改完成重启kubelet以及kub-proxy，同时观察nginx日志信息

	[root@localhost cfg]# systemctl restart kubelet kube-proxy
	[root@localhost cfg]# ps aux | grep -E "kubelet|kube-proxy"
	root     16156  4.5  0.5  41780 21040 ?        Ssl  17:42   0:00 /opt/kubernetes/bin/kube-proxy --logtostderr=true --v=4 --hostname-override=192.168.200.117 --cluster-cidr=10.0.0.0/24 --proxy-mode=ipvs --kubeconfig=/opt/kubernetes/cfg/kube-proxy.kubeconfig
	root     16157 22.5  1.6 706608 63860 ?        Ssl  17:42   0:00 /opt/kubernetes/bin/kubelet --logtostderr=true --v=4 --address=192.168.200.117 --hostname-override=192.168.200.117 --kubeconfig=/opt/kubernetes/cfg/kubelet.kubeconfig --experimental-bootstrap-kubeconfig=/opt/kubernetes/cfg/bootstrap.kubeconfig --config=/opt/kubernetes/cfg/kubelet.config --cert-dir=/opt/kubernetes/ssl --pod-infra-container-image=registry.cn-hangzhou.aliyuncs.com/google-containers/pause-amd64:3.0
	root     16322  0.0  0.0 112720   996 pts/0    S+   17:42   0:00 grep --color=auto -E kubelet|kube-proxy
	[root@localhost cfg]# 

##### 观察nginx日志信息

	[root@localhost ~]# tail -f /var/log/nginx/k8s-access.log 
	192.168.200.118 192.168.200.111:6443 22/Nov/2018:17:34:19 +0800 200
	192.168.200.117 192.168.200.116:6443 22/Nov/2018:17:34:19 +0800 200
	192.168.200.117 192.168.200.116:6443 22/Nov/2018:17:40:27 +0800 200
	192.168.200.117 192.168.200.111:6443 22/Nov/2018:17:40:27 +0800 200
	192.168.200.117 192.168.200.116:6443 22/Nov/2018:17:40:27 +0800 200
	192.168.200.117 192.168.200.116:6443 22/Nov/2018:17:40:27 +0800 200
	192.168.200.117 192.168.200.111:6443 22/Nov/2018:17:42:03 +0800 200
	192.168.200.117 192.168.200.111:6443 22/Nov/2018:17:42:03 +0800 200
	192.168.200.117 192.168.200.111:6443 22/Nov/2018:17:42:03 +0800 200
	192.168.200.117 192.168.200.111:6443 22/Nov/2018:17:42:03 +0800 200
	192.168.200.118 192.168.200.116:6443 22/Nov/2018:17:43:44 +0800 200
	192.168.200.118 192.168.200.111:6443 22/Nov/2018:17:43:44 +0800 200
	192.168.200.118 192.168.200.116:6443 22/Nov/2018:17:43:44 +0800 200
	192.168.200.118 192.168.200.111:6443 22/Nov/2018:17:43:44 +0800 200

#### 至此Kubernetes的多Master高可用集群已经成功部署完成
