### 一、二进制部署（prometheus-2.7.1.linux-amd64.tar.gz）

##### 1、下载地址： https://prometheus.io/download/#node_exporter

    # 下载prometheus安装包
    wget https://github.com/prometheus/prometheus/releases/download/v2.7.1/prometheus-2.7.1.linux-amd64.tar.gz
	# 解压二进制安装包
	tar zxvf prometheus-2.7.1.linux-amd64.tar.gz
	# 移动重命名
	mv prometheus-2.7.1.linux-amd64 /usr/local/prometheus
	# 生成启动脚本
	cat << EOF > /usr/lib/systemd/system/prometheus.service
	[Unit]
	Description=prometheus.io

	[Service]
	ExecStart=/usr/local/prometheus/prometheus --config.file=/usr/local/prometheus/prometheus.yml
	Restart=on-failure

	[Install]
	WantedBy=multi-user.target
	EOF

	# 重载启动文件
	systemctl daemon-reload
	# 启动prometheus
	systemctl start prometheus
	
##### 2、查看prometheus配置文件

	[root@localhost prometheus]# cat prometheus.yml 
	# my global config
	global:
	  scrape_interval:     15s # Set the scrape interval to every 15 seconds. Default is every 1 minute.
	  evaluation_interval: 15s # Evaluate rules every 15 seconds. The default is every 1 minute.
	  # scrape_timeout is set to the global default (10s).

	# Alertmanager configuration
	alerting:
	  alertmanagers:
	  - static_configs:
		- targets:
		  # - alertmanager:9093

	# Load rules once and periodically evaluate them according to the global 'evaluation_interval'.
	rule_files:
	  # - "first_rules.yml"
	  # - "second_rules.yml"

	# A scrape configuration containing exactly one endpoint to scrape:
	# Here it's Prometheus itself.
	scrape_configs:
	  # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
	  - job_name: 'prometheus'

		# metrics_path defaults to '/metrics'
		# scheme defaults to 'http'.

		static_configs:
		- targets: ['localhost:9090']
	
##### 3、访问prometheus的web(监听9090端口)

    http://192.168.200.33:9090
    
##### 4、示意图

![image](https://github.com/hdpingshao/ops/tree/master/prometheus/images/prometheus3-1.jpg)