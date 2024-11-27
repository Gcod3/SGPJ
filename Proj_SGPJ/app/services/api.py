import requests
from requests.exceptions import RequestException

def get_data(cnpj, chave_api):
    print('Teste', cnpj)
    headers = {
        'api-key': str(chave_api),
        'Content-Type': 'application/json'
    }
    body = {
        "search": {
            "search_type": "cnpj",
            "search_key": str(cnpj)
        },
        "with_attachments": False
    }
    try:
        response = requests.post('http://127.0.0.1:5000/buscar', headers=headers, json=body)
        response.raise_for_status()  # Lança uma exceção para respostas 4xx/5xx
        return response.json()
    except RequestException as e:
        print(f"Erro ao buscar dados: {e}")
        return None

def get_results(page, request_id, chave_api, filter_by_processos=None):
    print(f"Iniciando get results para a página {page}")
    
    headers = {
        'api-key': str(chave_api),
    }

    # Definir a URL base para consulta
    url = f'http://127.0.0.1:5000/responses?request_id={request_id}&page_size=100&page={page}'
    
    # Se houver um filtro de processos, vamos adicioná-lo à URL
    if filter_by_processos:
        process_filter = ','.join(filter_by_processos)  # Junta os IDs com vírgula
        url += f"&processos={process_filter}"  # Adiciona o filtro de processos à URL

    print(f"URL da API: {url}")  # Log da URL que será chamada

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(f"Finalizando get results para a página {page}")
        print(response)
        return response.json()
    except RequestException as e:
        print(f"Erro ao recuperar resultados: {e}")
        return None





def get_results_detalhes(page, request_id, chave_api, codigo_processo):
    print(f"Iniciando get results para a página {page}")
    headers = {'api-key': str(chave_api)}

    while True:  # Continua o loop até que todas as páginas sejam verificadas
        url = f'http://127.0.0.1:5000/responses?request_id={request_id}&page_size=100&page={page}&codigo_processo={codigo_processo}'
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            for processo in data.get('processos', []):
                if processo.get('processo', {}).get('codigo') == codigo_processo:
                    print(f"Processo encontrado na página {page}")
                    return processo  # Retorna o processo específico se encontrado

            # Checa se existe próxima página
            if page >= data.get('total_pages', 0):
                print("Processo não encontrado em nenhuma página.")
                break  # Sai do loop se não houver mais páginas para verificar

            page += 1  # Incrementa para verificar a próxima página
        except RequestException as e:
            print(f"Erro ao recuperar resultados: {e}")
            return None

    return None  # Retorna None se o processo não for encontrado em nenhuma página

def get_Users(chave_api):
    headers = {
        'api-key': str(chave_api),
    }
    url = f'http://127.0.0.1:5000/GetUsers'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print('API get user')
        return response.json()
    except RequestException as e:
        print(f"Erro ao recuperar resultados: {e}")
        return None
    
def update_user(chave_api, userData):
    headers = {
        'api-key': str(chave_api),
        'Content-Type': 'application/json',  # Especifica que o conteúdo é JSON
    }
    url = f'http://127.0.0.1:5000/update_user/{userData["id"]}'
    
    try:
        # Faz a requisição PUT enviando o JSON no corpo
        response = requests.put(url, json=userData, headers=headers)
        response.raise_for_status()  # Lança uma exceção para status de erro
        print(response.json())
        return response.json()
    except RequestException as e:
        print(f"Erro ao recuperar resultados: {e}")
        return None
def add_user(chave_api, userData):
    headers = {
        'api-key': str(chave_api),
        'Content-Type': 'application/json',  # Especifica que o conteúdo é JSON
    }
    url = f'http://127.0.0.1:5000/create_user'
    
    try:
        # Faz a requisição PUT enviando o JSON no corpo
        response = requests.put(url, json=userData, headers=headers)
        response.raise_for_status()  # Lança uma exceção para status de erro
        print(response.json())
        return response.json()
    except RequestException as e:
        print(f"Erro ao gravar usuário resultados: {e}")
        return None
    
def remove_user(chave_api, userData):
    headers = {
        'api-key': str(chave_api),
        'Content-Type': 'application/json',  # Especifica que o conteúdo é JSON
    }
    url = f'http://127.0.0.1:5000/delete_user/{userData["id"]}'
    
    try:
        # Faz a requisição PUT enviando o JSON no corpo
        response = requests.delete(url, json=userData, headers=headers)
        response.raise_for_status()  # Lança uma exceção para status de erro
        print(response.json())
        return response.json()
    except RequestException as e:
        print(f"Erro ao gravar usuário resultados: {e}")
        return None
    
def login(chave_api, userData):
    headers = {
        'api-key': str(chave_api),
        'Content-Type': 'application/json',
    }
    url = 'http://127.0.0.1:5000/login'

    try:
        # Incluindo os dados do usuário no corpo da requisição
        response = requests.post(url, headers=headers, json=userData)
        response.raise_for_status()  # Levanta exceções para status >= 400
        data = response.json()
        if data.get('status') == 'success':
            # Aqui você pode acessar 'user_id' e 'perfil' da resposta
            user_id = data.get('user_id')
            perfil = data.get('perfil')
            print(f"User ID: {user_id}, Perfil: {perfil}")
            return data
        else:
            print(f"Login failed: {data.get('message')}")
            return None
    except requests.RequestException as e:
        print(f"Erro ao recuperar resultados: {e}")
        return None
    
def get_Compromissos(chave_api, id_user):
    headers = {
        'api-key': str(chave_api),
    }
    url = f'http://127.0.0.1:5000/GetCompromissos'
    try:
        response = requests.get(url, headers=headers, json={"id_user": id_user})
        response.raise_for_status()
        print('API get compromissos')
        return response.json()
    except RequestException as e:
        print(f"Erro ao recuperar resultados: {e}")
        return None  
     
def add_compromisso(chave_api, CompromissoData):
    headers = {
        'api-key': str(chave_api),
        'Content-Type': 'application/json',  # Especifica que o conteúdo é JSON
    }
    url = f'http://127.0.0.1:5000/create_compromisso'
    
    try:
        # Faz a requisição PUT enviando o JSON no corpo
        response = requests.put(url, json=CompromissoData, headers=headers)
        response.raise_for_status()  # Lança uma exceção para status de erro
        print(response.json())
        return response.json()
    except RequestException as e:
        print(f"Erro ao gravar compromisso resultados: {e}")
        return None
    
def remove_compromisso(chave_api, ComprmissoData):
    headers = {
        'api-key': str(chave_api),
        'Content-Type': 'application/json',  # Especifica que o conteúdo é JSON
    }
    url = f'http://127.0.0.1:5000/delete_compromisso/{ComprmissoData["id"]}'
    
    try:
        # Faz a requisição PUT enviando o JSON no corpo
        response = requests.delete(url, json=ComprmissoData, headers=headers)
        response.raise_for_status()  # Lança uma exceção para status de erro
        print(response.json())
        return response.json()
    except RequestException as e:
        print(f"Erro ao deletar evento resultados: {e}")
        return None



# # # # # # # # Testando def's # # # # # # # #
# chave_api = '895a8p82-5k40-37w7-z595-99abxn8q4fgx'
# cnpj = '60892098001990'
# primeira_chamada = get_data(cnpj,chave_api)
# print(primeira_chamada)


# page = 1
# request_id = '17c735f4-0894-4319-b14e-d9723af55130'
# segunda_chamada = get_results(page,request_id,chave_api)
# print(segunda_chamada)