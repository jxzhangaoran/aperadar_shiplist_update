import hashlib
import os
import random
import requests
import yaml

from utils import parent_directory

class TranslateUtil:

    def __init__(self):
        with open(os.path.join(parent_directory, "config.yaml"), 'r') as file:
            config = yaml.safe_load(file)
            self.appid = config['translate']['baidu']['appid']
            self.secret_key = config['translate']['baidu']['secret_key']
            self.url = config['translate']['baidu']['host']

    def translate(self, query: str, from_lang: str, to_lang: str) -> str:
        salt = str(random.randint(32768, 65536))
        sign_source = self.appid + query + salt + self.secret_key
        sign = self._make_md5(sign_source)
        params = {
            'q': query,
            'from': from_lang,
            'to': to_lang,
            'appid': self.appid,
            'salt': salt,
            'sign': sign,
            'needIntervene': 1
        }
        response = requests.post(self.url, params=params,
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'})
        result = response.json()
        if 'trans_result' in result:
            return result['trans_result'][0]['dst']
        else:
            raise Exception(f"Error {result.get('error_code')}: {result.get('error_msg')}")

    def _make_md5(self, s, encoding='utf-8'):
        return hashlib.md5(s.encode(encoding)).hexdigest()



if __name__ == '__main__':
    translator = TranslateUtil()
    translated_text = translator.translate("Azuma B", "en", "zh")
    print(translated_text)