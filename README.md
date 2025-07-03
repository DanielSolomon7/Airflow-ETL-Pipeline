# 🌀 Airflow ETL Pipeline

## 📄 Overview

This project demonstrates a simple **ETL (Extract, Transform, Load)** pipeline orchestrated with **Apache Airflow**. The pipeline:

- **Extracts** user data from the [Random User API](https://randomuser.me/)
- **Transforms** the data into a normalized relational format
- **Loads** the structured data into a PostgreSQL database

![ERD](ERD.png)
![Airflow ETL Project](Airflow_ETL_Project.png)

---

## 📚 Table of Contents

1. [Overview](#-overview)
2. [Setup Instructions](#-setup-instructions)
3. [Running the Project](#-running-the-project)
4. [Stopping Services](#-stopping-services)
5. [Project Structure](#-project-structure)
6. [Contact](#-contact)
7. [Contributing](#-contributing)

---

## 🛠️ Setup Instructions

### ✅ Prerequisites

Make sure the following are installed:

- [Docker](https://www.docker.com/)
- [Python 3.12.x](https://www.python.org/)
- [uv (Python package manager)](https://docs.astral.sh/uv/)

### ⚙️ Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DanielSolomon7/Airflow-ETL-Pipeline
   cd Airflow-ETL-Pipeline
   ```

2. **Create and activate a virtual environment:**
   ```bash
   uv venv --python 3.12.6
   source .venv/bin/activate
   ```

3. **Install required packages:**
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Start services using Docker Compose:**
   ```bash
   docker compose up
   ```

---

## 🚀 Running the Project

Once the containers are running:

1. Access the **Airflow UI** by navigating to `http://localhost:8080`  
2. Navigate to: `Admin` → `Connections`
3. Configure the PostgreSQL connection as follows:
   - **Connection ID**: `postgres`
   - **Connection Type**: `postgres`
   - **Host**: `postgres`
   - **Login**: `airflow`
   - **Password**: `airflow`
   - **Port**: `5432`

Trigger the DAG to run the ETL pipeline.

---

## 🛑 Stopping Services

To gracefully stop the running Docker containers, return to the terminal where they're running and press:

```bash
Ctrl + C
```

---

## 🗂️ Project Structure

```plaintext
Airflow-ETL-Pipeline/
│
├── dags/
│   └── etl_pipeline.py         # Defines the DAG and tasks for the ETL workflow
│
│
├── docker-compose.yml         # Docker services including Airflow, Postgres, and supporting containers
├── requirements.txt           # Python dependencies for the pipeline
├── .env                       # (Optional) Environment variables for local development
├── README.md                  # Project overview and setup guide
└── .venv/                     # Local Python virtual environment (ignored in version control)
```

---

## 📬 Contact

For questions, issues, or suggestions, feel free to open an issue or reach out via GitHub.

---

## 🧑‍💻 Contributing

Contributions are welcome and encouraged! If you'd like to improve this project, please follow these steps:

1. **Fork the repository**
2. **Create a new branch** for your feature or fix:
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. **Make your changes**, keeping the codebase clean and consistent
4. **Commit your changes** with clear, descriptive messages:
   ```bash
   git commit -m "Add new feature: descriptive summary"
   ```
5. **Push to your forked repository**:
   ```bash
   git push origin feature/my-new-feature
   ```
6. **Create a pull request** from your fork back to the `main` branch of this repo

### 🧼 Code Style

- Ensure Python code is linted and formatted (e.g. with `black`)
- Keep commit messages meaningful

