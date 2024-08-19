import requests
import xml.etree.ElementTree as ET
from model.xml_cervello import JSONXMLCervelloList
from controller.config import ConfigLoader

class ApiCervelloController:

    def __init__(self):
        self.configs = ConfigLoader()
        self.data_json_xml = JSONXMLCervelloList()
        self.headers = self.data_json_xml.headers()
        self.end_point = self.configs.end_point_cervello
    
    def request_result(self):
        root = ET.fromstring(self.xml_string)
        result_element = root.find(".//{http://tempuri.org/}AprovarSolicitacaoFormulario_CodigoResult")
        if result_element is not None:
            return result_element.text
        else:
            return None

    def call_capture(self, chamado):
        data = self.data_json_xml.xml_call_capture(chamado)
        
        response = requests.post(f'{self.end_point}',
                                 headers=self.headers,
                                 data=data)
        self.xml_string = response.content

        if response.status_code == 200:
            retorno = self.request_result()
            if retorno == 'OK|Solicitação em processo de aprovação.':
                return True, True
            else:
                return False, retorno
        else:
            return False, response.content
        
    def advance_call(self, chamado, nunota):
        data = self.data_json_xml.xml_advance_call(chamado, nunota)
        response = requests.post(f'{self.end_point}',
                                 headers=self.headers,
                                 data=data)
        self.xml_string = response.content
        
        if response.status_code == 200:
            retorno = self.request_result()
            if retorno == 'OK|Solicitação em processo de aprovação.':
                return True, True
            else:
                return False, retorno
        else:
            return False, retorno