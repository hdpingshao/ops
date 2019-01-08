#### YAML语法格式：

- YAML是一种简洁的非标记语言
- 缩进表示层级关系
- 不支持制表符“tab”缩进，使用空格缩进
- 通常开头缩进2个空格
- 字符后缩进1个空格，如冒号、逗号等
- “---”表示YAML格式，一个我呢见的开始
- “#” 注释

#### YAML配置文件说明：

- 定义配置时，指定最新稳定版API（当前为v1）；
- 配置文件应该存储在集群之外的版本控制仓库中。如果需要，可以快速回滚配置、重新创建和恢复；
- 应该使用YAML格式编写配置文件，而不是JSON。尽管这些格式都可以使用，但YAML对用户更加友好；
- 可以将相关对象组合成单个文件，通常会更容易管理；
- 不要没必要的去指定默认值，简单和最小配置减少错误；
- 在注释中说明一个对象描述更好维护

#### 部署一个nginx的deployment的YAML配置文件

	apiVersion: extensions/v1beta1
	kind: Deployment
	metadata:
	  name: nginx-deployment
	  namespace: default
	spec:
	  replicas: 3
	  selector:
		matchLabels:
		  app: nginx
	  template:
		metadata:
		  labels:
			app: nginx
		spec:
		  containers:
		  - name: nginx
            image: nginx:1.10
            ports:
            - containerPort: 80
			
#### 为上述deployment控制器创建service提供外部访问接口的配置文件

	apiVersion: v1
	kind: Service
	metadata:
	  name: nginx-svc
	  labels:
		app: nginx
	spec:
	  ports:
	  - port: 80
		targetPort: 80
	  selector:
		app: nginx