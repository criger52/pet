import logging

import uvicorn

from src.app import Application
from src.config import get_settings


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logging.getLogger("sqlalchemy.engine").setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)


def main():
    """Create the FastAPI app and start the uvicorn server."""
    settings = get_settings()
    app = Application(settings).create_app()
    logger.info(f"Starting {settings.SERVICE_NAME} on port {settings.SERVICE_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)


if __name__ == "__main__":
    main()
