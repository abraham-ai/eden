echo "Starting server..."
python3 setup.py develop
python3 eden/tests/start_server.py &
(
    echo "Running tests..."
    pytest eden/tests
    echo "Stopping server..."
    python3 eden/tests/stop_server.py
)
