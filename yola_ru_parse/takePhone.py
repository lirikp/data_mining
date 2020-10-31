

import base64
import  re
import requests

class takePhoneYoula():

    phone: str

    def __init__(self, responce):
        self.response = responce
        self.encode_trapped(self.trapped_from_regex())



    def trapped_from_regex(self):
        regex = re.compile(r'phone\%22\%2C\%22([0-9|a-zA-Z]+)\%3D\%3D\%22\%2C\%22time')
        trapped = re.findall(regex, self.response.text)
        return trapped[0] + '=='

    def encode_trapped(self, trapped):
        str_base64 = base64.b64decode(trapped)
        self.phone = base64.b64decode(str_base64)





if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0',
    }
    resp = requests.get('https://auto.youla.ru/advert/used/land_rover/discovery/avs-genzes--6aa0b8350837076f/', headers=headers)

    t = takePhoneYoula(resp)
    print(t.phone)