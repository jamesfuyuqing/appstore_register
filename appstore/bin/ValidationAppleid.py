#_*_coding:utf-8_*_

import requests
from MyEmailCaptcha2 import getAppleUrl
from time import sleep

class ValidationAppleid(object):
    def __init__(self,user,email_passwd,account_passwd):
        '''
        初始化参数：appleid，邮件密码，appleid密码.
        :param user:
        :param email_passwd:
        :param account_passwd:
        '''
        self.user = user
        self.email_passwd = email_passwd
        self.account_passwd = account_passwd
        self.s = requests.Session()
        self.url = getAppleUrl(self.user,self.email_passwd)
        self.ctkn = None

    def redirctForEmail(self):
        '''
        redirect to apple validation page.
        from html page get ctkn value.
        :return:
        '''
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Host': 'id.apple.com',
            'Referer': 'http://mail.126.com/js6/read/readhtml.jsp?mid=239:1tbi7wzRR1Uw5JEpwAAAsM&font=15&color=138144',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }
        result = self.s.get(self.url,headers=headers)
        resultList = result.text.strip().split('\n')
        for i in enumerate(resultList):
            if 'ctkn' in i[1]:
                target_line = i[0] + 1
        ctkn = resultList[target_line].split('"')[1]
        self.ctkn = ctkn                             #此处的token是从页面抓取，后面的请求要用到
        return

    def validation(self):
        '''
        This method completes the account verification.
        :return:
        '''
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'id.apple.com',
            'Referer': self.url,
            'Origin': 'https://id.apple.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }
        data = {
            'fdcBrowserData': {
                'U': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
                'L': "zh-CN",
                'Z': 'GMT+08:00',
                'V': '1.1',
                'F': 'N0a44j1e3NlY5BSo9z4ofjb75PaK4Vpjt.gEngMQEjZr_WhXTA2s.XTVV26y8GGEDd5ihORoVyFGh8cmvSuCKzIlnY6xljQlpRDCAQnKqumqPJypZHgfLMC7AeLd7FmrpwoNN5uQ4s5uQ.gEx4xUC541jlS7spjt.gEngMQEjZr_WhXTA2s.XTVV26y8GGEDd5ihORoVyFGh8cmvSuCKzIlnY6xljQlpRDCAQnKqumqPJypZHgfLMC7Afyz.sUAuyPBDovE9XXTneNufuyPBDjaY2ftckuyPB884akHGOg42q1ccI01MfAUfSHolk2dUf.j7J1gBZEMgzH_y3Cmd.1wcDhveCQ6Twhw.Tf5.EKWG1JslrMukAm58L5H6eJfx8bsFrJ5tJV0TKMLv37lhQwMAj9htsfHOrf8M2Lz4mvmfTT9oaSzeCQxi3NlYiMeBNlYCa1nkBMfs.9X0'
            },
            'myAppleIDURL': 'https://appleid.apple.com/cgi-bin/WebObjects/MyAppleId.woa?localang=zh_CN',
            'imagePath': 'images/vetting/images/CN-ZH/myappleid_title.png',
            'vetting': 'true',
            'language': 'CN-ZH',
            'appleId': self.user,
            'accountPassword': self.account_passwd,
            'ctkn': self.ctkn
        }

        url = r'https://id.apple.com/IDMSEmailVetting/authenticate.html'
        result = self.s.post(url=url,params=data,headers=headers)
        return result.text

if __name__ == '__main__':
    try:
        validationAppleid = ValidationAppleid('dvmkf@126.com','m48577','123TabcdE')
        validationAppleid.redirctForEmail()
        sleep(3)
        print validationAppleid.validation()
    except Exception,e:
        print "Error Message: ",e