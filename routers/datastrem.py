# pylint: disable=no-name-in-module
# pylint: disable=too-few-public-methods
# """The above code is importing the necessary libraries for the program to run.
# """
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
from fastapi import Request, HTTPException, Depends, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from config.config import SETTING
from models.models import User
from routers.user import get_current_user_from_token


load_dotenv()

APP = APIRouter(tags=["creating shipment api's"])

APP.mount("/static", StaticFiles(directory="static"), name="static")

TEMPLATES = Jinja2Templates(directory="Templates")

CLIENT = SETTING.CLIENT

DATA_STREAM = SETTING.DATA_STREAM
# --------------------------------------------------------------------------
# Data stream Page
# --------------------------------------------------------------------------
# A Data stream page that only logged in users can access.
@APP.get("/Devicedata", response_class=HTMLResponse)
def stream_page(request: Request, user: User = Depends(get_current_user_from_token)):
    # """
    # # A route function that handles HTTP GET requests to "/datastream".
    # # This function fetches data from a MongoDB collection called "DATA_STREAM".
    # # The data is then passed to the "Devicedata.html" template for rendering.
    # # Args:
    # # request (Request): A `Request` object representing the incoming HTTP request.
    # # user (User, optional): An optional `User` object representing the current user.
    # # Returns:
    # # A `TemplateResponse` object that renders the "Devicedata.html" template
    # # with the given request context. The response's `Content-Type` header is
    # # set to "datastream.html".
    # # """
    try:
        streaming_data = []
        all_shipments = DATA_STREAM.find({})
        for i in all_shipments:
            streaming_data.append(i)
        context = {
            "user": user,
            "streaming_data":streaming_data,
            "request": request
        }
        return TEMPLATES.TemplateResponse("datastream.html", context)
    except Exception as e:
        error_msg = f"An error occurred while trying to retrieve data from the database: {str(e)}"
        return HTTPException(status_code=500, detail=error_msg)
