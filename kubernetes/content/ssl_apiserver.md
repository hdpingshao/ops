#### 1、创建apiserver的ca根证书文件

	[root@localhost apiserver]# cat ca-config.json 
	{
	  "signing": {
		"default": {
		  "expiry": "87600h"
		},
		"profiles": {
		  "kubernetes": {
			 "expiry": "87600h",
			 "usages": [
				"signing",
				"key encipherment",
				"server auth",
				"client auth"
			]
		  }
		}
	  }
	}

#### 2、创建apiserver的ca根证书请求文件

	[root@localhost apiserver]# cat ca-csr.json 
	{
		"CN": "kubernetes",
		"key": {
			"algo": "rsa",
			"size": 2048
		},
		"names": [
			{
				"C": "CN",
				"L": "FuJian",
				"ST": "XiaMen",
				"O": "k8s",
				"OU": "System"
			}
		]
	}

#### 3、初始化apiserver的ca根证书

	[root@localhost apiserver]# cfssl gencert -initca ca-csr.json | cfssljson -bare ca -
	2018/11/21 10:28:29 [INFO] generating a new CA key and certificate from CSR
	2018/11/21 10:28:29 [INFO] generate received request
	2018/11/21 10:28:29 [INFO] received CSR
	2018/11/21 10:28:29 [INFO] generating key: rsa-2048
	2018/11/21 10:28:30 [INFO] encoded CSR
	2018/11/21 10:28:30 [INFO] signed certificate with serial number 146292274956691238849353089498704704391202689024
	[root@localhost apiserver]# ll
	总用量 20
	-rw-r--r--. 1 root root  294 11月 21 10:14 ca-config.json
	-rw-r--r--. 1 root root  997 11月 21 10:28 ca.csr
	-rw-r--r--. 1 root root  262 11月 21 10:24 ca-csr.json
	-rw-------. 1 root root 1675 11月 21 10:28 ca-key.pem
	-rw-r--r--. 1 root root 1354 11月 21 10:28 ca.pem
	[root@localhost apiserver]# 

#### 4、创建apiserver的请求文件

	[root@localhost apiserver]# cat server-csr.json 
	{
		"CN": "kubernetes",
		"hosts": [
		  "10.0.0.1",
		  "127.0.0.1",
		  "192.168.200.111",
		  "192.168.200.116",
		  "192.168.200.142",
		  "192.168.200.172",
		  "192.168.200.173",
		  "kubernetes",
		  "kubernetes.default",
		  "kubernetes.default.svc",
		  "kubernetes.default.svc.cluster",
		  "kubernetes.default.svc.cluster.local"
		],
		"key": {
			"algo": "rsa",
			"size": 2048
		},
		"names": [
			{
				"C": "CN",
				"L": "FuJian",
				"ST": "XiaMen",
				"O": "k8s",
				"OU": "System"
			}
		]
	}
	
