import os
import socket
import sys

# check the conncetion status keep alive or close


def check_connection(current_request):
    status = "close"
    for line in current_request:
        if "Connection:" in line:
            status = line.split(": ")[1]
            break
    return status

# return the file name that asked in request


def get_file_name(f_name):
    if f_name == "/":
        return "/index.html", 0
    f_type = f_name[-4:]
    if f_type == ".ico" or f_type == ".jpg":
        return f_name, 1
    return f_name, 0

# get the file from file folder


def get_file_content(f_name, f_type):
    if f_type == 0:
        current_file = open(f_name, "r")
        content = current_file.read().encode("utf-8")
    else:
        current_file = open(f_name, "rb")
        content = current_file.read()
    return content

# return the response to client


def get_response(f_name, type, status):
    if f_name == "/redirect":
        status = "close"
        response = f"HTTP/1.1 301 Moved Permanently\r\nConnection:" \
                   f" {status}\r\nLocation: /result.html\r\n\r\n".encode(
                       "utf-8")
    elif not os.path.exists("files" + f_name):
        status = "close"
        response = f"HTTP/1.1 404 Not Found\r\nConnection: {status}\r\n\r\n".encode(
            "utf-8")
    else:
        f_name = "files"+f_name
        f_content = get_file_content(f_name, type)
        response = f"HTTP/1.1 200 OK\nConnection: {status}\r\n" \
                   f"Content-Length: {len(f_content)}\r\n\r\n".encode(
                       "utf-8") + f_content
    return response, status


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = int(sys.argv[1])
    server.bind(('', port))
    BUFFER_SIZE = 1024
    server.listen(10)

    while True:
        client_socket, client_address = server.accept()
        client_socket.settimeout(1.0)
        status = ""
        # if the connection status is not close keep the same connection open
        while status != "close":
            request = ""
            while "\r\n\r\n" not in request:
                try:
                    request += client_socket.recv(BUFFER_SIZE).decode("utf-8")
                except socket.timeout as e:
                    print("timeout")
                    break
                except:
                    print("error")
                    break
            if request == "":
                break
            # in case of more than 1 request in same connection
            request_arr = request.split("\r\n\r\n")
            request_arr = request_arr[:-1]
            for request in request_arr:
                print('Received: ', request)
                request = request.split("\r\n")
                file_name, type = get_file_name(request[0].split(" ")[1])
                status = check_connection(request)
                response, status = get_response(file_name, type, status)
                client_socket.send(response)
        client_socket.close()
