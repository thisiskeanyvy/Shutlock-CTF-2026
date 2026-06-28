import os
import socket
from aes_given import encrypt
 
FLAG = os.getenv("FLAG", "SHLK{test}")
MAX = 1000
 
def sendline(f, data):
    f.write(data + b"\n")
    f.flush()
 
 
def handle(c):

    f = c.makefile("rwb")
 
    key = os.urandom(16)
    diagonal = bytes([key[0], key[5], key[10], key[15]])
    sendline(f, diagonal.hex().encode())
    sendline(f, b"Send me a plaintext to encrypt (32 hex chars), or KEY:<key> to submit")
 
    q = 0
    while q < MAX:
        line = f.readline().strip().decode(errors="replace")
        if not line:
            break
 
        if line.startswith("KEY:"):

            try:
                guess = bytes.fromhex(line[4:])

            except ValueError:

                guess = b""
            
            if guess==key:
                sendline(f,FLAG.encode())
            else:
                sendline(f, b"Nope!")

            break
 
        try:
            ct = encrypt(bytes.fromhex(line), key)
        except (ValueError, AssertionError):
            sendline(f, b"Invalid plaintext")
            q += 1
            continue
 
        sendline(f, ct.hex().encode())
        q += 1
 
 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind(("0.0.0.0", 8000))
server.listen()
 
while True:

    c, _ = server.accept()
    try:
        
        handle(c)
        
    except (OSError, EOFError):

        pass
    finally:
        c.close()
