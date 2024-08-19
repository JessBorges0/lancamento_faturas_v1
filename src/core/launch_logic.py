import os
import json
from controller.email import send_email
from core.validation import invoice_type, validate_values, check_codemp, clear_cnpj, conversation_values, encode_illegal_xml_chars
from core.file_manager import FileManager
from controller.openai import OpenAIController
from controller.sankhya import SankhyaController
from sql.db_integration import DatabaseIntegration

class LaunchLogic:

    def __init__(self, logger):
        self.logger = logger
        self.openai = OpenAIController()
        self.sankhya = SankhyaController()
        self.file_manager = FileManager(logger=logger)

    def process_call(self, token_sankhya, call, index_call, df_base_calls, df_attachments_calls):
        self.token_sankhya = token_sankhya
        self.call = call
        self.index_call = index_call
        self.df_base_calls = df_base_calls
        self.df_attachments_calls = df_attachments_calls

        self.status_execution = self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'].values[0]
        self.file = self.df_attachments_calls.loc[self.index_call, 'CaminhoServidorDireto']

        if self.status_execution != 'OK':
            self.logger.info(f"Chamado {self.call} não está com o status OK")
            return

        if self.file_manager.check_password_pdf(self.file):
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Arquivo com senha'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = '-'
            return

        if self.file_manager.is_pdf_image(self.file):
            input_pdf = self.file
            self.file = os.path.join(os.getcwd(), 'src/data/download_file_ocr/', f'{self.call}.pdf')

            success, err = self.file_manager.ocr_pdf(input_pdf, self.file)
            if err:
                self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro na conversão OCR'
                self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Robô'
                self.logger.error(f"Erro na conversão OCR do chamado {self.call}")
                return
            self.logger.info(f"OCR realizado com sucesso no chamado {self.call}")

        self.text, err = self.file_manager.extract_text_from_pdf(self.file)
        if err:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro na extração do PDF'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Robô'
            self.logger.error(f"Erro na extração do PDF do chamado {self.call}")
            return
        self.logger.info(f"Extração do PDF realizada com sucesso no chamado {self.call}")

        result_pi = self.process_invoice()
        if not result_pi:
            return

        result_lls = self.logic_launch_sankhya()
        if not result_lls:
            return

    def process_invoice(self):
        self.model_invoice, err = invoice_type(self.text)
        if err:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Fatura não mapeada'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Robô'
            self.logger.error(f"Chamado {self.call} - fatura não mapeada")
            return False
        self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'ModeloFatura'] = self.model_invoice
        self.logger.info(f"Chamado {self.call} - Fatura mapeada")

        barcode, err = self.file_manager.extract_barcode(self.text)
        if err:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro na extração do Código de Barras'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Robô'
            self.logger.error(f"Chamado {self.call} - erro na extração do Código de Barras")
            return False
        self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'CodigoBarras'] = barcode
        self.logger.info(f"Chamado {self.call} - extração do Código de Barras realizada com sucesso")

        self.prompt, err = self.openai.request_body(pdf_text=self.text, invoice_type=self.model_invoice)
        if err:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro na criação do prompt'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Robô'
            self.logger.error(f"Chamado {self.call} - erro na criação do prompt")
            return False
        self.logger.info(f"Chamado {self.call} - prompt criado com sucesso")

        self.json_data, err = self.openai.openai_request(self.prompt)
        if err:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro na execução do OpenAI'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Robô'
            self.logger.error(f"Chamado {self.call} - erro na execução do OpenAI")
            return False
        self.logger.info(f"Chamado {self.call} - execução do OpenAI realizada com sucesso")

        return True

    def logic_launch_sankhya(self):
        self.json_data = json.loads(self.json_data)

        result_vv, value_total = validate_values(self.json_data)
        if not result_vv:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Valores divergentes'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = '-'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'ValorFatura'] = value_total
            self.logger.error(f"Chamado {self.call} - valores não conferem com o total da fatura")
            return False
        self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'ValorFatura'] = value_total
        self.logger.info(f"Chamado {self.call} - valores conferem com o total da fatura")

        self.valor_df = self.json_data['documento_financeiro']['valor_total'][0]
        self.data_vencimento = self.json_data['datavencimento']
        self.forma_pagamento = self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'FormaPagamento'].values[0]
        self.descricao = encode_illegal_xml_chars(self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'Descricao'].values[0])
        self.centro_custo = self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'CentroCusto'].values[0]
        self.codigo_natureza = self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'Natureza'].values[0]
        self.codigo_barras = self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'CodigoBarras'].values[0]
        
        for index, nota in enumerate(self.json_data['notas_fiscais']):
            total_nf = len(self.json_data['notas_fiscais'])
            self.logger.info(f"Processando nota {index + 1} de {total_nf}")
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'QuantidadeNF'] = total_nf

            self.cnpj_raiz = clear_cnpj(self.json_data['notas_fiscais'][index]['cpfcnpj'])
            self.cnpj_fornecedor = clear_cnpj(self.json_data['notas_fiscais'][index]['cnpj'])
            self.numero_nota = self.json_data['notas_fiscais'][index]['numero']
            self.serie = self.json_data['notas_fiscais'][index]['serie']
            self.valor_nf = self.json_data['notas_fiscais'][index]['valor_total'][0]
            self.data_emissao = self.json_data['notas_fiscais'][index]['dataemissao']

            validation_result, validation_launch = self.sankhya.consulta_lancamento(self.token_sankhya,
                                                                                    self.cnpj_fornecedor,
                                                                                    self.numero_nota,
                                                                                    self.data_emissao)
            if validation_result and validation_launch != 0:
                self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Fatura já lançada'
                self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Humano'
                self.logger.info(f"Chamado {self.call} - nota {self.numero_nota} já consta lançado no sistema")
                send_email("FATURA JÁ LANÇADA", 
                           f"Chamado {self.call} - nota {self.numero_nota} já consta lançado no sistema")
                continue
            elif not validation_result:
                self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro na consulta de lançamento'
                self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Robô'
                self.logger.error(f"Chamado {self.call} - erro ao consultar lançamento no Sankhya")
                send_email("ERRO AO CONSULTAR FATURA", 
                           f"Chamado {self.call}, erro ao consultar lançamento no Sankhya")
                continue
            self.logger.info(f"Chamado {self.call} - nota {self.numero_nota} não lançado no sistema, pode seguir com o lançamento")
            
            result_emp, codemp = check_codemp(self.cnpj_raiz)
            if not result_emp:
                self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'CNPJ Raiz não encontrado'
                self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Robô'
                self.logger.info(f"Chamado {self.call} - CNPJ {self.cnpj_raiz} não encontrado no de-para de empresas")
                continue
            self.codigo_empresa = codemp
            self.logger.info(f"CNPJ {self.cnpj_raiz} encontrado no de-para, código {self.codigo_empresa} utilizado para a nota {self.numero_nota}")

            result_par, codparc, codtipoper = self.sankhya.consulta_codparc_codtipoper(self.token_sankhya, self.cnpj_fornecedor)
            if not result_par:
                self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'CNPJ Fornecedor não encontrado'
                self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Robô'
                self.logger.info(f"Chamado {self.call} - CNPJ {self.cnpj_fornecedor} não encontrado no sankhya")
                continue
            self.codigo_parceiro = codparc
            self.logger.info(f"CNPJ {self.cnpj_fornecedor} encontrado no Sankhya, código {self.codigo_parceiro} utilizado para a nota {self.numero_nota}")

            self.launch_nota_fical()

        self.status_execution = self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'].values[0]

        if self.status_execution == 'OK':
            self.launch_financial_document()
            return True

        return False

    def launch_nota_fical(self):
        result_launch, nunota = self.sankhya.lanca_titulo(token=self.token_sankhya,
                                                          chamado=self.call,
                                                          numero_nota=self.numero_nota,
                                                          serie=self.serie,
                                                          codigo_empresa=self.codigo_empresa,
                                                          codigo_parceiro=self.codigo_parceiro,
                                                          centro_custo=self.centro_custo,
                                                          codigo_natureza=self.codigo_natureza,
                                                          data_negociacao=self.data_emissao,
                                                          data_vencimento=self.data_vencimento,
                                                          descricao=self.descricao,
                                                          codigo_operacao=147,
                                                          codigo_venda=2)
        
        if not result_launch:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro no lançamento'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Robô'
            self.logger.error(f"Erro no lançamento para o chamado {self.call} - nota {self.numero_nota} com o erro {nunota}")
            send_email("ERRO NO LANÇAMENTO", 
                       f"Chamado {self.call} - nota {self.numero_nota} apresentou o erro {nunota}")
            return
        self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'NUNOTA'] = int(nunota)
        self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'Lançado'] = 'Sim'
        self.logger.info(f"Lançamento para o chamado {self.call} - nota {self.numero_nota} realizado com sucesso com o nunota {nunota}")

        return_inclusion_item, nunota_inclusion_item = self.sankhya.inclui_item(token=self.token_sankhya,
                                                                                nunota=nunota,
                                                                                produto=18325,
                                                                                valor_total=conversation_values(self.valor_nf))
        
        if not return_inclusion_item:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro na inclusão do item'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Sankhya'
            self.logger.error(f"Erro na inclusão do item para o chamado {self.call} - nota {self.numero_nota} com o erro {nunota_inclusion_item}")
            send_email("ERRO NA INCLUSÃO DE ITEM", 
                       f"Chamado {self.call} - nota {self.numero_nota} apresentou o erro {nunota_inclusion_item}")
            return
        self.logger.info(f"Inclusão do item para o chamado {self.call} - nota {self.numero_nota} realizado com sucesso")

        retorn_nufin, nufin = self.sankhya.consulta_nufin(self.token_sankhya, nunota)
        nufin = str(nufin[0])
        if not retorn_nufin:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro na consulta do NUFIN'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Sankhya'
            self.logger.error(f"Erro na consulta do nufin para o {self.call} - nota {self.numero_nota}")
            send_email("ERRO NA CONSULTA DE NUFIN", 
                       f"Chamado {self.call} - nota {self.numero_nota} apresentou o erro {retorn_nufin}")
            return
                                                 
        if len(nufin) == 0:
            if self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'FormaPagamento'] == '29':
                pass
            else:
                self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'NUFIN não encontrado'
                self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Sankhya'
                self.logger.info(f"NUFIN não encontrado para o chamado {self.call} - nota {self.numero_nota}")
                send_email("ERRO NUFIN", 
                           f"Chamado {self.call} - nota {self.numero_nota} apresentou o erro {nunota_inclusion_item}")
                return
        self.logger.info(f"NUFIN consultado com sucesso para o chamado {self.call} - nota {self.numero_nota} com o nufin {nufin}")

        retorno_alter_fin, alter_fin = self.sankhya.altera_financeiro(token=self.token_sankhya,
                                                                      nufin=nufin,
                                                                      valor=conversation_values(self.valor_nf),
                                                                      codtiptit=13,
                                                                      vencimento=self.data_vencimento,
                                                                      descricao=self.descricao[:255])
                                                        
        if not retorno_alter_fin:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro ao alterar financeiro'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Sankhya'
            self.logger.error(f"Erro ao alterar financeiro para o chamado {self.call} - nota {self.numero_nota} com o erro {alter_fin}")
            send_email("ERRO AO ALTERAR FINANCEIRO", 
                       f"Chamado {self.call} - nota {self.numero_nota} apresentou o erro {alter_fin}")
            return
        self.logger.info(f"Financeiro alterado com sucesso para o chamado {self.call} - nota {self.numero_nota} com o nufin {nufin}")                                    
                                                        
        retorn_confirm_nota, confirm_nota = self.sankhya.confirma_nota(self.token_sankhya, nunota)
        if not retorn_confirm_nota:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro ao confirmar nota'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Sankhya'
            self.logger.error(f"Erro ao confirmar nota para o chamado {self.call} - nota {self.numero_nota} erro {confirm_nota}")
            send_email("ERRO AO CONFIRMAR NOTA", 
                       f"Chamado {self.call} - nota {self.numero_nota} apresentou erro ao confirmar nota {confirm_nota}")
            return
        self.logger.info(f"Nota confirmada para o chamado {self.call} - nota {self.numero_nota} com o nunota {nunota}")
        
        retorno_consulta_nufin, nufin = self.sankhya.consulta_nufin(self.token_sankhya, nunota)
        nufin = str(nufin[0])
        if not retorno_consulta_nufin:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro ao consultar nufin após confirmação da nota'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Sankhya'
            self.logger.error(f"Erro ao consultar nufin para o chamado {self.call} - nota {self.numero_nota}")
            send_email("ERRO NA CONSULTA DE NUFIN", 
                       f"Chamado {self.call} - nota {self.numero_nota} apresentou erro na consulta de nufin")
            return
        self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'NUFIN'] = nufin
        self.logger.info(f"Consulta do novo nufin para o chamado {self.call} - nota {self.numero_nota} feita com sucesso")

        self.anexa_arquivos_chamado()

        qtd_caracteres_codigo_barra = len(self.codigo_barras)
        if not qtd_caracteres_codigo_barra >= 43 and not qtd_caracteres_codigo_barra <= 50:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] =  'Código de barras fora do padrão'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = '-'
            self.logger.error(f"Chamado {self.call} - Código de barras fora do padrão")
            send_email("CÓDIGO DE BARRAS FORA DO PADRÃO", 
                       f"Chamado {self.call} - nota {self.numero_nota} apresentou código de barras fora do padrão")
            return

        retorn_alter_bol, alter_bol = self.sankhya.altera_financeiro(token=self.token_sankhya,
                                                                     nufin=nufin,
                                                                     codtiptit=13,
                                                                     vencimento=self.data_vencimento,
                                                                     descricao=self.descricao[:255],
                                                                     codbarra=self.codigo_barras,
                                                                     valor=conversation_values(self.valor_nf))
        
        if not retorn_alter_bol:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] =  'Erro ao alterar boleto'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = '-'
            self.logger.error(f"Erro ao alterar boleto {nufin} com o erro {alter_bol}")
            send_email("ERRO AO ALTERAR BOLETO", 
                       f"Chamado {self.call} - nota {self.numero_nota} com o erro {alter_bol}")
            return
        self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] =  'OK'
        self.logger.info(f"Boleto alterado com sucesso para o chamado {self.call} - nota {self.numero_nota}")

    def launch_financial_document(self):
        result_launch, nunota = self.sankhya.lanca_titulo(token=self.token_sankhya,
                                                          chamado=self.call,
                                                          numero_nota=self.call,
                                                          serie="U",
                                                          codigo_empresa=self.codigo_empresa,
                                                          codigo_parceiro=self.codigo_parceiro,
                                                          centro_custo=self.centro_custo,
                                                          codigo_natureza=self.codigo_natureza,
                                                          data_negociacao=self.data_emissao,
                                                          data_vencimento=self.data_vencimento,
                                                          descricao=self.descricao,
                                                          codigo_operacao=111,
                                                          codigo_venda=2)
        
        if not result_launch:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro no lançamento'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Robô'
            self.logger.error(f"Erro no lançamento do documento financeiro para o chamado {self.call} com o erro {nunota}")
            send_email("ERRO NO LANÇAMENTO DO DOCUMENTO FINANCEIRO", 
                       f"Chamado {self.call} apresentou o erro {nunota} ao lançar o documento financeiro")
            return
        self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'NUNOTA'] = int(nunota)
        self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'Lançado'] = 'Sim'
        self.logger.info(f"Lançamento do documento financeiro para o chamado {self.call} realizado com sucesso com o nunota {nunota}")

        return_inclusion_item, nunota_inclusion_item = self.sankhya.inclui_item(token=self.token_sankhya,
                                                                                nunota=nunota,
                                                                                produto=18325,
                                                                                valor_total=conversation_values(self.valor_df))
        
        if not return_inclusion_item:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro na inclusão do item'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Sankhya'
            self.logger.error(f"Erro na inclusão do item do documento financeiro para o chamado {self.call} com o erro {nunota_inclusion_item}")
            send_email("ERRO NA INCLUSÃO DE ITEM DO DOCUMENTO FINANCEIRO", 
                       f"Chamado {self.call} apresentou o erro {nunota_inclusion_item} ao incluir o item do documento financeiro")
            return
        self.logger.info(f"Inclusão do item do documento financeiro para o chamado {self.call} realizado com sucesso")

        retorn_nufin, nufin = self.sankhya.consulta_nufin(self.token_sankhya, nunota)
        nufin = str(nufin[0])
        if not retorn_nufin:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro na consulta do NUFIN'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Sankhya'
            self.logger.error(f"Erro na consulta do nufin do documento financeiro para o {self.call}")
            send_email("ERRO NA CONSULTA DE NUFIN DO DOCUMENTO FINANCEIRO", 
                       f"Chamado {self.call} apresentou o erro {nunota_inclusion_item} ao consultar o nufin do documento financeiro")
            return
                                                        
        if len(nufin) == 0:
            if self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'FormaPagamento'] == '29':
                pass
            else:
                self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'NUFIN não encontrado'
                self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Sankhya'
                self.logger.info(f"NUFIN não encontrado para o chamado {self.call} - nota {self.numero_nota}")
                send_email("ERRO NUFIN DO DOCUMENTO FINANCEIRO", 
                           f"Chamado {self.call} apresentou o erro {nunota_inclusion_item} ao consultar o nufin do documento financeiro")
                return
        self.logger.info(f"NUFIN consultado com sucesso para o documento financeiro do chamado {self.call} com o nufin {nufin}")

        retorno_alter_fin, alter_fin = self.sankhya.altera_financeiro(token=self.token_sankhya,
                                                                      nufin=nufin,
                                                                      valor=conversation_values(self.valor_df),
                                                                      codtiptit=13,
                                                                      vencimento=self.data_vencimento,
                                                                      descricao=self.descricao[:255])
                                                        
        if not retorno_alter_fin:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro ao alterar financeiro'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Sankhya'
            self.logger.error(f"Erro ao alterar financeiro do documento financeiro para o chamado {self.call} com o erro {alter_fin}")
            send_email("ERRO AO ALTERAR FINANCEIRO DO DOCUMENTO FINANCEIRO", 
                       f"Chamado {self.call} apresentou o erro {alter_fin} ao alterar o financeiro do documento financeiro")
            return
        self.logger.info(f"Financeiro alterado com sucesso para o documento financeiro do chamado {self.call} com o nufin {nufin}")
                                                        
        retorn_confirm_nota, confirm_nota = self.sankhya.confirma_nota(self.token_sankhya, nunota)
        if not retorn_confirm_nota:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro ao confirmar nota'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Sankhya'
            self.logger.error(f"Erro ao confirmar documento financeiro para o chamado {self.call} erro {confirm_nota}")
            send_email("ERRO AO CONFIRMAR DOCUMENTO FINANCEIRO", 
                       f"Chamado {self.call} apresentou erro ao confirmar documento financeiro {confirm_nota}")
            return
        self.logger.info(f"Documento financeiro confirmado para o chamado {self.call} com o nunota {nunota}")                                                
        
        retorno_consulta_nufin, nufin = self.sankhya.consulta_nufin(self.token_sankhya, nunota)
        nufin = str(nufin[0])
        if not retorno_consulta_nufin:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro ao consultar nufin após confirmação da nota'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = 'Sankhya'
            self.logger.error(f"Erro ao consultar nufin para o chamado {self.call} - nota {self.numero_nota}")
            send_email("ERRO NA CONSULTA DE NUFIN", 
                       f"Chamado {self.call} no documento financeiro apresentou erro na consulta de nufin")
            return
        self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'NUFIN'] = nufin
        self.logger.info(f"Consulta do novo nufin para o documento financeiro do chamado {self.call} feita com sucesso")

        self.anexa_arquivos_chamado()

        if 'outros_lancamentos' in self.json_data:
            retorn_rateio, mensage = self.sankhya.rateio_nota(self.token_sankhya, nunota, self.json_data, self.centro_custo, self.codigo_natureza)
            if not retorn_rateio:
                self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] = 'Erro no Rateio'
                self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = '-'
                self.logger.error(f"Erro ao realizar o rateio {self.call} - {mensage}")
                send_email("ERRO NO RATEIO", 
                           f"Chamado {self.call} com erro no rateio {mensage}")
                return
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'Rateio'] = 'Sim'
            self.logger.info(f"Rateio realizado para o chamado {self.call}")

        qtd_caracteres_codigo_barra = len(self.codigo_barras)
        if not qtd_caracteres_codigo_barra >= 43 and not qtd_caracteres_codigo_barra <= 50:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] =  'Código de barras fora do padrão'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = '-'
            self.logger.error(f"Chamado {self.call} - Código de barras fora do padrão")
            send_email("CÓDIGO DE BARRAS FORA DO PADRÃO", 
                       f"Chamado {self.call} no documento financeiro apresentou código de barras fora do padrão")
            return

        retorn_alter_bol, alter_bol = self.sankhya.altera_financeiro(token=self.token_sankhya,
                                                                     nufin=nufin,
                                                                     codtiptit=13,
                                                                     vencimento=self.data_vencimento,
                                                                     descricao=self.descricao[:255],
                                                                     codbarra=self.codigo_barras,
                                                                     valor=conversation_values(self.valor_df))
        
        if not retorn_alter_bol:
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] =  'Erro ao alterar boleto'
            self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'TipoErro'] = '-'
            self.logger.error(f"Erro ao alterar boleto {nufin} com o erro {alter_bol}")
            send_email("ERROR AO ALTERAR BOLETO", 
                       f"Chamado {self.call} com o erro {alter_bol} para o documento financeiro")
            return
        self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'StatusExecucao'] =  'OK'
        self.logger.info(f"Boleto alterado com sucesso para o chamado {self.call} no documento financeiro")

    def anexa_arquivos_chamado(self):
        self.nunota = self.df_base_calls.loc[self.df_base_calls['Chamado'] == self.call, 'NUNOTA'].values[0]

        retorno, anexos_chamado = DatabaseIntegration().attachments_queue(self.call)
        if not retorno:
            self.logger.error(f"Erro ao consultar anexos para o chamado {self.call} - nota {self.numero_nota}")
            return
        
        for index_anexo, chamado_anexo in enumerate(anexos_chamado["Chamado"]):
            nome_arquivo = str(anexos_chamado["CaminhoServidorDireto"][index_anexo]).split("\\")[-1]

            anexa_arquivo = self.sankhya.anexa_arquivo_nunota(token=self.token_sankhya, 
                                                              nunota=self.nunota, 
                                                              nome_arquivo=nome_arquivo, 
                                                              caminho_arquivo=anexos_chamado["CaminhoServidorDireto"][index_anexo], 
                                                              descricao=anexos_chamado["TipoAnexo"][index_anexo])
            
            if not anexa_arquivo:
                self.logger.error(f"Erro ao anexar arquivo para o chamado {self.call} - nota {self.numero_nota}")
                continue
            
            if anexa_arquivo == True:
                self.logger.info(f"Arquivo anexado com sucesso para o chamado {self.call} - {anexos_chamado['NomeArquivo'][index_anexo]}")
            else:
                self.logger.info(anexa_arquivo)