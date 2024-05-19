import socket
import threading

# Function to handle client requests
def handle_client(client_socket, remote_server_sock):
    # Receive client request
    request_data = client_socket.recv(4096).decode()
    
    # Parse HTTP request to extract method, URL, and HTTP version
    try:
        method, url, http_version = request_data.strip().split(' ')
    except ValueError:
        # Invalid request format
        client_socket.sendall(b'HTTP/1.0 500 Internal Error\r\n\r\n')
        client_socket.close()
        return

    # Parse the requested URL
    try:
        protocol, url_without_protocol = url.split('://')
        host_port, path = url_without_protocol.split('/', 1)
        host, port = host_port.split(':')
    except ValueError:
        # URL parsing error
        client_socket.sendall(b'HTTP/1.0 500 Internal Error\r\n\r\n')
        client_socket.close()
        return
    except IndexError:
        # Port not specified in URL
        host = host_port
        port = 80

    # Construct request to the remote server
    remote_request = f"{method} /{path} HTTP/1.0\r\nHost: {host}\r\nConnection: close\r\n\r\n"
    print("sending data to remote server")
    # Send request to the remote server
    remote_server_sock.sendall(remote_request.encode())

    # Forward response from remote server to the client
    while True:
        response_data = remote_server_sock.recv(4096)
        if not response_data:
            break
        client_socket.sendall(response_data)

    # Close connections
    remote_server_sock.close()
    client_socket.close()

# Main function
def main():
    # Create a socket for the proxy server to listen for client connections
    proxy_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the proxy server socket to the local address and port
    proxy_server_sock.bind(('localhost', 8888))  # Use the desired address and port

    # Listen for incoming connections
    proxy_server_sock.listen(5)

    print("[*] Listening on localhost:8888")

    while True:
        # Accept incoming connection from client
        client_socket, addr = proxy_server_sock.accept()
        print("[*] Accepted connection from client: %s:%d" % (addr[0], addr[1]))

        # Create a socket for communication with the remote server
        remote_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the remote server
        remote_server_sock.connect(('example.com', 8888))  

       

        # Handle client request in a new thread
        client_handler = threading.Thread(target=handle_client, args=(client_socket, remote_server_sock))
        print("starting client handler")
        client_handler.start()

if __name__ == "__main__":
    main()

