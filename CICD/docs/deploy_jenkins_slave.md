##### jenkins slave模式原理图

![image](https://github.com/hdpingshao/ops/blob/master/CICD/images/jenkins-slave.jpg)

##### 编写构建jenkins-slave镜像的Dockerfile文件

	FROM ubuntu
	MAINTAINER junping.huang

	ENV JAVA_HOME /usr/local/jdk
	ENV PATH=${JAVA_HOME}/bin:/usr/local/maven/bin:$PATH

	RUN apt-get update && \
		apt-get install -y curl git libltdl-dev && \ 
		apt-get clean all && \ 
		rm -rf /var/lib/apt && \
		mkdir -p /usr/share/jenkins

	COPY slave.jar /usr/share/jenkins/slave.jar  
	COPY jenkins-slave /usr/bin/jenkins-slave

	ENTRYPOINT ["jenkins-slave"]

> * 其中slave.jar是从部署起来的jenkins里下载的

##### jenkins-slave脚本文件内容

	#!/usr/bin/env sh

	if [ $# -eq 1 ]; then

		# if `docker run` only has one arguments, we assume user is running alternate command like `bash` to inspect the image
		exec "$@"

	else

		# if -tunnel is not provided try env vars
		case "$@" in
			*"-tunnel "*) ;;
			*)
			if [ ! -z "$JENKINS_TUNNEL" ]; then
				TUNNEL="-tunnel $JENKINS_TUNNEL"
			fi ;;
		esac

		# if -workDir is not provided try env vars
		if [ ! -z "$JENKINS_AGENT_WORKDIR" ]; then
			case "$@" in
				*"-workDir"*) echo "Warning: Work directory is defined twice in command-line arguments and the environment variable" ;;
				*)
				WORKDIR="-workDir $JENKINS_AGENT_WORKDIR" ;;
			esac
		fi

		if [ -n "$JENKINS_URL" ]; then
			URL="-url $JENKINS_URL"
		fi

		if [ -n "$JENKINS_NAME" ]; then
			JENKINS_AGENT_NAME="$JENKINS_NAME"
		fi  

		if [ -z "$JNLP_PROTOCOL_OPTS" ]; then
			echo "Warning: JnlpProtocol3 is disabled by default, use JNLP_PROTOCOL_OPTS to alter the behavior"
			JNLP_PROTOCOL_OPTS="-Dorg.jenkinsci.remoting.engine.JnlpProtocol3.disabled=true"
		fi

		# If both required options are defined, do not pass the parameters
		OPT_JENKINS_SECRET=""
		if [ -n "$JENKINS_SECRET" ]; then
			case "$@" in
				*"${JENKINS_SECRET}"*) echo "Warning: SECRET is defined twice in command-line arguments and the environment variable" ;;
				*)
				OPT_JENKINS_SECRET="${JENKINS_SECRET}" ;;
			esac
		fi
		
		OPT_JENKINS_AGENT_NAME=""
		if [ -n "$JENKINS_AGENT_NAME" ]; then
			case "$@" in
				*"${JENKINS_AGENT_NAME}"*) echo "Warning: AGENT_NAME is defined twice in command-line arguments and the environment variable" ;;
				*)
				OPT_JENKINS_AGENT_NAME="${JENKINS_AGENT_NAME}" ;;
			esac
		fi

		#TODO: Handle the case when the command-line and Environment variable contain different values.
		#It is fine it blows up for now since it should lead to an error anyway.

		exec java $JAVA_OPTS $JNLP_PROTOCOL_OPTS -cp /usr/share/jenkins/slave.jar hudson.remoting.jnlp.Main -headless $TUNNEL $URL $WORKDIR $OPT_JENKINS_SECRET $OPT_JENKINS_AGENT_NAME "$@"
	fi

##### 构建jenkins-slave镜像并上传至harbor仓库

	[root@localhost jenkins-slave]# ll
	total 764
	-rw-r--r-- 1 root root    403 Jan  5 14:55 Dockerfile
	-rw-r--r-- 1 root root   1980 Apr  6  2018 jenkins-slave
	-rw-r--r-- 1 root root 770802 Jun 11  2018 slave.jar
	[root@localhost jenkins-slave]# docker build -t 192.168.200.120/devops/jenkins-slave .
	[root@localhost jenkins-slave]# docker push 192.168.200.120/devops/jenkins-slave:latest

##### 至此，jenkins-slave镜像制作成功并上传到harbor仓库供后期所用

### 注意：因为创建的镜像有使用宿主机的jdk以及maven工具，所以我们需要先在所有的宿主机上安装好jdk以及maven，统一放在/usr/local/目录下。

	[root@localhost ~]# ls
	anaconda-ks.cfg  apache-maven-3.6.0-bin.tar.gz  get-pip.py  jdk-8u191-linux-x64.tar.gz
	[root@localhost ~]# tar zxvf apache-maven-3.6.0-bin.tar.gz -C /usr/local/
	[root@localhost ~]# mv /usr/local/apache-maven-3.6.0 /usr/local/maven
	[root@localhost ~]# tar zxvf jdk-8u191-linux-x64.tar.gz -C /usr/local/
	[root@localhost ~]# mv /usr/local/jdk1.8.0_191 /usr/local/jdk