### pfinal-AgentPlatform

--------------------------------

pfinal-AgentPlatform 自建的代理IP池平台

工作面板如图所示:
![](https://github.com/PFinal-tool/pfinal-AgentPlatform/blob/master/image/main.jpg)

提取接口:

```python
import requests

url = "http://127.0.0.1:8456/api"

payload={}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

```

返回结果:

```json
{
  "data": {
    "http": "http://5.78.41.44:8080"
  },
  "status": true
}

```