#### 5、使用ca根证书为apiserver请求文件签署证书

	[root@localhost apiserver]# cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes server-csr.json | cfssljson -bare server
	2018/11/21 11:02:16 [INFO] generate received request
	2018/11/21 11:02:16 [INFO] received CSR
	2018/11/21 11:02:16 [INFO] generating key: rsa-2048
	2018/11/21 11:02:16 [INFO] encoded CSR
	2018/11/21 11:02:16 [INFO] signed certificate with serial number 326391874989886034168347318281429299494619753324
	2018/11/21 11:02:16 [WARNING] This certificate lacks a "hosts" field. This makes it unsuitable for
	websites. For more information see the Baseline Requirements for the Issuance and Management
	of Publicly-Trusted Certificates, v.1.1.6, from the CA/Browser Forum (https://cabforum.org);
	specifically, section 10.2.3 ("Information Requirements").
	[root@localhost apiserver]# ll
	总用量 36
	-rw-r--r--. 1 root root  294 11月 21 10:14 ca-config.json
	-rw-r--r--. 1 root root  997 11月 21 10:28 ca.csr
	-rw-r--r--. 1 root root  262 11月 21 10:24 ca-csr.json
	-rw-------. 1 root root 1675 11月 21 10:28 ca-key.pem
	-rw-r--r--. 1 root root 1354 11月 21 10:28 ca.pem
	-rw-r--r--. 1 root root 1273 11月 21 11:02 server.csr
	-rw-r--r--. 1 root root  611 11月 21 10:58 server-csr.json
	-rw-------. 1 root root 1675 11月 21 11:02 server-key.pem
	-rw-r--r--. 1 root root 1639 11月 21 11:02 server.pem
	[root@localhost apiserver]# 

#### 6、创建kubectl证书请求文件-提供给kubectl连接apiserver用的证书

	[root@localhost apiserver]# cat admin-csr.json 
	{
	  "CN": "admin",
	  "hosts": [],
	  "key": {
		"algo": "rsa",
		"size": 2048
	  },
	  "names": [
		{
		  "C": "CN",
		  "L": "FuJian",
		  "ST": "XiaMen",
		  "O": "system:masters",
		  "OU": "System"
		}
	  ]
	}

#### 7、使用ca根证书为kubectl请求文件签署证书

	[root@localhost apiserver]# cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes admin-csr.json | cfssljson -bare admin
	2018/11/21 11:06:46 [INFO] generate received request
	2018/11/21 11:06:46 [INFO] received CSR
	2018/11/21 11:06:46 [INFO] generating key: rsa-2048
	2018/11/21 11:06:47 [INFO] encoded CSR
	2018/11/21 11:06:47 [INFO] signed certificate with serial number 567637367338185054980432577604540230354173402568
	2018/11/21 11:06:47 [WARNING] This certificate lacks a "hosts" field. This makes it unsuitable for
	websites. For more information see the Baseline Requirements for the Issuance and Management
	of Publicly-Trusted Certificates, v.1.1.6, from the CA/Browser Forum (https://cabforum.org);
	specifically, section 10.2.3 ("Information Requirements").
	[root@localhost apiserver]# ll
	总用量 52
	-rw-r--r--. 1 root root 1005 11月 21 11:06 admin.csr
	-rw-r--r--. 1 root root  227 11月 21 11:04 admin-csr.json
	-rw-------. 1 root root 1675 11月 21 11:06 admin-key.pem
	-rw-r--r--. 1 root root 1395 11月 21 11:06 admin.pem
	-rw-r--r--. 1 root root  294 11月 21 10:14 ca-config.json
	-rw-r--r--. 1 root root  997 11月 21 10:28 ca.csr
	-rw-r--r--. 1 root root  262 11月 21 10:24 ca-csr.json
	-rw-------. 1 root root 1675 11月 21 10:28 ca-key.pem
	-rw-r--r--. 1 root root 1354 11月 21 10:28 ca.pem
	-rw-r--r--. 1 root root 1273 11月 21 11:02 server.csr
	-rw-r--r--. 1 root root  611 11月 21 10:58 server-csr.json
	-rw-------. 1 root root 1675 11月 21 11:02 server-key.pem
	-rw-r--r--. 1 root root 1639 11月 21 11:02 server.pem
	[root@localhost apiserver]# 
	
#### 8、创建kube-proxy请求文件-提供给kube-proxy组件连接apiserver用的证书

	[root@localhost apiserver]# cat kube-proxy-csr.json 
	{
	  "CN": "system:kube-proxy",
	  "hosts": [],
	  "key": {
		"algo": "rsa",
		"size": 2048
	  },
	  "names": [
		{
		  "C": "CN",
		  "L": "FuJian",
		  "ST": "XiaMen",
		  "O": "k8s",
		  "OU": "System"
		}
	  ]
	}
	
#### 9、使用ca根证书为kube-proxy请求文件签署证书

	[root@localhost apiserver]# cfssl gencert -ca=ca.pem -ca-key=ca-key.pem  -config=ca-config.json -profile=kubernetes kube-proxy-csr.json | cfssljson -bare kube-proxy
	2018/11/21 11:10:35 [INFO] generate received request
	2018/11/21 11:10:35 [INFO] received CSR
	2018/11/21 11:10:35 [INFO] generating key: rsa-2048
	2018/11/21 11:10:36 [INFO] encoded CSR
	2018/11/21 11:10:36 [INFO] signed certificate with serial number 714124531389424083657375808623127897748672451267
	2018/11/21 11:10:36 [WARNING] This certificate lacks a "hosts" field. This makes it unsuitable for
	websites. For more information see the Baseline Requirements for the Issuance and Management
	of Publicly-Trusted Certificates, v.1.1.6, from the CA/Browser Forum (https://cabforum.org);
	specifically, section 10.2.3 ("Information Requirements").
	[root@localhost apiserver]# ll
	总用量 68
	-rw-r--r--. 1 root root 1005 11月 21 11:06 admin.csr
	-rw-r--r--. 1 root root  227 11月 21 11:04 admin-csr.json
	-rw-------. 1 root root 1675 11月 21 11:06 admin-key.pem
	-rw-r--r--. 1 root root 1395 11月 21 11:06 admin.pem
	-rw-r--r--. 1 root root  294 11月 21 10:14 ca-config.json
	-rw-r--r--. 1 root root  997 11月 21 10:28 ca.csr
	-rw-r--r--. 1 root root  262 11月 21 10:24 ca-csr.json
	-rw-------. 1 root root 1675 11月 21 10:28 ca-key.pem
	-rw-r--r--. 1 root root 1354 11月 21 10:28 ca.pem
	-rw-r--r--. 1 root root 1009 11月 21 11:10 kube-proxy.csr
	-rw-r--r--. 1 root root  228 11月 21 11:08 kube-proxy-csr.json
	-rw-------. 1 root root 1679 11月 21 11:10 kube-proxy-key.pem
	-rw-r--r--. 1 root root 1395 11月 21 11:10 kube-proxy.pem
	-rw-r--r--. 1 root root 1273 11月 21 11:02 server.csr
	-rw-r--r--. 1 root root  611 11月 21 10:58 server-csr.json
	-rw-------. 1 root root 1675 11月 21 11:02 server-key.pem
	-rw-r--r--. 1 root root 1639 11月 21 11:02 server.pem
	
#### 至此apiserver相关的证书已经生成完成
