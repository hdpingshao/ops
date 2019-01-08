### gitlab+jenkins+pipeline实现自动化部署到k8s集群

##### 1、创建pipeline流水线工程并配置与gitlab结合以及流水线脚本配置

- 配置gitlab调用地址

![image](https://github.com/hdpingshao/ops/blob/master/CICD/images/jenkinsfile1.jpg)

- 流水线脚本配置

![image](https://github.com/hdpingshao/ops/blob/master/CICD/images/jenkinsfile2.jpg)

##### 2、以网上拉取的一个开源博客系统举例部署自动化工程案例

###### 2.1、 准备好博客系统源代码，并创建好deploy目录用于存放自动化Jenkinsfile等文件

	[root@localhost solo]# ll
	total 392
	-rw-r--r-- 1 root root 104684 Jan  7 13:51 CHANGE_LOGS.html
	-rw-r--r-- 1 root root   3209 Jan  7 13:51 CODE_OF_CONDUCT.md
	-rw-r--r-- 1 root root    931 Jan  7 13:51 CONTRIBUTING.md
	drwxr-xr-x 2 root root   4096 Jan  8 15:33 deploy
	-rw-r--r-- 1 root root    426 Jan  7 13:51 docker-compose.yml
	-rw-r--r-- 1 root root    897 Jan  7 13:51 Dockerfile
	-rw-r--r-- 1 root root   3664 Jan  7 13:51 gulpfile.js
	-rw-r--r-- 1 root root  34522 Jan  7 13:51 LICENSE
	-rw-r--r-- 1 root root   1049 Jan  7 13:51 package.json
	-rw-r--r-- 1 root root 192993 Jan  7 13:51 package-lock.json
	-rw-r--r-- 1 root root  18655 Jan  7 13:51 pom.xml
	-rw-r--r-- 1 root root    313 Jan  7 13:51 PULL_REQUEST_TEMPLATE.md
	-rw-r--r-- 1 root root   4852 Jan  7 13:51 README.md
	drwxr-xr-x 2 root root     33 Jan  7 13:51 scripts
	drwxr-xr-x 4 root root     28 Jan  7 13:51 src
	
###### 2.2、准备好deploy目录下的脚本文件

- Jenkinsfile(自动化部署流水线脚本):
> * https://github.com/hdpingshao/ops/blob/master/CICD/sh/Jenkinsfile

- Dockerfile(构建博客系统镜像的脚本):
> * https://github.com/hdpingshao/ops/blob/master/CICD/sh/Dockerfile

- docker-entrypoint.sh（启动参数环境）:
> * https://github.com/hdpingshao/ops/blob/master/CICD/sh/docker-entrypoint.sh

- deploy.yaml(博客系统k8s资源部署yaml文件):
> * https://github.com/hdpingshao/ops/blob/master/CICD/sh/deploy.yaml

###### 2.3、将准备好的这些文件一起上传到git仓库中，保存到代码仓库中，当jenkins去自动化部署的时候会下载仓库的代码，同时使用仓库中的deploy目录下的自动化脚本进行自动化部署

##### 3、gitlab配置webhook钩子（简单，网上很多介绍）

![image](https://github.com/hdpingshao/ops/blob/master/CICD/images/jenkinsfile5.jpg)

##### 4、进入到gitlab工程项目中生成一个tag即会触发jenkins进行自动化部署操作

![image](https://github.com/hdpingshao/ops/blob/master/CICD/images/jenkinsfile3.jpg)

jenkins自动生成任务

![image](https://github.com/hdpingshao/ops/blob/master/CICD/images/jenkinsfile2.jpg)

查看jenkins下改项目的部署日志

![image](https://github.com/hdpingshao/ops/blob/master/CICD/images/jenkinsfile6.jpg)

##### 5、查看k8s集群部署情况

![image](https://github.com/hdpingshao/ops/blob/master/CICD/images/jenkinsfile7.jpg)
