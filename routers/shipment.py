# pylint: disable=import-error
"""The above code is importing the necessary libraries for the program to run.
"""
from dotenv import load_dotenv
from pymongo.errors import PyMongoError
from fastapi.responses import HTMLResponse
from fastapi import Form, Request, HTTPException, Depends, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from config.config import SETTING
from models.models import Shipment
from models.models import User
from routers.user import get_current_user_from_token, get_current_user_from_cookie


load_dotenv()

APP = APIRouter(tags=["creating shipment api's"])

APP.mount("/static", StaticFiles(directory="static"), name="static")

TEMPLATES = Jinja2Templates(directory="Templates")

CLIENT = SETTING.CLIENT

SHIPMENT_COLLECTION = SETTING.SHIPMENT_COLLECTION

SHIPMENT_TEMPLATE = "shipment.html"

# --------------------------------------------------------------------------
# Create shipment Page GET
# --------------------------------------------------------------------------
# Create shipment page that only logged in users can access.


@APP.get("/shipment", response_class=HTMLResponse)
def get_shipment_page(request: Request, user: User = Depends(get_current_user_from_token)):
    # """
    # Render the shipment creation page for a logged-in user.
    # :param request: The HTTP request object.
    # :param user: The `User` object representing the currently logged-in user,
    # obtained from the access token.:return: A `TemplateResponse`
    # object containing the rendered "createshipment.html" template.
    # This function handles GET requests to the "/shipment" endpoint. It expects a valid access token
    # to be included in the request headers, which is used to retrieve the current user. If the user
    # is not logged in or the access token is invalid, a 401 Unauthorized response is returned.
    # The function returns a `TemplateResponse` object containing
    # the rendered "createshipment.html"
    # template, along with a context dictionary containing information
    # about the current user and request.
    # Note that this function assumes that the user is authenticated
    # and authorized to access the "/shipment"
    # endpoint. Any authentication and authorization checks should be
    # handled by a middleware or in the
    # application's business logic.
    # """
    try:
        context = {
            "user": user,
            "request": request
        }
        return TEMPLATES.TemplateResponse(SHIPMENT_TEMPLATE, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------------------------------------------------------
# Create shipment Page POST
# --------------------------------------------------------------------------
# Create shipment page that only logged in users can access.


@APP.post("/shipment", response_class=HTMLResponse)
def post_shipment_page(request: Request, shipment_invoice_number:
                       str = Form(...), container_number: int = Form(...), description: str = Form(...),
                       route_details: str = Form(...), goods_type: str = Form(...), device: str = Form(...),
                       delivery_date: str = Form(...), po_number: int = Form(...), delivery_number: int = Form(...),
                       ndcnumber: int = Form(...), batch_id: int = Form(...), serialnumberofgoods: int = Form(...)):
    """this is shipment post method"""
    user_name = get_current_user_from_cookie(request)
    user = Shipment(Shipment_Invoice_Number=shipment_invoice_number, \
        Container_Number=container_number, Description=description, \
            Route_Details=route_details, Goods_Type=goods_type, \
                Device=device, Expected_Delivery_Date=delivery_date,\
                     Po_Number=po_number, Delivery_number=delivery_number,\
                         NDCNumber=ndcnumber, Batch_Id=batch_id, \
                            Serialnumberofgoods=serialnumberofgoods,\
                                 mailid=user_name["Email"])
    data = SHIPMENT_COLLECTION.find_one(
        {"Shipment_Invoice_Number": shipment_invoice_number})
    try:
        if not data:
            SHIPMENT_COLLECTION.insert_one(user.dict())
            return TEMPLATES.TemplateResponse("shipsuccess.html",
                                              {"request": request, "user": user_name,
                                               "success_message": "Success! Your shipment has been created"})
        return TEMPLATES.TemplateResponse("shipment.html",
                                          {"request": request, "user": user_name,
                                           "message": "*Shipment_Invoice_Number already exists"})
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail="Invalid input. Please check your input values.") from exc
    except PyMongoError as exc:
        raise HTTPException(
            status_code=500, detail="Database error. Please try again later.") from exc
    except Exception as exception:
        raise HTTPException(
            status_code=500, detail=f"Internal Server Error: {str(exception)}") from exception


