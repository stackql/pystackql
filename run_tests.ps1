# install packages
# pip.exe install -r requirements.txt --user
# pip install psycopg2-binary --user

# Load environment variables
. .\tests\creds\env_vars\test.env.ps1

# Run tests
python.exe -m tests.pystackql_tests
