from framework.util.settings import get_setting

HOST = get_setting("HOST", "localhost")
PORT = get_setting("PORT", 8000, convert=int)
DATABASE_URL = get_setting("DATABASE_URL")
