#_*_coding:utf-8_*_

from requests_appleid3 import GetCaptcha
from data_insert import main as db_main
import commands
import time
from time import sleep
import os
import requests
import poplib
import random


firstName = ['zhao','qian','sun','li','zhou','wu','zheng','wang','feng','cheng','chu','wei','jiang','sheng','han','yang']
lastName = ['tian','di','ling','hua','yan','bing','shan','xia','qiu','shi','xu','shi','wen','ming','jiang','chang','hui']
birthday_year = ['1986','1987','1988','1989','1990','1991','1992','1993','1994','1995','1996']
birthday_month = ['01','02','03','04','05','06','07','08','09','10','11','12']
birthday_day = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21']

def swichIp(account):
    '''
    调用shell脚本，切换IP地址
    :param account:
    :return:
    '''
    cmd = "sh swichip.sh"
    status_code,command_result = commands.getstatusoutput(cmd)
    if status_code != 0:
        raise NameError("IpSwichFailed")
    else:
        with open("../logs/ipswich_record.txt",'a') as f:
            f.write(account+': '+command_result+'\n')

def main(appleid,passwd,number_retry=1,error_record=None):
    '''
    主调用方法，申请成功的记录文件，申请失败的根据异常处理重试
    :param appleid:
    :param passwd:
    :param number_retry: 重试次数，默认5次
    :return:
    '''
    random_birthday = random.choice(birthday_year)+'-'+random.choice(birthday_month)+'-'+random.choice(birthday_day)
    getCaptcha = GetCaptcha(appleid, '123TabcdE', 'CHN', random.choice(firstName), random.choice(lastName),random_birthday,
                            "What was the name of your first pet?",
                            "What is your dream job?",
                            "What was the first name of your first boss?",
                            'DISC', 'CSID', 'SSID')
    try:
        getCaptcha.log_define("============================apply for %s==========================" % appleid)
        getCaptcha.captcha()
        getCaptcha.getCountry()
        sleep(2)
        getCaptcha.postAppleid()
        sleep(2)
        getCaptcha.postPassword()
        sleep(2)
        getCaptcha.postPassword()
        sleep(2)
        getCaptcha.postPassword()
        sleep(2)
        getCaptcha.postRegister()
        sleep(2)
        getCaptcha.requestEmailCaptcha()
        sleep(30)
        getCaptcha.putEmailCaptchaResult(passwd)
        sleep(2)
        getCaptcha.postRegisterForm()

        #如果申请成功的处理
        appleid_file = "../logs/appleid_%s.txt" % time.strftime('%Y-%m-%d',time.localtime(time.time()))
        with open(appleid_file,'a') as f:
            #f.write(appleid + '\n')
            f.write(appleid +'----'+passwd)
    except poplib.error_proto as e: #处理邮箱连接失败
        getCaptcha.log_define("MailBox Connect Error: " + str(e))
        if number_retry > 0:
            number_retry -= 1
            sleep(10)
            main(appleid, passwd, number_retry,error_record)
        else:
            if "failure_appleid" in error_record:
                with open(error_record, 'a') as f:
                    f.write(appleid + "----" + passwd)
            else:
                with open(error_record, 'a') as f:
                    f.write(appleid + "----" + passwd.strip() + " error_msg: " + str(e) + '\n')
    except requests.Timeout as e: #处理请求超时
        getCaptcha.log_define("Access Failed: "+str(e))
        if number_retry > 0:
            number_retry -= 1
            sleep(10)
            main(appleid,passwd,number_retry,error_record)
        else:
            if "failure_appleid" in error_record:
                with open(error_record, 'a') as f:
                    f.write(appleid + "----" + passwd)
            else:
                with open(error_record, 'a') as f:
                    f.write(appleid + "----" + passwd.strip() + " error_msg: " + str(e) + '\n')
    except Exception as e:
        getCaptcha.log_define("script executed has error: " + str(e))
        error_message = str(e)
        if error_message == "accountName.alreadyUsed" or error_message == "-31607": #appleid已存在,或者邮箱使用次数已达上限
            with open("../logs/failure_record_%s.txt" % time.strftime('%Y-%m-%d', time.localtime(time.time())), 'a') as f:
                f.write(appleid + "----" + passwd.strip() + " error_msg: " + error_message + '\n')
        elif number_retry > 0:
            if error_message == "captchaAnswer.Invalid": #图片验证码错误
                number_retry -= 1
                sleep(10)
                main(appleid, passwd, number_retry, error_record)
            elif error_message == "-21418":  #邮箱验证码错误
                number_retry -= 1
                sleep(10)
                main(appleid, passwd, number_retry,error_record)
            elif error_message == "-34607001": #未知错误
                number_retry -= 1
                sleep(10)
                main(appleid, passwd, number_retry,error_record)
            elif error_message == "-790000": #图片解码失败
                number_retry -= 1
                sleep(10)
                main(appleid, passwd, number_retry,error_record)
        else:
            if "failure_appleid" in error_record:
                with open(error_record,'a') as f:
                    f.write(appleid+"----"+passwd)
            else:
                with open(error_record,'a') as f:
                    f.write(appleid+"----"+passwd.strip()+" error_msg: "+error_message+'\n')

if __name__ == '__main__':
    with open('../logs/maillist','r') as f:
        for i in f.readlines():
            appleid,passwd = i.split('----')
            error_record = "../logs/failure_appleid_%s.txt" % time.strftime('%Y-%m-%d',time.localtime(time.time()))
            main(appleid,passwd,error_record=error_record)
            sleep(10)

    '''申请完成后对之前申请失败的进行重试'''
    if os.path.exists("../logs/failure_appleid_%s.txt" % time.strftime('%Y-%m-%d',time.localtime(time.time()))):
        with open("../logs/failure_appleid_%s.txt" % time.strftime('%Y-%m-%d',time.localtime(time.time()))) as f:
            for i in f.readlines():
                appleid,passwd = i.split('----')
                error_record = "../logs/failure_record_%s.txt" % time.strftime('%Y-%m-%d', time.localtime(time.time()))
                main(appleid,passwd,number_retry=0,error_record=error_record)
    db_main()