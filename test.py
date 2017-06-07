# -*- coding: utf-8 -*-
import urllib.request
import json
import pandas as pd
import hashlib
url = "https://www.joinquant.com/algorithm/live/shareTransaction?isAjax=1&backtestId=72c4b71e92a06f9e77845d7a83cfa057&date=2017-05-11&isMobile=1&isForward=1&ajax=1"
data = urllib.request.urlopen(url).read()
data = data.decode('UTF-8')
decoded = json.loads(data)
decoded = decoded['data']['html']
index = decoded.rfind("</tbody>")
x = '<table>%s</table>' % decoded[:index]
df = pd.read_html(x)
print(df)


m = hashlib.md5(x.encode("utf-8"))
print(m.hexdigest())