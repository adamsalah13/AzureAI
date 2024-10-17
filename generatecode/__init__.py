import os
import logging
import openai
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing a code generation request.')

    try:
        # Get the 'prompt' from the query string
        prompt = req.params.get('prompt')
        if not prompt:
            logging.error("No prompt provided in the query string")
            return func.HttpResponse("Please pass a prompt in the query string", status_code=400)

        # Set OpenAI API configuration using environment variables
        openai.api_type = "azure"
        openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
        openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        openai.api_version = "2024-08-01-preview"

        # Ensure that the endpoint and API key are set correctly
        if not openai.api_base or not openai.api_key:
            logging.error("AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY is not set.")
            return func.HttpResponse("Internal Server Error: Missing OpenAI configuration.", status_code=500)

        # Deployment model name
        deployment_name = "gpt-35-turbo"

        # Add a specific system message to narrow the output focus
        system_message = "You are an AI that writes Python code for specific tasks. Only provide Python code for the requested task."

        # Log the prompt and deployment details
        logging.info(f"Calling OpenAI API with deployment: {deployment_name} and prompt: {prompt}")

        # Call the OpenAI Completion API with increased max_tokens and focused context
        response = openai.Completion.create(
            engine=deployment_name,
            prompt=f"{system_message}\n{prompt}",
            max_tokens=200,  # Increased to ensure full response
            temperature=0.2   # Lower temperature for more deterministic output
        )

        # Extract the generated code from the response
        generated_text = response['choices'][0]['text'].strip()

        # Clean up any separators or markers that may appear
        cleaned_text = generated_text.replace('<|im_sep|>', '').strip()

        # Format the response output for readability
        formatted_text = f"```\n{cleaned_text}\n```"

        logging.info(f"Generated Code: {formatted_text}")

        # Return the generated code as the HTTP response
        return func.HttpResponse(formatted_text, status_code=200, mimetype="text/plain")

    except Exception as e:
        logging.error(f"Error generating code: {str(e)}")
        return func.HttpResponse(f"Error generating code: {str(e)}", status_code=500)
