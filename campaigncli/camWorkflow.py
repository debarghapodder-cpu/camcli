import argparse
from utils.soapRequests import soapRequests
import os
from dotenv import load_dotenv, set_key
from baseClasses.campaignBaseModule import CampaignBaseModule
from lxml import etree as et
import getpass

load_dotenv()
class AdobeWorkflow(CampaignBaseModule):
    """Class to manage Adobe Campaign sessions."""
    def __init__(self):
        pass


    # --- campaign command methods ---
    def campaign_workflow_cleanup(self , wkfid:str )->str:
        if wkfid == "":
            wkfid = input("Enter Workflow ID: ")
        try:
            gen_req = soapRequests(
                    method="Cleanup",
                    wsdl_json_path="schemaJsonCollection/xtk_workflow.json", 
                    parameters={
                        "sessiontoken": os.getenv("ADOBE_SESSION_TOKEN"),
                        "strWorkflowId":wkfid
                    }
                )
            gen_res = gen_req.send_request(url=os.getenv("ADOBE_INSTANCE_URL"))
            gen_res.raise_for_status()
            print(f"workflow {wkfid} cleaned up successfully!")
            return f"workflow {wkfid} cleaned up successfully!"
        except Exception as e:
            print(f"An error occurred during workflow cleanup: {e}")
            return f"Workflow cleanup failed: {e}"     

    def campaign_workflow_start(self , wkfid:str )->str:
        if wkfid == "":
            wkfid = input("Enter Workflow ID: ")
        try:
            gen_req = soapRequests(
                    method="Start",
                    wsdl_json_path="schemaJsonCollection/xtk_workflow.json", 
                    parameters={
                        "sessiontoken": os.getenv("ADOBE_SESSION_TOKEN"),
                        "strWorkflowId":wkfid
                    }
                )
            gen_res = gen_req.send_request(url=os.getenv("ADOBE_INSTANCE_URL"))
            gen_res.raise_for_status()
            print(f"workflow {wkfid} started successfully!")
            return f"workflow {wkfid} started successfully!"
        except Exception as e:
            print(f"An error occurred during workflow start: {e}")
            return f"Starting Workflow failed: {e}"     
        
    

    # --- CLI WRAPPER (Argparse calls this) ---
    def _cli_workflow_cleanup(self, args):
        """starts workflow cleanup"""
        self.campaign_workflow_cleanup(wkfid=args.wkfid)
    
    def _cli_workflow_start(self, args):
        """starts a workflow"""
        self.campaign_workflow_start(wkfid=args.wkfid)
    

    #create subparser object
    def get_cli_commands(self, subparsers):
        workflow_parser = subparsers.add_parser('workflow', help="commands related to workflows")  

        workflow_subparsers = workflow_parser.add_subparsers(dest='workflow_command', help="workflow operations")
        workflow_cleanup = workflow_subparsers.add_parser('cleanup', help="cleanup a workflow")
        workflow_cleanup.add_argument('--wkfid',  help="Workflow ID")
        workflow_cleanup.set_defaults(func=self._cli_workflow_cleanup)

        workflow_start = workflow_subparsers.add_parser('start', help="start a workflow")
        workflow_start.add_argument('--wkfid',  help="Workflow ID")
        workflow_start.set_defaults(func=self._cli_workflow_start)