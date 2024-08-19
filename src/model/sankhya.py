from core.validation import conversation_values

class SankhyaModel:

    def __init__(self):
        pass

    def headers(self, cookie=None):

        if cookie:
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Cookie': f'JSESSIONID={cookie}'
            }
        else: 
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json; charset=UTF-8'
            }
        return headers
    
    def params(self, servico, mgesession=None):
        
        if not mgesession:
            return {
                'serviceName': f'{servico}',
                'outputType': 'json'
            }
        else:
            return {
                'serviceName': f'{servico}',
                'outputType': 'json',
                'mgeSession': f'{mgesession}'
            }

    def json_auth(self, user, passw):
        json_data = {
            'serviceName': 'MobileLoginSP.login',
            'requestBody': {
                'NOMUSU': {
                    '$': f'{user}',
                },
                'INTERNO': {
                    '$': f'{passw}',
                },
                'KEEPCONNECTED': {
                    '$': 'S',
                },
            },
        }
        return json_data
    
    def json_consulta_codparc_codtipoper(self, cnpj):
        return {
            'serviceName': 'DbExplorerSP.executeQuery',
            'requestBody': {
                "sql": f"""SELECT TOP 1 c.CODPARC, 
                        c.CODTIPOPER, 
                        COUNT(codtipoper) AS CONTAGEM 
                FROM Siade.sankhya.TGFCAB C 
                JOIN Siade.sankhya.TGFPAR P ON C.CODPARC = P.CODPARC 
                WHERE P.CGC_CPF = '{cnpj}' 
                AND c.CODTIPOPER in (147, 111) 
                AND P.FORNECEDOR = 'S' 
                GROUP BY c.codparc, c.codtipoper 
                ORDER by COUNT(codtipoper) DESC"""
                }
            }
    
    def json_consulta_existencia_cnpj(self, cnpj):
        return {
                'serviceName': 'ParceiroSP.verificaExistenciaCpfInscEstRepetido',
                'requestBody': {
                    'param': {
                        'codParc': '',
                        'cgcCpf': f'{cnpj}'
                    },
                    'clientEventList': {
                        'clientEvent': [
                            {
                                '$': 'br.com.sankhya.mgecore.ie.repetida.transportadora'
                            },
                            {
                                '$': 'br.com.sankhya.actionbutton.clientconfirm'
                            }
                        ]
                    }
                }
            }
    
    def json_consulta_lancamento(self, cnpj, numnota, dtneg):
        return {
        'serviceName': 'DbExplorerSP.executeQuery',
        'requestBody': {
            'sql': f"""SELECT COUNT(1)
                    FROM SIADE.SANKHYA.TGFCAB C (NOLOCK)
                    JOIN SIADE.SANKHYA.TGFPAR P (NOLOCK) ON C.CODPARC=P.CODPARC
                    WHERE P.CGC_CPF = '{cnpj}' 
                    AND C.NUMNOTA = '{numnota}'
                    AND C.DTNEG = '{dtneg}'""",
        },
        }
    
    def json_rateio(self, nunota, json_data, centro_custo, codigo_natureza): 
        self.json_data = json_data
        self.centro_custo = centro_custo
        self.natureza = codigo_natureza

        lista_rateio = self.leitura_rateio()
    
        if isinstance(lista_rateio, list):
            json = {
        "serviceName": "CriteriosDeRateioSP.confirmarRateio",
        "requestBody": {
            "rateios": {
                "nuFin": f"{nunota}",
                "origem": "E",
                "rateio": lista_rateio
            },
            "clientEventList": {
                "clientEvent": [
                    {
                        "$": "br.com.sankhya.comercial.recalcula.pis.cofins"
                    },
                    {
                        "$": "br.com.sankhya.actionbutton.clientconfirm"
                    },
                    {
                        "$": "br.com.sankhya.aprovar.nota.apos.baixa"
                    },
                    {
                        "$": "br.com.sankhya.exibir.variacao.valor.item"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.compra.SolicitacaoComprador"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.valida.ChaveNFeCompraTerceiros"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.expedicao.SolicitarUsuarioConferente"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.nota.adicional.SolicitarUsuarioGerente"
                    },
                    {
                        "$": "br.com.sankhya.mgecomercial.event.cadastrarDistancia"
                    },
                    {
                        "$": "br.com.sankhya.mgecomercial.event.baixaPortal"
                    },
                    {
                        "$": "br.com.sankhya.mgecomercial.event.faturamento.confirmacao"
                    },
                    {
                        "$": "br.com.sankhya.mgecomercial.event.compensacao.credito.debito"
                    },
                    {
                        "$": "br.com.utiliza.dtneg.servidor"
                    },
                    {
                        "$": "br.com.sankhya.mgefin.solicitacao.liberacao.orcamento"
                    },
                    {
                        "$": "br.com.sankhya.exibe.msg.variacao.preco"
                    },
                    {
                        "$": "br.com.sankhya.importacaoxml.cfi.para.produto"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.parcelas.financeiro"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.cancelamento.notas.remessa"
                    },
                    {
                        "$": "br.com.sankhya.comercial.solicitaContingencia"
                    },
                    {
                        "$": "central.save.grade.itens.mostrar.popup.serie"
                    },
                    {
                        "$": "central.save.grade.itens.mostrar.popup.info.lote"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.central.itens.VendaCasada"
                    },
                    {
                        "$": "br.com.sankhya.exclusao.gradeProduto"
                    },
                    {
                        "$": "br.com.sankhya.mgecomercial.event.estoque.componentes"
                    },
                    {
                        "$": "br.com.sankhya.mgecomercial.event.estoque.insuficiente.produto"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.central.itens.KitRevenda"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.central.itens.KitRevenda.msgValidaFormula"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.imobilizado"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.item.multiplos.componentes.servico"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.coleta.entrega.recalculado"
                    },
                    {
                        "$": "br.com.sankhya.central.alteracao.moeda.cabecalho"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.event.troca.item.por.produto.substituto"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.event.troca.item.por.produto.alternativo"
                    },
                    {
                        "$": "br.com.sankhya.mgeprod.producao.terceiro.inclusao.item.nota"
                    }
                ]
            }
        }
        }
            return json
        else:
            return lista_rateio
        
    def leitura_rateio(self):
        try:
            lista_rateios = []

            if 'outros_lancamentos' in self.json_data:
                outros_lancamentos = self.json_data['outros_lancamentos']
                valor_outros = conversation_values(outros_lancamentos['valor'][0])
                porcentagem_outros = (valor_outros / conversation_values(self.json_data['documento_financeiro']['valor_total'][0])) * 100

                rateio_juros = {
                    "PERCRATEIO": {
                        "isAdicional": False,
                        "$": round(porcentagem_outros, 6)
                    },
                    "CODCENCUS": {
                        "isAdicional": False,
                        "$": self.centro_custo
                    },
                    "CODNAT": {
                        "isAdicional": False,
                        "$": 250205
                    },
                    "CODPROJ": {
                        "isAdicional": False,
                        "$": 101024
                    }
                }
                lista_rateios.append(rateio_juros)

            if 'documento_financeiro' in self.json_data:
                documento_financeiro = self.json_data['documento_financeiro']
                valor_cobrado = conversation_values(documento_financeiro['valor_cobrado'][0])
                porcentagem_cobrado = (valor_cobrado / conversation_values(self.json_data['documento_financeiro']['valor_total'][0])) * 100

                rateio_df = {
                    "PERCRATEIO": {
                        "isAdicional": False,
                        "$": round(porcentagem_cobrado, 6)
                    },
                    "CODCENCUS": {
                        "isAdicional": False,
                        "$": self.centro_custo
                    },
                    "CODNAT": {
                        "isAdicional": False,
                        "$": self.natureza
                    },
                    "CODPROJ": {
                        "isAdicional": False,
                        "$": 101024
                    }
                }
                lista_rateios.append(rateio_df)

            return lista_rateios

        except Exception as e:
            return f"Erro ao processar o JSON: {e}"
    
    def json_lancamento(self, **kwargs):
        return {
                    "serviceName": "CACSP.incluirAlterarCabecalhoNota",
                    "requestBody": {
                        "nota": {
                            "ownerServiceCall": "CentralNotas_CentralNotas_0",
                            "txProperties": {
                                "prop": [
                                    {
                                        "name": "br.com.sankhya.mgefin.checarfinanceiro.VlrEntrada",
                                        "value": 0
                                    },
                                    {
                                        "name": "br.com.sankhya.mgefin.recalculo.custopreco.Automatico",
                                        "value": 'false'
                                    },
                                    {
                                        "name": "cabecalhoNota.inserindo.pedidoWeb",
                                        "value": 'false'
                                    },
                                    {
                                        "name": "br.com.sankhya.mgefin.checarfinanceiro.RecalcularVencimento",
                                        "value": 'false'
                                    }
                                ]
                            },
                            "cabecalho": {
                                "NUNOTA": {
                                    "$": ""
                                },
                                "CODEMP": {
                                    "$": f"{kwargs['codigo_empresa']}"
                                },
                                "CODPARC": {
                                    "$": f"{kwargs['codigo_parceiro']}"
                                },
                                "CODCENCUS": {
                                    "$": f"{kwargs['centro_custo']}"
                                },
                                "CODNAT": {
                                    "$": f"{kwargs['codigo_natureza']}"
                                },
                                "CODPROJ": {
                                    "$": "101024"
                                },
                                "OBSERVACAO": {
                                    "$": f"{kwargs['descricao']}"
                                },
                                "TIPMOV": {
                                    "$": "C"
                                },
                                "CODTIPOPER": {
                                    "$": f"{kwargs['codigo_operacao']}"
                                },
                                "NUMNOTA": {
                                    "$": f"{kwargs['numero_nota']}"
                                },
                                "DTNEG": {
                                    "$": f"{kwargs['data_negociacao']}"
                                },
                                "DTFATUR": {
                                    "$": f"{kwargs['data_vencimento']}"
                                },
                                "CODTIPVENDA": {
                                    "$": f"{kwargs['codigo_venda']}"
                                },
                                "AD_NROSA": {
                                    "$": f"{kwargs['chamado']}"
                                },                        
                                "SERIENOTA": {
                                    "$": f"{kwargs['serie']}"
                                }
                            }
                        },
                        "clientEventList": {
                            "clientEvent": [
                                {
                                    "$": "br.com.sankhya.comercial.recalcula.pis.cofins"
                                },
                                {
                                    "$": "br.com.sankhya.actionbutton.clientconfirm"
                                },
                                {
                                    "$": "br.com.sankhya.aprovar.nota.apos.baixa"
                                },
                                {
                                    "$": "br.com.sankhya.exibir.variacao.valor.item"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.compra.SolicitacaoComprador"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.valida.ChaveNFeCompraTerceiros"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.expedicao.SolicitarUsuarioConferente"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.nota.adicional.SolicitarUsuarioGerente"
                                },
                                {
                                    "$": "br.com.sankhya.mgecomercial.event.cadastrarDistancia"
                                },
                                {
                                    "$": "br.com.sankhya.mgecomercial.event.baixaPortal"
                                },
                                {
                                    "$": "br.com.sankhya.mgecomercial.event.faturamento.confirmacao"
                                },
                                {
                                    "$": "br.com.sankhya.mgecomercial.event.compensacao.credito.debito"
                                },
                                {
                                    "$": "br.com.utiliza.dtneg.servidor"
                                },
                                {
                                    "$": "br.com.sankhya.mgefin.solicitacao.liberacao.orcamento"
                                },
                                {
                                    "$": "br.com.sankhya.exibe.msg.variacao.preco"
                                },
                                {
                                    "$": "br.com.sankhya.importacaoxml.cfi.para.produto"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.parcelas.financeiro"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.cancelamento.notas.remessa"
                                },
                                {
                                    "$": "br.com.sankhya.comercial.solicitaContingencia"
                                },
                                {
                                    "$": "central.save.grade.itens.mostrar.popup.serie"
                                },
                                {
                                    "$": "central.save.grade.itens.mostrar.popup.info.lote"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.central.itens.VendaCasada"
                                },
                                {
                                    "$": "br.com.sankhya.exclusao.gradeProduto"
                                },
                                {
                                    "$": "br.com.sankhya.mgecomercial.event.estoque.componentes"
                                },
                                {
                                    "$": "br.com.sankhya.mgecomercial.event.estoque.insuficiente.produto"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.central.itens.KitRevenda"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.central.itens.KitRevenda.msgValidaFormula"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.imobilizado"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.item.multiplos.componentes.servico"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.coleta.entrega.recalculado"
                                },
                                {
                                    "$": "br.com.sankhya.central.alteracao.moeda.cabecalho"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.event.troca.item.por.produto.substituto"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.event.troca.item.por.produto.alternativo"
                                },
                                {
                                    "$": "br.com.sankhya.mgeprod.producao.terceiro.inclusao.item.nota"
                                }
                            ]
                        }
                    }
                }
    
    def json_item(self, **kwargs):
        return {
        "serviceName": "CACSP.incluirAlterarItemNota",
        "requestBody": {
            "nota": {
                "NUNOTA": f"{kwargs['nunota']}",
                "txProperties": {
                    "prop": [
                        {
                            "name": "br.com.sankhya.mgefin.checarfinanceiro.VlrEntrada",
                            "value": 0
                        },
                        {
                            "name": "br.com.sankhya.mgefin.recalculo.custopreco.Automatico",
                            "value": "false"
                        },
                        {
                            "name": "br.com.sankhya.mgefin.mostrar.sugestao.venda",
                            "value": "true"
                        },
                        {
                            "name": "br.com.sankhya.mgecom.gradeItens.pedidoWeb",
                            "value": "false"
                        }
                    ]
                },
                "ownerServiceCall": "GradeItens_alu1rkwbj",
                "itens": {
                    "ATUALIZACAO_ONLINE": "true",
                    "item": {
                        "NUNOTA": {
                            "$": ""
                        },
                        "CODPROD": {
                            "$": f"{kwargs['produto']}"
                        },
                        "QTDNEG": {
                            "$": "1"
                        },
                        "VLRUNIT": {
                            "$": f"{kwargs['valor_total']}"
                        },
                        "VLRTOT": {
                            "$": f"{kwargs['valor_total']}"
                        },
                        "PERCDESC": {
                            "$": "0"
                        },
                        "VLRDESC": {
                            "$": "0"
                        },
                        "SEQUENCIA": {
                            "$": "1"
                        },
                        "CODVOL": {
                            "$": "UN"
                        }
                    }
                }
            },
            "clientEventList": {
                "clientEvent": [
                    {
                        "$": "br.com.sankhya.comercial.recalcula.pis.cofins"
                    },
                    {
                        "$": "br.com.sankhya.actionbutton.clientconfirm"
                    },
                    {
                        "$": "br.com.sankhya.aprovar.nota.apos.baixa"
                    },
                    {
                        "$": "br.com.sankhya.exibir.variacao.valor.item"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.compra.SolicitacaoComprador"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.valida.ChaveNFeCompraTerceiros"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.expedicao.SolicitarUsuarioConferente"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.nota.adicional.SolicitarUsuarioGerente"
                    },
                    {
                        "$": "br.com.sankhya.mgecomercial.event.cadastrarDistancia"
                    },
                    {
                        "$": "br.com.sankhya.mgecomercial.event.baixaPortal"
                    },
                    {
                        "$": "br.com.sankhya.mgecomercial.event.faturamento.confirmacao"
                    },
                    {
                        "$": "br.com.sankhya.mgecomercial.event.compensacao.credito.debito"
                    },
                    {
                        "$": "br.com.utiliza.dtneg.servidor"
                    },
                    {
                        "$": "br.com.sankhya.mgefin.solicitacao.liberacao.orcamento"
                    },
                    {
                        "$": "br.com.sankhya.exibe.msg.variacao.preco"
                    },
                    {
                        "$": "br.com.sankhya.importacaoxml.cfi.para.produto"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.parcelas.financeiro"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.cancelamento.notas.remessa"
                    },
                    {
                        "$": "br.com.sankhya.comercial.solicitaContingencia"
                    },
                    {
                        "$": "central.save.grade.itens.mostrar.popup.serie"
                    },
                    {
                        "$": "central.save.grade.itens.mostrar.popup.info.lote"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.central.itens.VendaCasada"
                    },
                    {
                        "$": "br.com.sankhya.exclusao.gradeProduto"
                    },
                    {
                        "$": "br.com.sankhya.mgecomercial.event.estoque.componentes"
                    },
                    {
                        "$": "br.com.sankhya.mgecomercial.event.estoque.insuficiente.produto"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.central.itens.KitRevenda"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.central.itens.KitRevenda.msgValidaFormula"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.imobilizado"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.item.multiplos.componentes.servico"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.coleta.entrega.recalculado"
                    },
                    {
                        "$": "br.com.sankhya.central.alteracao.moeda.cabecalho"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.event.troca.item.por.produto.substituto"
                    },
                    {
                        "$": "br.com.sankhya.mgecom.event.troca.item.por.produto.alternativo"
                    },
                    {
                        "$": "br.com.sankhya.mgeprod.producao.terceiro.inclusao.item.nota"
                    }
                ]
            }
        }
    }

    def json_altera_financeiro(self, **kwargs):
        if kwargs['codbarra'] is not None:
            return {
                        "serviceName": "CACSP.incluirAlterarFinanceiro",
                        "requestBody": {
                            "nota": {
                                "itens": {
                                    "item": {
                                        "NUFIN": {
                                            "$": f"{kwargs['nufin']}"
                                        },
                                        "DTVENC": {
                                                "$": f"{kwargs['dtvenc']}"
                                            },
                                            
                                            "VLRDESDOB": {
                                                "$": f"{kwargs['valor']}"
                                            },
                                            "HISTORICO": {
                                                "$": f"{kwargs['descricao']}"
                                            },
                                            "CODBARRA": {
                                                "$": f"{kwargs['codbarra']}"
                                            },
                                        "CODBCO": {
                                            "$": "33"
                                        },
                                        "CODCTABCOINT": {
                                            "$": "239"
                                        }
                                    }
                                }
                            },
                            "clientEventList": {
                                "clientEvent": [
                                    {
                                        "$": "br.com.sankhya.comercial.recalcula.pis.cofins"
                                    },
                                    {
                                        "$": "br.com.sankhya.actionbutton.clientconfirm"
                                    },
                                    {
                                        "$": "br.com.sankhya.aprovar.nota.apos.baixa"
                                    },
                                    {
                                        "$": "br.com.sankhya.exibir.variacao.valor.item"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.compra.SolicitacaoComprador"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.valida.ChaveNFeCompraTerceiros"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.expedicao.SolicitarUsuarioConferente"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.nota.adicional.SolicitarUsuarioGerente"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecomercial.event.cadastrarDistancia"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecomercial.event.baixaPortal"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecomercial.event.faturamento.confirmacao"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecomercial.event.compensacao.credito.debito"
                                    },
                                    {
                                        "$": "br.com.utiliza.dtneg.servidor"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgefin.solicitacao.liberacao.orcamento"
                                    },
                                    {
                                        "$": "br.com.sankhya.exibe.msg.variacao.preco"
                                    },
                                    {
                                        "$": "br.com.sankhya.importacaoxml.cfi.para.produto"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.parcelas.financeiro"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.cancelamento.notas.remessa"
                                    },
                                    {
                                        "$": "br.com.sankhya.comercial.solicitaContingencia"
                                    },
                                    {
                                        "$": "central.save.grade.itens.mostrar.popup.serie"
                                    },
                                    {
                                        "$": "central.save.grade.itens.mostrar.popup.info.lote"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.central.itens.VendaCasada"
                                    },
                                    {
                                        "$": "br.com.sankhya.exclusao.gradeProduto"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecomercial.event.estoque.componentes"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecomercial.event.estoque.insuficiente.produto"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.central.itens.KitRevenda"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.central.itens.KitRevenda.msgValidaFormula"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.imobilizado"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.item.multiplos.componentes.servico"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.coleta.entrega.recalculado"
                                    },
                                    {
                                        "$": "br.com.sankhya.central.alteracao.moeda.cabecalho"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.event.troca.item.por.produto.substituto"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.event.troca.item.por.produto.alternativo"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgeprod.producao.terceiro.inclusao.item.nota"
                                    }
                                ]
                            }
                        }
                    }
        else:
            return {
                        "serviceName": "CACSP.incluirAlterarFinanceiro",
                        "requestBody": {
                            "nota": {
                                "itens": {
                                    "item": {
                                        "NUFIN": {
                                            "$": f"{kwargs['nufin']}"
                                        },
                                        "CODTIPTIT": {
                                            "$": f"{kwargs['codtiptit']}"
                                        },
                                        "HISTORICO": {
                                            "$": f"{kwargs['descricao']}"
                                        },
                                        "DTVENC": {
                                            "$": f"{kwargs['dtvenc']}"
                                        },
                                        "CODBCO": {
                                            "$": "33"
                                        },
                                        "CODCTABCOINT": {
                                            "$": "239"
                                        }
                                    }
                                }
                            },
                            "clientEventList": {
                                "clientEvent": [
                                    {
                                        "$": "br.com.sankhya.comercial.recalcula.pis.cofins"
                                    },
                                    {
                                        "$": "br.com.sankhya.actionbutton.clientconfirm"
                                    },
                                    {
                                        "$": "br.com.sankhya.aprovar.nota.apos.baixa"
                                    },
                                    {
                                        "$": "br.com.sankhya.exibir.variacao.valor.item"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.compra.SolicitacaoComprador"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.valida.ChaveNFeCompraTerceiros"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.expedicao.SolicitarUsuarioConferente"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.nota.adicional.SolicitarUsuarioGerente"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecomercial.event.cadastrarDistancia"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecomercial.event.baixaPortal"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecomercial.event.faturamento.confirmacao"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecomercial.event.compensacao.credito.debito"
                                    },
                                    {
                                        "$": "br.com.utiliza.dtneg.servidor"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgefin.solicitacao.liberacao.orcamento"
                                    },
                                    {
                                        "$": "br.com.sankhya.exibe.msg.variacao.preco"
                                    },
                                    {
                                        "$": "br.com.sankhya.importacaoxml.cfi.para.produto"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.parcelas.financeiro"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.cancelamento.notas.remessa"
                                    },
                                    {
                                        "$": "br.com.sankhya.comercial.solicitaContingencia"
                                    },
                                    {
                                        "$": "central.save.grade.itens.mostrar.popup.serie"
                                    },
                                    {
                                        "$": "central.save.grade.itens.mostrar.popup.info.lote"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.central.itens.VendaCasada"
                                    },
                                    {
                                        "$": "br.com.sankhya.exclusao.gradeProduto"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecomercial.event.estoque.componentes"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecomercial.event.estoque.insuficiente.produto"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.central.itens.KitRevenda"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.central.itens.KitRevenda.msgValidaFormula"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.imobilizado"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.item.multiplos.componentes.servico"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.coleta.entrega.recalculado"
                                    },
                                    {
                                        "$": "br.com.sankhya.central.alteracao.moeda.cabecalho"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.event.troca.item.por.produto.substituto"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgecom.event.troca.item.por.produto.alternativo"
                                    },
                                    {
                                        "$": "br.com.sankhya.mgeprod.producao.terceiro.inclusao.item.nota"
                                    }
                                ]
                            }
                        }
                    }
    
    def json_confirma_nota(self, nunota):
        return {
                    "serviceName": "CACSP.confirmarNota",
                    "requestBody": {
                        "nota": {
                            "confirmacaoCentralNota": "true",
                            "ehPedidoWeb": "false",
                            "atualizaPrecoItemPedCompra": "false",
                            "ownerServiceCall": "CentralNotas_CentralNotas_0",
                            "NUNOTA": {
                                "$": f"{nunota}"
                            }
                        },
                        "clientEventList": {
                            "clientEvent": [
                                {
                                    "$": "br.com.sankhya.comercial.recalcula.pis.cofins"
                                },
                                {
                                    "$": "br.com.sankhya.actionbutton.clientconfirm"
                                },
                                {
                                    "$": "br.com.sankhya.aprovar.nota.apos.baixa"
                                },
                                {
                                    "$": "br.com.sankhya.exibir.variacao.valor.item"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.compra.SolicitacaoComprador"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.valida.ChaveNFeCompraTerceiros"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.expedicao.SolicitarUsuarioConferente"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.nota.adicional.SolicitarUsuarioGerente"
                                },
                                {
                                    "$": "br.com.sankhya.mgecomercial.event.cadastrarDistancia"
                                },
                                {
                                    "$": "br.com.sankhya.mgecomercial.event.baixaPortal"
                                },
                                {
                                    "$": "br.com.sankhya.mgecomercial.event.faturamento.confirmacao"
                                },
                                {
                                    "$": "br.com.sankhya.mgecomercial.event.compensacao.credito.debito"
                                },
                                {
                                    "$": "br.com.utiliza.dtneg.servidor"
                                },
                                {
                                    "$": "br.com.sankhya.mgefin.solicitacao.liberacao.orcamento"
                                },
                                {
                                    "$": "br.com.sankhya.exibe.msg.variacao.preco"
                                },
                                {
                                    "$": "br.com.sankhya.importacaoxml.cfi.para.produto"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.parcelas.financeiro"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.cancelamento.notas.remessa"
                                },
                                {
                                    "$": "br.com.sankhya.comercial.solicitaContingencia"
                                },
                                {
                                    "$": "central.save.grade.itens.mostrar.popup.serie"
                                },
                                {
                                    "$": "central.save.grade.itens.mostrar.popup.info.lote"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.central.itens.VendaCasada"
                                },
                                {
                                    "$": "br.com.sankhya.exclusao.gradeProduto"
                                },
                                {
                                    "$": "br.com.sankhya.mgecomercial.event.estoque.componentes"
                                },
                                {
                                    "$": "br.com.sankhya.mgecomercial.event.estoque.insuficiente.produto"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.central.itens.KitRevenda"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.central.itens.KitRevenda.msgValidaFormula"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.imobilizado"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.item.multiplos.componentes.servico"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.coleta.entrega.recalculado"
                                },
                                {
                                    "$": "br.com.sankhya.central.alteracao.moeda.cabecalho"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.event.troca.item.por.produto.substituto"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.event.troca.item.por.produto.alternativo"
                                },
                                {
                                    "$": "br.com.sankhya.mgeprod.producao.terceiro.inclusao.item.nota"
                                },
                                {
                                    "$": "br.com.sankhya.mgecom.calculo.inss.especial.tgfimn"
                                }
                            ]
                        }
                    }
                }
    
    def json_consulta_nufin(self, nunota):
        return {
            'serviceName': 'DbExplorerSP.executeQuery',
            'requestBody': {
                'sql': f'SELECT NUFIN FROM TGFFIN (NOLOCK) WHERE NUNOTA = {nunota}',
            },
        }