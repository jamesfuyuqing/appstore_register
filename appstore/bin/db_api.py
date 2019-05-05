#_*_coding:utf-8_*_

import MySQLdb as mysql
import time

class Db(object):
    '''
    每个方法内部并没有关闭数据库连接，需调用方调用close()方法
    '''
    def __init__(self,user,passwd,addr,port):
        '''
        初始化获取数据库参数，创建数据库对象、游标
        :param user:
        :param passwd:
        :param addr:
        :param port:
        '''
        self._user = user
        self._passwd = passwd
        self._addr = addr
        self._port = port
        try:
            self.conn = mysql.Connect(user=self._user,passwd=self._passwd,host=self._addr,port=self._port)
            self.conn.autocommit(True)
            self.cur = self.conn.cursor()
        except mysql.Error as e:
            error_message = "mysql connect session create failed: "+str(e)
            self.log_define(error_message)

    def log_define(self,logMessage):
        timeStamp = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        with open('../logs/db.log','a') as f:
            f.write(timeStamp+' '+logMessage+'\n')

    def close(self):
        '''
        数据库连接关闭方法
        :return:
        '''
        return self.conn.close()

    def dbInsert(self,appleid,passwd,email_passwd,question1,answer1,question2,answer2,question3,answer3,gmt_create,gmt_modified,status=0):
        '''
        数据插入
        :param appleid:
        :param timestamp:
        :return:
        '''
        sql = "INSERT INTO yueyu.apple_id (appleid,apple_passwd,email_passwd,question1,answer1,question2,answer2,question3,answer3,status,gmt_create,gmt_modified)" \
              " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%r,%s,%s)"
        args = (appleid,passwd,email_passwd,question1,answer1,question2,answer2,question3,answer3,status,gmt_create,gmt_modified)
        try:
            self.cur.execute(sql,args)
        except mysql.Error as e:
            error_message = "data insert failed: "+str(e)
            self.log_define(error_message)

    def dbSelect(self,field,**kwargs):
        '''
        数据查询
        :param 字段名，条件
        :return:
        '''
        sql = 'SELECT %s From yueyu.apple_id WHERE %s = "%s"' % (field,kwargs.keys()[0],kwargs[kwargs.keys()[0]])
        try:
            result = self.cur.execute(sql)
            fechmany = self.cur.fetchmany(result)
            return fechmany
        except mysql.Error as e:
            error_messge = "data select failed: "+str(e)
            self.log_define(error_messge)

    def dbUpdate(self,sql):
        '''
        数据更新
        :param sql:
        :return:
        '''
        pass

    def dbDelete(self,sql):
        '''
        数据删除
        :param sql:
        :return:
        '''
        pass
