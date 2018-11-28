#### 1、启动两个web容器用于测试Ingress（nginx和apache），并通过service提供统一的接口

	[root@localhost ingress]# kubectl run --image=nginx nginx
	kubectl run --generator=deployment/apps.v1beta1 is DEPRECATED and will be removed in a future version. Use kubectl create instead.
	deployment.apps/nginx created
	[root@localhost ingress]# kubectl expose deploy/nginx --port=80
	service/nginx exposed
	[root@localhost ingress]# kubectl run --image=httpd httpd
	kubectl run --generator=deployment/apps.v1beta1 is DEPRECATED and will be removed in a future version. Use kubectl create instead.
	deployment.apps/httpd created
	[root@localhost ingress]# kubectl expose deploy/httpd --port=80
	service/httpd exposed
	[root@localhost ingress]# kubectl get svc
	NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
	httpd        ClusterIP   10.0.0.147   <none>        80/TCP    5s
	kubernetes   ClusterIP   10.0.0.1     <none>        443/TCP   5d23h
	nginx        ClusterIP   10.0.0.16    <none>        80/TCP    53s
	[root@localhost ingress]# kubectl get deploy
	NAME    DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
	httpd   1         1         1            1           53s
	nginx   1         1         1            1           86s
	[root@localhost ingress]# 
	
#### 2、将两个web容器的默认页面修改下方便后续测试直观的查看

	[root@localhost ingress]# kubectl get svc -o wide
	NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE     SELECTOR
	httpd        ClusterIP   10.0.0.147   <none>        80/TCP    3m37s   run=httpd
	kubernetes   ClusterIP   10.0.0.1     <none>        443/TCP   6d      <none>
	nginx        ClusterIP   10.0.0.16    <none>        80/TCP    4m25s   run=nginx
	[root@localhost ingress]# 
	
	[root@localhost ~]# curl 10.0.0.147
	hello httpd!
	[root@localhost ~]# curl 10.0.0.16
	hello nginx!
	[root@localhost ~]# 
	
#### 3、使用YAML配置文件为两web容器部署Ingress

##### 配置文件内容

	apiVersion: extensions/v1beta1
	kind: Ingress
	metadata:
	  name: http-test
	spec:
	  rules:
	  - host: nginx.techniques.cn
		http:
		  paths:
		  - backend:
			  serviceName: nginx
			  servicePort: 80
	  - host: http.techniques.cn
		http:
		  paths:
		  - backend:
			  serviceName: httpd
			  servicePort: 80

##### 启动并观察运行情况

	[root@localhost ingress]# kubectl apply -f ingress.yaml 
	ingress.extensions/http-test created
	[root@localhost ingress]# kubectl get ingress
	NAME        HOSTS                                    ADDRESS   PORTS   AGE
	http-test   nginx.techniques.cn,http.techniques.cn             80      5s
	[root@localhost ingress]# kubectl get svc -n ingress-nginx
	NAME            TYPE       CLUSTER-IP   EXTERNAL-IP   PORT(S)                      AGE
	ingress-nginx   NodePort   10.0.0.185   <none>        80:35621/TCP,443:47037/TCP   14m
	[root@localhost ingress]# 

##### 使用域名+NodePort的端口号进行访问测试（同样的也可以进入到pod里去查看nginx的转发规则，都是自动生成的）

##### 再本机进行测试的时候，如果域名未做DNS解析到话记得再本机hosts里添加进去（域名指定到node节点的IP上）

	[root@localhost ingress]# curl nginx.techniques.cn:35621
	hello nginx!
	[root@localhost ingress]# 
	[root@localhost ingress]# curl http.techniques.cn:35621
	hello httpd!
	[root@localhost ingress]# 
	
#### 4、Ingress TLS配置及测试

##### 创建证书文件

