import asyncio

import click
import uvicorn
from fastapi import FastAPI

app = FastAPI()


async def main():
    from core.environment import Config
    from core.handlers import router

    app.include_router(router)

    uvicorn_config = uvicorn.Config(
        app="main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.ENVIRONMENT == "dev",
    )
    server = uvicorn.Server(uvicorn_config)

    await server.serve()


@click.group()
def cli():
    pass


@click.command()
def runserver():
    asyncio.run(main())


@click.command()
def generate_secret_key():
    from core.scripts.generate_secret_key import generate_secret_key

    generate_secret_key()


@click.command()
def generate_dotenv():
    from core.scripts.generate_dotenv_file import generate_dotenv_files

    generate_dotenv_files()


@click.command("genuser")
def gen_user():
    from core.scripts.add_user import gen_superuser

    gen_superuser()


cli.add_command(runserver)
cli.add_command(generate_dotenv)
cli.add_command(generate_secret_key)
cli.add_command(gen_user)

if __name__ == "__main__":
    cli()
