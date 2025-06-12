from flask import Blueprint, request, jsonify
import os
import requests

line_bp = Blueprint(\'line_bp\', __name__)

# LINE Messaging API設定 (環境変数から取得することを推奨)
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get(\'LINE_CHANNEL_ACCESS_TOKEN\', \'YOUR_CHANNEL_ACCESS_TOKEN\')
LINE_CHANNEL_SECRET = os.environ.get(\'LINE_CHANNEL_SECRET\', \'YOUR_CHANNEL_SECRET\')

# Webhookからのメッセージ受信
@line_bp.route(\'/webhook\', methods=[\'POST\'])
def webhook():
    signature = request.headers[\'X-Line-Signature\']
    body = request.get_data(as_text=True)

    # LINEからのリクエスト検証 (ここでは簡易化。実際はline-bot-sdkなどを使用)
    # if not validate_signature(body, signature, LINE_CHANNEL_SECRET):
    #     return jsonify({\'error\': \'Invalid signature\'}), 400

    events = request.get_json()[\'events\']
    for event in events:
        if event[\'type\'] == \'message\' and event[\'message\'][\'type\'] == \'text\':
            handle_message(event)

    return jsonify({\'status\': \'ok\'}), 200

def handle_message(event):
    user_id = event[\'source\'][\'userId\']
    message_text = event[\'message\'][\'text\']

    # ユーザーが送ってきたメッセージが特典コードかどうかを検証
    # ここでは簡易的に、特定のプレフィックスで始まるかをチェック
    if message_text.startswith(\'JP-\' ) or \
       message_text.startswith(\'BW-\' ) or \
       message_text.startswith(\'SW-\' ):
        # バックエンドのverify_code APIを呼び出す
        api_url = request.url_root + \'api/verify_code\'
        response = requests.post(api_url, json={\'code\': message_text})
        
        if response.status_code == 200:
            data = response.json()
            if data[\'valid\']:
                reply_text = f\'おめでとうございます！{data[\'win_type\']}の特典コードが確認できました。\n景品をお渡しします！\'
            else:
                reply_text = \'申し訳ありません、その特典コードは無効です。\'
        else:
            reply_text = \'コードの検証中にエラーが発生しました。\'
    else:
        # それ以外のメッセージにはゲームリンクを返信
        # ここでは固定のURLを返していますが、実際はユーザーIDを付与したURLを生成すべきです
        game_url = request.url_root.replace(\'api/\', \'\') + f\'?user_id={user_id}\'
        reply_text = f\'スロットゲームで運試し！\n{game_url}\n\n特典コードを送信すると景品がもらえます！\'

    reply_token = event[\'replyToken\']
    send_reply_message(reply_token, reply_text)

def send_reply_message(reply_token, text):
    headers = {
        \'Content-Type\': \'application/json\',
        \'Authorization\': f\'Bearer {LINE_CHANNEL_ACCESS_TOKEN}\'
    }
    data = {
        \'replyToken\': reply_token,
        \'messages\': [
            {
                \'type\': \'text\',
                \'text\': text
            }
        ]
    }
    requests.post(\'https://api.line.me/v2/bot/message/reply\', headers=headers, json=data )

# 簡易的な署名検証関数 (実際はLINE Bot SDKを使用することを推奨)
def validate_signature(body, signature, channel_secret):
    import hmac
    import hashlib
    import base64

    hash = hmac.new(channel_secret.encode(\'utf-8\'), body.encode(\'utf-8\'), hashlib.sha256).digest()
    return hmac.compare_digest(base64.b64encode(hash), signature.encode(\'utf-8\'))
