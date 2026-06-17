import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    model_base_url: str
    model_api_key: str
    model_name: str

    def __init__(self):
        missing = []
        self.model_base_url = os.getenv("MODEL_BASE_URL", "https://api.minimax.chat/v1")
        self.model_api_key = os.getenv("MODEL_API_KEY", "")
        self.model_name = os.getenv("MODEL_NAME", "MiniMax-M2.5")

        if not self.model_api_key:
            missing.append("MODEL_API_KEY")
        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                "Copy .env.example to .env and fill in your credentials."
            )

settings = Settings()
