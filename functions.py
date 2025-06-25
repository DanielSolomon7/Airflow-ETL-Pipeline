from airflow.sdk import dag, task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sdk.bases.sensor import PokeReturnValue
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.standard.operators.python import PythonOperator


@task.sensor(poke_interval=30, timeout=300)
def is_api_available() -> PokeReturnValue:
    import requests
    response = requests.get("https://randomuser.me/api/?results=50")
    
    if response.status_code == 200:
        available = True
        users = response.json()
    else:
        available = False
        users = None

    return PokeReturnValue(is_done=available, xcom_value=users)

is_api_available()



#     @task.sensor(poke_interval=30, timeout=300)
#     def is_api_available():
#         import requests

#         response = requests.get("https://www.spartaglobal.com/")
#         print(response.status_code)

#         if response.status_code == 200:
#             condition = True
#             fake_user = response.json()
#         else:
#             condition = False
#             fake_user = None
        
#         return PokeReturnValue(is_done=condition, xcom_value=fake_user)