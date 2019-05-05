#_*_coding:utf-8_*_

import poplib
import re

from email.parser import Parser

def emailCaptcha(user,password):
    '''
    this function get mail result,appleid
    :param user:
    :param password:
    :return:
    '''
    if "163.com" in user:
        server = "pop.163.com"
    elif "126.com" in user:
        server = "pop.126.com"
    elif "sina.com" in user:
        server = "pop3.sina.com.cn"
    elif "sina.cn" in user:
        server = "pop3.sina.com"
    elif "sohu.com" in user:
        server = "pop3.sohu.com"
    elif "qq.com" in user:
        server = "pop.qq.com"
    elif "tom.com" in user:
        server = "pop.tom.com"
    else:
        server = "mail.xsroad.com"

    try:
        ser_obj = poplib.POP3(server)
        ser_obj.user(user)
        ser_obj.pass_(password)

        a,b,c = ser_obj.list()
        msg_all = ser_obj.retr(len(b))
        msg = '\r\n'.join(msg_all[1])
        msg_obj = Parser().parsestr(msg)

        result = []
        for par in msg_obj.walk():
            if not par.is_multipart():
                for i in  par.get_payload(decode=True).split('\r\n'):
                    if i:
                        result.append(i)
                    else:
                        continue
    except poplib.error_proto,e:
        print "poplib.error: ",e
    finally:
        ser_obj.quit()
    return result

def getAppleUrl(user,passwd):
    '''
    from E-mail get apple redirect url
    :param user:
    :param passwd:
    :return:
    '''
    mailString = []
    mailResult = emailCaptcha(user,passwd)
    for i in mailResult:
        if "a href" in i:
            mailString.append(i)
    pattern = re.compile('<a href="(.*?)" ',re.S)
    item = re.findall(pattern=pattern,string=mailString[0])
    return item[0]