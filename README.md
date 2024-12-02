# don't actually use empty strings
export DB_USER='';    
export DB_PASS='';
export DB_HOST='';
export DB_NAME='';
# to run tests
python test_endpoints.py
# to run server
python endpoints.py


# For database migratons 
# first time
alembic init migrations
# when you change the DB in python files
alembic revision --autogenerate -m "Description of changes"
alembic upgrade <insert_hash_here>