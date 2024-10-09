from fastapi.security import OAuth2PasswordBearer

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60

LOGIN_ROUTE = "/login"  # After router prefix


backend = OAuth2PasswordBearer(f"/auth/{LOGIN_ROUTE}", scheme_name="JWT")
