import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters, MessageHandler
from pymongo import MongoClient

# Initialize MongoDB client
mongo_client = MongoClient(os.environ['mongodb+srv://soumyadeepdas765:<password>@cluster0.qjom2aq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'])
db = mongo_client.get_default_database()
videos_collection = db['videos']

# Function to shorten URL using tnshort API
def shorten_url(url):
    api_key = os.environ.get('2982bf9774b94d3d9f20f822a00204d876ce3a57')
    response = requests.post(f'https://tnshort.net/api?api={api_key}&url={url}')
    if response.status_code == 200:
        return response.json().get('shorturl')
    else:
        return None

# Bot command handlers
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to the bot!')

def new_video(update: Update, context: CallbackContext) -> None:
    video_message = update.message.video
    video_url = video_message.file_id
    video_title = update.message.caption
    
    # Shorten the video URL
    short_url = shorten_url(video_url)
    
    # Generate direct download link
    download_link = short_url
    
    # Create inline button
    button = InlineKeyboardButton(text="Fast Download", url=download_link)
    reply_markup = InlineKeyboardMarkup([[button]])
    
    # Save video details to MongoDB with short URL
    if short_url:
        videos_collection.insert_one({'title': video_title, 'url': short_url})
    else:
        videos_collection.insert_one({'title': video_title, 'url': video_url})
    
    # Send message with inline button
    update.message.reply_text('New video uploaded!', reply_markup=reply_markup)

def main():
    updater = Updater(token=os.environ['6736279952:AAF_FBnzXElejWmqh5-pdUYnITKPb1L_Ots'])
    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.video & Filters.chat_type.private, new_video))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
