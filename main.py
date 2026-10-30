import asyncio

import uvicorn
from fastapi import FastAPI

from core.environment import Config

app = FastAPI()


async def main():
    uvicorn_config = uvicorn.Config(
        app="main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.ENVIRONMENT == "dev",
    )
    server = uvicorn.Server(uvicorn_config)

    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
