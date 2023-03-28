# pylint: disable=logging-format-interpolation
import random
import string
import datetime as dt
from typing import Dict, List, Optional
from dotenv import load_dotenv
from fastapi.logger import logger
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import  Form, Request, HTTPException, status, Depends, Response, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2, OAuth2PasswordRequestForm
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param
from passlib.context import CryptContext
from jose import JWTError, jwt
from config.config import SETTING
from models.models import User

load_dotenv()

APP = APIRouter(tags=["creating shipment api's"])

APP.mount("/static", StaticFiles(directory="static"), name="static")

TEMPLATES = Jinja2Templates(directory="Templates")

CLIENT = SETTING.CLIENT

SIGNUP_COLLECTION = SETTING.SIGNUP_COLLECTION



PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    """Function to change plain password to Hash"""
    return PWD_CONTEXT.hash(password)

def verify_password(password: str, hashed_password: str):
    """Function to verify hased password"""
    return PWD_CONTEXT.verify(password, hashed_password)


def get_user(email: str) -> User:
    """
    Return user data from the specified MongoDB collection based on the user's email address.

    :param email: The email address of the user to retrieve data for.
    :type email: str
    :param collection: The MongoDB collection to retrieve data from.
    :type collection: pymongo.collection.Collection
    :return: A dictionary containing the user data, or None if the user does not exist.
    :rtype: dict or None
    """
    user = SIGNUP_COLLECTION.find_one({"Email":email})
    if user:
        return user
    return None

class OAuth2PasswordBearerWithCookie(OAuth2):
    """
    This class is taken directly from FastAPI:
    https://github.com/tiangolo/fastapi/blob/26f725d259c5dbe3654f221e608b14412c6b40da/fastapi/security/oauth2.py#L140-L171

    The only change made is that authentication is taken from a cookie
    instead of from the header!

    An OAuth2 authentication scheme that uses the "password" flow to authenticate users.

    :param tokenUrl: The URL to use to request an access token.
    :type tokenUrl: str
    :param scheme_name: The name of the authentication scheme.
    :type scheme_name: str, optional
    :param scopes: The scopes that are available for this authentication scheme.
    :type scopes: dict, optional
    :param description: A description of the authentication scheme.
    :type description: str, optional
    :param auto_error: Whether to automatically raise an HTTPException if authentication fails.
    :type auto_error: bool, optional

    """
    def __init__(self, tokenUrl: str, scheme_name: Optional[str] = None, scopes: Optional[Dict[str, str]] = None, description: Optional[str] = None, auto_error: bool = True):
        """
        Create a new instance of the MyOAuth2PasswordBearer class with the specified parameters.

        If the `scopes` parameter is not provided, an empty dictionary will be used instead.

        :param tokenUrl: The URL to use to request an access token.
        :type tokenUrl: str
        :param scheme_name: The name of the authentication scheme.
        :type scheme_name: str, optional
        :param scopes: The scopes that are available for this authentication scheme.
        :type scopes: dict, optional
        :param description: A description of the authentication scheme.
        :type description: str, optional
        :param auto_error: Whether to automatically raise an HTTPException if authentication fails.
        :type auto_error: bool, optional
        """
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        """
        IMPORTANT: this is the line that differs from FastAPI. Here we use
         `request.cookies.get(settings.COOKIE_NAME)` instead of
         `request.headers.get("Authorization")`
        """
        authorization: str = request.cookies.get(SETTING.COOKIE_NAME)
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                #redirect to login page
            return None
        return param

OAUTH2_SCHEME = OAuth2PasswordBearerWithCookie(tokenUrl="token")
"""
An instance of the OAuth2PasswordBearerWithCookie class that can be used to authenticate
requests that require an OAuth2 bearer token and/or an HTTP cookie.

Args:
    tokenUrl (str, optional): The URL of the token endpoint. Defaults to "token".
    scheme_name (str, optional): The name of the authentication scheme. Defaults to "bearer".
    scopes (dict, optional): A dictionary of OAuth2 scopes that the client is authorized to use.
    description (str, optional): A description of the authentication scheme.
    auto_error (bool, optional): Whether to automatically return an HTTP 401 response
        if authentication fails.

Returns:
    OAuth2PasswordBearerWithCookie: An instance of the OAuth2PasswordBearerWithCookie class.
"""