1、使用cfssl工具创建ca默认的csr请求文件并做简单修改

    [root@localhost https]# cfssl print-defaults csr > ca-csr.json
    
	[root@localhost https]# cat ca-csr.json 
	{
		"CN": "junping.huang",
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
	
2、使用cfssl工具创建ca默认的配置文件

	[root@localhost https]# cfssl print-defaults config > ca-config.json
	[root@localhost https]# ll
	total 8
	-rw-r--r-- 1 root root 567 Nov 27 16:41 ca-config.json
	-rw-r--r-- 1 root root 214 Nov 27 16:40 ca-csr.json
	[root@localhost https]# cat ca-config.json 
	{
		"signing": {
			"default": {
				"expiry": "168h"
			},
			"profiles": {
				"www": {
					"expiry": "8760h",
					"usages": [
						"signing",
						"key encipherment",
						"server auth"
					]
				},
				"client": {
					"expiry": "8760h",
					"usages": [
						"signing",
						"key encipherment",
						"client auth"
					]
				}
			}
		}
	}

	[root@localhost https]# 
	
3、生成ca证书文件

	[root@localhost https]# cfssl gencert --initca ca-csr.json | cfssljson -bare ca -
	2018/11/27 16:43:13 [INFO] generating a new CA key and certificate from CSR
	2018/11/27 16:43:13 [INFO] generate received request
	2018/11/27 16:43:13 [INFO] received CSR
	2018/11/27 16:43:13 [INFO] generating key: rsa-2048
	2018/11/27 16:43:13 [INFO] encoded CSR
	2018/11/27 16:43:13 [INFO] signed certificate with serial number 214425891397086178385347946693610147304915218363
	[root@localhost https]# ll
	total 20
	-rw-r--r-- 1 root root  567 Nov 27 16:41 ca-config.json
	-rw-r--r-- 1 root root  960 Nov 27 16:43 ca.csr
	-rw-r--r-- 1 root root  214 Nov 27 16:40 ca-csr.json
	-rw------- 1 root root 1675 Nov 27 16:43 ca-key.pem
	-rw-r--r-- 1 root root 1277 Nov 27 16:43 ca.pem
	[root@localhost https]# 

4、为主机网站生成请求文件

    [root@localhost https]# cfssl print-defaults csr > server-csr.json
    
	[root@localhost https]# cat server-csr.json 
	{
		"CN": "test.techniques.cn",
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

5、生成网站证书

	[root@localhost https]# cfssl gencert -ca=ca.pem -ca-key=ca-key.pem --config=ca-config.json --profile=www server-csr.json | cfssljson -bare server
	2018/11/27 16:47:16 [INFO] generate received request
	2018/11/27 16:47:16 [INFO] received CSR
	2018/11/27 16:47:16 [INFO] generating key: rsa-2048
	2018/11/27 16:47:16 [INFO] encoded CSR
	2018/11/27 16:47:16 [INFO] signed certificate with serial number 436534675730573242548459183083994505108631399936
	2018/11/27 16:47:16 [WARNING] This certificate lacks a "hosts" field. This makes it unsuitable for
	websites. For more information see the Baseline Requirements for the Issuance and Management
	of Publicly-Trusted Certificates, v.1.1.6, from the CA/Browser Forum (https://cabforum.org);
	specifically, section 10.2.3 ("Information Requirements").
	[root@localhost https]# ll
	total 36
	-rw-r--r-- 1 root root  567 Nov 27 16:41 ca-config.json
	-rw-r--r-- 1 root root  960 Nov 27 16:43 ca.csr
	-rw-r--r-- 1 root root  214 Nov 27 16:40 ca-csr.json
	-rw------- 1 root root 1675 Nov 27 16:43 ca-key.pem
	-rw-r--r-- 1 root root 1277 Nov 27 16:43 ca.pem
	-rw-r--r-- 1 root root  968 Nov 27 16:47 server.csr
	-rw-r--r-- 1 root root  219 Nov 27 16:45 server-csr.json
	-rw------- 1 root root 1675 Nov 27 16:47 server-key.pem
	-rw-r--r-- 1 root root 1306 Nov 27 16:47 server.pem
	[root@localhost https]# 
	
6、将证书使用secret资源导入到k8s集群中去

	[root@localhost https]# kubectl create secret tls jason-https --key server-key.pem --cert server.pem 
	secret/jason-https created
	[root@localhost https]# kubectl get secret
	NAME                  TYPE                                  DATA   AGE
	default-token-p4p6m   kubernetes.io/service-account-token   3      6d2h
	jason-https           kubernetes.io/tls                     2      5s
	[root@localhost https]# 

7、编写Ingress关联配置文件，并启动Ingress

	[root@localhost https]# cat ingress-https.yaml 
	apiVersion: extensions/v1beta1
	kind: Ingress
	metadata:
	  name: https-test
	spec:
	  tls:
	  - hosts:
		- test.techniques.cn
		secretName: jason-https
	  rules:
	  - host: test.techniques.cn
		http:
		  paths:
		  - backend:
			  serviceName: nginx
			  servicePort: 80
	[root@localhost https]# 
	[root@localhost https]# kubectl apply -f ingress-https.yaml 
	ingress.extensions/https-test created
	[root@localhost https]# kubectl get ingress
	NAME         HOSTS                                    ADDRESS   PORTS     AGE
	http-test    nginx.techniques.cn,http.techniques.cn             80        176m
	https-test   test.techniques.cn                                 80, 443   10s
	[root@localhost https]# 

8、测试Ingress的tls功能

![image](https://github.com/hdpingshao/ops/blob/master/kubernetes/images/7-2.jpg)