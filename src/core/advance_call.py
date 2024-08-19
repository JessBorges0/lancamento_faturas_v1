import time
from controller.cervello import ApiCervelloController

cervello = ApiCervelloController()

def logic_advance_call(logger, df_base_chamados):
    for indexChamado, chamado in enumerate(df_base_chamados["Chamado"]):
        if df_base_chamados.loc[indexChamado, "StatusExecucao"] != "OK":
            continue
        retorno_captura_chamado, captura_chamado = cervello.call_capture(chamado)
        if not retorno_captura_chamado:
            df_base_chamados.loc[indexChamado, "StatusExecucao"] == "Erro ao Capturar Chamado"
            df_base_chamados.loc[indexChamado, "TipoErro"] == "Cervello"
            logger.warning(f"Erro ao capturar chamado {chamado} - Erro {captura_chamado}")
            continue

    time.sleep(40)

    for indexChamado, chamado in enumerate(df_base_chamados["Chamado"]):
        if df_base_chamados.loc[indexChamado, "StatusExecucao"] != "OK":
            continue
        retorno_avanca_chamado, avanca_chamado = cervello.advance_call(chamado, df_base_chamados.loc[indexChamado, "NUNOTA"])
        if not retorno_avanca_chamado:
            df_base_chamados.loc[indexChamado, "StatusExecucao"] == "Erro ao Avançar Chamado"
            df_base_chamados.loc[indexChamado, "TipoErro"] == "Cervello"
            logger.warning(f"Erro ao avançar chamado {chamado} - Erro {avanca_chamado}")
            continue

    return df_base_chamados