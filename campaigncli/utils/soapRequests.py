import json
import requests
from lxml import etree as et
import os
from dotenv import load_dotenv
load_dotenv()

class soapRequests:
    def __init__(self, method, wsdl_json_path , parameters=None):
        self.method = method
        self.wsdl_json_path = wsdl_json_path
        self.parameters = parameters
        self.wsdl_json = json.load(open(wsdl_json_path))

    def send_request(self, url, cookies=None):
        soap_body = self.generate_soap_payload()
        headers = {
            "X-Security-Token": os.getenv("ADOBE_SECURITY_TOKEN"),
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": self.wsdl_json['operations'][self.method]['soapAction']
        }

        try:
            response = requests.post(url+"/nl/jsp/soaprouter.jsp", data=soap_body, headers=headers, cookies=cookies)
            return response
        except Exception as e:
            return None
            

    def generate_soap_payload(self): 
        """Generates the SOAP XML payload based on the WSDL JSON and provided parameters."""
        param_xml = ""
        for param in self.wsdl_json['operations'][self.method]["input"]['parameters']:
            if self.parameters:
                param_xml += f"<urn:{param['name']}>{self.parameters.get(param['name'], '')}</urn:{param['name']}>"
            else:
                param_xml += f"<urn:{param['name']}>{''}</urn:{param['name']}>"
        
        soap_body = f"""<?xml version='1.0' encoding='utf-8'?>
                            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="{self.wsdl_json['schema']}">
                                <soapenv:Header/>
                                <soapenv:Body>
                                    <urn:{self.method}>
                                        {param_xml}
                                    </urn:{self.method}>
                                </soapenv:Body>
                            </soapenv:Envelope>"""
        return soap_body
