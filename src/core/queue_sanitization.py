import re
from datetime import datetime, timedelta
from core.file_manager import FileManager
from controller.email import send_email
from sql.db_integration import DatabaseIntegration

class QueueSanitization:

    def __init__(self, logger):
        self.logger = logger
        self.db_integration = DatabaseIntegration()
        self.file_manager = FileManager(logger=logger)
        self.tomorrow = datetime.today() + timedelta(days=1)

    def base_calls_queue(self):
        result, executed_calls = self.file_manager.result_calls_executed()
        if not result:
            self.logger.error("Erro na consulta de chamados executados.")

        result, self.df_call_queue = self.db_integration.calls_queue(executed_calls)
        if result and self.df_call_queue is not None:      
            size = len(self.df_call_queue['Chamado'])
            self.logger.info(f"Consulta de chamados realizada com sucesso, {size} registros.")
            self.df_call_queue['StatusExecucao'] = '-'
            self.df_call_queue['TipoErro'] = '-'
            self.df_call_queue['CodigoBarras'] = '-'
            self.df_call_queue['ModeloFatura'] = '-'
            self.df_call_queue['QuantidadeNF'] = '-'
            self.df_call_queue['ValorFatura'] = '-'
            self.df_call_queue['Lançado'] = '-'
            self.df_call_queue['Rateio'] = '-'
            self.df_call_queue['NUFIN'] = '-'
            self.df_call_queue['NUNOTA'] = '-'
            self.processes_calls()

            result = self.file_manager.save_calls_executed(map(str, self.df_call_queue['Chamado']))
            if not result:
                self.logger.error("Erro ao salvar chamados executados.")

            return True, self.df_call_queue
        
        elif result and self.df_call_queue is None:
            self.logger.info("Não há chamados para processar.")
            return False, None

        else:
            self.logger.error("Erro na consulta de chamados.")
            return False, False

    def processes_calls(self):
        
        for self.call in self.df_call_queue["Chamado"].tolist():
     
            natureza_matches = re.findall(r"(.*)\((\d+)\)", self.df_call_queue.loc[self.df_call_queue['Chamado'] == self.call, 'Natureza'].values[0])
            centrocusto_matches = re.findall(r"(.*)\((\d+)\)", self.df_call_queue.loc[self.df_call_queue['Chamado'] == self.call, 'CentroCusto'].values[0])

            self.df_call_queue.loc[self.df_call_queue['Chamado'] == self.call, 'Natureza'] = natureza_matches[0][-1]
            self.df_call_queue.loc[self.df_call_queue['Chamado'] == self.call, 'CentroCusto'] = centrocusto_matches[0][-1]

            vencimento_cervello = str(self.df_call_queue.loc[self.df_call_queue['Chamado'] == self.call, 'VencimentoCervello'].values[0])
            vencimento_data = datetime.strptime(vencimento_cervello, "%d/%m/%Y")
            
            if vencimento_data >= self.tomorrow:
                self.df_call_queue.loc[self.df_call_queue['Chamado'] == self.call, 'StatusExecucao'] = 'OK'
            else:
                self.df_call_queue.loc[self.df_call_queue['Chamado'] == self.call, 'StatusExecucao'] = 'Vencimento próximo'
                send_email(assunto="Fatura Ignorada",
                            mensagem=f"O Chamado {self.call} está com data de vencimento na criação em {vencimento_data}.")
                self.logger.info(f"{self.call} - data de vencimento do chamado menor que o permitido")