echo "Starting redis..."
docker run -d  -p 6379:6379 --name redis redis

echo "Building eden..."
docker build . -t eden-test-server

echo "Running eden..."
docker run -d -p --name eden-server 127.0.0.1:5656:5656/tcp eden-test-server 

echo "Running tests..."
pytest eden/tests

echo "Stopping stuff ..."
docker stop redis
docker stop eden-server

