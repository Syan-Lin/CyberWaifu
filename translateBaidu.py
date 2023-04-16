import http.client
import hashlib
import urllib
import random
import json

def translate_baidu(q,appid,secretKey):
    httpClient = None
    myurl = '/api/trans/vip/translate'
    fromLang = 'auto'   #原文语种
    toLang = 'jp'   #译文语种
    salt = random.randint(32768, 65536)

    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
    salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)

        ans = result.get("trans_result")[0].get("dst")

        return ans

        print (ans)

    except Exception as e:
        print (e)
    finally:
        if httpClient:
            httpClient.close()

if __name__ == '__main__':
    q = '可以参考百度翻译提供的demo'
    translate_baidu(q)