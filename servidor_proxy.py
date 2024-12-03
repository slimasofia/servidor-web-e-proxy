import socket
import os

# função para buscar o conteúdo do cache ou servidor remoto
def fetch_from_cache_or_server(url, cache_dir):
    # normaliza o nome do arquivo no cache (substitui '/' por '_')
    file_name = url.replace('/', '_')
    cache_path = os.path.join(cache_dir, file_name) # cria o caminho completo do arquivo de cache
    
    # verifica se o arquivo ou diretório especificado em 'cache_path' existe no sistema de arquivos
    if os.path.exists(cache_path):
        print(f"Cache hit: {url}")          # msg indicando que o conteúdo foi encontrado
        with open(cache_path, 'rb') as f:   # abre o arquivo de cache no modo 'rb'
            return f.read()                 # retorna o conteúdo armazenado em cache
    
    print(f"Cache miss: {url}")             # msg indicando que o conteúdo não foi encontrado
    
    # verifica e remove o prefixo "http://" ou "https://"
    if url.startswith("http://"):
        url = url.replace("http://", "")
    elif url.startswith("https://"):
        url = url.replace("https://", "")
    
    # dividindo a url em 'host' e 'path' 
    host, _, path = url.partition('/')
    path = '/' + path if path else '/'
    
    try:
        print(f"Conectando ao servidor remoto: {host}")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # cria um novo socket, os parâmetros passados especificam 
                                                                          # que ele usará o protocolo IPv4 e o protocolo TCP, respectivamente
   
        server_socket.connect((host, 80))                                 # tenta estabelecer uma conexão TCP com o servidor remoto 
                                                                          # especificado em 'host' na porta 80 (porta padrão pra HTTP)
        
        # Envia a solicitação GET
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n" # cria a solicitação HTTP GET no ofrmato correto
        server_socket.sendall(request.encode())   # converte a string 'request' para bytes (necessário pra enviar os dados através do socket) 
                                                  # e envia a solicitação HTTP ao servidor remoto 
        
        # Recebe a resposta
        response = b""      # inicializa variável response como string vazia
        while True:         # continua até que toda a resposta seja recebida
            data = server_socket.recv(4096) # (lê até 4096 bytes)
            if not data:    # verifica se não há mais dados recebidos
                break
            response += data
        
        server_socket.close()       # fecha a conexão TCP com servidor
        
        # Armazena a resposta no cache
        with open(cache_path, 'wb') as f:
            f.write(response)
        
        return response
    
    except Exception as e:
        print(f"Erro ao buscar do servidor remoto: {e}")
        return b"HTTP/1.1 502 Bad Gateway\r\n\r\nErro ao buscar do servidor remoto."

# função principal para executar o servidor proxy
def start_proxy_server(host='0.0.0.0', port=8888):
    cache_dir = "./cache"  # Diretório para armazenar o cache
    os.makedirs(cache_dir, exist_ok=True)  # Cria o diretório de cache se não existir
    
    # Cria o socket para o servidor proxy
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # permite reutilizar a porta
    proxy_socket.bind((host, port))                                     # associa o socket ao IP e porta especificados 
    proxy_socket.listen(5)   # coloca o socket em modo de escuta para que o servidor possa aceitar conexões de entrada
                             # o parâmetro '5' indica que o servidor pode manter até 5 conexões aguardando para serem processadas 
                             # enquanto o servidor lida com outras conexões.

    print(f"Servidor proxy iniciado em http://{host}:{port}")
    
    while True:
        # aceita conexões de clientes
        client_socket, client_address = proxy_socket.accept()
        print(f"Conexão recebida de {client_address}")
        
        try:
            # recebe a requisição do cliente
            request = client_socket.recv(4096).decode()
            print("Requisição recebida:")
            print(request)
            
            # processa a linha de requisição
            lines = request.splitlines()
            if len(lines) > 0:
                method, path, _ = lines[0].split()
                if method == "GET":
                    if path.startswith("http://"):          # se a url começa com 'http://'
                        url = path.split("http://", 1)[1]   # remove esse prefixo
                    elif path.startswith("/"):
                        url = path[1:]  # remove o primeiro "/"
                    else:
                        url = path
                    
                    # busca o conteúdo no cache ou servidor remoto
                    response = fetch_from_cache_or_server(url, cache_dir)
                    
                    # envia a resposta para o cliente
                    client_socket.sendall(response)
        except Exception as e:
            print(f"Erro ao processar a requisição: {e}")
            client_socket.sendall(b"HTTP/1.1 500 Internal Server Error\r\n\r\nErro no servidor proxy.")
        
        # fecha a conexão com o cliente
        client_socket.close()

if __name__ == "__main__":
    start_proxy_server()
