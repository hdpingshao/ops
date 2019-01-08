### 准备好相关软件包

##### 部署docker环境

    [root@localhost ~]# setenforce 0
    [root@localhost ~]# systemctl stop firewalld
    [root@localhost ~]#systemctl disable firewalld
    [root@localhost ~]# yum install -y wget lrzsz yum-utils device-mapper-persistent-data lvm2
    [root@localhost ~]# yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    [root@localhost ~]# yum install -y docker-ce
    [root@localhost ~]# systemctl restart docker
	[root@localhost ~]# cat << EOF > /etc/docker/daemon.json
	{
	  "registry-mirrors": ["http://f1361db2.m.daocloud.io"],
	}
	EOF
    [root@localhost ~]# systemctl daemon-reload
    [root@localhost ~]# systemctl restart docker

##### Harbor下载地址：

> * https://github.com/goharbor/harbor/releases

> * 下载Harbor offline installer的安装包即可

##### 下载docker-compose工具来进行harbor的管理

> * 下载地址：

> * https://github.com/docker/compose/releases

> * 下载docker-compose-Linux-x86_64版的即可

> * 下载好后将其改名成docker-compose，并将该工具移至/usr/local/bin目录下(也就是添加到环境变量下去)

> * chmod +x /usr/local/bin/docker-compose

##### 准备好后上传到服务器上即可，或者直接在服务器上下载也行

##### 解压harbor包并修改相关配置信息

    [root@localhost src]# tar zxvf harbor-offline-installer-v1.7.0.tgz
    [root@localhost src]# cd harbor
    [root@localhost harbor]# sed -i 's/reg.mydomain.com/192.168.200.120/g' harbor.cfg
	[root@localhost harbor]# ./prepare 
	Generated and saved secret to file: /data/secretkey
	Generated configuration file: ./common/config/nginx/nginx.conf
	Generated configuration file: ./common/config/adminserver/env
	Generated configuration file: ./common/config/core/env
	Generated configuration file: ./common/config/registry/config.yml
	Generated configuration file: ./common/config/db/env
	Generated configuration file: ./common/config/jobservice/env
	Generated configuration file: ./common/config/jobservice/config.yml
	Generated configuration file: ./common/config/log/logrotate.conf
	Generated configuration file: ./common/config/registryctl/env
	Generated configuration file: ./common/config/core/app.conf
	Generated certificate, key file: ./common/config/core/private_key.pem, cert file: ./common/config/registry/root.crt
	The configuration files are ready, please use docker-compose to start the service.
    [root@localhost harbor]# ./install.sh
    [root@localhost harbor]# docker-compose ps
		   Name                     Command                  State                                    Ports                              
	-------------------------------------------------------------------------------------------------------------------------------------
	harbor-adminserver   /harbor/start.sh                 Up (healthy)                                                                   
	harbor-core          /harbor/start.sh                 Up (healthy)                                                                   
	harbor-db            /entrypoint.sh postgres          Up (healthy)   5432/tcp                                                        
	harbor-jobservice    /harbor/start.sh                 Up                                                                             
	harbor-log           /bin/sh -c /usr/local/bin/ ...   Up (healthy)   127.0.0.1:1514->10514/tcp                                       
	harbor-portal        nginx -g daemon off;             Up (healthy)   80/tcp                                                          
	nginx                nginx -g daemon off;             Up (healthy)   0.0.0.0:443->443/tcp, 0.0.0.0:4443->4443/tcp, 0.0.0.0:80->80/tcp
	redis                docker-entrypoint.sh redis ...   Up             6379/tcp                                                        
	registry             /entrypoint.sh /etc/regist ...   Up (healthy)   5000/tcp                                                        
	registryctl          /harbor/start.sh                 Up (healthy)   
	
##### 至此harbor部署完成，使用web登陆

- http://192.168.200.120

- 用户名： admin（默认）

- 密 码： Harbor12345（默认）

![image](https://github.com/hdpingshao/ops/blob/master/CICD/images/cicd1.jpg)