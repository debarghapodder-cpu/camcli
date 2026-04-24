#!/usr/bin/env python3
"""
CLI Tool Template

A modular CLI tool template using argparse for easy extension.
Add new commands by creating functions and registering them in the parser.
"""
import argparse
from parser import create_parser
import sys
import pprint
from utils.wsdlToJsonParser import WSDLParser
from utils.soapRequests import soapRequests
import os
from dotenv import load_dotenv, set_key

load_dotenv(override=True)

def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    if not args.auth:
        parser.print_help()
        sys.exit(1)
        
    args.func(args)

if __name__ == '__main__':
    main()