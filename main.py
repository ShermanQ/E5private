# -*- coding: UTF-8 -*-
import json
import os
import sys
import time

import requests as req

log_path = sys.path[0] + r'/info.log'


def get_token(refresh_token):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'
               }
    data = {'grant_type': 'refresh_token',
            'refresh_token': os.environ.get("refresh_token"),
            'client_id': os.environ.get('id'),
            'client_secret': os.environ.get('secret'),
            'redirect_uri': 'http://localhost:53682/'
            }
    html = req.post('https://login.microsoftonline.com/common/oauth2/v2.0/token', data=data, headers=headers)
    jsontxt = json.loads(html.text)
    refresh_token = jsontxt['refresh_token']
    access_token = jsontxt['access_token']
    expiry_time = jsontxt['expiry']

    # Check the response status code to ensure the secret was updated successfully
    response = updateToken(refresh_token)
    while response.status_code != 204:
        response = updateToken(refresh_token)

    print('Secret updated successfully!')

    return access_token, expiry_time


# Update the secret using the GitHub REST API
def updateToken(refresh_token):
    owner = os.environ['GITHUB_REPOSITORY'].split('/')[0]

    repo = os.environ['GITHUB_REPOSITORY'].split('/')[1]

    PAT = os.environ.get('token')

    # 要更新的 secret 的名称
    secret_name = 'REFRESH_TOKEN'

    # 要更新的 secret 的值
    new_secret_value = refresh_token

    # 获取仓库 ID
    repo_api_url = f'https://api.github.com/repos/{owner}/{repo}'
    response = req.get(url=repo_api_url, headers={'Authorization': f'token {PAT}'})
    repo_id = response.json()['id']

    # 更新 secret
    secrets_api_url = f'https://api.github.com/repos/{owner}/{repo}/actions/secrets/{secret_name}'
    response = req.put(url=secrets_api_url, headers={'Authorization': f'token {PAT}'},
                            json={'encrypted_value': new_secret_value, 'key_id': f'{repo_id}'})
    return response

def main():
    refresh_token = os.environ.get("refresh_token")

    with open(log_path, "r+") as fv:
        fv.write(f"Now time: {time.ctime()}")

    access_token, expiry_time = get_token(refresh_token)

    with open(log_path, "a+") as fv:
        fv.write(f"Access Token Expire Time: {expiry_time}")

    headers = {
        'Authorization': access_token,
        'Content-Type': 'application/json'
    }

    urls = [
        'https://graph.microsoft.com/v1.0/me/drive/root/children',
        'https://graph.microsoft.com/v1.0/me/drive/recent',
        'https://graph.microsoft.com/v1.0/drive/sharedWithMe',
        'https://graph.microsoft.com/v1.0/users',
        'https://graph.microsoft.com/v1.0/me/messages',
        'https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messageRules',
        'https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messageRules',
        'https://graph.microsoft.com/v1.0/me/drive/root/children',
        'https://api.powerbi.com/v1.0/myorg/apps',
        'https://graph.microsoft.com/v1.0/me/mailFolders',
        'https://graph.microsoft.com/v1.0/me/outlook/masterCategories'
    ]
    for url in urls:
        try:
            acture_nums = 0
            for num in range(10, 98):
                if req.get(url, headers=headers).status_code == 200:
                    acture_nums += 1
            with open(log_path, "a+") as fv:
                fv.write(f"The API of {url} Success Called {acture_nums}")
        except req.exceptions.RequestException as e:
            print(f"Failed Call API Of : {url}")
            print(e)


if __name__ == '__main__':
    main()
