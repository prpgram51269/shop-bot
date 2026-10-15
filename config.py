from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
PROXY = os.getenv('PROXY')
DATABASE_URL = os.getenv('DATABASE_URL')