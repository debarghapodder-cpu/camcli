import argparse
from utils.soapRequests import soapRequests
import os
from dotenv import load_dotenv, set_key
from baseClasses.campaignBaseModule import CampaignBaseModule
from lxml import etree as et
from datetime import datetime, timezone

load_dotenv()

def new_schema_template_generator(name , namespace , label , data):
    schema_template=f"""
        <srcSchema  label="{label}" name="{name}" namespace="{namespace}" xtkschema="xtk:srcSchema">    
            <element label="{label}" name="{name}">
                {data}
            </element>
        </srcSchema>
    """
    return schema_template


class AdobeSchema(CampaignBaseModule):
    def __init__(self):
        pass

    def build_schema_xml(self, schema_xml):
        gen_req = soapRequests(
                method="BuildSchema",
                wsdl_json_path="schemaJsonCollection/xtk_builder.json", 
                parameters={
                    "sessiontoken": os.getenv("ADOBE_SESSION_TOKEN"),
                    "elemSource": schema_xml 
                }
            )
        gen_res = gen_req.send_request(url=os.getenv("ADOBE_INSTANCE_URL"))
        return gen_res

    def create_campaign_schema(self, name:str = None , namespace:str = "" , label:str = "") -> str:
        table_name = name
        table_namespace = namespace
        table_label = label
        if namespace == "":
            table_namespace = "cus"
        if not name:
            table_name = input("enter schema name: ")
        if not label:
            table_label = input("enter schema label (optional): ")
        schema_xml = new_schema_template_generator(name=table_name , namespace=table_namespace , label=table_label , data="")
        try:
            reqobj = soapRequests(
                    method="Write"
                    , wsdl_json_path="schemaJsonCollection/xtk_session.json",
                    parameters={
                        "sessiontoken": os.getenv("ADOBE_SESSION_TOKEN")
                        , "domDoc": schema_xml
                    }
                )    
            res = reqobj.send_request(url=os.getenv("ADOBE_INSTANCE_URL"))
            res.raise_for_status()
            
            gen_res = self.build_schema_xml(schema_xml)
            gen_res.raise_for_status()
            print(f"Schema {table_name} generated successfully.")
            return f"Schema {name} created successfully."
        
        except Exception as e:
            print(f"Schema creation failed: {e}")
            return f"Schema creation failed: {e}"


     # --- CLI WRAPPER (Argparse calls this) ---
    def _cli_schema_create(self, args):
        """Bridges CLI arguments to the sessionLogin method."""
        self.create_campaign_schema(name=args.name, namespace=args.namespace , label=args.label)

        
     #create subparser object
    def get_cli_commands(self, subparsers):
        schema_parser = subparsers.add_parser('schema', help="Schema management commands")
        
        # 2. Add a subparser specifically FOR the schema command
        schema_subparsers = schema_parser.add_subparsers(dest='schema_command', help="Schema operations")
        schema_create = schema_subparsers.add_parser('create', help="Generate and save a schema")
        schema_create.add_argument('--name', required=True, help="SQL table name to reverse engineer")
        schema_create.add_argument('--namespace',  help="Target namespace (default: cus)")
        schema_create.add_argument('--label',  help="Schema label (default: None)")
        schema_create.set_defaults(func=self._cli_schema_create)