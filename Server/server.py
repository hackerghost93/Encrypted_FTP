from multiprocessing import Process
from Crypto.Cipher import AES
import os
import sys
import threading
import socket
import platform


printing_lock = threading.Lock()
obj = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
counterTcp = 0
counterUdp = 0


def udp_handler(client_socket, address, number, data, filename='ahmed.txt'):   # this will take an address and send the file to the client
    print('udp client is starting ' ,address)
    if os.path.isfile(filename):
        print('file is valid ');
        file_size = os.path.getsize(filename)
        #socket.sendto(str(file_size).zfill(25), address)  # sending size
    else:
        print("'file couldn't be found thread is terminating'")
        return -1
    with open(filename, 'rb') as f:
        while True:
            bytes_to_send = f.read(1024)
            if bytes_to_send != b'':
                if len(bytes_to_send) % 16 != 0:
                    bytes_to_send += bytes('\0'*(16-len(bytes_to_send)%16),'utf-8')
                    print(bytes_to_send)
                    ciphertext = obj.encrypt(bytes_to_send)
                    print(ciphertext)
                else:
                    ciphertext = obj.encrypt(bytes_to_send)
            else:
                ciphertext = b''
            client_socket.sendto(ciphertext, address)
            if bytes_to_send == b'':
                print('file completed of thread', number)
                break
    print('thread number', number, 'is terminating')


def tcp_handler(client_socket, address, number, filename='ahmed.txt'):
    print('tcp client', number, 'is starting with address', str(address))
    if os.path.isfile(filename):
        # print('file is valid ');
        file_size = str(os.path.getsize(filename))
        print('file size is',file_size)
        #assert isinstance(file_size, object)
        client_socket.send(bytes(file_size,'utf-8')) # sending size
    else:
        print("'file couldn't be found thread is terminating'")
        client_socket.close()
        return -1
    print('sending file')
    with open(filename, 'rb') as f:
        while True:
            bytes_to_send = f.read(1024)
            if bytes_to_send != b'':
                if len(bytes_to_send) % 16 != 0:
                    bytes_to_send += bytes('\0' * (16 - len(bytes_to_send) % 16), 'utf-8')
                    print(bytes_to_send)
                    ciphertext = obj.encrypt(bytes_to_send)
                    print(ciphertext)
                else:
                    ciphertext = obj.encrypt(bytes_to_send)
            else:
                ciphertext = b''
            client_socket.send(ciphertext)
            if bytes_to_send == b'':                   # terminating condition
                print('file completed of thread', number)
                break
    client_socket.close()
    print('thread number', number, 'is terminating')


def udp_server(name):
    print(name)
    threads = []
    host = '127.0.0.1'
    port = 5671
    connections = 0
    printing_lock.acquire()
    print(name,' process has just started')
    printing_lock.release()
    listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)          # socket creation
    listener_socket.bind((host, port))                                         # add to socket the address and port
    #listener_socket.setblocking(0)
    FILE_CONSTANT = 'family.jpeg'
    print('udp process is waiting for any datagram')
    agenda = []
    while True:
        data, address = listener_socket.recvfrom(1024)
        print('data received from address', str(address))
        if address not in agenda:
            agenda.append(address)
            try:
                connections += 1
                t1 = threading.Thread(target=udp_handler, args=(listener_socket, address, connections, data))
                t1.start()
                threads.append(t1)
            except:
                print('cannot be done')
    listener_socket.close()


def tcp_server(name):
    #print(name)
    threads = []
    connections = 0
    host = '127.0.0.1'
    port = 5572
    printing_lock.acquire()
    print(name, ' process has just started')
    printing_lock.release()
    listener_socket = socket.socket()
    listener_socket.bind((host, port))
    listener_socket.listen(1000)
    print('tcp process is waiting to accept any connection')
    while True:
        try:
            connection_socket, address = listener_socket.accept()
            connections += 1
            t1 = threading.Thread(target=tcp_handler, args=(connection_socket, address, connections))
            t1.start()
            t1.join()
        except:
            break
    listener_socket.close()


def main():
    print('current platform',platform.platform())
    print('Main process has just started')
    p1 = Process(target=udp_server, args=('the udp ftp server shadow',))
    p2 = Process(target=tcp_server, args=('the tcp ftp server ghost' ,))
    p1.start()
    p2.start()
    #p1.join()
    #p2.join()
    while True:
        order = input("Enter quit to terminate -> ")
        if order == 'quit':
            p1.terminate()
            p2.terminate()
            break
    print('program is terminating.. goodbye')

if __name__ == '__main__':              # is running as a script
    main()                              # run main function
