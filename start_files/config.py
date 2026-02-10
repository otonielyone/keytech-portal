# start_files/config.py
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Union
from fastapi import Request
import os
from dotenv import load_dotenv

load_dotenv()


flash_messages = []

def flash(request: Request, message: str, category: str):
    """
    Store a flash message.
    """
    flash_messages.append({"message": message, "category": category})

def get_flashed_messages(request: Request) -> List[Dict[str, Union[str, List[str]]]]:
    """
    Retrieve all flash messages and clear them from the store.
    """
    messages = flash_messages[:]
    flash_messages.clear()
    return messages


def get_templates() -> Jinja2Templates:
    return Jinja2Templates(directory="start_files/templates")


# -------------------------
# Application configuration
# -------------------------

DEBUG = True

# ⚠️ Move this to an environment variable in production
SECRET_KEY = "SuprSecretKeyThatOnlyIknowrightNow001"
ALGORITHM = "HS256"

HOST = "keytech.yonesolutions.com"
PORT = 5000   # FastAPI default (Uvicorn)

# -------------------------
# LDAP Configuration
# -------------------------
# LDAP server
#LDAP_SERVER_URI = "ldap://keytech.yonesolutions.com:389"  # or 
LDAP_SERVER_URI = "ldaps://keytech.yonesolutions.com:636"

# Base DNs
LDAP_BASE_DN = "dc=keytech,dc=yonesolutions,dc=com"
LDAP_USER_BASE_DN = "ou=people,dc=keytech,dc=yonesolutions,dc=com"
LDAP_GROUP_BASE_DN = "ou=groups,dc=keytech,dc=yonesolutions,dc=com"

# Service account (used for search)
LDAP_BIND_DN = "cn=admin,dc=keytech,dc=yonesolutions,dc=com"
LDAP_BIND_PASSWORD = "admin123"  # or whatever you set

# LDAP attributes
LDAP_USERNAME_ATTR = "uid"        # what LDAP uses for username
LDAP_GROUP_NAME = None            # optional, if you filter by group CN
LDAP_GROUP_MEMBERS_ATTR = "uniqueMember"

# Search scopes (ldap3 constants)
LDAP_USER_SEARCH_SCOPE = "SUBTREE"
LDAP_GROUP_SEARCH_SCOPE = "SUBTREE"

# SSL / TLS
LDAP_USE_SSL = True
LDAP_TLS_VALIDATE = True   # set False ONLY for self-signed certs

# Timeouts
LDAP_TIMEOUT = 5


