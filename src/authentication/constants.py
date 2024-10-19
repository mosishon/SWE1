from fastapi.security import OAuth2PasswordBearer

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60
RESET_PASSWORD_EXP_TIME = 10


LOGIN_ROUTE = "/login"  # After router prefix
REGISTRATION_ROUTE = "/register"


backend = OAuth2PasswordBearer(f"/auth{LOGIN_ROUTE}", scheme_name="JWT")
