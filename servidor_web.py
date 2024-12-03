# importando o módulo socket, ele é uma biblioteca padrão que fornece suporte para a comunicação em rede 
# usando os protocolos TCP e UDP. Através dele é possível enviar e receber dados através de conexões de rede.
import socket
# biblioteca que fornece as funções para interagir com o sistema operacional (permite que os programas manipulem 
# arquivos e diretórios, coletem informações do sistema e controlem processos)
import os      

# Função que cria a resposta HTTP
def create_http_response(file_path):
    if os.path.exists(file_path) and os.path.isfile(file_path): # verificando se o caminho existe no sistema de arquivos e e se o caminho é um arquivo
        with open(file_path, 'rb') as f:                        # abre o arquivo no modo "rb" (read binary)
            content = f.read()                                  # lê o conteúdo completo do arquivo e armazena em "content"
        
        # se o arquivo existe e foi lido com sucesso, é construída uma resposta com o código de status HTTP 200 OK:
        header = "HTTP/1.1 200 OK\r\n"                          # especifica a versão do protocolo HTTP (HTTP/1.1) e o código de status de solicitação bem-sucedida (200)
        header += "Content-Type: text/html; charset=UTF-8\r\n"  # informa que o conteúdo da resposta é HTML e está codificado como UTF-8
        header += f"Content-Length: {len(content)}\r\n"         # comprimento em bytes do arquivo lido
        header += "\r\n"                                        # sópara separar o cabeçalho do corpo

        return header.encode() + content                        # concatenando o cabeçalho e o corpo e retornando eles como a resposta HTTP
    else:
        # Caso o arquivo não exista
        header = "HTTP/1.1 404 Não Encontrado\r\n"                   # especifica o código de status 404 - o recurso solicitado não foi encontrado no servidor
        header += "Content-Type: text/html; charset=UTF-8\r\n"
        header += "\r\n"
        body = "<html><body><h1>404 Não Encontrado</h1></body></html>" # corpo da repsosta   
        return header.encode() + body.encode()                         # resposta HTTP 


# Função principal que executa o servidor web - define onde e como o servidor escutará conexões de clientes
# o parâmetro '0.0.0.0' significa que o servidor aceitará conexões de qualquer interface de rede no dispositivo (localhost e endereços IP externos)
# (se fosse '127.0.0.1' o servidor aceitaria conexões da própria máquina apenas)
def start_server(host='0.0.0.0', port=8080):  
    # Cria um socket TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # cria um novo socket, os parâmetros passados especificam 
                                                                      # que ele usará o protocolo IPv4 e o protocolo TCP, respectivamente
    server_socket.bind((host, port))                                  # associa o socket ao host e port especificados
    server_socket.listen(1)                                           # limite de 1 cliente simultâneo

    print(f"Servidor iniciado em http://{host}:{port}")

    while True:
        # Aguarda uma conexão de um cliente
        client_socket, client_address = server_socket.accept()        # aguarda uma conexão de um cliente e quando ele se conecta, retorna: 
                                                                      # novo socket para comunicação com ele e endereço IP e porta do cliente conectado
        print(f"Conexão recebida de {client_address}")                # informa que o cliente se conectou

        # recebe a requisição HTTP do cliente
        request = client_socket.recv(1024).decode()                   # lê até 1024 bytes da requisição enviada pelo cliente e retorna os dados como um objeto binário
        print("Requisição recebida: ")
        print(request)

        lines = request.splitlines()                                   # divide a requisição em linhas, resultando em uma lista de strings
        if len(lines) > 0:                                             # verifica se há pleo menos uma linha na requisição
                                                                       # a primeira linha é a que contém o método HTTP e o caminho (Ex.: GET /index.html HTTP/1.1)
            method, path, _ = lines[0].split()                         # divide a primeira linha em uma lista de 3 strings e atribui cada parte às variáveis 'method', 'path' e '_' 
                                                                       # (a versão do protocolo é ignorada, não é utilizada aqui)
            # Converte o caminho solicitado (retira o '/') e monta o caminho completo
            file_path = '.' + path

            # Cria a resposta HTTP
            response = create_http_response(file_path)

            # Envia a resposta para o cliente
            client_socket.sendall(response)

        # Fecha a conexão com o cliente
        client_socket.close()

if __name__ == "__main__":
    start_server()