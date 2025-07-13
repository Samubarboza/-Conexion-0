import socket
import threading

clientes_conectados = []
clientes_info = {}

# funcion para mandar mensajes a todos los conectados
def broadcast(mensaje, cliente_emisor):
    for cliente in clientes_conectados:
        if cliente != cliente_emisor: # si es el emisor, no le mandamos
            try:
                cliente.send(mensaje.encode()) # envio de mensaje codificado en bytes
            except:
                # si no se pudo mandar, se desconecto o hubo error
                cliente.close()
                if cliente in clientes_conectados:
                    clientes_conectados.remove(cliente)
                    
# funcion que maneja la comunicacion dde un solo cliente, corre en hilo separado para atender varios
def gestionar_cliente(cliente_socket, direccion_cliente):
    nombre = cliente_socket.recv(50).decode().strip()
    # guardamos el nombre en el direccionario
    clientes_info[cliente_socket] = nombre
    
    print(f'[NUEVO] {nombre} conectado desde, {direccion_cliente}')
    
    # agregamos el socket del cliente a la lista global de conectados
    clientes_conectados.append(cliente_socket)
    print(f'[NUEVO] {nombre} conectado desde {direccion_cliente}.\nTotal de clientes {len(clientes_conectados)}')
    
    broadcast(f'{nombre} se unio al chat', cliente_socket)
    
    try:
        # seguir escuchando mensaje hasta que sedescoencte
        while True:
            datos = cliente_socket.recv(1024)
            
            if not datos: # si no hay mensajes, se desconecto el cliente y salimos del bucle
                break
            
            mensaje_recibido = datos.decode()
            
            print(f'{direccion_cliente} {mensaje_recibido}') # mensaje del cliente en consola del servidor
            
            # nombre del cliente para mostrar en el chat
            nombre = clientes_info.get(cliente_socket, 'desconocido')
            broadcast(f'[{nombre}] {mensaje_recibido}', cliente_socket)
            
    except Exception as e:
        # si hay error mostramos
        print(f'[ERROR] {e}')
        
    finally:
        # si se desconecta o hay error, avisamos a los demas
        broadcast(f'{nombre} se ha desconectado', cliente_socket)
        
        # sacamos de el socekt y el nombre asociado
        clientes_info.pop(cliente_socket, None)
        cliente_socket.close() # cerramos el socekt
        if cliente_socket in clientes_conectados:
            clientes_conectados.remove(cliente_socket)
            
        print(f'[DESCONECTADO] {direccion_cliente} desconectado')

# funcion para iniciar el servidor y crear hilos        
def iniciar_servidor():
    host = '127.0.0.1' # ip local
    port = 12345 # puerto donde escucha el servidor
    
    # creamos un socket tcp protocolo confiable, con sock transportamos datos de manera segura y ordenada a diferencia de udp
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # configuramos socket, a nivel general y reutilizamos puerto si es que queremos arrancar otv el servidor
    servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        servidor_socket.bind((host, port)) # con bind asociamos a la ip del puerto
        servidor_socket.listen()
        print(f'[INICIADO] servidor iniciado en {host}:{port}')
        
        while True: # aceptamos clientes todo el tiempo
            cliente_socket, direccion_cliente = servidor_socket.accept() # aguardamos que se conecte
            
            # cuando un cliente se conecta, creamos un hilo para manejarlo con la funcion gestionar
            hilo_cliente = threading.Thread(target=gestionar_cliente, args=(cliente_socket, direccion_cliente))
            hilo_cliente.daemon = True
            hilo_cliente.start()
            
            print(f'[CONEXIONES ACTIVAS] {threading.active_count() - 1}')
            
    except KeyboardInterrupt:
        # cuando cerramos el servidor 
        print('\nEl servidor se esta apagando')
    
    finally:
        servidor_socket.close() # cerramos el socket del servidor
        print('[CERRADO socket cerrado]')