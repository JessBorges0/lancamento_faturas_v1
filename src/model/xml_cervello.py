from datetime import datetime
from controller.config import ConfigLoader

class JSONXMLCervelloList:
    
    def __init__(self):
        self.configs = ConfigLoader()
        self.useradm = self.configs.user_adm_cervello
        self.passadm = self.configs.pass_adm_cervello
        self.codusuaprov = self.configs.cod_usu_aprov_cervello
        self.passusuaprov = self.configs.pass_usu_aprov_cervello
        self.codusucap = self.configs.cod_usu_cap_cervello
        self.usucap = self.configs.usu_cap_cervello
        self.host = self.configs.host_cervello

    def headers(self):
        return {
            'Content-Type': 'text/xml; charset=utf-8',
            'Host': f'{self.host}',
        }

    def xml_call_capture(self, call):
        return f'''<soapenv:Envelope
            xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:tem="http://tempuri.org/"
            xmlns:xs="http://www.w3.org/2001/XMLSchema">\n   
            <soapenv:Header/>\n   
            <soapenv:Body>\n      
                <tem:AprovarSolicitacaoFormulario_Codigo>\n         
                    <tem:USERADM>{self.useradm}</tem:USERADM>\n         
                    <tem:PASSADM>{self.passadm}</tem:PASSADM>\n         
                    <tem:CodigoUsuarioAprovador>{self.codusuaprov}</tem:CodigoUsuarioAprovador>\n
                    <tem:SenhaUsuarioAprovador>{self.passusuaprov}</tem:SenhaUsuarioAprovador>\n         
                    <tem:CodigoSolicitacao>{call}</tem:CodigoSolicitacao>\n         
                    <tem:dsModeloFormulario>\n            
                        <xs:schema
                            xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" id="NewDataSet">\n               
                            <xs:element name="NewDataSet" msdata:IsDataSet="true" msdata:UseCurrentLocale="true">\n                  
                                <xs:complexType>\n                    
                                    <xs:choice minOccurs="0" maxOccurs="unbounded">\n                      
                                        <xs:element name="Campos">\n                       
                                            <xs:complexType>\n                        
                                                <xs:sequence>\n                  
                                                    <xs:element name="Codigo" type="xs:int" default="0" minOccurs="0" />\n                  
                                                    <xs:element name="CodigoCampo" type="xs:int" default="0" minOccurs="0" />\n                  
                                                    <xs:element name="CodigoSolicitacao" type="xs:int" default="0" minOccurs="0" />\n                  
                                                    <xs:element name="Alias_Campo" type="xs:string" default="" minOccurs="0" />\n                  
                                                    <xs:element name="ValorNumerico" type="xs:double" default="0" minOccurs="0" />\n                  
                                                    <xs:element name="ValorTexto" type="xs:string" minOccurs="0" />\n                  
                                                    <xs:element name="Oculto" type="xs:int" default="0" minOccurs="0" />\n                
                                                </xs:sequence>\n              
                                            </xs:complexType>\n            
                                        </xs:element>\n          
                                    </xs:choice>\n        
                                </xs:complexType>\n      
                            </xs:element>\n    
                        </xs:schema>\n             
                        <diffgr:diffgram
                            xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1"
                            xmlns:msdata="urn:schemas-microsoft-com:xml-msdata">\n               
                            <NewDataSet
                                xmlns="">\n                  
                                <Campos diffgr:id="Campos1" msdata:rowOrder="0" diffgr:hasChanges="inserted">\n                     
                                    <Codigo>0</Codigo>\n     
                                    <CodigoCampo>0</CodigoCampo>\n     
                                    <CodigoSolicitacao>0</CodigoSolicitacao>\n     
                                    <Alias_Campo>selecione o responsável</Alias_Campo>\n     
                                    <ValorNumerico>{self.codusucap}</ValorNumerico>
                                    <ValorTexto>{self.usucap}</ValorTexto> 
                                    <Oculto>0</Oculto>\n                  
                                </Campos>\n                   
                                <Campos diffgr:id="Campos2" msdata:rowOrder="0" diffgr:hasChanges="inserted">\n                     
                                    <Codigo>0</Codigo>\n     
                                    <CodigoCampo>0</CodigoCampo>\n     
                                    <CodigoSolicitacao>0</CodigoSolicitacao>\n     
                                    <Alias_Campo>descrição</Alias_Campo>\n     
                                    <ValorNumerico>0</ValorNumerico>\n     
                                    <ValorTexto>Execução por Integração</ValorTexto>\n     
                                    <Oculto>0</Oculto>\n                  
                                </Campos>\n               
                            </NewDataSet>\n            
                        </diffgr:diffgram>\n            
                        <!--You may enter ANY elements at this point-->\n         
                    </tem:dsModeloFormulario>\n      
                </tem:AprovarSolicitacaoFormulario_Codigo>\n   
            </soapenv:Body>\n
        </soapenv:Envelope>'''.encode()
    
    def xml_advance_call(self, call, nunota, data=datetime.now().strftime('%d/%m/%Y')):
        return f'''<soapenv:Envelope
            xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:tem="http://tempuri.org/"
            xmlns:xs="http://www.w3.org/2001/XMLSchema">\n   
            <soapenv:Header/>\n   
            <soapenv:Body>\n      
                <tem:AprovarSolicitacaoFormulario_Codigo>\n         
                    <tem:USERADM>{self.useradm}</tem:USERADM>\n         
                    <tem:PASSADM>{self.passadm}</tem:PASSADM>\n         
                    <tem:CodigoUsuarioAprovador>{self.codusuaprov}</tem:CodigoUsuarioAprovador>\n
                    <tem:SenhaUsuarioAprovador>{self.passusuaprov}</tem:SenhaUsuarioAprovador>\n         
                    <tem:CodigoSolicitacao>{call}</tem:CodigoSolicitacao>\n         
                    <tem:dsModeloFormulario>\n            
                        <xs:schema
                            xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" id="NewDataSet">\n               
                            <xs:element name="NewDataSet" msdata:IsDataSet="true" msdata:UseCurrentLocale="true">\n                  
                                <xs:complexType>\n                    
                                    <xs:choice minOccurs="0" maxOccurs="unbounded">\n                      
                                        <xs:element name="Campos">\n                       
                                            <xs:complexType>\n                        
                                                <xs:sequence>\n                  
                                                    <xs:element name="Codigo" type="xs:int" default="0" minOccurs="0" />\n                  
                                                    <xs:element name="CodigoCampo" type="xs:int" default="0" minOccurs="0" />\n                  
                                                    <xs:element name="CodigoSolicitacao" type="xs:int" default="0" minOccurs="0" />\n                  
                                                    <xs:element name="Alias_Campo" type="xs:string" default="" minOccurs="0" />\n                  
                                                    <xs:element name="ValorNumerico" type="xs:double" default="0" minOccurs="0" />\n                  
                                                    <xs:element name="ValorTexto" type="xs:string" minOccurs="0" />\n                  
                                                    <xs:element name="Oculto" type="xs:int" default="0" minOccurs="0" />\n                
                                                </xs:sequence>\n              
                                            </xs:complexType>\n            
                                        </xs:element>\n          
                                    </xs:choice>\n        
                                </xs:complexType>\n      
                            </xs:element>\n    
                        </xs:schema>\n             
                        <diffgr:diffgram
                            xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1"
                            xmlns:msdata="urn:schemas-microsoft-com:xml-msdata">\n               
                            <NewDataSet
                            xmlns="">
                            <Campos diffgr:id="Campos1" msdata:rowOrder="0" diffgr:hasChanges="inserted">
                        <Codigo>0</Codigo>
                    <CodigoCampo>0</CodigoCampo>
                    <CodigoSolicitacao>0</CodigoSolicitacao>
                    <Alias_Campo>documentação/informação conforme?</Alias_Campo>
                    <ValorNumerico>10</ValorNumerico>
                    <ValorTexto>Sim</ValorTexto>
                    <Oculto>0</Oculto>
                    </Campos>
                    <Campos diffgr:id="Campos2" msdata:rowOrder="0" diffgr:hasChanges="inserted">
                        <Codigo>0</Codigo>
                    <CodigoCampo>0</CodigoCampo>
                    <CodigoSolicitacao>0</CodigoSolicitacao>
                    <Alias_Campo>parecer do atendimento</Alias_Campo>
                    <ValorNumerico>0</ValorNumerico>
                    <ValorTexto>Execução por Integração - Lançamento programado</ValorTexto>
                    <Oculto>0</Oculto>
                    </Campos>
                                    <Campos diffgr:id="Campos3" msdata:rowOrder="0" diffgr:hasChanges="inserted">
                        <Codigo>0</Codigo>
                    <CodigoCampo>0</CodigoCampo>
                    <CodigoSolicitacao>0</CodigoSolicitacao>
                    <Alias_Campo>número único</Alias_Campo>
                    <ValorNumerico>0</ValorNumerico>
                    <ValorTexto>{nunota}</ValorTexto>
                    <Oculto>0</Oculto>
                    </Campos>
                                    <Campos diffgr:id="Campos4" msdata:rowOrder="0" diffgr:hasChanges="inserted">
                        <Codigo>0</Codigo>
                    <CodigoCampo>0</CodigoCampo>
                    <CodigoSolicitacao>0</CodigoSolicitacao>
                    <Alias_Campo>data do lançamento</Alias_Campo>
                    <ValorNumerico>0</ValorNumerico>
                    <ValorTexto>{data}</ValorTexto>
                    <Oculto>0</Oculto>
                    </Campos>
                        </NewDataSet>\n            
                        </diffgr:diffgram>\n            
                        <!--You may enter ANY elements at this point-->\n         
                    </tem:dsModeloFormulario>\n      
                </tem:AprovarSolicitacaoFormulario_Codigo>\n   
            </soapenv:Body>\n
        </soapenv:Envelope>'''.encode()