### 1、二进制包下载地址

- https://github.com/etcd-io/etcd/releases

### 2、部署前准备

- 关闭selinux
- 关闭iptables以及firewalled

### 3、下载etcd包并拷贝可执行文件到指定目录

    

### 4、使用自己创建的etcd脚本来创建etcd集群

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
	

### 5、查看集群状态

    /opt/etcd/bin/etcdctl \
    --ca-file=ca.pem --cert-file=server.pem --key-file=server-key.pem \
    --endpoints="https://192.168.200.1111:2379,https://192.168.200.116:2379,https://192.168.200.117:2379" \
    cluster-health


