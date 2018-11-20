#### 所有操作都是在master01上操作

#### 自签SSL证书组件图

|组件|使用的证书|
|------|------|
|etcd|ca.pem,server.pem,server-key.pem|
|flannel|ca.pem,server.pem,server-key.pem|
|kube-apiserver|ca.pem,server.pem,server-key.pem|
|kubelet|ca.pem,ca-key.pem|
|kube-proxy|ca.pem,kube-proxy.pem,kube-proxy-key.pem|
|kubectl|ca.pem,admin.pem,admin-key.pem|

#### 下载制作证书的工具：

##### cfssl.sh脚本内容(执行该脚本)：

    curl -L https://pkg.cfssl.org/R1.2/cfssl_linux-amd64 -o /usr/local/bin/cfssl
    curl -L https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64 -o /usr/local/bin/cfssljson
    curl -L https://pkg.cfssl.org/R1.2/cfssl-certinfo_linux-amd64 -o /usr/local/bin/cfssl-certinfo
    chmod +x /usr/local/bin/cfssl /usr/local/bin/cfssljson /usr/local/bin/cfssl-certinfo

##### 1、ca根证书文件
    
 	cat > ca-config.json <<EOF
	{
	  "signing": {
		"default": {
		  "expiry": "87600h"
		},
		"profiles": {
		  "www": {
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
	EOF

##### 2、ca根证书请求文件

	cat > ca-csr.json <<EOF
	{
		"CN": "etcd CA",
		"key": {
			"algo": "rsa",
			"size": 2048
		},
		"names": [
			{
				"C": "CN",
				"L": "FuJian",
				"ST": "XiaMen"
			}
		]
	}
	EOF

##### 3、初始化ca根证书

    cfssl gencert -initca ca-csr.json | cfssljson -bare ca -
    
#### 为etcd签署证书

##### 1、创建etcd证书请求文件：

	{
		"CN": "etcd",
		"hosts": [
		"192.168.200.111",
		"192.168.200.116",
		"192.168.200.117"
		],
		"key": {
			"algo": "rsa",
			"size": 2048
		},
		"names": [
			{
				"C": "CN",
				"L": "FuJian",
				"ST": "XiaMen"
			}
		]
	}
	EOF

#### 2、使用ca根证书为etcd请求文件签署证书

    cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=www server-csr.json | cfssljson -bare server