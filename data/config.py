import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

admins = int(os.getenv("ADMIN_ID"))

ip = os.getenv("ip")
PORT = int(os.getenv("PORT"))
PGDATABASE = str(os.getenv("DB_NAME"))
PGUSER = str(os.getenv("PG_USER"))
PGPASSWORD = str(os.getenv("PG_PASSWORD"))

REDIS_HOST = str(os.getenv("REDIS_HOST"))
REDIS_PASS = str(os.getenv("REDIS_PASS"))

EMAIL_ADDRESS = str(os.getenv("EMAIL_USER"))
EMAIL_PASSWORD = str(os.getenv("EMAIL_PASS"))

