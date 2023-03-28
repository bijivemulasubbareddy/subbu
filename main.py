# pylint: disable=no-name-in-module
# pylint: disable=too-few-public-methods
"""The above code is importing the necessary libraries for the program to run.
"""
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from config.config import SETTING
from routers import user, shipment, datastrem


load_dotenv()

# Create a FastAPI app instance
APP = FastAPI(title=SETTING.TITLE,\
DESCRIPTION=SETTING.DESCRIPTION, version=SETTING.PROJECT_VERSION)

@APP.exception_handler(HTTPException)
async def redirect_to_login(request: Request, exc: HTTPException) -> Response:
    """
    Exception handler that redirects the user to the login page if
    the HTTPException has a status code of 401.
    If the status code is anything other than 401, the exception is
     re-raised for handling by other exception
    handlers.

    Args:
        request (Request): The request that caused the exception.
        exc (HTTPException): The HTTPException that was raised.

    Returns:
        Response: A response object that either redirects the user
        to the login page or re-raises the exception
        for other status codes.
    """
     # pylint: disable=unused-argument
    if exc.status_code == 401:
        # Redirect to login page
        return HTMLResponse("<script>window.location.href = '/auth/login';</script>")
    # Re-raise the exception for other status codes
    raise exc

APP.mount("/static", StaticFiles(directory="static"), name="static")

TEMPLATES = Jinja2Templates(directory="templates")

APP.include_router(shipment.APP)
APP.include_router(datastrem.APP)
APP.include_router(user.APP)
