import logging

import uvicorn
from src.app import Application
from src.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def main():
    settings = get_settings()
    app = Application(settings).create_app()
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)


if __name__ == "__main__":
    main()
