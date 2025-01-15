import logging
from collections import defaultdict
from typing import DefaultDict, Optional, Set
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ExtBot,
)
import asyncio
import os
import json
import dotenv
from telegram import Bot

# Initialize your bot with your token
dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
# Global Variables
space = "&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;"

def load_json_data(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

descText = f"""
🥰 Welcome to LoveBook Creator! 🥰
Let’s create a personalized book to express your love!
Ready to get started? Type "Let's begin" or choose below:
"""
helpContent = f"""
<b>🔍 Lookbook Bot help 🔍</b>\n
Some content comes here...
\n\n\n\n\n
"""
certification = f"\n\n<b>Made with ❤️ by The Lovebook Team</b>{space}"
homepageBtn = InlineKeyboardButton(
    text="🌎Website", url="https://lovebookonline.com/"
)
docsBtn = InlineKeyboardButton(text="📜   Help", callback_data="helpBtn")
mainKeyboardMarkup = InlineKeyboardMarkup([
    [homepageBtn, docsBtn]
])

startBtn = InlineKeyboardButton(text="Let's Begin", callback_data="startBtn")
uploadBtn = InlineKeyboardButton(text="Upload Photo & Describe", callback_data="uploadBtn")
selectFeatureBtn = InlineKeyboardButton(text="Let's Begin", callback_data="selectFeatureBtn")

roundBtn = InlineKeyboardButton(text="Round", callback_data="roundBtn")
ovalBtn = InlineKeyboardButton(text="Oval", callback_data="ovalBtn")
squareBtn = InlineKeyboardButton(text="Square", callback_data="squareBtn")

blondeBtn = InlineKeyboardButton(text="Blonde", callback_data="blondeBtn")
brownBtn = InlineKeyboardButton(text="Brown", callback_data="brownBtn")
blackBtn = InlineKeyboardButton(text="Black", callback_data="blackBtn")
redBtn = InlineKeyboardButton(text="Red", callback_data="redBtn")

lightBtn = InlineKeyboardButton(text="Light", callback_data="lightBtn")
mediumBtn = InlineKeyboardButton(text="Medium", callback_data="mediumBtn")
darkBtn = InlineKeyboardButton(text="Dark", callback_data="darkBtn")

yesBtn = InlineKeyboardButton(text="Yes", callback_data="yesBtn")
noBtn = InlineKeyboardButton(text="No", callback_data="noBtn")

nextBtn = InlineKeyboardButton(text="Next", callback_data="nextBtn")
editBtn = InlineKeyboardButton(text="Edit", callback_data="editBtn")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class ChatData:
    """Custom class for chat_data. Here we store data per message."""

    def __init__(self) -> None:
        self.data = {
            "state": "default",
            "ChatID":"",
            "tagLine": "",
        }
        self.clicks_per_message: DefaultDict[int, int] = defaultdict(int)

    def __setitem__(self, key, value):
        """Allow setting arbitrary attributes."""
        self.data[key] = value

    def __getitem__(self, key):
        """Allow getting arbitrary attributes."""
        return self.data.get(key)

class CustomContext(CallbackContext[ExtBot, dict, ChatData, dict]):
    """Custom class for context."""

    def __init__(
        self,
        application: Application,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ):
        super().__init__(application=application, chat_id=chat_id, user_id=user_id)
        self._message_id: Optional[int] = None

    @property
    def bot_user_ids(self) -> Set[int]:
        """Custom shortcut to access a value stored in the bot_data dict"""
        return self.bot_data.setdefault("user_ids", set())

    @property
    def message_clicks(self) -> Optional[int]:
        """Access the number of clicks for the message this context object was built for."""
        if self._message_id:
            return self.chat_data.clicks_per_message[self._message_id]
        return None

    @message_clicks.setter
    def message_clicks(self, value: int) -> None:
        """Allow to change the count"""
        if not self._message_id:
            raise RuntimeError(
                "There is no message associated with this context object."
            )
        self.chat_data.clicks_per_message[self._message_id] = value

    @classmethod
    def from_update(cls, update: object, application: "Application") -> "CustomContext":
        """Override from_update to set _message_id."""
        # Make sure to call super()
        context = super().from_update(update, application)

        if (
            context.chat_data
            and isinstance(update, Update)
            and update.effective_message
        ):
            # pylint: disable=protected-access
            context._message_id = update.effective_message.message_id

        # Remember to return the object
        return context

def initializeOrderDetail(context):
    context.chat_data["state"] = "default"
    context.chat_data["ChatId"] = ""
    context.chat_data["tagLine"] = ""

async def clickHandler(update: Update, context: CustomContext) -> None:
    """Handle the button click."""
    query = update.callback_query
    await query.answer()  # Acknowledge the button click

    # Extract the callback data from the clicked button
    callback_data = query.data
    replyKeyBoardMarkUp = InlineKeyboardMarkup([])
    responseText = ""
    if callback_data == "startBtn":
        context.chat_data["state"] = "startBtn"
        replyKeyBoardMarkUp = InlineKeyboardMarkup(
            [
                [uploadBtn, selectFeatureBtn]
            ]
        )
        context.chat_data["tagLine"] = f"🎨 Step 1: Customize Characters! 🎨"
        responseText = f"""
{context.chat_data["tagLine"]}

We’ll start by personalizing the main characters: You and your loved one. 
You’ll see live previews with each choice.
How would you like to start?
"""
    elif callback_data == "selectFeatureBtn" or callback_data == "uploadBtn":
        context.chat_data["state"] = callback_data
        replyKeyBoardMarkUp = InlineKeyboardMarkup(
            [
                [roundBtn, ovalBtn, squareBtn]
            ]
        )
        context.chat_data["tagLine"] = f"Step-by-Step Character Customization with Layered Previews"
        responseText = f"""
{context.chat_data["tagLine"]}
-------- ⬇️ --------
📸 Let’s build your character’s look! Each time you make a choice, you’ll see an updated preview below.

Start with Face Shape:
"""
    elif callback_data.startswith("roundBtn") or callback_data.startswith("ovalBtn") or callback_data.startswith("squareBtn") :
        context.chat_data["state"] = callback_data
        replyKeyBoardMarkUp = InlineKeyboardMarkup(
            [
                [blondeBtn, brownBtn, blackBtn, redBtn]
            ]
        )
        context.chat_data["tagLine"] = (f"Great! Now choose Hair Color:")
        responseText = f"""
{context.chat_data["tagLine"]}
-------- ⬇️ --------
"""
    elif callback_data.startswith("blondeBtn") or callback_data.startswith("brownBtn") or callback_data.startswith("blackBtn") or callback_data.startswith("redBtn")  :
        context.chat_data["state"] = callback_data
        replyKeyBoardMarkUp = InlineKeyboardMarkup(
            [
                [lightBtn, mediumBtn, darkBtn]
            ]
        )
        context.chat_data["tagLine"] = (f"Next, select Skin Tone:")
        responseText = f"""
{context.chat_data["tagLine"]}
-------- ⬇️ --------
"""
    elif callback_data.startswith("lightBtn") or callback_data.startswith("mediumBtn") or callback_data.startswith("darkBtn")  :
        replyKeyBoardMarkUp = InlineKeyboardMarkup(
            [
                [yesBtn, noBtn]
            ]
        )
        context.chat_data["tagLine"] = (f"Choose Beard (Optional):")
        responseText = f"""
{context.chat_data["tagLine"]}
-------- ⬇️ --------
"""
    elif callback_data.startswith("yesBtn") or callback_data.startswith("noBtn")  :
        context.chat_data["state"] = callback_data
        replyKeyBoardMarkUp = InlineKeyboardMarkup(
            [
                [nextBtn, editBtn]
            ]
        )
        context.chat_data["tagLine"] = (f"✨ Here’s how you look!")
        responseText = f"""
{context.chat_data["tagLine"]}
-------- ⬇️ --------
Type "Next" to customize your loved one’s character or click "Edit" to adjust any details.
"""
    elif callback_data.startswith("nextBtn") or callback_data.startswith("editBtn")  :
        context.chat_data["state"] = callback_data
        replyKeyBoardMarkUp = InlineKeyboardMarkup(
            [
                [roundBtn, ovalBtn, squareBtn]
            ]
        )
        context.chat_data["tagLine"] = (f"""3. Creating the Loved One’s Character with the Same Layered Process Bot responds:
🎨 Now let’s create your loved one’s character!""")
        responseText = f"""
{context.chat_data["tagLine"]}
-------- ⬇️ --------
Start with Face Shape:
"""
    await query.message.reply_html(responseText, reply_markup=replyKeyBoardMarkUp)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userName = update.message.chat.username
    userId = str(update.message.chat.id)
    storage_file_path = "userList.json"
    thread_ids = {}
    if os.path.exists(storage_file_path):
        with open(storage_file_path, "r") as file:
            thread_ids = json.load(file)
    else:
        with open(storage_file_path, "w") as file:
            json.dump(thread_ids, file)
    all_keys = list(thread_ids.keys())
    # Check if the specific user_id exists in the dictionary
    if userId in all_keys:
        pass
    else:
        thread_ids[userId] = userName
        # Save the updated dictionary to the storage file
        with open(storage_file_path, "w") as file:
            json.dump(thread_ids, file)
    initializeOrderDetail(context)
    context.chat_data["ChatID"] = userId
    inputData = update.message.text.removeprefix("/start").strip()
    response_text = f"{descText}{certification}"
    inlineKeyboardMarkup = InlineKeyboardMarkup(
        [
            [startBtn],
        ]
    )
    await update.message.reply_html(response_text, reply_markup=inlineKeyboardMarkup)
    await getUserInfo(update)
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response_text = f"{helpContent}{certification}"
    await update.message.reply_html(response_text, reply_markup=mainKeyboardMarkup)

async def getUserInfo(update: Update) -> None:
    try:
        chat_id= update.message.chat.id
        # chat_id = 1085353685
        # chat_id = 6233962537
        # Get chat information
        chat_info = await bot.get_chat(chat_id)
        
        # Accessing username
        username = chat_info.username
        first_name = chat_info.first_name
        last_name = chat_info.last_name
        
        print(f"Username: {username}, First Name: {first_name}, Last Name: {last_name}")
    except Exception as e:
        print(f"Failed to retrieve user info: {e}")

def main() -> None:
    """Run the bot."""
    context_types = ContextTypes(context=CustomContext, chat_data=ChatData)
    application = Application.builder().token(TOKEN).context_types(context_types).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CallbackQueryHandler(clickHandler))
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    
if __name__ == "__main__":
     main()

