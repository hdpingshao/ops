### Flannel网络工作原理

- Overlay Network：覆盖网络，在基础网络上叠加的一种虚拟网络技术模式，该网络中的主机通过虚拟链路连接起来
- VXLAN：将源数据包封装到UDP中，并使用基础网络的IP/MAC作为外层报文头进行封装，然后在以太网上传输，到达目的地后由隧道端点解封装并将数据发送给目标地址
- Flannel：是Overlay网络的一种，也是将源数据包封装在另一种网络包里面进行路由转发和通信，目前已经支持UDP、VXLAN、AWS VPC和GCE路由等数据转发方式。

#### VXLAN网络工作原理图

![image](https://github.com/hdpingshao/ops/blob/master/kubernetes/images/2-5-1.jpg)

#### 不同主机中容器互相通信原理图

![image](https://github.com/hdpingshao/ops/blob/master/kubernetes/images/2-5-2.jpg)

#### 在Node节点上部署Flannel网络使得Node节点上的容器可以互相通信

##### 1、在etcd节点上写入分配的子网段到etcd，供flanneld使用

	[root@localhost ssl]# cd /opt/etcd/ssl/
	# set设置网络地址段
	[root@localhost ssl]# /opt/etcd/bin/etcdctl --ca-file=ca.pem --cert-file=server.pem --key-file=server-key.pem --endpoints="https://192.168.200.111:2379,https://192.168.200.116:2379,https://192.168.200.117:2379" set /coreos.com/network/config '{ "Network": "172.17.0.0/16", "Backend": {"Type": "vxlan"}}'
	{ "Network": "172.17.0.0/16", "Backend": {"Type": "vxlan"}}
	# get获取下刚刚设置的网络地址段，看是否正确
	[root@localhost ssl]# /opt/etcd/bin/etcdctl --ca-file=ca.pem --cert-file=server.pem --key-file=server-key.pem --endpoints="https://192.168.200.111:2379,https://192.168.200.116:2379,https://192.168.200.117:2379" get /coreos.com/network/config '{ "Network": "172.17.0.0/16", "Backend": {"Type": "vxlan"}}'
	{ "Network": "172.17.0.0/16", "Backend": {"Type": "vxlan"}}
	[root@localhost ssl]# 
	
##### 2、下载Flannel二进制包

    https://github.com/coreos/flannel/releases
    
##### 3、编辑flanneld配置文件

	[root@localhost ~]# cat <<EOF >/opt/kubernetes/cfg/flanneld
	> 
	> FLANNEL_OPTIONS="--etcd-endpoints="https://192.168.200.111:2379,https://192.168.200.116:2379,https://192.168.200.117:2379" \
	> -etcd-cafile=/opt/etcd/ssl/ca.pem \
	> -etcd-certfile=/opt/etcd/ssl/server.pem \
	> -etcd-keyfile=/opt/etcd/ssl/server-key.pem"
	> 
	> EOF
	[root@localhost ~]# cat /opt/kubernetes/cfg/flanneld 

	FLANNEL_OPTIONS="--etcd-endpoints=https://192.168.200.111:2379,https://192.168.200.116:2379,https://192.168.200.117:2379 -etcd-cafile=/opt/etcd/ssl/ca.pem -etcd-certfile=/opt/etcd/ssl/server.pem -etcd-keyfile=/opt/etcd/ssl/server-key.pem"

	[root@localhost ~]# 
	
##### 4、systemd管理flannel的配置文件编写

	[root@localhost ~]# cat <<EOF >/usr/lib/systemd/system/flanneld.service
	> [Unit]
	> Description=Flanneld overlay address etcd agent
	> After=network-online.target network.target
	> Before=docker.service
	> 
	> [Service]
	> Type=notify
	> EnvironmentFile=/opt/kubernetes/cfg/flanneld
	> ExecStart=/opt/kubernetes/bin/flanneld --ip-masq \$FLANNEL_OPTIONS
	> ExecStartPost=/opt/kubernetes/bin/mk-docker-opts.sh -k DOCKER_NETWORK_OPTIONS -d /run/flannel/subnet.env
	> Restart=on-failure
	> 
	> [Install]
	> WantedBy=multi-user.target
	> 
	> EOF
	
##### 5、配置docker使用Flannel生成的子网（修改文件/usr/lib/systemd/system/docker.service）

	[Service]
	Type=notify
	# the default is not to use systemd for cgroups because the delegate issues still
	# exists and systemd currently does not support the cgroup feature set required
	# for containers run by docker
	EnvironmentFile=/run/flannel/subnet.env
	ExecStart=/usr/bin/dockerd $DOCKER_NETWORK_OPTIONS
	ExecReload=/bin/kill -s HUP $MAINPID
	TimeoutSec=0
	RestartSec=2
	Restart=always

> * 修改完配置后重启docker
> * systemctl daemon-reload
> * systemctl restart docker

