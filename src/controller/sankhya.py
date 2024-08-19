import requests
import json
from typing import Tuple, Optional
from model.sankhya import SankhyaModel
from controller.config import ConfigLoader
from playwright.sync_api import sync_playwright

class SankhyaController:
    
    def __init__(self):
        self.configs = ConfigLoader()
        self.model = SankhyaModel()
        self.user = self.configs.user_sankhya
        self.passw = self.configs.passw_sankhya
        self.end_point_inclusao = self.configs.url_sankhya_inclusao
        self.end_point_mge = self.configs.url_sankhya_mge
        self.end_point_mge_anexo = self.configs.url_sankhya_mge_anexo
    
    def token_sankhya(self) -> Tuple[Optional[str], Optional[str]]:
        response = requests.post(
                f'{self.end_point_mge}',
                params=self.model.params("MobileLoginSP.login"),
                headers=self.model.headers(),
                json=self.model.json_auth(user=self.user, passw=self.passw)
            )

        data = json.loads(response.content.decode('ISO-8859-1'))

        if response.status_code == 200:
            try:
                jsessionid = data["responseBody"]["jsessionid"]["$"]
                return True, jsessionid
            except:
                error = f"""Erro ao autenticar na API da sankhya: Código {response.status_code} - Erro {data}"""
                return False, error
        else:
            error = f"""Erro ao autenticar na API da sankhya: Código {response.status_code} - Erro {data}"""
            return False, error
        
    def consulta_existencia_cnpj(self,token,cnpj):
        json_data = self.model.json_consulta_existencia_cnpj(cnpj)

        response = requests.post(
            f'{self.end_point_mge}',
            params=self.model.params("ParceiroSP.verificaExistenciaCpfInscEstRepetido"),
            headers=self.model.headers(cookie=token),
            data=json.dumps(json_data)
        )

        data_exec = json.loads(response.content.decode('latin-1'))
        status = data_exec['status']

        if response.status_code == 200 and status == '1':
            response = data_exec['responseBody']
            if response:
                return True, response['codParc']
            else:
                mensagem = f"""Parceiro não encontrado"""
                return True, None
        else:
            mensagem = f"""Erro ao consultar parceiro: {data_exec}"""
            return False, None
        
    def consulta_codparc_codtipoper(self, token, cnpj):
        json_data = self.model.json_consulta_codparc_codtipoper(cnpj)

        response = requests.post(
            f'{self.end_point_mge}',
            params=self.model.params("DbExplorerSP.executeQuery"),
            headers=self.model.headers(cookie=token),
            data=json.dumps(json_data)
        )

        data_exec = json.loads(response.content.decode('latin-1'))
        status = data_exec['status']

        if response.status_code == 200 and status == '1':
            try:
                codparc = data_exec['responseBody']['rows'][0][0]
                codtipoper = data_exec['responseBody']['rows'][0][1]
                return True, codparc, codtipoper
            except:
                mensagem = f"""Parceiro não encontrado"""
                return False, None, None
    
        else:
            mensagem = f"""Erro ao consultar parceiro: {data_exec}"""
            return False, False, False
    
    def rateio_nota(self, token, nunota, json_data, centro_custo, codigo_natureza):

        json_rateio = self.model.json_rateio(nunota=nunota, json_data=json_data, centro_custo=centro_custo, codigo_natureza=codigo_natureza)
        
        response = requests.post(
            f'{self.end_point_mge}',
            params=self.model.params("CriteriosDeRateioSP.confirmarRateio"),
            headers=self.model.headers(cookie=token),
            data=json.dumps(json_rateio)
        )

        data_exec = json.loads(response.content.decode('latin-1'))
        status = data_exec['status']
        if response.status_code == 200 and status == '1':
            return True, True
    
        else:
            mensagem = f"""Erro ao lançar título: {data_exec}"""
            return False, mensagem

    def consulta_lancamento(self, token, cnpj, numnota, dtneg):
        json_data = self.model.json_consulta_lancamento(cnpj, numnota, dtneg)

        response = requests.post(
            f'{self.end_point_mge}',
            params=self.model.params("DbExplorerSP.executeQuery"),
            headers=self.model.headers(cookie=token),
            data=json.dumps(json_data)
        )

        data_exec = json.loads(response.content.decode('latin-1'))
        status = data_exec['status']

        if response.status_code == 200 and status == '1':
            result = data_exec['responseBody']['rows'][0][0]
            return True, result
    
        else:
            mensagem = f"""Erro ao consultar lançamento anterior: {data_exec}"""
            return False, 0

    def lanca_titulo(self,**kwargs):
        json_data = self.model.json_lancamento(codigo_empresa=kwargs["codigo_empresa"],
                                                   codigo_parceiro=kwargs["codigo_parceiro"],
                                                   centro_custo=kwargs["centro_custo"],
                                                   codigo_natureza=kwargs["codigo_natureza"],
                                                   descricao=kwargs["descricao"],
                                                   numero_nota=kwargs["numero_nota"],
                                                   data_negociacao=kwargs["data_negociacao"],
                                                   data_vencimento=kwargs["data_vencimento"],
                                                   codigo_venda=kwargs["codigo_venda"],
                                                   codigo_operacao=kwargs["codigo_operacao"],
                                                   chamado=kwargs["chamado"],
                                                   serie=kwargs["serie"]
                                                   )
        
        json.dumps(json_data)

        response = requests.post(
            f'{self.end_point_inclusao}',
            params=self.model.params(servico="CACSP.incluirAlterarCabecalhoNota", mgesession=kwargs["token"]),
            headers=self.model.headers(cookie=kwargs["token"]),
            data=json.dumps(json_data)
        )

        data = json.loads(response.content.decode('latin-1'))
        status = data['status']

        if response.status_code == 200 and status == '1':
            nunota = data['responseBody']['pk']['NUNOTA']['$']
            return True, int(nunota)

        else:
            return False, data

    def inclui_item(self, **kwargs):
        json_data = self.model.json_item(nunota=kwargs["nunota"],
                                             produto=kwargs["produto"],
                                             valor_total=kwargs["valor_total"])

        response = requests.post(
            f'{self.end_point_inclusao}',
            params=self.model.params("CACSP.incluirAlterarItemNota"),
            headers=self.model.headers(cookie=kwargs["token"]),
            data=json.dumps(json_data)
        )

        data = json.loads(response.content.decode('latin-1'))
        status = data["status"]

        if response.status_code == 200 and status == '1':
            nunota = data['responseBody']['pk']['NUNOTA']['$']
            return True, nunota
        else:
            mensagem = f"Erro ao incluir item: {data} - Status code: {response.status_code}"
            return False, data

    def altera_financeiro(self, codbarra=None, **kwargs):
        json_data = self.model.json_altera_financeiro(nufin=kwargs["nufin"],
                                                        codtiptit=kwargs["codtiptit"],
                                                        dtvenc=kwargs["vencimento"],
                                                        descricao=kwargs["descricao"],
                                                        codbarra=codbarra,
                                                        valor=kwargs["valor"])

        response = requests.post(
            f'{self.end_point_inclusao}',
            params=self.model.params(servico="CACSP.incluirAlterarFinanceiro", mgesession=kwargs["token"]),
            headers=self.model.headers(cookie=kwargs["token"]),
            data=json.dumps(json_data)
        )

        data = json.loads(response.content.decode('latin-1'))
        status = data["status"]

        if response.status_code == 200 and status == '1':
            nufin = data['responseBody']['pk']['NUFIN']['$']
            return True, int(nufin)
        else:
            return False, data

    def consulta_nufin(self, token, nunota):
        json_data = self.model.json_consulta_nufin(nunota)

        response = requests.post(
            f'{self.end_point_mge}',
            params=self.model.params("DbExplorerSP.executeQuery"),
            headers=self.model.headers(cookie=token),
            data=json.dumps(json_data)
        )

        data = json.loads(response.content.decode('latin-1'))
        status = data["status"]

        if response.status_code == 200 and status == '1':
            nufin_lista = []
            nufin = data["responseBody"]["rows"]
            
            for i, value in enumerate(nufin):
                nufin_lista.append(nufin[i][0])
            
            return True, nufin_lista
    
        else:
            mensagem = f"""Erro ao fazer consulta do nufin: Código {response.status_code} - Erro {data}"""
            return False, data

    def confirma_nota(self, token, nunota):
        json_data = self.model.json_confirma_nota(nunota)
        
        response = requests.post(
            f'{self.end_point_inclusao}',
            params=self.model.params(servico="CACSP.confirmarNota", mgesession=token),
            headers=self.model.headers(cookie=token),
            data=json.dumps(json_data)
        )

        data = json.loads(response.content.decode('latin-1'))
        status = data["status"]

        if response.status_code == 200 and status == '1':
            return True, True
        
        else:
            mensagem = f"Erro ao confirmar nota: {data} - Status code: {response.status_code}"
            return False, data

    def anexa_arquivo_nunota(self, token, nunota, nome_arquivo, caminho_arquivo, descricao):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
                context = browser.new_context(ignore_https_errors=True)
                page = context.new_page()  
                page.context.add_cookies([{
                    'name': 'JSESSIONID',
                    'value': token,
                    'url': f"{self.end_point_mge_anexo}"
                }])
                page.goto(f'{self.end_point_mge_anexo}/uploadAnexo.mge?acao=carregar&closeScript=window.opener.loadAttach_070();&codata={nunota}&sequencia=0&tipo=N')
                page.set_input_files('input[name=conteudo]', caminho_arquivo)
                page.fill('input[name=descricao]', descricao)
                page.locator('input[type="submit"][value="Salvar"]').click()
                page.wait_for_timeout(3000)
                if f'{nome_arquivo}' in page.content(): 
                    result = True
                else:
                    result = False
                browser.close()
                return result
        except Exception as e:
            return e