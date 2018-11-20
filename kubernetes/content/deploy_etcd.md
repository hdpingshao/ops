### 1、二进制包下载地址

- https://github.com/etcd-io/etcd/releases

### 2、部署前准备

- 关闭selinux
- 关闭iptables以及firewalled

### 3、下载etcd包并拷贝可执行文件到指定目录

    [root@localhost k8s]# ll
	总用量 10320
	-rwxr-xr-x. 1 root    root       342 10月 20 23:08 cfssl.sh
	drwxr-xr-x. 3 6810230 users      123 10月 11 01:33 etcd-v3.3.10-linux-amd64
	-rw-r--r--. 1 root    root  10561089 11月 20 14:09 etcd-v3.3.10-linux-amd64.tar.gz
	drwxr-xr-x. 3 root    root        18 11月 19 17:24 pki
	[root@localhost k8s]# cd etcd-v3.3.10-linux-amd64
	[root@localhost etcd-v3.3.10-linux-amd64]# ll
	总用量 32324
	drwxr-xr-x. 11 6810230 users     4096 10月 11 01:33 Documentation
	-rwxr-xr-x.  1 6810230 users 18101056 10月 11 01:33 etcd
	-rwxr-xr-x.  1 6810230 users 14930816 10月 11 01:33 etcdctl
	-rw-r--r--.  1 6810230 users    38864 10月 11 01:33 README-etcdctl.md
	-rw-r--r--.  1 6810230 users     7262 10月 11 01:33 README.md
	-rw-r--r--.  1 6810230 users     7855 10月 11 01:33 READMEv2-etcdctl.md
	[root@localhost etcd-v3.3.10-linux-amd64]# mkdir /opt/etcd/{bin,cfg,ssl} -p
	[root@localhost etcd-v3.3.10-linux-amd64]# ls /opt/etcd/
	bin  cfg  ssl
	[root@localhost etcd-v3.3.10-linux-amd64]# mv etcd etcdctl /opt/etcd/bin/
	[root@localhost etcd-v3.3.10-linux-amd64]# ls /opt/etcd/bin/
	etcd  etcdctl
	[root@localhost etcd-v3.3.10-linux-amd64]# 

### 4、使用自己创建的etcd脚本来创建etcd集群(三个节点执行)
### 可以将第一个节点生成的配置文件直接拷贝到另外两个节点上稍作修改即可
### 2379端口：读取数据的端口
### 2380端口：集群通讯的端口

#### 脚本内容如下：

	#!/bin/bash
	# example: ./etcd.sh etcd01 192.168.1.10 etcd02=https://192.168.1.11:2380,etcd03=https://192.168.1.12:2380

	ETCD_NAME=$1
	ETCD_IP=$2
	ETCD_CLUSTER=$3

	WORK_DIR=/opt/etcd

	cat <<EOF >$WORK_DIR/cfg/etcd
	#[Member]
	ETCD_NAME="${ETCD_NAME}"
	ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
	ETCD_LISTEN_PEER_URLS="https://${ETCD_IP}:2380"
	ETCD_LISTEN_CLIENT_URLS="https://${ETCD_IP}:2379"

	#[Clustering]
	ETCD_INITIAL_ADVERTISE_PEER_URLS="https://${ETCD_IP}:2380"
	ETCD_ADVERTISE_CLIENT_URLS="https://${ETCD_IP}:2379"
	ETCD_INITIAL_CLUSTER="etcd01=https://${ETCD_IP}:2380,${ETCD_CLUSTER}"
	ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster"
	ETCD_INITIAL_CLUSTER_STATE="new"
	EOF

	cat <<EOF >/usr/lib/systemd/system/etcd.service
	[Unit]
	Description=Etcd Server
	After=network.target
	After=network-online.target
	Wants=network-online.target

	[Service]
	Type=notify
	EnvironmentFile=${WORK_DIR}/cfg/etcd
	ExecStart=${WORK_DIR}/bin/etcd \
	--name=\${ETCD_NAME} \
	--data-dir=\${ETCD_DATA_DIR} \
	--listen-peer-urls=\${ETCD_LISTEN_PEER_URLS} \
	--listen-client-urls=\${ETCD_LISTEN_CLIENT_URLS},http://127.0.0.1:2379 \
	--advertise-client-urls=\${ETCD_ADVERTISE_CLIENT_URLS} \
	--initial-advertise-peer-urls=\${ETCD_INITIAL_ADVERTISE_PEER_URLS} \
	--initial-cluster=\${ETCD_INITIAL_CLUSTER} \
	--initial-cluster-token=\${ETCD_INITIAL_CLUSTER_TOKEN} \
	--initial-cluster-state=new \
	--cert-file=${WORK_DIR}/ssl/server.pem \
	--key-file=${WORK_DIR}/ssl/server-key.pem \
	--peer-cert-file=${WORK_DIR}/ssl/server.pem \
	--peer-key-file=${WORK_DIR}/ssl/server-key.pem \
	--trusted-ca-file=${WORK_DIR}/ssl/ca.pem \
	--peer-trusted-ca-file=${WORK_DIR}/ssl/ca.pem
	Restart=on-failure
	LimitNOFILE=65536

	[Install]
	WantedBy=multi-user.target
	EOF

	systemctl daemon-reload
	systemctl enable etcd
	systemctl restart etcd
	

### 5、将etcd的ssl相关证书拷贝到ssl目录下

    [root@localhost ssl]# cd /opt/local/k8s/pki/etcd/
	[root@localhost etcd]# cp ca.pem  server.pem server-key.pem /opt/etcd/ssl/
	[root@localhost etcd]# ll /opt/etcd/ssl/
	总用量 12
	-rw-r--r--. 1 root root 1261 11月 20 14:25 ca.pem
	-rw-------. 1 root root 1679 11月 20 14:25 server-key.pem
	-rw-r--r--. 1 root root 1334 11月 20 14:25 server.pem

### 5、启动etcd集群

    [root@localhost k8s]# cd /opt/local/k8s/
    [root@localhost k8s]# ll
    总用量 10324
    -rwxr-xr-x. 1 root    root       342 10月 20 23:08 cfssl.sh
    -rwxr-xr-x. 1 root    root      1764 8月  27 21:51 etcd.sh
    drwxr-xr-x. 3 6810230 users       96 11月 20 14:16 etcd-v3.3.10-linux-arm64
    -rw-r--r--. 1 root    root  10561089 11月 20 14:09 etcd-v3.3.10-linux-arm64.tar.gz
    drwxr-xr-x. 3 root    root        18 11月 19 17:24 pki
    [root@localhost k8s]# ./etcd.sh etcd01 192.168.200.111 etcd02=https://192.168.200.116:2380,etcd03=https://192.168.200.117:2380

### 6、查看集群状态

	[root@localhost ssl]# cd /opt/etcd/ssl/
	[root@localhost ssl]# /opt/etcd/bin/etcdctl --ca-file=ca.pem --cert-file=server.pem --key-file=server-key.pem --endpoints="https://192.168.200.1111:2379,https://192.168.200.116:2379,https://192.168.200.117:2379" cluster-health
	member 1eed6caa93890e3a is healthy: got healthy result from https://192.168.200.111:2379
	member 59e0fb8c536fe888 is healthy: got healthy result from https://192.168.200.117:2379
	member b5f1909b2e61a5e3 is healthy: got healthy result from https://192.168.200.116:2379
	cluster is healthy
	[root@localhost ssl]# 

### 至此etcd集群部署完成

