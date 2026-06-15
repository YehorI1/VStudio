import os
from typing import Literal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:

    def init(self):
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

        self._load_env_file()

    def _load_env_file(self):
        env_files = {
            "local": BASE_DIR / ".env.local",
            "development": BASE_DIR / ".env.development",
            "production": BASE_DIR / ".env.production",
        }

        env_file = env_files[self.ENVIRONMENT]

        if env_file and env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        value = value.strip().strip('"').strip("'")
                        os.environ.setdefault(key.strip(), value)

    # @property
    # def SECRET_KEY(self) -> str:
    #     key = os.environ.get("SECRET_KEY")
    #     if not key:
    #         raise ValueError("SECRET_KEY environment variable not set")
    #     return key

    @property
    def DEBUG(self) -> bool:
        return os.environ.get("DEBUG", False).lower() in ["true", "1", "yes"]

    @property
    def SITE_ID(self) -> int:
        return int(os.environ.get("SITE_ID", 1))

    @property
    def ALLOWED_HOSTS(self) -> list:
        hosts = os.environ.get("ALLOWED_HOSTS", "")
        return [h.strip() for h in hosts.split(",") if h.strip()]

    @property
    def CSRF_TRUSTED_ORIGINS(self) -> list:
        hosts = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
        return [h.strip() for h in hosts.split(",") if h.strip()]



    @property
    def DJANGO_SUPERUSER_USERNAME(self):
        return os.environ.get("DJANGO_SUPERUSER_USERNAME")

    @property
    def DJANGO_SUPERUSER_EMAIL(self):
        return os.environ.get("DJANGO_SUPERUSER_EMAIL")

    @property
    def DJANGO_SUPERUSER_PASSWORD(self):
        return os.environ.get("DJANGO_SUPERUSER_PASSWORD")

    # Додаткові властивості
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_local(self) -> bool:
        return self.ENVIRONMENT == "local"


# Singleton instance
config = Config()