def create_access_token(data: Dict) -> str:
    """
    Create a JSON Web Token (JWT) access token from given dictionary of data.

    Parameters:
        data (Dict): A dictionary of data to encode in the access token.

    Args:
        data (Dict): A dictionary of data to include in the access token payload.

    Returns:
        str: The encoded JWT access token.

    Raises:
        ValueError: If the `data` argument is empty or not a dictionary.
    """
    to_encode = data.copy()
    expire = dt.datetime.utcnow() + dt.timedelta(minutes=SETTING.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        SETTING.SECRET_KEY,
        algorithm=SETTING.ALGORITHM
    )
    return encoded_jwt

def authenticate_user(username: str, plain_password: str) -> User:
    """
    Authenticates a user with the given username and plain-text password.

    Parameters:
        username (str): The username of the user to authenticate.
        plain_password (str): The plain-text password of the user to authenticate.

    Returns:
        Union[User, bool]: The authenticated user object as a `User` instance, or `False`
        if the user is not found or the password is incorrect.

    Raises:
        Union[bool, User]: If authentication fails, returns False. Otherwise,
        returns a User object for the authenticated user.
    """
    user = get_user(username)
    if not user:
        return False
    if not verify_password(plain_password, user['Password']):
        return False
    return user

def decode_token(token: str) -> User:
    """
    Decode a JWT token and return the associated user,
    or redirect to the login page if the token is invalid.

    Parameters:
        token (str): The JWT token to decode.

    Returns:
        Union[User, RedirectResponse]: If the token is valid,
        returns a User object for the associated user. Otherwise,
        returns a RedirectResponse object that redirects to the login page.

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials."
    )
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials."
    )
    token = str(token).replace("Bearer", "").strip()

    try:
        payload = jwt.decode(token, SETTING.SECRET_KEY, algorithms=[SETTING.ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    user = get_user(username)
    return user

def get_current_user_from_token(token: str = Depends(OAUTH2_SCHEME)) -> User:
    """
    Returns the authenticated user by decoding the provided JWT token

    Args:
    token (str, optional): The JWT token to decode. Defaults to Depends(OAUTH2_SCHEME).

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If the provided token is invalid or the user cannot be found.
    """
    user = decode_token(token)
    return user

def get_current_user_from_cookie(request: Request) -> User:
    """
    Get the current user from a cookie in a request.

    Parameters:
    - request (Request): The HTTP request containing the access token cookie.

    Returns:
    - user (User): The User object corresponding to the access token cookie.

    """
    token = request.cookies.get(SETTING.COOKIE_NAME)
    user = decode_token(token)
    return user




@APP.post("token")
def login_for_access_token(response: Response,\
        form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    """
    Endpoint to handle user authentication and access token generation.

    Args:
        response (fastapi.Response): The HTTP response object.
        form_data (OAuth2PasswordRequestForm): The OAuth2 password request form data.

    Returns:
        A dictionary containing the access token and token type.
    """
    # Authenticate the user with the provided credentials
    user = authenticate_user(form_data.login_user, form_data.login_password)
    if not user:
        # If the user is not authenticated, raise an HTTPException with 401 status code
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, \
            detail="Incorrect username or password")

    # Create an access token for the authenticated user
    access_token = create_access_token(data={"username": user["Email"]})

    # Set an HttpOnly cookie in the response. `httponly=True` prevents
    # JavaScript from reading the cookie.
    response.set_cookie(
        key=SETTING.COOKIE_NAME,
        value=f"Bearer {access_token}",
        httponly=True
    )
    # Return the access token and token type in a dictionary
    return {SETTING.COOKIE_NAME: access_token, "token_type": "bearer"}

class LoginForm:
    """
    A class that represents a login form and provides methods to load and validate form data.

    Attributes:
        request (Request): A `Request` object representing the incoming HTTP request.
        errors (List): A list of error messages that can be returned during form validation.
        login_user (Optional[str]): A string representing the user's login email,
        or `None` if not specified.
        login_password (Optional[str]): A string representing the user's login password,
        or `None` if not specified.
    """

    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.login_user: Optional[str] = None
        self.login_password: Optional[str] = None

    async def load_data(self):
        """
        Asynchronously loads form data from the incoming request
        and sets the `login_user` and `login_password`
        attributes of the `LoginForm` object.

        Args:
            self (LoginForm): The `LoginForm` object to load data into.

        Returns:
            None.
        """
        form = await self.request.form()
        self.login_user = form.get("login_user")
        self.login_password = form.get("login_password")

    async def is_valid(self):
        """
        Asynchronously validates the `LoginForm` object's `login_user`
        and `login_password` attributes and
        returns a boolean indicating whether the attributes are valid.

        If either the `login_user` or `login_password` attributes are invalid,
        an error message is added to
        the `errors` attribute of the `LoginForm` object.

        Args:
            self (LoginForm): The `LoginForm` object to validate.

        Returns:
            A boolean indicating whether the `login_user` and `login_password`
            attributes are valid and
            there are no errors. Returns `True` if the attributes are valid
            and there are no errors,
            otherwise `False`.
        """
        if not self.login_user or not (self.login_user.__contains__("@")):
            self.errors.append("Email is required")
        if not self.login_password or not len(self.login_password) >= 4:
            self.errors.append("A valid password is required")
        if not self.errors:
            return True
        return False

LOGIN_TEMPLATE = "index.html"

# --------------------------------------------------------------------------
# Dashboard Page
# --------------------------------------------------------------------------
@APP.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    """Home Page"""
    try:
        user = get_current_user_from_cookie(request)
    except ValueError:
        user = None
    context = {
        "user": user,
        "request": request,
    }
    return TEMPLATES.TemplateResponse("Dashboard.html", context)

# --------------------------------------------------------------------------
# Login - GET
# --------------------------------------------------------------------------

@APP.get("/auth/login", response_class=HTMLResponse)
def login_get(request: Request, message: str = None):
    """
    A route function that handles HTTP GET requests for the login page.

    Args:
        request (Request): A `Request` object representing the incoming HTTP request.

    Returns:
        A `TemplateResponse` object that renders the "login.html"
        template with the given request context.
        The response's `Content-Type` header is set to "text/html".
    """
    context = {
        "request": request,
        "message": message,
    }
    return TEMPLATES.TemplateResponse(LOGIN_TEMPLATE, context)

# --------------------------------------------------------------------------
# Login - POST
# --------------------------------------------------------------------------

@APP.post("/auth/login", response_class=HTMLResponse)
async def login_post(request: Request):
    """
    Handle a login request. :param request:
    The HTTP request object representing the login request.
    :return: A `TemplateResponse` object containing the rendered
    "login.html" template. This function handles POST requests to
    the "/auth/login" endpoint. It expects a valid
    `LoginForm` object to be submitted in the request body. If the submitted form data is
    valid, the user is redirected to the homepage ("/") with a newly created access token.
    If the submitted form data is not valid,
    the user is redirected back to the login page
    with an error message indicating what went wrong.
    Note that this function does not perform any authentication or authorization checks.
    Those should be handled separately in a middleware or in the application's business
    logic.
    """
    form = LoginForm(request)
    await form.load_data()
    try:
        if not await form.is_valid():
            # Form data is not valid
            raise HTTPException(status_code=400, detail="Form data is not valid")
        # Form data is valid, generate new access token
        response = RedirectResponse("/", status.HTTP_302_FOUND)
        login_for_access_token(response=response, form_data=form)
        form.__dict__.update(msg="Login Successful!")
        return response
    except HTTPException as exception:
        # Catch HTTPException and update form with error message
        form.__dict__.update(msg="")
        form.__dict__.get("errors").append(exception.detail)
        return TEMPLATES.TemplateResponse("Invalid.html", form.__dict__)
    except Exception as exception:
        # Catch any other exception and return 500 Internal Server Error
        raise HTTPException(status_code=500, detail=str(exception)) from exception


# --------------------------------------------------------------------------
# signup - GET
# --------------------------------------------------------------------------
@APP.get("/signup", response_class=HTMLResponse)
def get_signup_page(request: Request):
    """Returns the HTML page for user signup. This function handles GET requests to the
    "/signup" endpoint and returns the HTML page for user signup. The HTML page contains
    a form that allows users to input their details to create an account. The page also
    includes links to other relevant pages, such as the login page. :param request: The
    HTTP request object. :return: A `TemplateResponse` object containing the signup HTML page.
    """
    try:
        return TEMPLATES.TemplateResponse("index.html", {"request": request})
    except Exception as exception:
        # Log the error and raise an HTTPException with a 500 status code
        # to indicate a server error to the client.
        logger.exception(f"An error occurred while rendering the signup page: {exception}")
        raise HTTPException(status_code=500, detail="Server error") from exception

# --------------------------------------------------------------------------
# signup - POST
# --------------------------------------------------------------------------
@APP.post("/signup", response_class=HTMLResponse)
def signup_page(request: Request, username: str = Form(...), email: str = Form(...),\
        password: str = Form(...), cpassword: str = Form(...)):
    """
    Handle user registration requests.    :param request: The HTTP request object.
    :param username: The username for the new user, as a string.
    :param email: The email address for the new user, as a string.
    :param password: The password for the new user, as a string.
    :param cpassword: The confirmed password for the new user, as a string.
    :return: A `TemplateResponse` object with either the login template
    or the signup template and an error message.
    This function handles POST requests to the "/signup" endpoint.
    It expects the "username", "email", "password"
    and "cpassword" form fields to be included in the request data.
    The password is hashed before being added to the database.
    The function checks whether a user with the provided
    email already exists in the database. If not,
    and the provided password matches the confirmed password, the new user is added to the database
    and a response with the login template is returned.
    If a user with the provided email already exists or
    the password does not match the confirmed password, a response with the signup template
    and an appropriate error message is returned.    If an error occurs during database insertion,
    an HTTPException with a 500 Internal Server Error status code is raised.
    """
    hashed_password = hash_password(password)
    user = User(Username=username, Email=email, Password=hashed_password,\
    CPassword=cpassword)
    data = SIGNUP_COLLECTION.find_one({"Email":email})
    try:
        if not data and (password == cpassword):
            SIGNUP_COLLECTION.insert_one(user.dict())
            return TEMPLATES.TemplateResponse("regsuccess.html", {"request":request})
        random_string = ''.join(random.choice(string.ascii_letters) for i in range(5))
        email = f"{email.split('@')[0]}_{random_string}@{email.split('@')[1]}"
        print(email)
        return TEMPLATES.TemplateResponse("reguserexists.html", \
            {"request":request, "message":"Email already exists", "SUGGESTED_EMAIL":email})
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Missing parameter: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal Server Error") from exc
# --------------------------------------------------------------------------
# Logout
# --------------------------------------------------------------------------
@APP.get("/auth/logout", response_class=HTMLResponse)
def logout_get():
    """
    Handle a GET request to the logout endpoint.
    This function deletes the authentication cookie and redirects the user to the root page ("/").
    The authentication cookie is deleted by setting its value to an empty string and setting its
    max age to 0. This ensures that the browser deletes the cookie on the client side.
    :return: A `RedirectResponse` object that redirects the user to the root page ("/").
    """
    try:
        response = RedirectResponse(url="/auth/login")
        response.delete_cookie(SETTING.COOKIE_NAME)
        return response
    except KeyError as exc:
        raise HTTPException(status_code=400, detail="Cookie name not found.") from exc
    except Exception as exception:
        raise HTTPException(status_code=500, detail=str(exception)) from exception
