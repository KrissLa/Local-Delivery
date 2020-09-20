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
REDIS_PASS = str(os.getenv("REDIS_PASS"))

aiogram_redis = {
    'host': ip,
}

redis = {
    'address': (ip, 6379),
    'encoding': 'utf8'
}
