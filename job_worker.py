from fastapi import FastAPI
from easyjobs.workers.worker import EasyJobsWorker
import httpx
import uvicorn
import os
server = FastAPI()

environment = "PROD" #CA:MBIAR A DEV SI DESEA LOCALHOST
if environment == "PROD":
    manager_host='https://manager-pipeline-challenge.herokuapp.com'
    manager_port=443
    api_url="https://api-challenge-pipeline.herokuapp.com"
    api_port=443
else:
    manager_host='0.0.0.0'
    manager_port=8220
    api_url="http://localhost:8000"



@server.on_event('startup')
async def setup():
    worker = await EasyJobsWorker.create(
        server,
        server_secret='abcd1234',
        manager_host=manager_host, # cambiar esto por 0.0.0.0 en caso de ejecutar localmente el manager
        manager_port=manager_port, # cambiar este puerto a 8220 en caso de ejecutar localmente el manager
        manager_secret='abcd1234',
        jobs_queue='ETL',
        max_tasks_per_worker=5
    )

    every_minute = '*/45 * * * *'
    default_args = {'args': ['http://stats']}

    async def get_data(url):
        print(f"Iniciando proceso insert vehicles...: {url}")
        timeout = httpx.Timeout(None)
        async with httpx.AsyncClient() as client:
           r = await client.get(url, timeout=timeout)
        print("Proceso insert vehicles finalizado correctamente....")
        return {'message': "insert_vehicles finalizado correctamente"}


    async def insert_delegaciones(url):
        timeout = httpx.Timeout(None)
        async with httpx.AsyncClient() as client:
           r = await client.get(url, timeout=timeout)
        return {'message': "insert_delegaciones finalizado correctamente"}

    @worker.task(schedule=every_minute)
    async def extract():
        url = f"{api_url}/api/v1/insert_vehicles"
        print("entreeeeeeeeee")
        print(f"PROCESO DE INSERCION INICIADO...")
        await get_data(url)
        url = f"{api_url}/api/v1/insert_delegaciones"
        await insert_delegaciones(url)
        print(f"PROCESO DE INSERCION FINALIZADO...")
        return {'data': "INSERCION DE DATOS FINALIZADA CORRECTAMENTE"}

    
    
    

if __name__=="__main__":
	PORT = int(os.environ.get('PORT', 8221))
	uvicorn.run("job_worker:server",host='0.0.0.0',port=PORT ,reload=True)