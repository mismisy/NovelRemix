import requests

# 此代码测试你的api是不是可以用，这个是测试第三方的

url = "写https开头的url"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer apikey前面的bearer别动"
}

payload = {
    "model": "gemini-2.5-pro-free",
    "messages": [
        {
            "role": "user",
            "content": "你好，请问你是谁？"
        }
    ]
}

response = requests.post(url, headers=headers, json=payload)


print(response.status_code)
print(response.json())
