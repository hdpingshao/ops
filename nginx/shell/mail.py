#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding('utf8')
import getopt
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from subprocess import *


def sendqqmail(username, password, mailfrom, mailto, subject, content):
    gserver = 'smtp.qq.com'
    gport = 25

    try:
        # msg = MIMEText(unicode(content).encode('utf-8')) //如果发送的邮件有乱码，可以尝试把这行改成如下：
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['from'] = mailfrom
        msg['to'] = mailto
        msg['Reply-To'] = mailfrom
        msg['Subject'] = subject

        smtp = smtplib.SMTP(gserver, gport)
        smtp.set_debuglevel(0)
        smtp.ehlo()
        smtp.login(username, password)

        smtp.sendmail(mailfrom, mailto, msg.as_string())
        smtp.close()
    except Exception, err:
        print
        "Send mail failed. Error: %s" % err


def main():
    to = sys.argv[1]
    subject = sys.argv[2]
    content = sys.argv[3]
    ##定义QQ邮箱的账号和密码，你需要修改成你自己的账号和密码（请不要把真实的用户名和密码放到网上公开，否则你会死的很惨）
    # sendqqmail('junping.huang@zkteco.com','aaaaaaaaaa','junping.huang@zkteco.com',to,subject,content)
    sendqqmail('123@qq.com', 'axxudrojprdgbgde', '123@qq.com', to, subject, content)


if __name__ == "__main__":
    main()

#####脚本使用说明######
# 1. 首先定义好脚本中的邮箱账号和密码
# 2. 脚本执行命令为：python mail.py 目标邮箱 "邮件主题" "邮件内容"