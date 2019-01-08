### 在kubernetes中部署Jenkins

##### 部署Jenkins所需的yaml文件

> * https://github.com/jenkinsci/kubernetes-plugin/tree/master/src/main/kubernetes

##### 自己修改后的yaml文件如下：

> * https://github.com/hdpingshao/ops/blob/master/sh/jenkins.yml

##### 构建jenkins镜像并推送到harbor仓库中

1、创建Dockerfile文件来构建jenkins镜像

	[root@localhost jenkins]# cat Dockerfile 
	FROM jenkinsci/jenkins:2.150.1
	USER root
	[root@localhost jenkins]# docker build -t 192.168.200.120/devops/jenkinsci:2.150.1 .
	Sending build context to Docker daemon 2.048 kB
	Step 1 : FROM jenkinsci/jenkins:2.150.1
	 ---> a6266e13a5b8
	Step 2 : USER root
	 ---> Running in ed79147c4c46
	 ---> a290e92413cd
	Removing intermediate container ed79147c4c46
	Successfully built a290e92413cd
	[root@localhost jenkins]# 

2、将生成的镜像推送到本地harbor仓库中

	[root@localhost jenkins]# docker login 192.168.200.120
	Username: junping.huang
	Password: 
	Login Succeeded
	[root@localhost jenkins]# docker push 192.168.200.120/devops/jenkinsci:2.150.1
	The push refers to a repository [192.168.200.120/devops/jenkinsci]
	a4157a3ccda1: Pushed 
	d41267da31e9: Pushed 
	590df6670f65: Pushed 
	cf24a00a4375: Pushed 
	2c6ad22a8e03: Pushed 
	877964a0e610: Pushed 
	0e09955c4188: Pushed 
	409468cac1c3: Pushed 
	25a76ab6817d: Pushed 
	d38957d1f87c: Pushed 
	313e226824e9: Pushed 
	ed6f0bd39121: Pushed 
	0c3170905795: Pushed 
	df64d3292fd6: Pushed 
	lts-alpine: digest: sha256:643583bb11c4c15b22fbf211e586ab1ade2d26524099575b8e2695c9aa65de98 size: 3239
	[root@localhost jenkins]# 
	
##### 生成拉取harbor镜像仓库镜像的secret

> * 注：只要你在本机上有登陆过harbor的仓库就会在本机上生成一个文件

    [root@localhost jenkins]# cat ~/.docker/config.json 
    {
            "auths": {
                    "192.168.200.120": {
                            "auth": "anVucGluZy5odWFuZzoxcWF6QFdTWA=="
                    }
            }
    }

> * 使用该文件生成一个base64的编码用于创建secret拉取镜像

    [root@localhost jenkins]# cat ~/.docker/config.json | base64 -w0
    ewoJImF1dGhzIjogewoJCSIxOTIuMTY4LjIwMC4xMjAiOiB7CgkJCSJhdXRoIjogImFuVnVjR2x1Wnk1b2RXRnVaem94Y1dGNlFGZFRXQT09IgoJCX0KCX0KfQ==

> * 编辑secret的yaml文件

    [root@localhost jenkins]# cat registry-pull-secret.yaml 
    apiVersion: v1
    kind: Secret
    metadata:
      name: registry-pull-secret
      namespace: default
    data:
      .dockerconfigjson: ewoJImF1dGhzIjogewoJCSIxOTIuMTY4LjIwMC4xMjAiOiB7CgkJCSJhdXRoIjogImFuVnVjR2x1Wnk1b2RXRnVaem94Y1dGNlFGZFRXQT09IgoJCX0KCX0KfQ==
    type: kubernetes.io/dockerconfigjson

    [root@localhost jenkins]# 

> * 创建secret、sa、以及jenkins

    [root@localhost jenkins]# kubectl apply -f jenkins-service-account.yml 
    serviceaccount/jenkins unchanged
    role.rbac.authorization.k8s.io/jenkins unchanged
    rolebinding.rbac.authorization.k8s.io/jenkins unchanged
    [root@localhost jenkins]# kubectl apply -f registry-pull-secret.yaml 
    secret/registry-pull-secret created
    [root@localhost jenkins]# kubectl apply -f jenkins.yml 
    persistentvolume/jenkins-pv-gluster created
    persistentvolumeclaim/jenkins-pvc-gluster created
    statefulset.apps/jenkins created
    service/jenkins created
    [root@localhost jenkins]# 
    
> * 使用日志中打印出来的密码串来初始化jenkins

##### 必须安装的几个插件

- Git Parameter
- Kubernetes Continuous Deploy
- Kubernetes
- Extended Choice Parameter