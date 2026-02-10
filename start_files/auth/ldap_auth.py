from ldap3 import Server, Connection, SUBTREE, ALL, Tls
from ldap3.core.exceptions import LDAPBindError, LDAPException
import ssl
import logging
from start_files.config import (
    LDAP_TLS_VALIDATE,
    LDAP_SERVER_URI,
    LDAP_USE_SSL,
    LDAP_TIMEOUT,
    LDAP_BIND_DN,
    LDAP_BIND_PASSWORD,
    LDAP_USER_BASE_DN,
    LDAP_USERNAME_ATTR
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def authenticate_ldap(username: str, password: str) -> bool:
    """
    Authenticate a user via LDAP.
    Returns True if credentials are valid, False otherwise.
    """
    
    logger.debug(f"=" * 60)
    logger.debug(f"LDAP Authentication attempt for user: {username}")
    logger.debug(f"LDAP Server URI: {LDAP_SERVER_URI}")
    logger.debug(f"LDAP Use SSL: {LDAP_USE_SSL}")
    logger.debug(f"=" * 60)
    
    # -------------------------
    # TLS setup (only if using SSL)
    # -------------------------
    tls_config = None
    if LDAP_USE_SSL:
        tls_config = Tls(
            validate=ssl.CERT_REQUIRED if LDAP_TLS_VALIDATE else ssl.CERT_NONE
        )
        logger.debug(f"TLS configuration enabled with validate={LDAP_TLS_VALIDATE}")
    
    # -------------------------
    # Create server object
    # -------------------------
    try:
        server = Server(
            LDAP_SERVER_URI,
            use_ssl=LDAP_USE_SSL,
            tls=tls_config,
            get_info=ALL,
            connect_timeout=LDAP_TIMEOUT
        )
        logger.debug(f"Server object created successfully")
    except Exception as e:
        logger.error(f"Failed to create LDAP server object: {e}")
        return False
    
    # -------------------------
    # 1️⃣ Bind with service account
    # -------------------------
    try:
        logger.debug(f"Attempting service account bind with DN: {LDAP_BIND_DN}")
        conn = Connection(
            server,
            user=LDAP_BIND_DN,
            password=LDAP_BIND_PASSWORD,
            auto_bind=True
        )
        logger.debug(f"✅ Service account bind successful")
        logger.debug(f"Server info: {server.info}")
    except LDAPBindError as e:
        logger.error(f"❌ Service account bind failed: {e}")
        logger.error(f"Check LDAP_BIND_DN and LDAP_BIND_PASSWORD in config.py")
        return False
    except LDAPException as e:
        logger.error(f"❌ LDAP connection error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during service bind: {e}")
        return False
    
    # -------------------------
    # 2️⃣ Search for user DN
    # -------------------------
    search_filter = f"({LDAP_USERNAME_ATTR}={username})"
    logger.debug(f"Searching for user with filter: {search_filter}")
    logger.debug(f"Search base DN: {LDAP_USER_BASE_DN}")
    
    try:
        search_result = conn.search(
            search_base=LDAP_USER_BASE_DN,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=["cn", "uid"]  # <-- NO dn EVER
        )
        logger.debug(f"Search executed, result: {search_result}")
        logger.debug(f"Number of entries found: {len(conn.entries)}")
        
    except LDAPException as e:
        logger.error(f"❌ LDAP search failed: {e}")
        conn.unbind()
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during search: {e}")
        conn.unbind()
        return False
    
    if not conn.entries:
        logger.error(f"❌ User '{username}' not found in LDAP")
        logger.error(f"Make sure user exists in: {LDAP_USER_BASE_DN}")
        logger.error(f"And has attribute: {LDAP_USERNAME_ATTR}={username}")
        conn.unbind()
        return False
    
    user_dn = conn.entries[0].entry_dn
    logger.debug(f"✅ Found user DN: {user_dn}")
    logger.debug(f"User entry: {conn.entries[0]}")
    conn.unbind()
    
    # -------------------------
    # 3️⃣ Bind as user to check password
    # -------------------------
    try:
        logger.debug(f"Attempting user authentication bind with DN: {user_dn}")
        user_conn = Connection(
            server,
            user=user_dn,
            password=password,
            auto_bind=True
        )
        logger.debug(f"✅ User '{username}' authentication successful!")
        user_conn.unbind()
        return True
        
    except LDAPBindError as e:
        logger.error(f"❌ Invalid password for user '{username}'")
        logger.debug(f"Bind error details: {e}")
        return False
    except LDAPException as e:
        logger.error(f"❌ LDAP error during user bind: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during user authentication: {e}")
        return False