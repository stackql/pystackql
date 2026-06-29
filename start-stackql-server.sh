#!/bin/bash
# Start the stackql server (port 5466) if it is not already running.
# Matches the 'srv' invocation specifically so a repo path containing the word
# "stackql" does not produce false "already running" detections.
ADDRESS=127.0.0.1
PORT=5466

if pgrep -f "stackql.*srv" >/dev/null 2>&1; then
    echo "server is already running"
else
    echo "starting stackql server on ${ADDRESS}:${PORT}..."
    # Bind to loopback only: the tests connect on 127.0.0.1, binding to loopback
    # avoids firewall prompts and does not expose the server to the network.
    nohup ./stackql -v --pgsrv.address=${ADDRESS} --pgsrv.port=${PORT} srv > stackql-server.log 2>&1 &
    sleep 5
fi
