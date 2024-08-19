import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from controller.config import ConfigLoader

configs = ConfigLoader()

def criar_relatorio_sintetico(df):
    relatorio = df[["TipoErro", "StatusExecucao","Lançado"]].value_counts().reset_index()
    relatorio.columns = ['TipoErro', 'Status', 'Lançado', 'Quantidade']
    relatorio = relatorio.sort_values('Quantidade', ascending=False)
    return relatorio

def send_email(assunto, mensagem, anexo=None, df_boletos=None, df_notas=None, relatorio=None):
    smtp_server = configs.server_smtp
    smtp_port = configs.port_smtp
    smtp_usuario = configs.user_smtp
    destinatarios = configs.to_smtp
    msg = MIMEMultipart('alternative')
    msg['From'] = smtp_usuario
    msg['Subject'] = assunto
    
    corpo_email = mensagem

    if relatorio is not None:
        corpo_email += '<br>Relatório Sintético:<br>' + relatorio.to_html(index=False)

    if df_notas is not None:
        corpo_email += '<br>Analítico das notas LANÇADAS:<br>' + df_notas.to_html(index=False)

    if df_boletos is not None:
        corpo_email += '<br>Analítico dos boletos das notas com status OK:<br>' + df_boletos.to_html(index=False)


    html = MIMEText(corpo_email, 'html')
    msg.attach(html)

    if anexo is not None:
        with io.BytesIO() as buffer:
            anexo.to_excel(buffer, index=False)
            buffer.seek(0)
            excel_attachment = buffer.getvalue()

        excel_part = MIMEApplication(excel_attachment)
        excel_part.add_header('Content-Disposition', 'attachment', filename='DadosFaturas.xlsx')
        msg.attach(excel_part)

    try:
        servidor_smtp = smtplib.SMTP(smtp_server, smtp_port)
        for destinatario in destinatarios:
            msg['To'] = destinatario
            servidor_smtp.sendmail(smtp_usuario, destinatario, msg.as_string())

        return True, True
    except Exception as e:
        return False, e