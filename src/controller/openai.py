import json
import requests
from typing import Tuple, Optional
from controller.config import ConfigLoader

class OpenAIController:

    def __init__(self):
        self.config = ConfigLoader()
        self.url_openai = self.config.url_openai
        self.token_openai = self.config.token_openai
        self.load_prompt = self.config.load_prompt

    def request_body(self, pdf_text: str, invoice_type: str) -> Tuple[Optional[str], Optional[str]]:
        prompt_type, err = self.load_prompt(invoice_type)
        if err:
            return None, err
        prompt = prompt_type + pdf_text
        body = {
            "model": "gpt-4o",
            "response_format": { "type": "json_object" },
            "messages": [{
                "role": "system",
                "content": f"""{prompt}"""
            },{
                "role": "user",
                "content": "Considerando todas as instruções deste prompt, a sua resposta em JSON é:"
            }],
            "temperature": 0,
            "top_p": 0,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None
        }
        return body, None

    def openai_request(self, body: dict) -> Tuple[Optional[str], Optional[str]]:
        """
        Makes a request to the OpenAI endpoint with the provided body.

        Args:
            body (dict): The request body to be sent.

        Returns:
            Tuple[Optional[str], Optional[str]]: Response content or error message.
        """
        headers = { 
            "api-key": self.token_openai,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.url_openai,
                                     data=json.dumps(body),
                                     headers=headers)

            if response.status_code != 200:
                return None, f"Error: {response.status_code} - {response.text}"

            response_json = response.json()
            return response_json['choices'][0]['message']['content'], None
        
        except requests.exceptions.RequestException as e:
            return None, f"Request failed: {str(e)}"