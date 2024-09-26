# Finance Dashboard

Welcome to the Finance Dashboard, a Streamlit application designed to streamline and visualize the profit and loss for various projects within a company, including Sushibar, restaurants, and factories. This dashboard leverages SQLAlchemy for database management, performs data analytics for insightful financial health checks, and uses Prophet for future financial projections.

## Getting Started

To run this project locally, follow these steps:

1. Clone the repository to your local machine.
2. Ensure you have Python 3.11.8 installed.
3. Install the required dependencies:
    ```pip install -r requirements.txt```
4. Navigate to the project directory and run the application:
    ```streamlit run app.py```


## Handling Secrets

The application may require access to sensitive information, such as API keys, database credentials, and other secrets. It is crucial to handle these securely and never commit them to your version control system.

We recommend using environment variables or a secret management tool to manage your secrets. For development purposes, you can use a `.streamlit/secrets.toml` file to store your environment variables locally. **Never** commit this file to your repository by adding `.streamlit` to your `.gitignore` file.

For example, to set up environment variables in a `.streamlit/secrets.toml` file:

```
[connections.db]
dialect = "mysql"
username = "username"
password = "password"
host = "host"
database = "database"

# Everything in this section will be available as an environment variable
db_username = "Jane"
db_password = "mypassword"
```

And access them in your application:

```python
import streamlit as st

# Create the SQL connection to pets_db as specified in your secrets file.
conn = st.connection('db', type='sql')

# Everything is accessible via the st.secrets dict:
st.secrets["db_username"]
st.secrets["db_password"]
```

Alternatively, you can use a `.env` file to manage your environment variables:

```
NETSUITE_ACCOUNT_ID=your_account_id
NETSUITE_CONSUMER_KEY=your_consumer_key
NETSUITE_CONSUMER_SECRET=your_consumer_secret
NETSUITE_TOKEN_ID=your_token_id
NETSUITE_TOKEN_SECRET=your_token_secret
```

And load them in your application:

```python
from dotenv import load_dotenv
import os

load_dotenv()

ACCOUNT_ID = os.getenv("NETSUITE_ACCOUNT_ID")
CONSUMER_KEY = os.getenv("NETSUITE_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("NETSUITE_CONSUMER_SECRET")
TOKEN_ID = os.getenv("NETSUITE_TOKEN_ID")
TOKEN_SECRET = os.getenv("NETSUITE_TOKEN_SECRET")
```

## Project Structure

Below is the structure of the project, detailing the main components and their purposes:
```
spt-finance/
│
├── app.py - Main Streamlit application entry point.
│
├── pages/ - Contains individual pages of the Streamlit app.
│ ├── __init__.py
│ ├── overview.py - Overview page.
│ ├── sushibar.py - Page for Sushibar analytics.
│ ├── restaurant.py - Page for Restaurant analytics.
│ └── factory.py - Page for Factory analytics.
│
├── database/
│ ├── __init__.py
│ ├── models.py - SQLAlchemy models for database schema.
│ └── session.py - Manages database sessions.
│
├── analytics/
│ ├── __init__.py
│ ├── profit_loss.py - Profit and Loss calculations.
│ └── projections.py - Future financial projections using Prophet.
│
├── visuals/
│ ├── __init__.py
│ ├── graphs.py - Functions to create various graphs.
│ └── layouts.py - Defines layout/styling for the visuals.
│
└── netsuite_api.py - Functions to interact with NetSuite API.
```

## Running the NetSuite Integration

To run the NetSuite integration, follow these steps:

1. Ensure you have set up your environment variables as described in the "Handling Secrets" section.
2. Navigate to the project directory and run the NetSuite page:
    ```streamlit run pages/4_Netsuite.py```

## Contributing

We welcome contributions! Please read our contributing guidelines for details on how to submit pull requests to the project.

## License

This project is licensed under the MIT License.
