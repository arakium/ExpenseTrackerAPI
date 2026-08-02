import os

from dotenv import load_dotenv, find_dotenv

# looks for .env and loads its variables.
load_dotenv(
    dotenv_path=find_dotenv(raise_error_if_not_found=True)
)
SECRET_KEY = os.getenv('SECRET_JWT')