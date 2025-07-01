from airflow.sdk import dag, task, task_group
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sdk.bases.sensor import PokeReturnValue
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.standard.operators.python import PythonOperator


@dag
def user_processing():

    create_tables = SQLExecuteQueryOperator(
        task_id="create_tables",
        conn_id="postgres",
        sql="DROP TABLE IF EXISTS user_table;"
        "DROP TABLE IF EXISTS address;"
        "DROP TABLE IF EXISTS street;"
        "DROP TABLE IF EXISTS city;"
        "DROP TABLE IF EXISTS state;"
        "DROP TABLE IF EXISTS country;"
        "DROP TABLE IF EXISTS title;"
        "DROP TABLE IF EXISTS gender;"
        "CREATE TABLE IF NOT EXISTS gender ("
        "   gender_id INT PRIMARY KEY,"
        "   gender VARCHAR(50)"
        ")"
        ";"
        "CREATE TABLE IF NOT EXISTS title ("
        "   title_id INT PRIMARY KEY,"
        "   title VARCHAR(50)"
        ")"
        ";"
        "CREATE TABLE IF NOT EXISTS country ("
        "   country_id INT PRIMARY KEY,"
        "   country VARCHAR(50)"
        ")"
        ";"
        "CREATE TABLE IF NOT EXISTS state ("
        "   state_id INT PRIMARY KEY,"
        "   state VARCHAR(50),"
        "   country_id INT,"
        "   CONSTRAINT fk_country FOREIGN KEY (country_id)"
        "   REFERENCES country(country_id)"
        ")"
        ";"
        "CREATE TABLE IF NOT EXISTS city ("
        "   city_id INT PRIMARY KEY,"
        "   city VARCHAR(50),"
        "   state_id INT,"
        "   CONSTRAINT fk_state FOREIGN KEY (state_id)"
        "   REFERENCES state(state_id)"
        ")"
        ";"
        "CREATE TABLE IF NOT EXISTS address ("
        "   address_id INT PRIMARY KEY,"
        "   street_number INT,"
        "   street_name VARCHAR(250),"
        "   postcode VARCHAR(100),"
        "   city_id INT,"
        "   CONSTRAINT fk_city FOREIGN KEY (city_id)"
        "   REFERENCES city(city_id)"
        ")"
        ";"
        "CREATE TABLE IF NOT EXISTS user_table ("
        "   user_id INT PRIMARY KEY,"
        "   first_name VARCHAR(200),"
        "   last_name VARCHAR(200),"
        "   email VARCHAR(200),"
        "   phone VARCHAR(200),"
        "   cell_phone VARCHAR(200),"
        "   login_username VARCHAR(300),"
        "   login_password VARCHAR(300),"
        "   dob_date DATE,"
        "   registered_date DATE,"
        "   gender_id INT,"
        "   CONSTRAINT fk_gender FOREIGN KEY (gender_id)"
        "   REFERENCES gender(gender_id),"
        "   title_id INT,"
        "   CONSTRAINT fk_title FOREIGN KEY (title_id)"
        "   REFERENCES title(title_id),"
        "   address_id INT,"
        "   CONSTRAINT fk_address FOREIGN KEY (address_id)"
        "   REFERENCES address(address_id)"
        ")"
        ";",
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
            "cell",
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
    def transform_users_as_csvs(users_details):
        import pandas as pd

        def base_df():
            df = pd.DataFrame(users_details)
            print(df)
            return df

        def create_gender(given_df):
            # Create a gender DataFrame, with duplicate values dropped
            column_df = given_df["gender"].drop_duplicates().reset_index()

            # Drop the created 'index' column
            column_df = column_df.drop("index", axis=1)

            # Create a gender_id column
            column_df.insert(loc=0, column="gender_id", value=(column_df.index + 1))

            print(column_df)
            return column_df

        def create_title(given_df):
            # Create a title DataFrame, with duplicate values dropped
            title_df = given_df["name_title"].drop_duplicates().reset_index()

            # Rename column to just 'title'
            title_df.rename(columns={"name_title": "title"}, inplace=True)

            # Drop the created 'index' column
            title_df = title_df.drop("index", axis=1)

            # Create a title_id column
            title_df.insert(loc=0, column="title_id", value=(title_df.index + 1))

            print(title_df)
            return title_df

        def create_country(given_df):
            # Create a country DataFrame, with duplicate values dropped
            country_df = given_df["location_country"].drop_duplicates().reset_index()

            # Rename column to just 'country'
            country_df.rename(columns={"location_country": "country"}, inplace=True)

            # Drop the created 'index' column
            country_df = country_df.drop("index", axis=1)

            # Create a country_id column
            country_df.insert(loc=0, column="country_id", value=(country_df.index + 1))

            print(country_df)
            return country_df

        def create_state(base_df, country_df):
            # Create a state DataFrame, with duplicate values dropped
            state_df = (
                base_df[["location_state", "location_country"]]
                .drop_duplicates()
                .reset_index()
            )

            # Rename column to just 'state'
            state_df.rename(columns={"location_state": "state"}, inplace=True)

            # Create a state_id column
            state_df.insert(loc=0, column="state_id", value=(state_df.index + 1))

            # merge country_df to state_df, to get the country_id
            state_df = pd.merge(
                state_df, country_df, left_on="location_country", right_on="country"
            )

            # Drop unwanted columns
            state_df = state_df.drop(["index", "location_country", "country"], axis=1)

            print(state_df)
            return state_df

        def create_city(base_df, state_df, country_df):
            # Create a city DataFrame, with duplicate values dropped
            city_df = (
                base_df[["location_city", "location_state", "location_country"]]
                .drop_duplicates()
                .reset_index()
            )

            # Rename column to just 'city'
            city_df.rename(columns={"location_city": "city"}, inplace=True)

            # Create a city_id column
            city_df.insert(loc=0, column="city_id", value=(city_df.index + 1))

            # merge country_df to city_df, to get the country_id
            city_df = pd.merge(
                city_df, country_df, left_on="location_country", right_on="country"
            )

            # merge state_df to city_df, to get the state_id
            city_df = pd.merge(
                city_df,
                state_df,
                left_on=["location_state", "country_id"],
                right_on=["state", "country_id"],
            )

            # Drop unwanted columns
            city_df = city_df.drop(
                [
                    "index",
                    "location_state",
                    "state",
                    "country_id",
                    "location_country",
                    "country",
                ],
                axis=1,
            )
            print(city_df)

            return city_df

        def create_address(base_df, city_df, state_df, country_df):
            # Create an address DataFrame, with duplicate values dropped
            address_df = (
                base_df[
                    [
                        "street_number",
                        "street_name",
                        "location_postcode",
                        "location_city",
                        "location_state",
                        "location_country",
                    ]
                ]
                .drop_duplicates()
                .reset_index()
            )

            # Rename 'location_postcode' column to just 'postcode'
            address_df.rename(columns={"location_postcode": "postcode"}, inplace=True)

            # Create an address_id column
            address_df.insert(loc=0, column="address_id", value=(address_df.index + 1))

            # merge country_df to address_df, to get the country_id
            address_df = pd.merge(
                address_df, country_df, left_on="location_country", right_on="country"
            )

            # merge state_df to address_df, to get the state_id
            address_df = pd.merge(
                address_df,
                state_df,
                left_on=["location_state", "country_id"],
                right_on=["state", "country_id"],
            )

            # merge city_df to address_df, to get the city_id
            address_df = pd.merge(
                address_df,
                city_df,
                left_on=["location_city", "state_id"],
                right_on=["city", "state_id"],
            )

            # Drop unwanted columns
            address_df = address_df.drop(
                [
                    "index",
                    "location_city",
                    "city",
                    "location_state",
                    "state_id",
                    "state",
                    "country_id",
                    "location_country",
                    "country",
                ],
                axis=1,
            )
            print(address_df)

            return address_df

        def create_user(base_df, gender_df, title_df, address_df):
            # Create a user DataFrame, with duplicate values dropped
            user_df = (
                base_df[
                    [
                        "name_title",
                        "name_first",
                        "name_last",
                        "gender",
                        "email",
                        "phone",
                        "cell",
                        "login_username",
                        "login_password",
                        "dob_date",
                        "registered_date",
                        "street_number",
                        "street_name",
                    ]
                ]
                .drop_duplicates()
                .reset_index()
            )

            # Create a user_id column
            user_df.insert(loc=0, column="user_id", value=(user_df.index + 1))

            # merge gender_df to user_df, to get the gender_id
            user_df = pd.merge(user_df, gender_df, on="gender")

            # merge title_df to user_df, to get the title_id
            user_df = pd.merge(
                user_df, title_df, left_on="name_title", right_on="title"
            )

            # merge address_df to user_df, to get the address_id
            user_df = pd.merge(user_df, address_df, on=["street_number", "street_name"])

            # Drop unwanted columns
            user_df = user_df.drop(
                [
                    "index",
                    "name_title",
                    "title",
                    "postcode",
                    "city_id",
                    "gender",
                    "street_number",
                    "street_name",
                ],
                axis=1,
            )

            # Rename columns
            user_df.rename(
                columns={
                    "name_first": "first_name",
                    "name_last": "last_name",
                    "cell": "cell_phone",
                },
                inplace=True,
            )

            # Extract just date from datetime of dob_date + convert to datetime type
            user_df["dob_date"] = user_df["dob_date"].str.slice(0, 10)
            user_df["dob_date"] = pd.to_datetime(user_df["dob_date"])

            # Extract just date from datetime of registered_date + convert to datetime type
            user_df["registered_date"] = user_df["registered_date"].str.slice(0, 10)
            user_df["registered_date"] = pd.to_datetime(user_df["registered_date"])

            print(user_df)
            return user_df

        def users_to_csv(
            gender_df, title_df, country_df, state_df, city_df, address_df, user_df
        ):
            dfs = {
                "gender": gender_df,
                "title": title_df,
                "country": country_df,
                "state": state_df,
                "city": city_df,
                "address": address_df,
                "user_table": user_df,
            }

            for table_name, df in dfs.items():
                df.to_csv(f"/tmp/{table_name}.csv", index=False)

        df = base_df()

        gender_df = create_gender(df)
        title_df = create_title(df)
        country_df = create_country(df)
        state_df = create_state(df, country_df)
        city_df = create_city(df, state_df, country_df)
        address_df = create_address(df, city_df, state_df, country_df)
        user_df = create_user(df, gender_df, title_df, address_df)

        users_to_csv(
            gender_df, title_df, country_df, state_df, city_df, address_df, user_df
        )

    @task
    def store_users():
        hook = PostgresHook(postgres_conn_id="postgres")

        table_names = [
            "gender",
            "title",
            "country",
            "state",
            "city",
            "address",
            "user_table",
        ]

        for table in table_names:
            hook.copy_expert(
                sql=f"COPY {table} FROM STDIN WITH CSV HEADER;",
                filename=f"/tmp/{table}.csv",
            )

    (
        transform_users_as_csvs(
            extract_users_details(create_tables >> is_api_available())
        )
        >> store_users()
    )


user_processing()
