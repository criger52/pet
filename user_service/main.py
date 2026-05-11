import uvicorn
from src.app import Application
from src.config import get_settings


def main():
    settings = get_settings()
    app = Application(settings).create_app()
    uvicorn.run(app, host="0.0.0.0", port=settings.USER_SERVICE_PORT)


if __name__ == "__main__":
    main()
