from eden.client import Client


def stop_server():
    c = Client(url="http://127.0.0.1:5656", username="test_abraham")
    c.stop_host(3)


if __name__ == "__main__":
    stop_server()
    print("stopped server")
