import requests
import os
from dotenv import load_dotenv
load_dotenv()
from utils.soapRequests import soapRequests

def exec_query(datasrc="" , query=""):
         gen_req = soapRequests(
                method="ExecuteQuery",
                wsdl_json_path="schemaJsonCollection/xtk_queryDef.json", 
                parameters={
                    "sessiontoken": os.getenv("ADOBE_SESSION_TOKEN"),
                    "entity":f"""<queryDef schema="nms:delivery" operation="get">
                                    <select>
                                        <node expr="[mapping/@schema]"/>
                                        
                                        <node expr="[mapping/@label]"/>
                                    
                                    </select>
                                    <where>
                                        <condition expr="@internalName = 'DM3250'"/>
                                    </where>
                                    </queryDef>"""
               }
         )
         gen_res = gen_req.send_request(url=os.getenv("ADOBE_INSTANCE_URL"))
         print(gen_res.text)
         return gen_res

url = "https://ac283eu.adobesandbox.com/nl/jsp/soaprouter.jsp"
token = os.getenv("ADOBE_SESSION_TOKEN")


def exec_sql(datasrc):
        gen_req = soapRequests(
                method="ExecSql",
                wsdl_json_path="schemaJsonCollection/xtk_builder.json", 
                parameters={
                    "sessiontoken": os.getenv("ADOBE_SESSION_TOKEN"),
                    "strSql":datasrc
                }
            )
        gen_res = gen_req.send_request(url=os.getenv("ADOBE_INSTANCE_URL"))
        print(gen_res.text)
        return gen_res



# genreq = exec_sql(datasrc="""
#   DELETE FROM MmaIpRecCopy
#   WHERE 1=1
# """
# )

genreq = exec_query()

