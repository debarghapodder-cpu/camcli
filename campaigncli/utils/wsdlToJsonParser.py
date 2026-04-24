from lxml import etree as et
from collections import defaultdict
import json


class WSDLParser:
    def __init__(self, wsdl_file=None , wsdl_content=None):
        print("Initializing WSDLParser...")
        self.wsdl_file = wsdl_file
        self.wsdl_content = wsdl_content
        if self.wsdl_content:
            self.tree = et.fromstring(self.wsdl_content)
            self.root = self.tree
        else:
            self.tree = et.parse(self.wsdl_file)
            self.root = self.tree.getroot()
        self.namespaces = self.root.nsmap
        self.namespaces['wsdl'] = self.namespaces.get(None)  
        self.tns = self.namespaces.get('tns')
        self.schema = self.namespace_uri_to_schema(self.namespaces['tns'])
        self.operations=defaultdict(dict)
        self.methods=[]
        self.parse()
 
    def namespace_uri_to_schema(self, uri: str) -> str:
        if uri.startswith("urn:"):
            return uri.replace("urn:", "")
        return uri
        
    def detect_kind(self,input_element, ns):
        xsd = "{" + ns.get("s") + "}"
        sequence = input_element.find(f".//{xsd}sequence")
        if sequence is None:
            return "static"

        children = sequence.findall(f"{xsd}element")
        if len(children) == 1:
            child = children[0]
            type_attr = child.attrib.get("type", "")
            if (
                type_attr.endswith("Element")
                or child.find(f".//{xsd}any") is not None
            ):
                return "const"
        return "static"

    def find_operations(self, root , method , ns):
        input_element = root.find(f".//portType/operation[@name='{method}']", ns)
        input_message = input_element.find("input", ns).attrib['message'] 
        output_message = input_element.find("output", ns).attrib['message']
        return input_message.split(':')[-1], output_message.split(':')[-1]

    def find_operation_inout_elements(self, root , method_message_in , method_message_out , ns):
        root_inp = root.find(f".//message[@name='{method_message_in}']", ns)
        root_out = root.find(f".//message[@name='{method_message_out}']", ns)
        element_in = root_inp.find("part", ns)
        element_out = root_out.find("part", ns)
        return (element_in.attrib['element'].split(':')[-1] if element_in is not None else None,
                element_out.attrib['element'].split(':')[-1] if element_out is not None else None)

    def find_soap_action(self , root , method , ns):
        soap = "{" + ns.get("soap") + "}"
        binding = root.find(f".//binding/operation[@name='{method}']", ns)
        soap_action = binding.find(f"{soap}operation", ns).attrib.get('soapAction', '')
        return soap_action

    def find_method_parameters(self, root , in_meth , out_meth , ns):
        xsd = "{" + ns.get("s") + "}"
        meth_elements = [root.find(f".//{xsd}element[@name='{in_meth}']", ns) , root.find(f".//{xsd}element[@name='{out_meth}']", ns)]
        
        res=[]
        for meth in meth_elements:
            temp_arr=[]
            if meth is not None:
                sequence = meth.find(f".//{xsd}sequence", ns)
                if sequence is not None:
                    for param in sequence.findall(f"{xsd}element", ns):
                        temp = {
                            'name': param.attrib.get('name'),
                            'type': param.attrib.get('type', 'unknown').split(':')[-1],
                            'required': param.attrib.get('minOccurs', '1') != '0'
                        }
                        temp_arr.append(temp)
            res.append(temp_arr)
        return res[0], res[1]
    


    def parse(self):
        for operation in self.root.findall(".//wsdl:portType/wsdl:operation", self.namespaces):
            self.methods.append(operation.attrib['name'])
        operations = defaultdict(dict)

        for method in self.methods:
            kind= self.detect_kind(self.root.find('.//{'+f"{self.namespaces['s']}"+'}'+f"element[@name='{method}']",self.namespaces),self.namespaces)
            operations[method]['kind'] = kind
            soapAction = self.find_soap_action(self.root, method, self.namespaces)
            operations[method]['soapAction'] = soapAction
            input_message, output_message = self.find_operations(self.root, method, self.namespaces)
            operations[method]['input']= {'message': input_message, "parameters": []}
            operations[method]['output']= {'message': output_message, "parameters": []}            
            operations[method]['input']['element'] , operations[method]['output']['element'] = self.find_operation_inout_elements(self.root, input_message, output_message, self.namespaces)
            inp_parameters , out_parameters = self.find_method_parameters(self.root, operations[method]['input']['element'], operations[method]['output']['element'], self.namespaces)
            operations[method]['input']['parameters'] = inp_parameters
            operations[method]['output']['parameters'] = out_parameters
        self.operations = operations
    
    def to_dict(self):
        return{
            'schema': self.schema,
            'targetNamespace':self.tns,
            'namespaces':self.root.nsmap,
            'operations': self.operations
        }
    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)