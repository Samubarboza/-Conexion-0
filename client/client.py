import socket
import threading
import time

def recibir_mensajes(cliente_socket):
    while True:
        try:
            mensaje = cliente_socket.recv(1024).decode()
            if mensaje:
                print('\n' + mensaje)
            else:
                break
        except:
            break

def iniciar_cliente():
    # informacion del servidor al que conectarse
    host = '127.0.0.1' # localhost
    port = 12345
    
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # establecer un tiempo de espera para los intentos de conexion
    cliente_socket.settimeout(5)
    
    intentos = 5
    for intento in range(intentos):
        try:
        # conectarse al servidor
            print(f'[CONECTANDO] Intento {intento + 1} de {intentos}...')
            cliente_socket.connect((host, port))
            break
        except Exception as e:
            print(f'[ERROR] {e}')
            time.sleep(2) # esperamos 2 segundos antes de reintentar
            
    if not cliente_socket:
        # si llega aca es porque no pudo conectar despues de todos los intentos
        print('[FALLO] no se pudo conectar al servidor')
        return
    
        # reestablecer el tiempo de espera a None
    cliente_socket.settimeout(None)
    print('[CONECTADO] conectado al servidor')
    
    try:
        
        # enviar nombre al servidor
        nombre = input('Escribi tu nombre de usuario: ').strip()
        cliente_socket.send(nombre.encode())
        
        # hilo para recibir mensaje del servidor, args ponemos una coma para decir quees una tupla de un elemento
        hilo_receptor = threading.Thread(target=recibir_mensajes, args=(cliente_socket,))
        hilo_receptor.daemon = True
        hilo_receptor.start()
    
        # envio continuo de mensaje
        while True:
            # enviando mensaje al usuario
            mensaje = input('\nEscribe o /exit para salir:\n')
            
            # comprobamos si el usuario quiere salir
            if mensaje.lower() == '/exit':
                print('Cerrando conexion')
                break
            
            cliente_socket.send(mensaje.encode())
            
    except Exception as e:
        print(f'[ERROR] {e}')
    finally:
        cliente_socket.close()
        print('[DESCONECTADO] cliente cerrado')