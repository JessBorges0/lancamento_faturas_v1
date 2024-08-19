import sys
from core.advance_call import logic_advance_call
from controller.email import send_email, criar_relatorio_sintetico
from controller.logger import Logger
from core.file_manager import FileManager
from core.launch_logic import LaunchLogic
from controller.sankhya import SankhyaController
from sql.db_integration import DatabaseIntegration
from core.queue_sanitization import QueueSanitization

def main(logger):
    logger.info(f"Execution started")
    
    sankhya = SankhyaController()
    file_manager = FileManager(logger=logger)
    launch_logic = LaunchLogic(logger=logger)
    database_integration = DatabaseIntegration()
    queue_sanitization = QueueSanitization(logger=logger)

    result_sanitization, df_base_calls = queue_sanitization.base_calls_queue()
    if not result_sanitization:
        if df_base_calls is None:
            logger.info("Sem chamados para execução")
            send_email("AUTOMAÇÃO LANÇAMENTO DE FATURAS",
                       "Sem chamados para execução na fila da Cervello")
            return None, None
        elif df_base_calls is False:
            logger.info("Erro na consulta de chamados na fila da Cervello")
            send_email("AUTOMAÇÃO LANÇAMENTO DE FATURAS",
                       "Erro na consulta de chamados na fila da Cervello")
            return False, None
        return True, df_base_calls

    executed_calls = file_manager.result_str_calls_sql(df_base_calls["Chamado"].tolist())

    result_query_attachments, df_attachments_calls = database_integration.attachments_queue(executed_calls)
    if not result_query_attachments:
        logger.error("Erro na consulta de anexos na fila da Cervello")
        send_email("AUTOMAÇÃO LANÇAMENTO DE FATURAS",
                   "Erro na consulta de anexos na fila da Cervello")
        return False, None
    logger.info(f"Consulta de anexos realizada com sucesso")
    
    result_token, token_sankhya = sankhya.token_sankhya()
    if not result_token:
        logger.error("Erro ao autenticar no Sankhya")
        return False, None
    logger.info("Token Sankhya obtido com sucesso")

    for index_call, call in enumerate(df_attachments_calls["Chamado"]):
        launch_logic.process_call(token_sankhya, call, index_call, df_base_calls, df_attachments_calls)
    
    df_base_calls = logic_advance_call(logger, df_base_calls)
    logger.info("Chamados verificados para sequenciar com sucesso")

    return True, df_base_calls

if __name__ == "__main__":
    logger = Logger("log_main")

    retorno, df_base_calls = main(logger)
    if retorno is None:
        logger.info("Não há chamados para executar")
        sys.exit(2)
    elif not retorno:
        logger.error("Erro ao executar main")
        sys.exit(0)

    df_base_calls.to_excel("src\\data\\df_base_chamados.xlsx", index=False)
    df_base_chamados_email = df_base_calls.loc[:,['Chamado','Solicitante','TipoNota','StatusExecucao','TipoErro','Lançado','Rateio','NUFIN','NUNOTA','ValorFatura','ModeloFatura','QuantidadeNF','FormaPagamento','Natureza','CentroCusto']]
        
    df_base_chamados_email_corpo = df_base_chamados_email[df_base_chamados_email['Lançado'] == 'Sim']
    relatorio_sintetico = criar_relatorio_sintetico(df_base_calls)

    retorno_envio_email, envio_email = send_email("Relatório de Execução Faturas", 
                                                  "Segue resumo", 
                                                  anexo=df_base_chamados_email, 
                                                  df_notas=df_base_chamados_email_corpo, 
                                                  relatorio=relatorio_sintetico)
    logger.info(f"Execution finished")
    sys.exit(1)