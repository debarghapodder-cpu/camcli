from utils.wsdlToJsonParser import WSDLParser
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
def create_json():
   
    endpoints = [
        "xtk:srcSchema",
    ]
    for endpoint in endpoints:
        s_token = os.getenv("ADOBE_SESSION_TOKEN")
        sec_token = os.getenv("ADOBE_SECURITY_TOKEN")

        wsdl_url = f"{os.getenv('ADOBE_INSTANCE_URL')}/nl/jsp/schemawsdl.jsp?schema={endpoint}"
        headers = {
            "X-Security-Token": sec_token
        }
        cookies = {
            "__sessiontoken": s_token
        }
        response = requests.get(wsdl_url, headers=headers, cookies=cookies)

        if response.status_code == 200:
            wsdl_content = response.content
            parser = WSDLParser(wsdl_content=wsdl_content)
            json_output = parser.to_dict()
            with open(f"schemaJsonCollection/{endpoint.replace(':', '_')}.json", "w") as json_file:
                json.dump(json_output, json_file, indent=4)
        else:
            print(f"Failed to fetch WSDL for {endpoint}. Status code: {response.status_code}")
create_json()