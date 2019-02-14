### 1、prometheus简介

##### prometheus（普罗米修斯）是一个最初在SoundCloud上构建的监控系统。自2012年成为社区开源项目，拥有非常活跃的开发人员和用户社区。为强调开源及独立维护，Prometheus于2016年加入云原生云计算基金会（CNCF），成为继Kubernetes之后的第二个托管项目。

- 官网： https://prometheus.io
- github地址： https://github.com/prometheus

##### prometheus特点：

- 多维数据模型：由度量名称和键值对标识的时间序列数据
- PromSQL：一种灵活的查询语言，可以利用多维数据完成复杂的查询
- 不依赖分布式存储，单个服务器节点可直接工作
- 基于HTTP的pull方式采集时间序列数据
- 推送时间序列数据通过PushGateway组件支持
- 通过服务发现或静态配置发现目标
- 多种图形模式及仪表盘支持（grafana）

### 2、prometheus组成及架构图

##### 架构图

![image](https://github.com/hdpingshao/ops/tree/master/prometheus/images/prometheus2-1.jpg

##### 组成

- Prometheus Server：收集指标和存储时间序列数据，并提供查询接口
- ClientLibrary：客户端库
- Push Gateway：短期存储指标数据。主要用于临时性的任务
- Exporters：采集已有的第三方服务监控指标并暴露metrics
- Alertmanager：告警
- Web UI：简单的Web控制台

### 3、数据模型

##### Prometheus将所有数据存储为时间序列；具有相同度量名称以及标签属于同一个指标。

##### 每个时间序列都由度量标准名称和一组键值对（也称为标签）唯一标识。

##### 时间序列格式:

##### \<metric name\>{\<label name\>=\<label value\>, ...}

##### 示例：api_http_requests_total{method="POST", handler="/messages"}

### 4、指标类型

- Counter： 递增的计数器
- Gauge： 可以任意变化的数值
- Histogram： 对一段时间范围内数据进行采样，并对所有数值求和与统计数量
- Summary： 与Histogram类似

### 5、作业和实例

##### 实例： 可以抓取的目标称为实例（Instances）
##### 作业： 具有相同目标的实例集合称为作业（Job）

	scrape_configs:
	  - job_name: 'prometheus'
		static_configs:
		- targets: ['localhost:9090']
	  -job_name: 'node'
		static_configs:
		- targets: ['192.168.200.121:9090']