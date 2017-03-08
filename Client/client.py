import os
import sys
import socket
import threading
import platform
from Crypto.Cipher import AES


server_udp = ('127.0.0.1', 5671)
server_tcp = ('127.0.0.1', 5572)
obj = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')


def udp_request(number):
    print('requesting udp file')
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.bind(('127.0.0.1',0))
    message = 'here'
    try:
        my_socket.sendto(bytes(message,'utf-8'), server_udp)
        print('sent packet handshaking thread number', number)
    except:
        print('something went wrong in handshaking thread number',number)
    with open(str(number)+'_udp.txt','wb') as f:
        while True:                     # receiving the file
            buff , address= my_socket.recvfrom(1024)
            print(buff)
            #print(str('buff'))
            if buff == b'':
                print('file completed')
                break
            new_buff = obj.decrypt(buff)
            new_buff = new_buff.split(b'\0',1)[0]
            f.write(new_buff)
    print('ending udp thread number', number)
    my_socket.close()


def tcp_request(number):
    print('requesting tcp file')
    my_socket = socket.socket()
    my_socket.bind(('', 0))         # 0 means any port available
    print('listening on port:', my_socket.getsockname()[1])
    try:
        my_socket.connect(server_tcp)
    except:
        print("couldn't connect to server socket")
        return
    file_size = int(str(my_socket.recv(25).decode('utf-8')))
    print('file size is for thread', number, '=', file_size)
    file_name = str(number)+'_tcp.txt'
    total_received = 0
    with open(file_name,'wb') as f:
        while True:
            try:
                data = my_socket.recv(1024)
                total_received += len(obj.decrypt(data))
                print('thread number' ,number, 'download complete', total_received/file_size*100)
                if data == b'':
                    break
                if len(data) == 0:
                    break
                f.write(obj.decrypt(data).split(b'\0',1)[0])
            except:
                my_socket.close()
                print('something went wrong in receiving')
                break
    print('file successfully received in thread ', number)
    my_socket.close()



def main():
    tcp_count = int(input("Enter number of tcp -> "))
    udp_count = int(input("Enter number of udp -> "))
    print('creating tcp threads')
    threads = []
    for i in range(1, tcp_count+1):
        t = threading.Thread(target=tcp_request, args=(i,))
        t.start()
        threads.append(t)
    print('creating udp threads')
    for i in range(1, udp_count+1):
        t = threading.Thread(target=udp_request, args=(i,))
        t.start()
        threads.append(t)
    order = input('self destruct process on your click')
    print('terminating threads')
    #for t in threads:
        #t.terminate()

    print('everything is put to ashes')

if __name__ == '__main__':
    main()
