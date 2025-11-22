#just an offical example code

from dotenv import load_dotenv
import os
load_dotenv()

from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent,
    FollowEvent,
    UnfollowEvent
)

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="Hello! Thanks for adding me! 🎉\nHow can I help you today?")]
            )
        )

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    user_id = event.source.user_id
    app.logger.info(f"User {user_id} unfollowed")



@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text.lower().strip() # get message from user
    print(f"msg from user: {user_message}")

    reply = "This is a message for checking the function is work successfully"

    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply)]
            )
        )

@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image(event):
    with ApiClient(configuration) as api_client:
        # Use MessagingApiBlob to download the image
        blob_api = MessagingApiBlob(api_client)
        message_content = blob_api.get_message_content(message_id=event.message.id)
        
        # Save the image
        SAVE_DIR = "."
        file_path = os.path.join(SAVE_DIR, f"{event.message.id}.jpg")
        with open(file_path, 'wb') as f:
            f.write(message_content)
        
        # Reply to user
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f"Got your image! \nSaved as {event.message.id}.jpg")]
            )
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=25565)
