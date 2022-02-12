echo "installing pytest..."
pip install pytest
echo "Starting server..."
python3 setup.py develop
python3 eden/tests/start_server.py --port 5656 --host "0.0.0.0" --redis-host "localhost" --max-num-workers 1 &
(
    echo "Running tests..."
    pytest eden/tests 
    echo "Stopping server..."
    python3 eden/tests/stop_server.py
)
echo "removing test_image.jpg"
rm test_image.jpg
echo "tests complete!"