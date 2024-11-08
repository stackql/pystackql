# install packages
# pip.exe install -r requirements.txt --user
# pip install psycopg[binary]

# Load environment variables
. .\tests\creds\env_vars\test.env.ps1

$env:PYTHONPATH = "C:\LocalGitRepos\stackql\python-packages\pystackql"

# Run tests
python.exe -m tests.pystackql_tests
