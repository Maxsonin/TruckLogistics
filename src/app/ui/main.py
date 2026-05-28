from dotenv import load_dotenv

load_dotenv()

from app.ui.app import run_app

if __name__ == "__main__":
    run_app()