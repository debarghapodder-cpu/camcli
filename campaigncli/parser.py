import argparse
from camSession import AdobeSession
from camSchema import AdobeSchema
from camWorkflow import AdobeWorkflow
from camLogs import AdobeLogs
import json

def display_soap_methods(args):
    """
    Reads the JSON schema and prints the details of a specific SOAP method.
    """
    try:
        # Construct the path based on the namespace argument
        file_path = f"schemaJsonCollection/{args.ns}.json"
        with open(file_path, "r") as f:
            data = json.load(f)
            # Access the specific method within the operations dictionary
            method_details = data['operations'].get(args.method)
            if method_details:
                # Use json.dumps for a prettier, readable output
                print(json.dumps(method_details, indent=4))
            else:
                print(f"Error: Method '{args.method}' not found in {args.ns}.json")
    except FileNotFoundError:
        print(f"Error: Schema file 'schemaJsonCollection/{args.ns}.json' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
def create_parser():
    parser = argparse.ArgumentParser(
        description="Adobe Campaign CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Available Commands:"""
        )

    subparsers = parser.add_subparsers(dest='auth', help='Available commands')
    soapdesc = subparsers.add_parser('soapdesc', help="""
                                            view the soap method parameters
                                            parameters:
                                                --ns: namespace of the method
                                                --method: method name
                                            """)
    soapdesc.add_argument('--ns', required=True, type=str)
    soapdesc.add_argument('--method', required=True, type=str)
    soapdesc.set_defaults(func=display_soap_methods)
    
    # Register session management commands
    AdobeSession().get_cli_commands(subparsers)
    AdobeSchema().get_cli_commands(subparsers)
    AdobeWorkflow().get_cli_commands(subparsers)
    AdobeLogs().get_cli_commands(subparsers)
    return parser