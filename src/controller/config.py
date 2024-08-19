import os
import configparser
from dotenv import load_dotenv
from typing import Tuple, Optional

class ConfigLoader:
 
    def __init__(self, config_file=os.path.join(os.getcwd(),'config.ini')):
        self.config_file = config_file
        self.load_dot_env()
        self.load_config()

    def load_config(self):
        config = configparser.ConfigParser()
        config.read(self.config_file)
        self.url_openai = os.getenv("URL_OPENAI_CHATGPT_AZURE")
        self.token_openai = os.getenv("TOKEN_OPENAI_CHATGPT_AZURE")
        self.user_sankhya = os.getenv("USER_SANKHYA_API")
        self.passw_sankhya = os.getenv("PASSWORD_SANKHYA_API")
        self.url_sankhya_inclusao = os.getenv("URL_SANKHYA_INCLUSAO_API")
        self.url_sankhya_mge = os.getenv("URL_SANKHYA_MGE_API")
        self.url_sankhya_mge_anexo = os.getenv("URL_SANKHYA_MGE_ANEXO_API")
        self.server_sql = os.getenv("SERVER_SQL")
        self.database_sql = os.getenv("DATABASE_SQL")
        self.server_smtp = os.getenv("SERVER_SMTP")
        self.port_smtp = os.getenv("PORT_SMTP")
        self.user_smtp = os.getenv("USER_SMTP")
        self.to_smtp = os.getenv("TO_SMTP").split(",")
        self.user_adm_cervello = os.getenv("USERADM")
        self.pass_adm_cervello = os.getenv("PASSADM")
        self.cod_usu_aprov_cervello = os.getenv("CODUSUAPROV")
        self.cod_usu_cap_cervello = os.getenv("CODUSUCAP")
        self.pass_usu_aprov_cervello = os.getenv("PASSUSUAPROV")
        self.usu_cap_cervello = os.getenv("USUCAP")
        self.host_cervello = os.getenv("HOST")
        self.end_point_cervello = os.getenv("ENDPOINT")
  
    def load_dot_env(self):
        load_dotenv()

    def load_prompt(self, prompt_name: str) -> Tuple[Optional[str], Optional[str]]:
        file_path = rf"src\model\resources\prompt_{prompt_name}.txt"
        prompt = ""
        try:
            with open(file_path, "r") as file:
                prompt = file.read()
            return prompt, None
        except Exception as e:
            return None, f"Failed to load prompt: {str(e)}"