import uvicorn
from fastapi import FastAPI
from src.api.routes.router import auth_router


def include_routers(app: FastAPI) -> None:
    app.include_router(auth_router)

def create_app(**kwargs) -> FastAPI:
    app = FastAPI(
        debug=True,
        **kwargs
    )
    include_routers(app)

    return app

def main():
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    main()
