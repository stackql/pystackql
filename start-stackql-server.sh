# start server if not running
echo "checking if server is running"
if [ -z "$(ps | grep stackql)" ]; then
    nohup ./stackql -v --pgsrv.port=5466 srv &
    sleep 5
else
    echo "server is already running"
fi