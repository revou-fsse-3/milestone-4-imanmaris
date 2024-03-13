from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# --- yg gapake env file ---

# username = "root"
# password = "Allahuakbar99"
# host = "127.0.0.1"
# database_name = "coba_w18"
# ConnectionString = f'mysql+mysqlconnector://{username}:{password}@{host}/{database_name}'
# engine = create_engine(ConnectionString)

# connection = engine.connect()

# print(os.path.exists('app/templates/products/product_home.html'))

# --- yg pake env file ---
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
database_name = os.getenv("DB_NAME")

# Connection to Database
print("Connection to db SQL Database")
ConnectionString = f'mysql+mysqlconnector://{username}:{password}@{host}/{database_name}'
engine = create_engine(ConnectionString)

# Test connection activated
connection = engine.connect()
Session = sessionmaker(connection)
print(f'Success Connecting to db SQL Database at {host}')