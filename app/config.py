import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    minimax_base_url: str
    minimax_api_key: str
    model_name: str

    def __init__(self):
        missing = []
        self.minimax_base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
        self.minimax_api_key = os.getenv("MINIMAX_API_KEY", "")
        self.model_name = os.getenv("MODEL_NAME", "MiniMax-M2.5")

        if not self.minimax_api_key:
            missing.append("MINIMAX_API_KEY")
        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                "Copy .env.example to .env and fill in your credentials."
            )

settings = Settings()
