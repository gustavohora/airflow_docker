#intalar bibliotecas
#pip install -r requirements.txt

from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
import pandas as pd
import requests
import json

def captura_conta_dados():
        url = 'https://data.cityofnewyork.us/resource/rc75-m7u3.json'
        response = requests.get(url)
        df = pd.DataFrame(json.loads(response.content))
        qtd = len(df.index)
        return qtd

def e_valida(ti):
        qtd = ti.xcom_pull(task_id = captura_conta_dados)
        if (qtd > 1000):
                return 'valido'
        return 'nao_valido'

with DAG('etl_dag', start_date = datetime(2023, 1, 1),
        schedule = '30 * * * *',
        catchup = False
        ) as dag:

     captura_conta_dados = PythonOperator(
        task_id = 'captura_conta_dados',
        python_callable = captura_conta_dados
     )

     e_valida = BranchPythonOperator(
        task_id = 'e_valida',
        python_callable = e_valida
     )

     valido = BashOperator (
        task_id = 'valido',
        bash_command = "echo 'Quantidade Ok'"
     )

     nvalido = BashOperator (
        task_id = 'nao_valido',
        bash_command = "echo 'Quantidade Não Ok'"
     )

captura_conta_dados >> e_valida >> [valido, nvalido]