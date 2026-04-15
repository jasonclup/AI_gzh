# -*- coding: utf-8 -*-
import requests, json

r = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id':'cli_a9575e73e2381cd4','app_secret':'t05QZo7CHeWsJrVmA3QtEg460V850hws'})
token = r.json()['tenant_access_token']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json; charset=utf-8'}

chat_id = 'oc_cd6408709942d68abc3873cb7159e88c'
msg = {
    'receive_id': chat_id,
    'msg_type': 'text',
    'content': json.dumps({'text': '🚀 AI内容工厂系统上线成功！\n\n🤖 主控调度已连接\n💬 8名AI员工全部就位\n\n准备接收任务指令...'}, ensure_ascii=False)
}
r2 = requests.post('https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id', 
    headers=headers, json=msg)
print(json.dumps(r2.json(), indent=2))
