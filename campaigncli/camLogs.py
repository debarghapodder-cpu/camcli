import argparse
from utils.soapRequests import soapRequests
import os
from dotenv import load_dotenv, set_key
from baseClasses.campaignBaseModule import CampaignBaseModule
from lxml import etree as et


load_dotenv()
class AdobeLogs(CampaignBaseModule):
    """Class to manage Adobe Campaign sessions."""
    def __init__(self):
        pass
    

    def execute_query(self , entity=""):
        gen_req = soapRequests(
                method="ExecuteQuery",
                wsdl_json_path="schemaJsonCollection/xtk_queryDef.json", 
                parameters={
                    "sessiontoken": os.getenv("ADOBE_SESSION_TOKEN"),
                    "entity":entity
            }
        )
        gen_res = gen_req.send_request(url=os.getenv("ADOBE_INSTANCE_URL"))
        return gen_req , gen_res

    def get_broad_log_schema(self, dlvid):
        try:
            gen_req , res = self.execute_query(entity=f"""<queryDef schema="nms:delivery" operation="get">
                                                                <select>
                                                                    <node expr="[mapping/storage/@broadLogSchema]"/>
                                                                    <node expr="[mapping/@schema]"/>
                                                                </select>
                                                                <where>
                                                                    <condition expr="@internalName = '{dlvid}'"/>
                                                                </where>
                                                            </queryDef>"""
                                    )
            # print(res.text)
            storage = et.fromstring(res.content).find(".//{"+f"{gen_req.wsdl_json['targetNamespace']}"+"}"+f"storage")
            mapping = et.fromstring(res.content).find(".//{"+f"{gen_req.wsdl_json['targetNamespace']}"+"}"+f"mapping")
            return storage.attrib['broadLogSchema'] , mapping.attrib['schema']

        except Exception as e:
            print(f"broadlog search failed: {e}")
            return None
    
    def parse_logs(self , xml_string , gen_req=None):
        status_map = {
            "127": "Not applicable",
            "0": "Ignored",
            "1": "Sent",
            "2": "Failed",
            "3": "Pending (Provider)",
            "5": "Received on mobile",
            "6": "Pending",
            "7": "Delivery canceled",
            "8": "Prepared",
            "9": "Sent to provider"
        }
        root = et.fromstring(xml_string)
        logs = []    
        outs = root.find(".//{"+f"{gen_req.wsdl_json['targetNamespace']}"+"}pdomOutput").getchildren()[0].getchildren()
        
        for entry in outs:
            row = {
                "address": entry.attrib["address"],
                "eventDate": entry.attrib["eventDate"],
                "status": status_map[entry.attrib["status"]]
            }
            delivery = entry.find("./{"+f"{gen_req.wsdl_json['targetNamespace']}"+"}delivery")
            if delivery is not None:
                row["internalName"] = delivery.attrib["internalName"]
            else:
                row["internalName"] = None
            logs.append(row)
        return logs
        
    def get_delivery_logs(self, broadLogSchema , dlvid="" , schema=""):
        try:
            gen_req , res = self.execute_query(entity=f"""
                                                        <queryDef schema="{broadLogSchema}" operation="select" lineCount="10001">
                                                            <select>
                                                                <node expr="@address"/>
                                                                <node expr="@status"/>
                                                                <node expr="@eventDate"/>
                                                                <node expr="[delivery/@internalName]" />
                                                            </select>
                                                            
                                                            <orderBy>
                                                                <node expr="@address" sortDesc="true"/>
                                                            </orderBy>
                                                            
                                                            <where>
                                                                <condition expr="[delivery/@internalName] = '{dlvid}'"/>
                                                            </where>
                                                        </queryDef>"""
                                                    )
            # print(res.text)
            logs = self.parse_logs(res.content, gen_req)
            return logs

        except Exception as e:
            print(f"Delivery log retrieval failed: {e}")
            return None
        
        

    # --- campaign command methods ---
    def campaign_broadlogs(self , dlvid:str )->str:
        if dlvid == "":
            dlvid = input("Enter Delivery name: ")
        try:
            broadLogSchema , schema = self.get_broad_log_schema(dlvid)
            if not broadLogSchema:
                raise Exception("Broad log schema not found for the given delivery ID.")
            logs = self.get_delivery_logs(broadLogSchema, dlvid=dlvid , schema=schema.split(":")[-1])
            if logs is None:
                raise Exception("Failed to retrieve delivery logs.")
            print(f"\n--- Logs for {dlvid} ({len(logs)} records found) ---")
            for log in logs:
                print(f"Date: {log.get('eventDate')} | Status: {log.get('status')} | Address: {log.get('address')} | Delivery name: {log.get('internalName')}")

            return "broadLogs displayed"
        except Exception as e:
            print(f"An error occurred during displaying logs: {e}")
            return f"Workflow cleanup failed: {e}"     


    # --- CLI WRAPPER (Argparse calls this) ---
    def _cli_delivery_logs(self, args):
        """starts workflow cleanup"""
        self.campaign_broadlogs(dlvid=args.dlvid)
    
    

    #create subparser object
    def get_cli_commands(self, subparsers):
        logs_parse = subparsers.add_parser('logs', help="commands related to displaying logs")  

        log_subparsers = logs_parse.add_subparsers(dest='logs_command', help="logs operations")
        delivery_log = log_subparsers.add_parser('delivery', help="show delivery logs")
        delivery_log.add_argument('--dlvid',  help="Delivery ID")
        delivery_log.set_defaults(func=self._cli_delivery_logs)