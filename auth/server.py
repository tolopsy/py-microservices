import jwt, os
from datetime import datetime, timedelta
from flask import Flask, request, current_app
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

# NOTE: Accessing environment variables by dict indexing to
# emphasize and force availability of the variables.
server.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
server.config["MYSQL_HOST"] = os.environ["MYSQL_HOST"]
server.config["MYSQL_PORT"] = int(os.environ["MYSQL_PORT"])
server.config["MYSQL_USER"] = os.environ["MYSQL_USER"]
server.config["MYSQL_PASSWORD"] = os.environ["MYSQL_PASSWORD"]
server.config["MYSQL_DB"] = os.environ["MYSQL_DB"]


def create_jwt(username: str, is_admin: bool):
    now = datetime.utcnow()
    payload = {
        "username": username,
        "exp": now + timedelta(days=1),
        "iat": now,
        "admin": is_admin
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401

    cursor = mysql.connection.cursor()
    result = cursor.execute("SELECT email, password FROM user WHERE email=%s", (auth.username,))

    if result == 0:
        return "invalid credentials", 401

    user_row = cursor.fetchone()
    _, password = user_row

    # TODO: Don't compare raw password
    if auth.password != password:
        return "invalid credentials", 401
    
    return create_jwt(auth.username, is_admin=True)

@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]

    if not encoded_jwt:
        return "missing credentials", 401
    
    try:
        encoded_jwt = encoded_jwt.split("Bearer ")[1]
    except IndexError:
        return "invalid credentials", 401
    
    try:
        decoded_jwt = jwt.decode(encoded_jwt, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.exceptions.DecodeError:
        return "bad request", 400
    except jwt.exceptions.ExpiredSignatureError:
        return "expired credentials", 401
    except:
        return "invalid credentials", 401
    
    return decoded_jwt, 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
