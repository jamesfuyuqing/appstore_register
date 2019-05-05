#_*_coding:utf-8_*_
__author__ = 'FYQ'
import json
import requests
import urllib
import sys
reload(sys)
from EmailCaptcha import emailCaptcha
import datetime
from time import sleep
import ssl

sys.setdefaultencoding('UTF-8')

ssl._create_default_https_context = ssl._create_unverified_context

class GetCaptcha(object):
    def __init__(self,appleid,password,country,firstName,lastName,birthday,question1,question2,question3,
                 answer1,answer2,answer3):
        '''
        初始化首页数据、注册页数据
            获取 appleid、密码、地区、账户名、出生日期、问题1、答案1、问题2、答案2、问题3、答案3
        :param appleid:
        :param password:
        :param country:
        '''
        self.s = requests.session()
        self.scnt = None
        self.homepage = self.getHomePage()
        self.account_list = self.getAccountPage()
        self.appleid = appleid
        self.password = password
        self.country = country
        self.firstName = firstName
        self.lastName = lastName
        self.birthday = birthday
        self.question1 = question1
        self.question2 = question2
        self.question3 = question3
        self.answer1 = answer1
        self.answer2 = answer2
        self.answer3 = answer3
        self.id = None
        self.token = None
        self.image_content = None
        self.verificationId = None
        self.emailcaptcha = None

    def log_define(self,logMessage):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('../logs/apply.log','a') as f:
            f.write(timestamp + ' ' + str(logMessage)+'\n')

    def header(self):
        header = {
            'Content-Type':'application/json',
            'Accept':'application/json, text/javascript, */*; q=0.01',
            'Host':'appleid.apple.com',
            'Origin':'https://appleid.apple.com',
            'Referer':'https://appleid.apple.com/account',
            'X-Requested-With':'XMLHttpRequest',
            "X-Apple-I-FD-Client-Info": json.dumps({
                "U": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36",
                "L": "en-US", "Z": "GMT+08:00", "V": "1.1",
                "F": ".Wa44j1e3NlY5BSo9z4ofjb75PaK4Vpjt.gEngMQEjZr_WhXTA2s.XTVV26y8GGEDd5ihORoVyFGh8cmvSuCKzIlnY6xljQlpRDCAQnKqumqPJypZHgfLMC7AeLd7FmrpwoNN5uQ4s5uQ.gEx4xUC541jlS7spjt.gEngMQEjZr_WhXTA2s.XTVV26y8GGEDd5ihORoVyFGh8cmvSuCKzIlnY6xljQlpRDCAQnKqumqPJypZHgfLMC7Afyz.sUAuyPBDK43xhDnmccbguaDeyjaY2ftckuyPBDjaY1HGOg3ZLQ0FxdK8u_Je37AxQeLaD.SAxN4t1VKWZWuxbuJjkWiK7.M_0p5DsHrk0ugN.xL438IV64KxN4t23f282p9Kyfez1euVr9Z.AmeurNW5BNlYic.lY5BqNAE.lTjV.B52"}),
            'scnt':self.scnt,
            'X-Apple-Api-Key':self.account_list[0],
            'X-Apple-ID-Session-Id':self.account_list[1],
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
        }
        return header

    def getHomePage(self):
        '''
        获取首页
        :return:
        '''
        url = r'https://appleid.apple.com/account'
        self.s.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'}
        result = self.s.get(url)
        self.scnt = result.headers['Scnt']
        self.log_define("getHomePage Method header: "+str(result.request.headers))
        self.log_define("getHomePage Method status: "+str(result))

    def getAccountPage(self):
        '''
        获取注册页，返回注册页上随机生成的scnt、sessionId、apiKey的list
        :return: [scnt、sessionId、apiKey]
        '''
        url = r'https://appleid.apple.com/account#!&page=create'
        header = {
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36',
            'Referer':'https://appleid.apple.com/account'
        }
        result = self.s.get(url,headers=header)
        self._cookies = result.cookies

        for i in result.text.split('\n'):
            if r'apiKey' in i:
                apiKey = i.strip().split()[1][1:-2]

        for i in result.text.split('\n'):
            if r'sessionId' in i:
                sessionId = i.strip().split()[1][1:-2]

        self.log_define("getAccountPage status: "+str(result))
        # self.log_define("getScnt: "+str(scnt))
        self.log_define("getapiKey: " + str(apiKey))
        self.log_define("getsessionId: "+str(sessionId))
        return [apiKey,sessionId]

    def captcha(self):
        '''
        获取图片验证码信息
        第一个post请求，建立在前两个get请求的基础上
        :return: 返回验证码的token、id、图片base64编码，并将其声明为类全局属性，如下
                  {
                    "payload" : {
                        "contentType" : "image/jpeg",
                        "content": "此处是图片的数据"
                    },
                    "type" : "IMAGE",
                    "id" : -215367428,
                    "token" : "此处为token"
                }
        '''
        url = r'https://appleid.apple.com/captcha'
        self.s.headers = self.header()
        pyload = {'type':'IMAGE'}
        result = self.s.post(url,json=pyload)
        if result.status_code > 209:
            self.log_define("captcha post error status_code: "+str(result.status_code))
            self.log_define("captcha post error message: "+str(result.text))
        else:
            resultLoad = json.loads(result.text)
            self.id = resultLoad['id']
            self.token = resultLoad['token']
            self.image_content = resultLoad['payload']['content']
            self.scnt = result.headers['Scnt']
            self.log_define("captcha method request status_code: "+str(result.status_code))
            #self.log_define("captcha method result: "+str(result.text))
            return resultLoad

    '''
    经观察，注册页面在填写信息的过程中有几个请求会实时发送，分别是 appleid、password、country，下面代码实现这个步骤
    '''
    def postAppleid(self):
        '''
        post appleid
        :return:
        '''
        url = r'https://appleid.apple.com/account/validation/appleid'
        payload = self.appleid
        self.s.headers = self.header()
        result = self.s.post(url,json=payload)
        if result.status_code > 209:
            self.log_define("Post Appleid status_code: "+str(result.status_code))
            self.log_define("Post Appleid error: "+str(result.text))
        else:
            self.scnt = result.headers['Scnt']
            self.log_define("Post Appleid success,status_code: "+str(result.status_code))
        return

    def postPassword(self):
        '''
        post password
        :return:
        '''
        url = r'https://appleid.apple.com/account/validate/password'
        payload = {"password": self.password}
        self.s.headers = self.header()
        result = self.s.post(url, json=payload)
        if result.status_code > 209:
            self.log_define("Post password status_code: "+ str(result.status_code))
            self.log_define("Post password error: "+ str(result.text))
        else:
            self.scnt = result.headers['Scnt']
            self.log_define("Post password success,status_code: "+str(result.status_code))
        return

    def getCountry(self):
        '''
        get country
        :return:
        '''
        url = r'https://appleid.apple.com/account?countryCode=%s' % self.country
        self.s.headers = self.header()
        result = self.s.get(url)
        if result.status_code > 209:
            self.log_define("GET country status_code: "+ str(result.status_code))
            self.log_define("GET country error: "+ str(result.text))
        else:
            self.scnt = result.headers['Scnt']
        return

    def postRegister(self):
        '''
        正式将注册页面表单的所有信息post，no response
        post register message2
        :return:
        '''
        url = r'https://appleid.apple.com/account/validate'
        payload = {"account": {"name": self.appleid,
                         "password": self.password,
                         "person": {
                             "name": {
                                 "firstName": self.firstName,
                                 "lastName": self.lastName
                             },
                             "birthday": self.birthday,
                             "primaryAddress": {
                                 "country": self.country
                             }},
                         "preferences": {
                             "preferredLanguage": "en_US",
                             "marketingPreferences": {
                                 "appleNews": False,
                                 "appleUpdates": False,
                                 "iTunesUpdates": False}},
                         "security": {
                             "questions": [
                                 {'id': '130', 'question': self.question1, 'answer': self.answer1},
                                 {'id': '136', 'question': self.question2, 'answer': self.answer2},
                                 {'id': '143', 'question': self.question3, 'answer': self.answer3}
                             ]
                         }},
             "captcha": {
                 "id": self.id,
                 "token": self.token,
                 "answer": self.imageResolution() #此处为图片验证码，等待后续方法实现
            }}
        self.s.headers = self.header()
        result = self.s.post(url, json=payload)
        if result.status_code > 209:
            self.log_define("Post register status_code: "+ str(result.status_code))
            self.log_define("Post register form error: "+ str(result.text))
            resultLoad = json.loads(result.text)['validationErrors'][0]['code']
            raise NameError(resultLoad)
        else:
            self.log_define("Post register message(image captcha) success,status_code: "+str(result.status_code))
            self.scnt = result.headers['Scnt']
        return

    def requestEmailCaptcha(self):
        '''
        此方法用于请求邮件验证，成功后苹果会向账号发送一封邮件
            result response：{
                                "verificationId" : "000873-00-df3273d85d318daf75745192b8d613d98fb6eca34d2a7ff2d5e0518f085b263eLTOW",
                                "canGenerateNew" : true, #true表示发送成功
                                "length" : 6
                            }
        :return:
        '''
        url = r'https://appleid.apple.com/account/verification'
        payload = {"account":
                    {"name": self.appleid,
                        "person":
                            {"name": {"firstName": self.firstName, "lastName": self.lastName}}}}
        self.s.headers = self.header()
        result = self.s.post(url, json=payload)
        resultLoad = json.loads(result.text)
        self.verificationId = resultLoad['verificationId']
        if result.status_code > 209:
            resultLoad = json.loads(result.text)['service_errors'][0]['code']
            self.log_define("post request email captcha error: "+ str(result.text))
            self.log_define("post request email captcha errorcode: "+ str(result.status_code))
            raise NameError(resultLoad)
        else:
            resultLoad = json.loads(result.text)
            self.verificationId = resultLoad['verificationId']
            self.log_define("requestEmailCaptcha resp result is: " + str(result.text))
            self.scnt = result.headers['Scnt']
        return

    def putEmailCaptchaResult(self,passwd):
        '''
        此方法以put形式将邮件验证码传回，成功则注册成功,失败返回错误json信息、状态码400
        :return:
        '''
        self.emailcaptcha = emailCaptcha(self.appleid,passwd)
        url = r'https://appleid.apple.com/account/verification'
        payload = {"name": self.appleid,
             "verificationInfo": {
                 "id": self.verificationId,
                 "answer": self.emailcaptcha #此地是邮件验证码
             }}
        self.s.headers = self.header()
        result = self.s.put(url, json=payload)
        self.log_define("mail resolution result vaule: " + self.emailcaptcha)
        if result.status_code > 209:
            self.log_define("put email captcha result error: "+ str(result.text))
            self.log_define("put email captcha result errorcode: "+ str(result.status_code))
            resultLoad = json.loads(result.text)['service_errors'][0]['code']
            raise NameError(resultLoad)
        else:
            self.log_define("put email captcha success,status_code: "+str(result.status_code))
            self.log_define("put email captcha message: "+str(result.text))
            self.scnt = result.headers['Scnt']
        return result.text

    def postRegisterForm(self):
        url = r'https://appleid.apple.com/account'
        payload = {
            "account":{
                "name":self.appleid,
                "password":self.password,
                "person":{
                    "name":{
                        "firstName":self.firstName,
                        "lastName":self.lastName
                    },
                    "birthday":self.birthday,
                    "primaryAddress":{
                        "country":self.country
                    }
                },
                "verificationInfo":{
                    "id":self.verificationId,
                    "answer":self.emailcaptcha
                },
                "security":{
                    "questions":[
                        {"id":"131","question":self.question1,"answer":self.answer1},
                        {"id":"136","question":self.question2,"answer":self.answer2},
                        {"id":"143","question":self.question3,"answer":self.answer3}
                    ]},
                "preferences":{
                    "preferredLanguage":"en_US",
                    "marketingPreferences":{
                        "appleNews":False,
                        "appleUpdates":False,
                        "iTunesUpdates":False
                    }}}}
        self.s.headers = self.header()
        result = self.s.post(url,json=payload)
        if result.status_code > 209:
            self.log_define("post register form error code: "+str(result.status_code))
            self.log_define("post register form error message: "+str(result.text))
            resultLoad = json.loads(result.text)['service_errors'][0]['code']
            raise NameError(resultLoad)
        else:
            self.log_define("post register(mail captcha) success,status_code: "+str(result.status_code))
            self.log_define("post register(mail captcha) success,resp: "+str(result.text))
            self.scnt = result.headers['Scnt']
        return

    def imageResolution(self):
        '''
        此方法调用第三方接口完成图片验证码破解
        :return:
        '''
        url = r'http://ali-checkcode.showapi.com/checkcode'
        header = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Authorization': 'APPCODE 6d051550d6c74be1a1644c442e6d7'
        }
        data = urllib.urlencode({
            'convert_to_jpg': '0',
            'img_base64': self.image_content,
            'typeId': '3000'
        })
        try:
            result = requests.post(url=url,data=data,headers=header)
            self.log_define("The image captcha code: "+str(json.loads(result.text)['showapi_res_body']['Result']))
            return json.loads(result.text)['showapi_res_body']['Result']
        except Exception,e:
            raise NameError("-790000")

def main(appleid,password):
    getCaptcha = GetCaptcha(appleid, '123TabcdE', 'CHN', 'mao', 'jian', '1993-12-21',
                            "What was the name of your first pet?",
                            "What is your dream job?",
                            "What was the first name of your first boss?", 'DISC', 'CSID', 'SSID')
    try:
        getCaptcha.captcha()
        getCaptcha.postAppleid()
        getCaptcha.postPassword()
        getCaptcha.getCountry()
        getCaptcha.postPassword()
        getCaptcha.postRegister()
        getCaptcha.requestEmailCaptcha()
        sleep(4)
        getCaptcha.putEmailCaptchaResult(password)
        getCaptcha.postRegisterForm()
    except Exception as e:
        getCaptcha.log_define("script executed has error: "+str(e))

if __name__ == '__main__':
    main("fengx6@163.com","q16573")