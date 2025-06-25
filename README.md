# Airflow-ETL-Pipeline

### How to Use
Install uv 

uv venv --python 3.12.6

source .venv/bin/activate

uv pip install -r requirements.txt

uv pip install apache-airflow==3.0.0

uv pip install apache-airflow-providers-postgres==6.1.3

docker compose up

Airflow UI -> Admin -> Connections -> Connection ID = 'postgres', Connection Type = 'postgres', Host = 'postgres', Login = 'airflow', Password = 'airflow', Port = '5432'

To stop docker containers - Ctrl-C