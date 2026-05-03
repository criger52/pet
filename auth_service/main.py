import uvicorn
from fastapi import FastAPI
from src.routes.router import auth_router


def main():
    app = FastAPI(
        debug=True,
    )
    app.include_router(auth_router)

    uvicorn.run(app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    main()
