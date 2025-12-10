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


# Import RAG and conversation memory
from utils.agent.RAG import RAG
from LLM import rag_answer_with_memory
from utils.agent.conversation_memory import ConversationMemory
from summarizer import summarize_user_knowledge

# helper function from utils
import utils.env
from utils.args import parse_arguments
from utils.email import send_email_with_attachment

app = Flask(__name__)

configuration = Configuration(access_token=utils.env.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(utils.env.LINE_CHANNEL_SECRET)

# Initialize RAG and conversation memory globally
print("Initializing RAG system...")
rag_system = RAG(client=None, folder="documents", batch_size=5)
print("RAG system initialized.")

print("Initializing conversation memory...")
conversation_memory = ConversationMemory(storage_dir="conversation_history", max_history=10)
print("Conversation memory initialized.")


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
    # Get user_id from LINE event (or use "user" as default for now)
    user_id = getattr(event.source, 'user_id', 'user')
    user_message = event.message.text.strip()  # get message from user
    
    print(f"Message from user {user_id}: {user_message}")
    
    # Check for special commands
    if user_message.lower() in ['!clear', '!reset', '!clear history', '!reset history']:
        if conversation_memory.clear_history(user_id):
            reply = "Your conversation history has been cleared! 🗑️"
        else:
            reply = "You don't have any conversation history yet."
    
    elif user_message.lower() in ['!history', '!show history', '!my history']:
        count = conversation_memory.get_conversation_count(user_id)
        if count > 0:
            reply = f"You have {count} conversation(s) in your history. 📚"
        else:
            reply = "You don't have any conversation history yet. Start chatting!"

    elif user_message.lower() in ['!send'] and args.email != None:

        text, path = summarize_user_knowledge(user_name=user_id, model=args.model)

        success = send_email_with_attachment(
            to_email=args.email,
            subject="ACP Helper 總結",
            body="感謝使用本服務,請查收附件。",
            file_path=path
        )

        if success:
            reply = '已寄出信件'
        else:
            reply = '信件寄送失敗'
    
    else:
        # Get answer using RAG with conversation memory
        try:
            reply = rag_answer_with_memory(
                question=user_message,
                rag=rag_system,
                user_id=user_id,
                memory=conversation_memory,
                model=args.model
            )
        except Exception as e:
            print(f"Error processing message: {e}")
            reply = "Sorry, I encountered an error processing your request. Please try again. 🤔"
    
    # Send reply
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
    args = parse_arguments()
    app.run(host=args.host, port=args.port)
