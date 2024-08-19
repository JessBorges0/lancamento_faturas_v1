class QueryCervello:
    
    def __init__(self):
        pass

    def queue_calls_query(self, executed_calls):
        return f"""
            WITH CTE AS (
                SELECT 
                    E.set_CodigoSolicitacao, 
                    C.sec_ValorTexto, 
                    C.sec_CodigoCampo, 
                    F.foc_Descricao
                FROM cervello.dbo.SolicitacaoEtapaCampos C (NOLOCK)
                JOIN cervello.dbo.SolicitacaoEtapa E (NOLOCK) ON C.sec_CodigoSolicitacaoEtapa = E.set_Codigo
                JOIN cervello.dbo.FormularioCampos F (NOLOCK) ON C.sec_CodigoCampo = F.foc_Codigo
                WHERE 
                    F.foc_Descricao = 'Natureza' OR
                    F.foc_Descricao = 'Centro de Custo' OR
                    F.foc_Descricao = 'Forma de Pagamento' OR
                    F.foc_Descricao = 'Descrição' OR 
                    F.foc_Descricao = 'Quantidade de Parcelas' OR
                    F.foc_Descricao = 'Agência' OR
                    F.foc_Descricao = 'Código do Banco' OR
                    F.foc_Descricao = 'Tipo de Nota' OR
                    F.foc_Descricao = 'CNPJ do Fornecedor' OR
                    F.foc_Descricao = 'CNPJ' OR
                    F.foc_Descricao = 'Data do Vencimento' OR
                    F.foc_Descricao = 'Tipo de Nota' OR
                    F.foc_Descricao = 'Conta' OR
                    F.foc_Descricao = 'Tipo de Conta' OR
                    F.foc_Descricao = 'Possui Rateio?' OR
                    F.foc_Descricao = 'Data de Pagamento'
            )
            SELECT * FROM (
                SELECT 
                    s.sol_Codigo AS 'Chamado',
                    f.flu_Descricao AS 'Categoria',
                    u.usu_Nome AS 'Solicitante',
                    MAX(CASE WHEN C.foc_Descricao = 'Natureza' THEN C.sec_ValorTexto END) AS 'Natureza',
                    MAX(CASE WHEN C.foc_Descricao = 'Centro de Custo' THEN C.sec_ValorTexto END) AS 'CentroCusto',
                    CASE 
                        WHEN MAX(CASE WHEN C.foc_Descricao = 'Forma de Pagamento' THEN C.sec_ValorTexto END) = 'Depósito Bancário' THEN '12'
                        WHEN MAX(CASE WHEN C.foc_Descricao = 'Forma de Pagamento' THEN C.sec_ValorTexto END) = 'Boleto' THEN '3'
                        WHEN MAX(CASE WHEN C.foc_Descricao = 'Forma de Pagamento' THEN C.sec_ValorTexto END) = 'Apenas Lançamento da NF' THEN '29'
                        ELSE '0' 
                    END AS 'FormaPagamento',
                    ISNULL(CASE WHEN MAX(CASE WHEN C.foc_Descricao = 'Quantidade de Parcelas' THEN C.sec_ValorTexto END) = '' THEN 1 
                            ELSE MAX(CASE WHEN C.foc_Descricao = 'Quantidade de Parcelas' THEN C.sec_ValorTexto END) END,1) 
                    AS 'Parcelas',
                    CASE 
                        WHEN F.flu_Descricao = 'Lançamento de Nota' THEN MAX(CASE WHEN C.foc_Descricao = 'Tipo de Nota' THEN C.sec_ValorTexto END) 
                        ELSE 'Nota de Serviço' 
                    END AS 'TipoNota',
                    CASE 
                        WHEN F.flu_Descricao = 'Lançamento de Nota' THEN MAX(CASE WHEN C.foc_Descricao = 'Data do Vencimento' THEN C.sec_ValorTexto END) 
                        ELSE MAX(CASE WHEN C.foc_Descricao = 'Data de Pagamento' THEN C.sec_ValorTexto END) 
                    END AS 'VencimentoCervello',
                    ISNULL(REPLACE(RTRIM(LTRIM(MAX(CASE WHEN C.foc_Descricao = 'Agência' THEN C.sec_ValorTexto END))), '-', ''), '') AS 'Agencia',
                    ISNULL(REPLACE(RTRIM(LTRIM(MAX(CASE WHEN C.foc_Descricao = 'Conta' THEN C.sec_ValorTexto END))), '-', ''), '') AS 'Conta',
                    ISNULL(LEFT(RTRIM(LTRIM(MAX(CASE WHEN C.foc_Descricao = 'Código do Banco' THEN C.sec_ValorTexto END))), 3), '') AS 'CodBanco',
                    ISNULL(MAX(CASE WHEN C.foc_Descricao = 'Tipo de Conta' THEN C.sec_ValorTexto END), '') AS 'TipoConta',
                    REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(MAX(CASE WHEN C.foc_Descricao = 'CNPJ do Fornecedor' THEN C.sec_ValorTexto END))),'.',''),'/',''),'-','') AS 'CNPJFornecedorCervello',
                    (CASE WHEN (MAX(CASE WHEN C.foc_Descricao = 'Forma de Pagamento' THEN C.sec_ValorTexto END)) = 'Boleto' THEN 2 ELSE 1 END) AS 'Anexos',		
                    CONCAT(MAX(CASE WHEN C.foc_Descricao = 'Descrição' THEN C.sec_ValorTexto END), ' - CHAMADO: ', s.sol_Codigo) AS 'Descricao',
                    ISNULL(CASE WHEN MAX(CASE WHEN C.foc_Descricao = 'Possui Rateio?' THEN C.sec_ValorTexto END) = '' THEN 'Não'  
                        ELSE MAX(CASE WHEN C.foc_Descricao = 'Possui Rateio?' THEN C.sec_ValorTexto END) END,'Não') AS 'Rateio'
                FROM cervello.dbo.Solicitacao S (NOLOCK)
                JOIN cervello.dbo.Fluxo F (NOLOCK) ON S.sol_CodigoFluxo = F.flu_Codigo AND F.flu_Descricao IN ('Lançamento de Nota') 
                JOIN cervello.dbo.SolicitacaoEtapa E (NOLOCK) ON S.sol_CodigoEtapaAtual = E.set_Codigo
                JOIN Cervello.dbo.Etapas ET (NOLOCK) ON E.set_CodigoEtapa = ET.eta_Codigo AND ET.eta_Descricao IN ('Capturar Solicitação')
                LEFT JOIN CTE C ON E.set_CodigoSolicitacao = C.set_CodigoSolicitacao
                JOIN Cervello.dbo.Usuario U (NOLOCK) ON U.usu_Codigo = S.sol_CodigoUsuarioSolicitante
                WHERE 
                    S.sol_Codigo NOT IN ({executed_calls}) AND 
                    S.sol_DataInclusao >= '2023-11-23'
                GROUP BY 
                    S.sol_Codigo, 
                    U.usu_nome, 
                    S.sol_DataInclusao, 
                    F.flu_Descricao) T
            WHERE 
                T.FormaPagamento IN ('12','3','29') AND 
                T.TipoNota IN ('Fatura') AND Parcelas = 1
            """

    def queue_attachments_query(self, calls):
            return f"""
                DECLARE @CAMPOFT VARCHAR(MAX);

                SET @CAMPOFT = 'Anexar Documento Fiscal';

                WITH Anexos
                AS
                (SELECT
                    pro_descricao AS Fluxo
                ,sca_codigosolicitacao AS Solicitacao
                ,'Formulario_Inicial' AS Etapa
                ,sca_ValorTexto AS Nome_Arquivo_Formulario
                ,sca_Codigo AS CodigoLinha
                ,foc_descricao AS TipoAnexo
                ,sca_Folder AS Pasta_Servidor
                ,'form_produto_' + CONVERT(VARCHAR, sca_codigo) AS Nome_Arquivo_Servidor
                FROM Cervello.dbo.SolicitacaoCampos(nolock)
                INNER JOIN Cervello.dbo.FormularioCampos(nolock) ON foc_codigo = sca_codigocampo
                INNER JOIN Cervello.dbo.Solicitacao(nolock) ON sol_codigo = sca_codigosolicitacao
                INNER JOIN Cervello.dbo.produto(nolock) ON pro_codigo = sol_codigoproduto
                WHERE LEN(sca_Folder) > 0
                AND foc_codigotipocampo = 12
                UNION
                SELECT
                    pro_descricao AS Fluxo
                ,sec_CodigoSolicitacaoEtapa AS Solicitacao
                ,eta_descricao AS Etapa
                ,sec_valortexto AS Nome_Arquivo_Formulario
                ,sec_Codigo AS CodigoLinha
                ,foc_descricao AS TipoAnexo
                ,sec_Folder AS Pasta_Servidor
                ,'form_etapa_' + CONVERT(VARCHAR, sec_codigo) AS Nome_Arquivo_Servidor
                FROM Cervello.dbo.SolicitacaoEtapaCampos(nolock)
                INNER JOIN Cervello.dbo.FormularioCampos(nolock) ON foc_codigo = sec_CodigoCampo
                INNER JOIN Cervello.dbo.SolicitacaoEtapa(nolock) ON set_Codigo = sec_CodigoSolicitacaoEtapa
                INNER JOIN Cervello.dbo.Etapas(nolock) ON eta_codigo = set_codigoetapa
                INNER JOIN Cervello.dbo.Solicitacao(nolock) ON sol_codigo = set_codigosolicitacao
                INNER JOIN Cervello.dbo.produto(nolock) ON pro_codigo = sol_codigoproduto
                WHERE LEN(sec_folder) > 0
                AND eta_criacao = 0
                AND foc_codigotipocampo = 12
                UNION
                SELECT
                    pro_descricao AS Fluxo
                ,sca_codigosolicitacao AS Solicitacao
                ,'Formulario_Inicial' AS Etapa
                ,sca_ValorTexto AS Nome_Arquivo_Formulario
                ,sca_Codigo AS CodigoLinha
                ,foc_descricao AS TipoAnexo
                ,sca_Folder AS Pasta_Servidor
                ,'form_produto_' + CONVERT(VARCHAR, sca_codigo) AS Nome_Arquivo_Servidor
                FROM Cervello.dbo.SolicitacaoCampos_Finalizada(nolock)
                INNER JOIN Cervello.dbo.FormularioCampos(nolock) ON foc_codigo = sca_codigocampo
                INNER JOIN Cervello.dbo.solicitacao_Finalizada(nolock) ON sol_codigo = sca_codigosolicitacao
                INNER JOIN Cervello.dbo.produto(nolock) ON pro_codigo = sol_codigoproduto
                WHERE LEN(sca_Folder) > 0
                AND foc_codigotipocampo = 12
                UNION
                SELECT
                    pro_descricao AS Fluxo
                ,sec_CodigoSolicitacaoEtapa AS Solicitacao
                ,eta_descricao AS Etapa
                ,sec_valortexto AS Nome_Arquivo_Formulario
                ,sec_Codigo AS CodigoLinha
                ,foc_descricao AS TipoAnexo
                ,sec_Folder AS Pasta_Servidor
                ,'form_etapa_' + CONVERT(VARCHAR, sec_codigo) AS Nome_Arquivo_Servidor
                FROM Cervello.dbo.SolicitacaoEtapaCampos_Finalizada(nolock)
                INNER JOIN Cervello.dbo.FormularioCampos(nolock) ON foc_codigo = sec_CodigoCampo
                INNER JOIN Cervello.dbo.SolicitacaoEtapa_Finalizada(nolock) ON set_Codigo = sec_CodigoSolicitacaoEtapa
                INNER JOIN Cervello.dbo.Etapas(nolock) ON eta_codigo = set_codigoetapa
                INNER JOIN Cervello.dbo.solicitacao_Finalizada(nolock) ON sol_codigo = set_codigosolicitacao
                INNER JOIN Cervello.dbo.produto(nolock) ON pro_codigo = sol_codigoproduto
                WHERE LEN(sec_folder) > 0
                AND eta_criacao = 0
                AND foc_codigotipocampo = 12),

                Consulta AS (SELECT
                    Solicitacao AS Chamado
                ,Nome_Arquivo_Formulario AS NomeArquivo
                ,RIGHT(Nome_Arquivo_Formulario, 4) AS Formato
                ,(CASE
                    WHEN TipoAnexo = @CAMPOFT THEN 'Fatura'
                    END) AS TipoAnexo
                ,CONCAT('\\\\SRVUDI442\\Arquivos\\', Pasta_Servidor, '\\', Nome_Arquivo_Servidor
                ,RIGHT(a.Nome_Arquivo_Formulario, CHARINDEX('.', REVERSE(a.Nome_Arquivo_Formulario)))) AS CaminhoServidorDireto
                ,Pasta_Servidor
                ,ROW_NUMBER() OVER (PARTITION BY Solicitacao, TipoAnexo ORDER BY CodigoLinha DESC) AS Row
                FROM Anexos a
                WHERE Solicitacao IN ({calls})
                AND TipoAnexo IN (@CAMPOFT)
                AND RIGHT(a.Nome_Arquivo_Formulario, 4) IN ('.zip', '.pdf', '.jpg', 'jpeg', '.png', 'xlsx', '.xls', '.csv'))

                SELECT
                *
                FROM Consulta
                WHERE Row = 1
                AND TipoAnexo IN ('Fatura')
                ORDER BY Chamado, Row"""