from pprint import pprint
from urllib.parse import urljoin
from dotenv import load_dotenv

import requests
import sys
import os


load_dotenv()

api_token = os.getenv("API_TOKEN")
headers = {"Authorization": f"Token {api_token}"}

username = "widyadana735"  # update to match your USERNAME!

pythonanywhere_host = "www.pythonanywhere.com"  # or "eu.pythonanywhere.com" if your account is hosted on our EU servers
pythonanywhere_domain = "pythonanywhere.com"  # or "eu.pythonanywhere.com"

# make sure you don't use this domain already!
domain_name = f"{username}.{pythonanywhere_domain}"

api_base = f"https://{pythonanywhere_host}/api/v1/user/{username}/"

arg = sys.argv[1]

if arg == "create":
    command = (
        f"/home/{username}/.virtualenvs/amongus_fast_venv/bin/uvicorn "
        f"--app-dir /home/{username}/amongus-bot-2 "
        "--uds $DOMAIN_SOCKET "
        "main:app "
    )

    response = requests.post(
        urljoin(api_base, "websites/"),
        headers=headers,
        json={
            "domain_name": domain_name,
            "enabled": True,
            "webapp": {"command": command}
        },
    )
    pprint(response.json())
elif arg == "list":
    endpoint = urljoin(api_base, "websites/")
    response = requests.get(endpoint, headers=headers)
    pprint(response.json())
elif arg == "get":
    endpoint = urljoin(api_base, f"websites/{domain_name}/")
    response = requests.get(endpoint, headers=headers)
    pprint(response.json())
elif arg == "reload":
    endpoint = urljoin(api_base, f"websites/{domain_name}/")
    # disable:
    response = requests.patch(endpoint, headers=headers, json={"enabled": False})
    pprint(response.json())
    # enable:
    response = requests.patch(endpoint, headers=headers, json={"enabled": True})
    pprint(response.json())
elif arg == "delete":
    response = requests.delete(
        urljoin(api_base, f"websites/{domain_name}/"),
        headers=headers
    )
    pprint(response.json())
