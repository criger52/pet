import uvicorn
from fastapi import FastAPI

def main():
    app = FastAPI(
        debug=True,
    )

    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
