import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL", "")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))

GROUP_ID = int(os.getenv("GROUP_ID"))
POPUP_TOPIC_ID = int(os.getenv("POPUP_TOPIC_ID"))
ORDER_TOPIC_ID = int(os.getenv("ORDER_TOPIC_ID"))
FEEDBACK_TOPIC_ID = int(os.getenv("FEEDBACK_TOPIC_ID"))
SUPPORT_TOPIC_ID = int(os.getenv("SUPPORT_TOPIC_ID"))
USER_TOPIC_ID = int(os.getenv("USER_TOPIC_ID"))
