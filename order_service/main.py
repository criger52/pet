import logging

import uvicorn
from fastapi import FastAPI


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)


def main():
    """Create a stub FastAPI app and start the uvicorn server."""
    app = FastAPI(
        title="Order Service",
        debug=True,
    )
    logger.info("Starting Order Service on port 8005")
    uvicorn.run(app, host="0.0.0.0", port=8005)


if __name__ == "__main__":
    main()
