import logging
import os
import openai
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing a code generation request.')

    try:
        prompt = req.params.get('prompt')
        if not prompt:
            return func.HttpResponse("Please pass a prompt in the query string", status_code=400)
        
        openai.api_type = "azure"
        openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
        openai.api_version = "2023-05-15"
        openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")

        response = openai.Completion.create(
            engine="YourCodexDeploymentName",
            prompt=prompt,
            max_tokens=100,
            temperature=0
        )

        code = response['choices'][0]['text']
        return func.HttpResponse(code, status_code=200)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse("Error generating code", status_code=500)
