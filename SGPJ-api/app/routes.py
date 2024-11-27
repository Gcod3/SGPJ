from flask import request, jsonify, session ,Flask
from .utils import validate_api_key
from .models import Request, Processo, User, Compromissos, Responsavel_Processos, db
from sqlalchemy.exc import NoResultFound
from collections import OrderedDict
from werkzeug.security import generate_password_hash

def init_routes(app):

    @app.route('/home')
    def teste_route():
        return 'Hello World'
    
    @app.route('/buscar', methods=['POST'])
    def buscar_processo():
        # Verifica se o cabeçalho API key está correto
        api_key = request.headers.get('api-key')
        if not validate_api_key(api_key):
            return jsonify({'error': 'API key não autorizada'}), 401
        
        # Verifica se o content type é application/json
        if request.headers['Content-Type'] != 'application/json':
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.json
        search_type = data.get('search', {}).get('search_type')
        search_key = data.get('search', {}).get('search_key')

        if search_type != 'cnpj' or not search_key:
            return jsonify({"error": "Invalid search type or search key"}), 400
        
        # Busca no banco de dados
        request_data = Request.query.filter_by(cnpj=search_key).first()
        if request_data:
            return jsonify({"request_id": request_data.request_id}), 200
        else:
            return jsonify({"error": "CNPJ not found"}), 404

    @app.route('/responses', methods=['GET'])
    def get_process_by_request_id():
        # Autenticação por API-Key
        api_key = request.headers.get('api-key')
        if not validate_api_key(api_key):
            return jsonify({'error': 'Unauthorized'}), 401

        # Extrair parâmetros da URL
        request_id = request.args.get('request_id')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 30, type=int)

        # Captura do parâmetro 'processos' se fornecido
        processos_param = request.args.get('processos')
        processos_ids = []
        if processos_param:
            processos_ids = processos_param.split(',')  # Se houver, separa os processos por vírgula

        if not request_id:
            return jsonify({'error': 'Missing request_id parameter'}), 400

        try:
            # Consulta ao banco de dados considerando o filtro de processos (se houver)
            query = Processo.query.filter_by(request_id=request_id)
            
            # Se 'processos_ids' não estiver vazio, filtra pelos processos informados
            if processos_ids:
                query = query.filter(Processo.codigo.in_(processos_ids))

            # Paginação
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            processos = pagination.items

            if not processos:
                return jsonify({'error': 'No processes found for this request_id on page {}'.format(page)}), 404

            # Monta a resposta com os dados dos processos
            response_data = []
            for processo in processos:
                processo_info = {
                    'processo': {
                        'id': processo.id,
                        'codigo': processo.codigo,
                        'nome': processo.nome,
                        'nivel_sigilo': processo.nivel_sigilo,
                        'tribunal_acronimo': processo.tribunal_acronimo,
                        'data_distribuicao': processo.data_distribuicao.isoformat() if processo.data_distribuicao else None,
                        'valor': str(processo.valor),
                        'estado': processo.estado,
                        'fase': processo.fase,
                        'ultima_atualizacao': processo.ultima_atualizacao.isoformat() if processo.ultima_atualizacao else None,
                        'created_at': processo.created_at.isoformat() if processo.created_at else None,
                        'updated_at': processo.updated_at.isoformat() if processo.updated_at else None,
                        'status': processo.status,
                        'fase_processo': processo.fase_processo,
                        'justice': processo.justice,
                        'tribunal': processo.tribunal,
                        'county': processo.county,
                        'free_justice': processo.free_justice,
                        'judge': processo.judge,
                        'situation': processo.situation,
                        'response_id': processo.response_id,
                        'request_id': processo.request_id
                    },
                    'classificacoes': [{ 'id': c.id, 'codigo': c.codigo, 'nome': c.nome } for c in processo.classificacoes],
                    'tribunais': [{ 'id': t.id, 'nome': t.nome } for t in processo.tribunais],
                    'partes': [{ 'id': p.id, 'nome': p.nome, 'documento_principal': p.documento_principal,
                                'entity_id': p.entity_id, 'entity_type': p.entity_type, 'tipo_pessoa': p.tipo_pessoa,
                                'lado': p.lado, 'advogados': [{ 'id': a.id, 'nome': a.nome, 
                                'documento_principal': a.documento_principal, 'entity_type': a.entity_type,
                                'document': a.document, 'document_type': a.document_type } for a in p.advogados] 
                            } for p in processo.partes],
                    'assuntos': [{ 'id': a.id, 'codigo': a.codigo, 'nome': a.nome } for a in processo.assuntos],
                    'etapas': [{ 'id': e.id, 'etapa_id': e.etapa_id, 'data_etapa': e.data_etapa.isoformat() if e.data_etapa else None,
                                'conteudo': e.conteudo, 'quantidade_etapas': e.quantidade_etapas, 'lawsuit_cnj': e.lawsuit_cnj,
                                'lawsuit_instance': e.lawsuit_instance, 'private': e.private } for e in processo.etapas],
                    'passos': [{ 'id': ps.id, 'step_id': ps.step_id, 'nome': ps.nome, 'step_date': ps.step_date.isoformat() if ps.step_date else None,
                                'lawsuit_cnj': ps.lawsuit_cnj, 'lawsuit_instance': ps.lawsuit_instance, 'private': ps.private } 
                            for ps in processo.passos],
                }
                response_data.append(processo_info)

            return jsonify({
                'total_pages': pagination.pages,
                'total_items': pagination.total,
                'current_page': page,
                'per_page': per_page,
                'processos': response_data
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

        
    @app.route('/GetUsers', methods=['GET'])
    def get_users():
        # Verifica se o cabeçalho API key está correto
        api_key = request.headers.get('api-key')
        if not validate_api_key(api_key):
            return jsonify({'error': 'Unauthorized'}), 401

        try:
            # Consulta todos os usuários no banco de dados
            users = User.query.all()

            # Formatar os dados em uma lista de dicionários
            users_list = []
            for user in users:
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'password_hash': user.password_hash,
                    'perfil': user.perfil
                }
                users_list.append(user_data)

            # Retornar a lista de usuários como JSON
            return jsonify({'users': users_list}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/create_user', methods=['PUT'])
    def create_user():
        data = request.get_json()
        user = User.create_user(data['username'], data['password'], data.get('perfil', ''))
        return jsonify({'id': user.id, 'username': user.username}), 201

    @app.route('/update_user/<int:user_id>', methods=['PUT'])
    def update_user(user_id):
        data = request.get_json()
        user = User.update_user(user_id, data.get('username'), data.get('password'), data.get('perfil'))
        if user:
            return jsonify({'id': user.id, 'username': user.username}), 200
        return jsonify({'message': 'User not found'}), 404

    @app.route('/delete_user/<int:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        user = User.delete_user(user_id)
        if user:
            return jsonify({'message': 'User deleted'}), 200
        return jsonify({'message': 'User not found'}), 404

    @app.route('/login', methods=['POST'])
    def login():
        # Recebe os dados do corpo da requisição
        data = request.json
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()


        if user and user.check_password(password):
            # Armazena os dados na sessão
            return jsonify({
                'status': 'success',
                'message': 'Login successful',
                'user_id': user.id,
                'perfil': user.perfil
            }), 200
        else:
            return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401
        
    @app.route('/GetCompromissos', methods=['GET'])
    def get_compromissos():
        # Verifica se o cabeçalho API key está correto
        api_key = request.headers.get('api-key')
        if not validate_api_key(api_key):
            return jsonify({'error': 'Unauthorized'}), 401

        try:
            data = request.json
            idUser = data.get('id_user')
            if not idUser:
                return jsonify({'error': 'id_user não fornecido'}), 400
            
            # Consulta todos os compromissos no banco de dados
            compromissos = Compromissos.query.filter_by(id_user=idUser).all()  # Mudado para .all()

            # Verificar se há compromissos
            if not compromissos:
                return jsonify({'error': 'Nenhum compromisso encontrado'}), 404

            # Formatar os dados em uma lista de dicionários
            compromissos_list = []
            for compromisso in compromissos:
                compromisso_data = {
                    'id_compromisso': compromisso.id_compromisso,
                    'titulo': compromisso.titulo,
                    'Inicio': compromisso.Inicio,
                    'Fim': compromisso.Fim,
                    'id_user': compromisso.id_user
                }
                compromissos_list.append(compromisso_data)  # Corrigido para adicionar compromisso_data

            # Retornar a lista de compromissos como JSON
            print(compromissos_list)
            return jsonify({'compromissos': compromissos_list}), 200

        except Exception as e:
            print(f"Erro ao buscar compromissos: {e}")
            return jsonify({'error': str(e)}), 500

        
    @app.route('/create_compromisso', methods=['PUT'])
    def create_compromisso():
        data = request.get_json()
        compromisso = Compromissos.create(data['titulo'], data['Inicio'], data['Fim'], data['id_user'])
        return jsonify({'id_compromisso': compromisso.id_compromisso, 'titulo': compromisso.titulo}), 201
    
    @app.route('/delete_compromisso/<int:compromisso_id>', methods=['DELETE'])
    def delete_compromisso(compromisso_id):
        Compromisso = Compromissos.delete_compromisso(compromisso_id)
        if Compromisso:
            return jsonify({'message': 'Compromisso deleted'}), 200
        return jsonify({'message': 'Compromisso not found'}), 404

    @app.route('/adicionar_responsavel', methods=['POST'])
    def adicionar_responsavel():
        try:
            # Obtém os dados da requisição
            dados = request.get_json()
            id_responsavel = dados.get('id_responsavel')
            processo_id = dados.get('id_processo')  # Processo agora é uma string

            # Verifica se os dados foram fornecidos
            if not id_responsavel or not processo_id:
                return jsonify({"error": "ID do responsável e do processo são obrigatórios"}), 400
            
            # Encontra o processo pela string response_id
            processo = Processo.query.filter_by(response_id=processo_id).first()

            if processo is None:
                return jsonify({"error": "Processo não encontrado."}), 404

            # Cria um novo registro na tabela Responsaveis_processos
            novo_responsavel = Responsavel_Processos(
                id_responsavel=id_responsavel,
                id_processo=processo.id  # Usar o ID do processo encontrado
            )

            # Adiciona e confirma no banco de dados
            db.session.add(novo_responsavel)
            db.session.commit()

            return jsonify({"message": "Responsável adicionado ao processo com sucesso"}), 201
        
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

        
    @app.route('/responsaveis_processo/<processo_id>', methods=['GET'])
    def responsaveis_processo(processo_id):
        try:
            # Verificar se o processo_id corresponde ao tipo correto
            processo = Processo.query.filter_by(response_id=processo_id).first()

            if processo is None:
                return jsonify({"erro": "Processo não encontrado."}), 404

            responsaveis = db.session.query(Responsavel_Processos).join(User).filter(
                Responsavel_Processos.id_processo == processo.id
            ).all()

            data = [{"id": r.id, "nome": r.user.nome} for r in responsaveis]
            return jsonify({"responsaveis": data})
        
        except Exception as e:
            return jsonify({"erro": str(e)}), 500

