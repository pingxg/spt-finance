# Finance Dashboard

Welcome to the Finance Dashboard, a Streamlit application designed to streamline and visualize the profit and loss for various projects within a company, including Sushibar, restaurants, and factories. This dashboard leverages SQLAlchemy for database management, performs data analytics for insightful financial health checks, and uses Prophet for future financial projections.

## Getting Started

To run this project locally, follow these steps:

1. Clone the repository to your local machine.
2. Ensure you have Python 3.11.8 installed.
3. Install the required dependencies:
    pip install -r requirements.txt
4. Navigate to the project directory and run the application:
    streamlit run app.py


## Project Structure

Below is the structure of the project, detailing the main components and their purposes:

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
└── utils/
├── __init__.py
└── helper_functions.py - Utility functions for common tasks.

csharp
Copy code

## Contributing

We welcome contributions! Please read our contributing guidelines for details on how to submit pull requests to the project.

## License

This project is licensed under the MIT License.
