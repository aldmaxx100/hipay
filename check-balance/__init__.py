import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    
    logging.info(req.params)
    body=req.get_body()
    logging.info(body)
    return func.HttpResponse(f"Hello!")
    