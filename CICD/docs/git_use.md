### 部署Git仓库

##### 1、安装Git

    yum install git

##### 2、创建Git用户并设置密码

    useradd git
    passwd git

##### 3、创建仓库

    su - git
    mkdir app.git
    cd app.git
    git --bare init
    
##### 4、配置客户端SSH密钥认证

##### 5、提交代码

    git clone git@192.168.200.120:/home/git/app.git
    git add .
    git commit -m "init files"
    git push origin master