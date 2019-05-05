#_*_coding:utf-8_*_

from db_api import Db
import time

def accountInfo(apple_id,email_passwd):
    '''
    生成账户信息字典
    :param apple_id:
    :param email_passwd:
    :return:
    '''
    gmt_create = time.strftime('%Y-%m-%d %H-%M-%S',time.localtime(time.time()))
    info_dict = {
        'question1':'What was the name of your first pet?',
        'question2':'What is your dream job?',
        'question3':'What was the first name of your first boss?',
        'answer1':'DISC',
        'answer2':'CSID',
        'answer3':'SSID',
        'apple_id':apple_id,
        'gmt_create': gmt_create,
        'email_passwd': email_passwd,
        'passwd':'123TabcdE',
        'gmt_modified': gmt_create,
    }
    return info_dict

def main():
    '''
    连接数据库，插入数据
    :return:
    '''
    user = 'appstore_account'
    passwd = 'testpasswd'
    host = '10.0.0.2'
    port = 3306
    try:
        db_obj = Db(user=user, passwd=passwd, addr=host, port=port)
        datetime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        #with open('../logs/appleid_%s.txt' % datetime,'r') as f:
        with open('../logs/result.txt', 'r') as f:
            for i in f.readlines():
                if i:
                    apple_id, email_passwd = i.split('----')
                    accountinfo = accountInfo(apple_id,email_passwd.strip())
                    db_obj.dbInsert(
                        appleid=accountinfo['apple_id'],
                        passwd=accountinfo['passwd'],
                        email_passwd=accountinfo['email_passwd'],
                        question1=accountinfo['question1'],
                        answer1=accountinfo['answer1'],
                        question2=accountinfo['question2'],
                        answer2=accountinfo['answer2'],
                        question3=accountinfo['question3'],
                        answer3=accountinfo['answer3'],
                        gmt_create=accountinfo['gmt_create'],
                        gmt_modified=accountinfo['gmt_modified']
                    )
    except Exception,e:
        error_message="dbInsert method call failed: "+str(e)
        db_obj.log_define(error_message)
    finally:
        db_obj.close()

if __name__ == '__main__':
    main()