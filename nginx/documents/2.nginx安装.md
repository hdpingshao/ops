# 一、Nginx安装-yum安装
    >> cat /etc/yum.repos.d/nginx.repo
    [nginx]
    name=nginx repo
    baseurl=http://nginx.org/packages/centos/$releasever/$basearch/
    gpgcheck=0
    enabled=1
    >> yum install -y nginx
    >> systemctl start/stop/restart/reload nginx
### 测试：浏览器访问或者curl访问
> * 检查服务进程:ps aux | grep nginx
> * 检查端口监听:netstat -lntp | grep ":80"
> * 有防火墙，需要加规则iptables -I INPUT -p tcp --dport 80 -j ACCEPT
### nginx -V查看版本以及各个目录、参数
------
# 二、Nginx安装-源码安装
    wget http://nginx.org/download/nginx-1.14.0.tar.gz
    tar zxf nginx-1.14.0.tar.gz
    cd nginx-1.14.0; ./configure --prefix=/usr/local/nginx
    make && make install
    /usr/local/nginx/sbin/nginx  //启动

### 注：
> * pkill nginx //杀死nginx进程，停止nginx服务
> * /usr/local/nginx/sbin/nginx -t  //检测配置文件语法错误
> * /usr/local/nginx/sbin/nginx -s reload //重载配置

### 服务管理脚本
> * https://github.com/hdpingshao/ops/blob/master/nginx/etc_init_nginx.txt