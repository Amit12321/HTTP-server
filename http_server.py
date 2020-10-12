# Imports
import socket
import re
from os import path
from urllib.parse import urlparse

# Constants
IP = "0.0.0.0"
PORT = 80
DEFAULT_URL = "index.html"
REDIRECTION_DICTIONARY = {"page1.html": "page2.html"}
FORBBIDEN_FILES = ["js/no.txt", "forbbiden.txt", "noaccessforyou.txt"]
SOCKET_TIMEOUT = 5.0


def get_file_data(filename, filetype):
    """ Get data from file. We assume the file requested here does exist, as we checked it before invoking this function. """
    if filetype == ".jpg":
        with open(filename + filetype, "rb") as f:
            data = f.read()
    else:
        with open(filename + filetype, "r", encoding='utf-8') as f:
            data = f.read()
    return data


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""
    # TO DO : add code that given a resource (URL and parameters) generates the proper response
    if resource == "":
        url = DEFAULT_URL
    else:
        url = resource

    http_header = ""
    data = "\r\n"
    # TO DO: check if URL had been redirected, not available or other error code. For example:
    if url in REDIRECTION_DICTIONARY:
        http_header = f"HTTP/1.1 302 Found\r\nLocation: {REDIRECTION_DICTIONARY[url]}\r\n"
    elif not path.isfile(url):
        http_header = f"HTTP/1.1 404 Not Found\r\n"
    elif url in FORBBIDEN_FILES:
        http_header = "HTTP/1.1 403 Forbidden\r\n"
    else:
        filename, filetype = path.splitext(urlparse(url).path)
        http_header = f"HTTP/1.1 200 OK\r\nContent-Length: {path.getsize(filename + filetype)}\r\n"
        if filetype == '.html' or filetype == "html":
            http_header += "Content-Type: text/html; charset=utf-8"
        elif filetype == '.jpg' or filetype == "jpg":
            http_header += "Content-Type: image/jpeg"
        elif filetype == '.js' or filetype == "js":
            http_header += "Content-Type: text/javascript; charset=UTF-8"
        elif filetype == '.css' or filetype == "css":
            http_header += "Content-Type: text/css"
        http_header += "\r\n"
        data += str(get_file_data(filename, filetype))
    http_response = http_header + data
    client_socket.send(http_response.encode())


def validate_http_request(request):
    """ Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL """
    if re.match("^GET\s\S+\sHTTP/1[.]1\\r\\n", request):
        return (True, request.split(" ")[1][1::])
    else:
        return (False, None)


def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print('Client connected')
    while True:
        client_request = client_socket.recv(2048).decode()
        valid_http, resource = validate_http_request(client_request)
        if valid_http:
            print('Got a valid HTTP request')
            handle_client_request(resource, client_socket)
            break
        else:
            print('Error: Not a valid HTTP request')
            break
    print('Closing connection')
    client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))

    run = True
    while run:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        try:
            client_socket.settimeout(SOCKET_TIMEOUT)
            handle_client(client_socket)
        except socket.error as e:
            print(f"Recieved error: {e}. Quitting...")
            continue


if __name__ == "__main__":
    # Call the main handler function
    main()
