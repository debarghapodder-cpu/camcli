import argparse
from utils.soapRequests import soapRequests
import os
from dotenv import load_dotenv, set_key
from baseClasses.campaignBaseModule import CampaignBaseModule
from lxml import etree as et
import getpass

load_dotenv()
class AdobeSession(CampaignBaseModule):
    """Class to manage Adobe Campaign sessions."""
    def __init__(self):
        super().__init__()
        self.instance_url = None
        self.username = None
        self.session_token = None
        self.security_token = None
        self.password = None

    def check_authentication(self):
        url = self.instance_url or os.getenv("ADOBE_INSTANCE_URL")
        if not url:
            return False
        try:
            reqobj = soapRequests(
                method="GetUserInfo", 
                wsdl_json_path="schemaJsonCollection/xtk_session.json", 
                parameters={"sessiontoken": os.getenv("ADOBE_SESSION_TOKEN")} 
            )
            res = reqobj.send_request(url=url)
            result = et.fromstring(res.content).find(".//{"+f"{reqobj.wsdl_json['targetNamespace']}"+"}"+f"userInfo")
            return result.get("login") != ""

        except Exception as e:
            print(f"Session validation failed: {e}")
            return False
        
    def sessionLogout(self)->str:
        """Log out of the current Adobe Campaign session."""
        try:
            reqobj = soapRequests(
                method="Logoff",
                wsdl_json_path="schemaJsonCollection/xtk_session.json",
                parameters={"sessiontoken": os.getenv("ADOBE_SESSION_TOKEN")}
            )
            res = reqobj.send_request(url=os.getenv("ADOBE_INSTANCE_URL"))
            if not res:
                raise Exception("[CAMCLI ERROR]: Logout Failed!!")
            res.raise_for_status()
            env_path=".env"
            set_key(env_path, "ADOBE_SESSION_TOKEN", "")
            set_key(env_path, "ADOBE_SECURITY_TOKEN", "")
            set_key(env_path, "ADOBE_CLIENT_USERNAME", "")
            set_key(env_path, "ADOBE_INSTANCE_URL", "")
            set_key(env_path, "ADOBE_CLIENT_LOGIN_CS", "")
            set_key(env_path, "ADOBE_SESSION_LOGINID", "")

            print("Successfully logged out.")
            return "Successfully logged out."
        except Exception as e:
            print(f"Logged out")
            env_path=".env"
            set_key(env_path, "ADOBE_SESSION_TOKEN", "")
            set_key(env_path, "ADOBE_SECURITY_TOKEN", "")
            set_key(env_path, "ADOBE_CLIENT_USERNAME", "")
            set_key(env_path, "ADOBE_INSTANCE_URL", "")
            set_key(env_path, "ADOBE_CLIENT_LOGIN_CS", "")
            set_key(env_path, "ADOBE_SESSION_LOGINID", "")
            return f"Logged out"

    def get_session_info(self, url:str = None , session_token:  str = None)-> None:
        try:
            reqobj = soapRequests(
                method="GetUserInfo"
                , wsdl_json_path="schemaJsonCollection/xtk_session.json",
                parameters={
                    "sessiontoken": session_token
                }
            )    
            res = reqobj.send_request(url=url)
            res.raise_for_status()
            result = et.fromstring(res.content).find(".//{"+f"{reqobj.wsdl_json['targetNamespace']}"+"}"+f"userInfo")
            env_path=".env"
            set_key(env_path, "ADOBE_SESSION_LOGINID", result.attrib['loginId'])
            set_key(env_path, "ADOBE_CLIENT_LOGIN_CS", result.attrib['loginCS'])
            return
        except Exception as e:
            print(f"Failed to retrieve session info: {e}")
            return None
    
    def sessionLogin(self, url:str , username:str) -> str:
        """Authenticate with Adobe Campaign and store the session token."""
        try:
            if self.check_authentication():
                print(f"Already authenticated with instance {url} as {username}. Please log out.")
                return None
            password = getpass.getpass(f"Password for {username}: ")
            print(f"Attempting to authenticate with instance {url} as {username}")

            
            reqobj = soapRequests(method="Logon", wsdl_json_path="schemaJsonCollection/xtk_session.json", 
                                parameters={"strLogin": username, "strPassword": password}
            )
            res = reqobj.send_request(url=url)
            if not res:
                raise Exception("[CAMCLI ERROR]: Login failed!!")
            res.raise_for_status()
            root = et.fromstring(res.content)
            outparams = reqobj.wsdl_json['operations'][reqobj.method]['output']['parameters']
            temp={}
            for param in outparams:
                parameter_value = root.find(".//{"+f"{reqobj.wsdl_json['targetNamespace']}"+"}"+f"{param['name']}")
                temp[param['name']] = parameter_value.text if parameter_value is not None else None
            
            env_path = ".env"
            set_key(env_path, "ADOBE_SESSION_TOKEN", temp['pstrSessionToken'])
            set_key(env_path, "ADOBE_SECURITY_TOKEN", temp['pstrSecurityToken'])
            set_key(env_path, "ADOBE_CLIENT_USERNAME", username)
            set_key(env_path, "ADOBE_INSTANCE_URL", url)

            self.session_token = temp['pstrSessionToken']
            self.security_token = temp['pstrSecurityToken']
            self.instance_url = url
            print(f"Authenticated with instance {self.instance_url} as {username}")
            self.get_session_info(url=url, session_token=temp['pstrSessionToken'])
            return f"Authenticated with instance {self.instance_url} as {username}"
        except Exception as e:
            print(f"Authentication failed: {e}")
            return f"Authentication failed: {e}"
    
        

    # --- CLI WRAPPER (Argparse calls this) ---
    def _cli_login_wrapper(self, args):
        """Bridges CLI arguments to the sessionLogin method."""
        self.sessionLogin(url=args.url, username=args.username)
    
    def _cli_logout(self, args):
        """Bridges CLI arguments to the sessionLogout method."""
        self.sessionLogout()


    #create subparser object
    def get_cli_commands(self, subparsers):
        sessionlogin = subparsers.add_parser('login', help="""
                                            log into adobe campaign instance
                                            parameters:
                                                --url: URL of the Adobe Campaign instance
                                                --username: Username for authentication
                                              """)
        sessionlogout = subparsers.add_parser('logout', help="""log out off the instance""")
        
        #login parameters
        sessionlogin.add_argument('--url', required=True, type=str)
        sessionlogin.add_argument('--username', required=True, type=str)
        # Point to the wrapper, not the core logic

        sessionlogin.set_defaults(func=self._cli_login_wrapper)
        sessionlogout.set_defaults(func=self._cli_logout)