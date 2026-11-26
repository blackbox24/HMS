from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# Django core
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")

# Database — SQLite by default; set DB_ENGINE=django.db.backends.postgresql
# plus POSTGRES_* vars when moving to Postgres.
DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": config("DB_NAME", default=str(BASE_DIR / "db.sqlite3")),
    }
}

if config("DB_ENGINE", default="") == "django.db.backends.postgresql":
    DATABASES["default"].update(
        {
            "USER": config("POSTGRES_USER"),
            "PASSWORD": config("POSTGRES_PASSWORD", default=""),
            "HOST": config("POSTGRES_HOST", default="localhost"),
            "PORT": config("POSTGRES_PORT", default="5432"),
        }
    )
