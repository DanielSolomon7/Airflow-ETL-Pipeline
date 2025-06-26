from airflow.sdk import dag, task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sdk.bases.sensor import PokeReturnValue
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.standard.operators.python import PythonOperator
import pandas as pd


@dag
def user_processing():
    
    create_tables = SQLExecuteQueryOperator(
        task_id="create_tables",
        conn_id="postgres",
        sql="CREATE TABLE IF NOT EXISTS gender (" \
            "   gender_id SERIAL PRIMARY KEY," \
            "   gender VARCHAR(50)" \
            ")" \
            ";"
            "CREATE TABLE IF NOT EXISTS title (" \
                    "   title_id SERIAL PRIMARY KEY," \
                    "   title VARCHAR(50)" \
            ")" \
            ";"
            "CREATE TABLE IF NOT EXISTS country (" \
                    "   country_id SERIAL PRIMARY KEY," \
                    "   country VARCHAR(50)" \
            ")" \
            ";"
            "CREATE TABLE IF NOT EXISTS state (" \
                    "   state_id SERIAL PRIMARY KEY," \
                    "   state VARCHAR(50)," \
                    "   country_id INT," \
                    "   CONSTRAINT fk_country FOREIGN KEY (country_id)"
                    "   REFERENCES country(country_id)" \
            ")" \
            ";"
            "CREATE TABLE IF NOT EXISTS city (" \
                    "   city_id SERIAL PRIMARY KEY," \
                    "   city VARCHAR(50)," \
                    "   state_id INT," \
                    "   CONSTRAINT fk_state FOREIGN KEY (state_id)"
                    "   REFERENCES state(state_id)" \
            ")" \
            ";"
            "CREATE TABLE IF NOT EXISTS street (" \
                    "   street_id SERIAL PRIMARY KEY," \
                    "   street VARCHAR(250)," \
                    "   city_id INT," \
                    "   CONSTRAINT fk_city FOREIGN KEY (city_id)"
                    "   REFERENCES city(city_id)" \
            ")" \
            ";"
            "CREATE TABLE IF NOT EXISTS address (" \
                        "   address_id SERIAL PRIMARY KEY," \
                        "   street_number INT," \
                        "   street_id INT," \
                        "   CONSTRAINT fk_street FOREIGN KEY (street_id)"
                        "   REFERENCES street(street_id)," \
                        "   postcode VARCHAR(100)" \
            ")" \
            ";"
            "CREATE TABLE IF NOT EXISTS user_table (" \
                        "   user_id SERIAL PRIMARY KEY," \
                        "   title_id INT," \
                        "   CONSTRAINT fk_title FOREIGN KEY (title_id)"
                        "   REFERENCES title(title_id)," \
                        "   first_name VARCHAR(200)," \
                        "   last_name VARCHAR(200)," \
                        "   gender_id INT," \
                        "   CONSTRAINT fk_gender FOREIGN KEY (gender_id)"
                        "   REFERENCES gender(gender_id)," \
                        "   email VARCHAR(200)," \
                        "   phone VARCHAR(200)," \
                        "   cell_phone VARCHAR(200)," \
                        "   username VARCHAR(300)," \
                        "   password VARCHAR(300)," \
                        "   address_id INT," \
                        "   CONSTRAINT fk_address FOREIGN KEY (address_id)"
                        "   REFERENCES address(address_id)," \
                        "   date_of_birth DATE," \
                        "   date_registered DATE" \
            ")" \
            ";"
    )
    

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
    

    @task
    def extract_users_details(users):
        users_details = []

        # Specify wanted fields from the API response
        wanted_fields = [
            "gender",
            ["name", "title"],
            ["name", "first"],
            ["name", "last"],
            ["location", "street", "number"],
            ["location", "street", "name"],
            ["location", "city"],
            ["location", "state"],
            ["location", "country"],
            ["location", "postcode"],
            "email",
            ["login", "username"],
            ["login", "password"],
            ["dob", "date"],
            ["registered", "date"],
            "phone",
            "cell"
        ]

        # Iterate through each user from the API response
        for user in users["results"]:
            user_dict = {}

            # Iterate through each wanted field
            for field in wanted_fields:

                # Get the field name if not nested
                if isinstance(field, str):
                    user_dict[field] = user[field]

                # Get the field name if nested
                elif isinstance(field, list):
                    last_index = len(field) - 1
                    name_of_field = f"{field[last_index - 1]}_{field[last_index]}"

                    # Get the field value if nested once
                    if len(field) == 2:
                        user_dict[name_of_field] = user[field[0]][field[1]]

                    # Get the field value if nested twice
                    elif len(field) == 3:
                        user_dict[name_of_field] = user[field[0]][field[1]][field[2]]

            users_details.append(user_dict)

        print(users_details)
        return users_details


    @task
    def users_to_dfs(users_details):
        pass

    
    extract_users_details(create_tables >> is_api_available())

user_processing()