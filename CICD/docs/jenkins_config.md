### Jenkins配置

##### 1、添加Kubernetes配置

- 系统管理 ---> 系统设置 ---> Add a new cloud
- 填入Kubernetes URL以及Jenkins URL
- 都是通过k8s集群的dns来解析这两个URL的service的（集群内部使用）

![image](https://github.com/hdpingshao/ops/blob/master/CICD/images/jenkins1.jpg)

##### 2、添加Git密钥认证使得Jenkins可以直接拉取git代码

- 使用ssh-keygen生成一个密钥对
- 将公钥复制到git服务器的/root/.ssh/authorized_keys里
- 将私钥复制到Jenkins凭据里（凭据--->Jenkins--->全局凭据（unrestricted）--->添加凭据--->类型选择SSH Username with private key--->将私钥复制到Private Key即可）

![image](https://github.com/hdpingshao/ops/blob/master/CICD/images/jenkins2.jpg)

##### 3、添加Kubernetes认证

- 生成配置文件(准备好脚本文件、ca证书私钥、admin私钥公钥)，这些密钥都是之前部署集群的时候生成过的，直接拿来用即可

	kubectl config set-cluster kubernetes \
	  --server=https://192.168.200.142:6443 \
	  --embed-certs=true \
	  --certificate-authority=ca.pem \
	  --kubeconfig=config
	kubectl config set-credentials cluster-admin \
	  --certificate-authority=ca.pem \
	  --embed-certs=true \
	  --client-key=admin-key.pem \
	  --client-certificate=admin.pem \
	  --kubeconfig=config
	kubectl config set-context default --cluster=kubernetes --user=cluster-admin --kubeconfig=config
	kubectl config use-context default --kubeconfig=config


- 将所有用到的证书、脚本文件放同一个文件夹然后执行脚本即可（执行完成后会在该目录下生成config的文件）
- 拷贝生成到config文件到Jenkins使用即可（凭据--->Jenkins--->全局凭据（unrestricted）--->添加凭据--->类型选择Kubernetes configuration(kubeconfig)--->将刚生成的config的内容复制到Kubeconfig即可)

![image](https://github.com/hdpingshao/ops/blob/master/CICD/images/jenkins3.jpg)

### Jenkins Pipeline使用简单示例

##### 1、创建一个pipeline流水线任务并简单编写流水线脚本测试

![image](https://github.com/hdpingshao/ops/blob/master/CICD/images/jenkins4.jpg)

- 编写pipeline脚本

![image](https://github.com/hdpingshao/ops/blob/master/CICD/images/jenkins5.jpg)

##### 2、点击立即构建查看构建结果

![image](https://github.com/hdpingshao/ops/blob/master/CICD/images/jenkins6.jpg)

- 也可以进入查看构建运行的日志信息（构建出错时排查问题用）