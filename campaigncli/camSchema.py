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
        <srcSchema label="{label}" name="{name}" namespace="{namespace}" xtkschema="xtk:srcSchema">    
            <element label="{label}" name="{name}" autopk="true">
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
        

    def build_update_one_schema_diff(self, namespace , name , useNamingConventions):
        gen_req = soapRequests(
                method="BuildUpdateOneSchemaDiff",
                wsdl_json_path="schemaJsonCollection/xtk_builder.json", 
                parameters={
                    "sessiontoken": os.getenv("ADOBE_SESSION_TOKEN"),
                    "strSchemaId": f"{namespace}:{name}",
                    "useNamingConventions": useNamingConventions
                }
            )
        gen_res = gen_req.send_request(url=os.getenv("ADOBE_INSTANCE_URL"))
        return gen_req , gen_res
    
    def update_DB(self , parameters):
        gen_req = soapRequests(
                method="UpdateDb",
                wsdl_json_path="schemaJsonCollection/xtk_builder.json", 
                parameters={
                    "sessiontoken": os.getenv("ADOBE_SESSION_TOKEN"),
                    "elemParameters": parameters
                }
            )
        gen_res = gen_req.send_request(url=os.getenv("ADOBE_INSTANCE_URL"))
        return gen_res
    
    def write_schema_to_adobe(self, schema_xml):
        reqobj = soapRequests(
                    method="Write"
                    , wsdl_json_path="schemaJsonCollection/xtk_session.json",
                    parameters={
                        "sessiontoken": os.getenv("ADOBE_SESSION_TOKEN")
                        , "domDoc": schema_xml
                    }
                )    
        res = reqobj.send_request(url=os.getenv("ADOBE_INSTANCE_URL"))
        return res
    
    def build_sql_schema(self , name , namespace):
        gen_req = soapRequests(
                method="BuildSqlSchema",
                wsdl_json_path="schemaJsonCollection/xtk_sqlSchema.json", 
                parameters={
                    "sessiontoken": os.getenv("ADOBE_SESSION_TOKEN"),
                    "strTableName":namespace[0].upper() + namespace[1:]+name[0].upper()+name[1:]
                }
            )
        gen_res = gen_req.send_request(url=os.getenv("ADOBE_INSTANCE_URL"))
        # print(gen_res.text)
        return gen_req , gen_res


    # --- campaign command methods ---
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
            res = self.write_schema_to_adobe(schema_xml=schema_xml)
            res.raise_for_status()
            gen_res = self.build_schema_xml(schema_xml)
            gen_res.raise_for_status()
            print(f"Schema {table_name} generated successfully.")
            return f"Schema {name} created successfully."
        
        except Exception as e:
            print(f"Schema creation failed: {e}")
            return f"Schema creation failed: {e}"
    
    def migrate_campaign_schema(self, namespace:str , name:str , useNamingConventions :bool = 1) -> str:
        try:
            gen_req , res = self.build_update_one_schema_diff(namespace=namespace , name=name , useNamingConventions=1)
            res.raise_for_status()
            root = et.fromstring(res.content).find(".//{"+f"{gen_req.wsdl_json['targetNamespace']}"+"}"+f"table")
            xml_payload = et.tostring(root,  encoding="unicode")
            update_res = self.update_DB(parameters=xml_payload)
            update_res.raise_for_status()
            print(f"Schema {namespace}:{name} migrated successfully.")
            return f"Schema {namespace}:{name} migrated successfully."

        except Exception as e:
            print(f"Schema migration failed: {e}")
            return f"Schema migration failed: {e}"


     # --- CLI WRAPPER (Argparse calls this) ---
    def _cli_schema_create(self, args):
        """Bridges CLI arguments to the sessionLogin method."""
        self.create_campaign_schema(name=args.name,
                                    namespace=args.namespace , 
                                    label=args.label
                )

    def _cli_schema_migrate(self, args):
        self.migrate_campaign_schema(namespace=args.namespace, 
                                     name=args.name, 
                                     useNamingConventions=args.useNamingConventions
            )

    # --- create subparser object ---
    def get_cli_commands(self, subparsers):
        schema_parser = subparsers.add_parser('schema', help="Schema management commands")  

        schema_subparsers = schema_parser.add_subparsers(dest='schema_command', help="Schema operations")
        schema_create = schema_subparsers.add_parser('create', help="Generate and save a schema")
        schema_create.add_argument('--name', required=True, help="SQL table name to reverse engineer")
        schema_create.add_argument('--namespace',  help="Target namespace (default: cus)")
        schema_create.add_argument('--label',  help="Schema label (default: None)")
        schema_create.set_defaults(func=self._cli_schema_create)

        schema_migrate = schema_subparsers.add_parser('migrate', help="Migrate schema to Adobe")
        schema_migrate.add_argument('--namespace', required=True, help="Namespace of the schema to migrate")
        schema_migrate.add_argument('--name', required=True, help="Name of the schema to migrate")
        schema_migrate.add_argument('--useNamingConventions', action='store_true', help="Whether to apply Adobe's naming conventions during migration")
        schema_migrate.set_defaults(func=self._cli_schema_migrate)