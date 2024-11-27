from .services.api import get_results, get_results_detalhes, get_Users, update_user, add_user, remove_user, login, get_Compromissos, add_compromisso, remove_compromisso
from flask import render_template, request, redirect, url_for, session, g
from .models import Processo, db, Acao, User, Parte, Classificacao, Advogado, Compromissos, Documentos, Responsavel_Processos
from flask import flash, jsonify 
from datetime import datetime
from sqlalchemy.sql import func
import os
import psycopg2
from flask import make_response
from flask import jsonify



def init_routes(app):

    @app.before_request
    def before_request():
        g.logged_in = session.get('logged_in', False)

    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/Agenda')
    def Agenda():
        return render_template('Agenda.html')
    
    @app.route('/Login')
    def Login():
        session['logged_in'] = True
        return render_template('Login.html')
    
    @app.route('/Entrar', methods=['POST'])
    def Entrar():
        chave_api = '895a8p82-5k40-37w7-z595-99abxn8q4fgx'

        userData = {
            'username': request.json.get('username'),
            'password': request.json.get('password')
        }

        api_response = login(chave_api, userData)

        if api_response and api_response.get('status') == 'success':
            # Armazena o ID e o perfil do usuário na sessão do Flask
            session['logged_in'] = True
            session['user_id'] = api_response.get('user_id')
            session['perfil'] = api_response.get('perfil')
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'message': 'Login failed'}), 401
        
    @app.route('/logout')
    def logout():
        session.clear()  # Limpa a sessão
        return redirect(url_for('Login'))
        
    @app.route('/Controle_Acesso')
    def ControleAcesso():
        # Verifica se o usuário está logado e tem o perfil de administrador
        if 'user_id' not in session:
            return redirect(url_for('Login'))  # Redireciona para a página de login se o usuário não estiver logado

        # Obtém o perfil do usuário da sessão
        perfil = session.get('perfil')
       

        # Verifica se o perfil é de administrador
        if perfil != 'administrador':    
            session['notification_message'] = 'Você não tem acesso a essa pagina!'       
            return redirect(url_for('todos_processos'))
        
        session.pop('notification_message', None)  # Remove a mensagem da sessão

        chave_api = '895a8p82-5k40-37w7-z595-99abxn8q4fgx'
        data = get_Users(chave_api)
        users = data.get('users', [])
        return render_template('Users.html', users=users)

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/todosprocessos')
    def todos_processos():
        # Verifica se o usuário está logado
        if not session.get('logged_in'):
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('Login'))
        
        # Pega o ID do usuário da sessão
        user_id = session.get('user_id')
        perfil = session.get('perfil')

        print(f"Perfil do usuário: {perfil}")  # Log do perfil do usuário
        print(f"ID do usuário: {user_id}")  # Log do ID do usuário

        # Chave da API e ID de solicitação
        chave_api = '895a8p82-5k40-37w7-z595-99abxn8q4fgx'
        request_id = '17c735f4-0894-4319-b14e-d9723af55130'
        
        # Pega a página atual da URL ou define o padrão como 1
        page = request.args.get('page', 1, type=int)
        print(f"Páginas solicitadas: {page}")  # Log da página solicitada

        # Verifica o perfil do usuário
        if perfil == 'administrador':
            print("Usuário é administrador, consultando todos os processos.")
            # Se for administrador, consulta todos os processos
            data = get_results(page, request_id, chave_api)
        else:
            print(f"Usuário não é administrador, consultando apenas processos para o usuário ID {user_id}.")
            
            # Se não for administrador, consulta a tabela Responsavel_Processos para filtrar os processos
            processos_ids = db.session.query(Responsavel_Processos.id_processo).filter_by(id_responsavel=user_id).all()
            
            # Log dos processos encontrados para o usuário
            print(f"IDs de processos encontrados para o usuário {user_id}: {processos_ids}")
            
            # Converte a tupla de processos_ids para uma lista simples
            processos_ids = [p[0] for p in processos_ids]
            print(f"IDs de processos para filtro: {processos_ids}")

            # Passa a lista de processos_ids para filtrar os processos
            data = get_results(page, request_id, chave_api, filter_by_processos=processos_ids)

        processos = data.get('processos', []) if data else []
        total_pages = data.get('total_pages', 1) if data else 1

        # Log de dados recebidos da API
        print(f"Total de processos encontrados: {len(processos)}")
        print(f"Total de páginas disponíveis: {total_pages}")

        return render_template(
            'todos_processos.html',
            processos=processos,
            page=page,
            total_pages=total_pages
        )




    



    @app.route('/detalhes/<codigo_processo>')
    def detalhes_processo(codigo_processo):
        chave_api = '895a8p82-5k40-37w7-z595-99abxn8q4fgx'
        request_id = '17c735f4-0894-4319-b14e-d9723af55130'
        page = request.args.get('page', 1, type=int)  # Se houver paginação envolvida na API

        # Supondo que a função `get_results` possa buscar por código específico de processo
        data = get_results_detalhes(page, request_id, chave_api,codigo_processo)
        
        

        #print (processo)
        if not data:
            return render_template('404.html'), 404  # Página de erro se não encontrar o processo

        acoes = Acao.query.filter_by(processo_id=data['processo']['id']).all()

        return render_template('detalhes.html', processo=data, acoes=acoes)
   

    @app.route('/adicionar_acao/<codigo_processo>', methods=['POST'])
    def adicionar_acao(codigo_processo):
        # Busca o processo pelo código
        processo = Processo.query.filter_by(codigo=codigo_processo).first()

        if not processo:
            return render_template('404.html'), 404  # Página de erro se não encontrar o processo

        # Captura os dados do formulário
        data = request.form.get('data')
        comentario = request.form.get('comentario')
        status = request.form.get('status')
        tipo = request.form.get('tipo')
        responsavel = request.form.get('responsavel')

        # Cria uma nova instância de Acao
        nova_acao = Acao(data=data, comentario=comentario, status=status, processo_id=processo.id, tipo=tipo, id_responsavel=responsavel)

        # Adiciona a nova ação ao banco de dados
        db.session.add(nova_acao)
        db.session.commit()

        # Captura e salva os arquivos anexados no banco de dados
        if 'anexos' in request.files:
            files = request.files.getlist('anexos')
            for file in files:
                if file.filename != '':
                    # Lê o conteúdo do arquivo como binário diretamente
                    file_content = file.read()  # Lê o arquivo em binário
                    file_name = file.filename

                    # Cria uma nova instância de Documentos
                    novo_documento = Documentos(
                        acoes_id=nova_acao.id,  # ID da ação associada
                        nome_arq=file_name,
                        conteudo_arq=file_content
                    )

                    # Adiciona o documento ao banco de dados
                    db.session.add(novo_documento)

            # Confirma as mudanças no banco de dados
            db.session.commit()

        return redirect(url_for('detalhes_processo', codigo_processo=codigo_processo))
    
    @app.route('/alterar_acao/<int:id>', methods=['POST'])
    def alterar_acao(id):
        # Busca a ação pelo ID
        acao = Acao.query.get(id)

        if not acao:
            return render_template('404.html'), 404  # Página de erro se não encontrar a ação

        # Captura os dados do formulário
        tipo = request.form.get('tipo')
        data = request.form.get('data')
        comentario = request.form.get('comentario')
        status = request.form.get('status')
        responsavel = request.form.get('responsavel')

        print(tipo, data, comentario, status, responsavel)

        # Atualiza a ação com os novos dados
        acao.tipo = tipo
        acao.data = data
        acao.comentario = comentario
        acao.status = status
        acao.id_responsavel = responsavel

        # Atualiza os arquivos anexados
        if 'anexos' in request.files:
            files = request.files.getlist('anexos')
            for file in files:
                if file.filename != '':
                    # Lê o conteúdo do arquivo como binário diretamente
                    file_content = file.read()
                    file_name = file.filename

                    # Cria um novo documento com o arquivo anexado
                    novo_documento = Documentos(
                        acoes_id=acao.id,  # Ação existente
                        nome_arq=file_name,
                        conteudo_arq=file_content
                    )

                    # Adiciona o documento ao banco de dados
                    db.session.add(novo_documento)

        # Confirma as mudanças no banco de dados
        db.session.commit()

        # Recupera o código do processo associado à ação
        processo = Processo.query.get(acao.processo_id)

            # Recupera o código do processo associado à ação
        processo = Processo.query.get(acao.processo_id)
        if not processo:
            return jsonify({"error": "Processo não encontrado"}), 404  # Se o processo não existir, retorna erro

        # Retorna um JSON de sucesso
        return jsonify({"success": True, "codigo_processo": processo.codigo})





    @app.route('/documentos/<int:acao_id>', methods=['GET'])
    def get_documentos(acao_id):
        if not acao_id:
            return jsonify({'error': 'ID da ação inválido'}), 400

        try:
            # Consulta os documentos associados à ação
            documentos = Documentos.query.filter_by(acoes_id=acao_id).all()

            # Serializa os dados para enviar como JSON
            documentos_json = [
                {
                    'id': doc.id_documento,
                    'nome_arq': doc.nome_arq
                } for doc in documentos
            ]

            return jsonify(documentos_json), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    @app.route('/download/<int:documento_id>', methods=['GET'])
    def download_documento(documento_id):
        try:
            # Busca o documento pelo ID
            documento = Documentos.query.get(documento_id)
            if not documento:
                return "Documento não encontrado.", 404

            # Cria a resposta com o conteúdo do arquivo
            response = make_response(documento.conteudo_arq)
            response.headers.set('Content-Type', 'application/octet-stream')  # Define o tipo de arquivo genérico
            response.headers.set(
                'Content-Disposition', 
                f'attachment; filename="{documento.nome_arq}"'  # Define o nome do arquivo para o download
            )
            return response
        except Exception as e:
            return f"Erro ao tentar baixar o arquivo: {str(e)}", 500

    @app.route('/excluir_acao/<int:acao_id>', methods=['POST'])
    def excluir_acao(acao_id):
        try:
            # Busca a ação pelo ID
            acao = Acao.query.get(acao_id)
            if not acao:
                return {"message": "Ação não encontrada."}, 404

            # Exclui os documentos associados à ação
            Documentos.query.filter_by(acoes_id=acao_id).delete()

            # Exclui a ação
            db.session.delete(acao)
            db.session.commit()

            return {"message": "Ação excluída com sucesso."}, 200
        except Exception as e:
            db.session.rollback()
            return {"message": f"Erro ao excluir a ação: {str(e)}"}, 500
        
    @app.route('/excluir_anexo/<int:documento_id>', methods=['DELETE'])
    def excluir_documento(documento_id):
        try:
            # Encontrar o documento no banco de dados
            documento = Documentos.query.get(documento_id)
            if not documento:
                return jsonify({'error': 'Documento não encontrado'}), 404

            # Lógica para excluir o arquivo do sistema de arquivos
            arquivo_path = f'caminho/para/anexos/{documento.nome_arq}'
            if os.path.exists(arquivo_path):
                os.remove(arquivo_path)

            # Excluir o documento do banco de dados
            db.session.delete(documento)
            db.session.commit()

            return jsonify({'success': True})

        except Exception as e:
            return jsonify({'error': str(e)}), 500


    @app.route('/filtrar-processos', methods=['POST'])
    def filtrar_processos():
        dados_filtro = request.json
        tipo_busca = dados_filtro.get('tipoBusca')
        valor_filtro = dados_filtro.get('valorFiltro')
        page = int(dados_filtro.get('page', 1))  # Página atual da requisição
        per_page = 30  # Número de itens por página
        

        # Construir a query dinamicamente com base no tipo de busca
        query = Processo.query

        if tipo_busca == 'numero':
            query = query.filter(Processo.codigo.like(f'%{valor_filtro}%'))
        elif tipo_busca == 'nome':
            query = query.join(Processo.partes).filter(Parte.nome.like(f'%{valor_filtro}%'))
        elif tipo_busca == 'data':
            data_convertida = datetime.strptime(valor_filtro, '%d/%m/%Y').strftime('%Y-%m-%d')
            query = query.filter(
                func.to_char(Processo.data_distribuicao, 'YYYY-MM-DD').like(f'%{data_convertida}%')
            )
        elif tipo_busca == 'tipoprocesso':
            query = query.join(Processo.classificacoes).filter(Classificacao.nome.like(f'%{valor_filtro}%'))
        elif tipo_busca == 'responsavel':
            query = query.join(Processo.acoes).join(User).filter(User.username.like(f'%{valor_filtro}%'))
        elif tipo_busca == 'statusprocesso':
            query = query.filter(Processo.status.like(f'%{valor_filtro}%'))
        elif tipo_busca == 'oab':
            query = query.join(Processo.partes).join(Parte.advogados).filter(Advogado.documento_principal.like(f'%{valor_filtro}%'))
        elif tipo_busca == 'cnpj':
            query = query.join(Processo.partes).filter(Parte.documento_principal.like(f'%{valor_filtro}%'))

         # Paginação manual
        total_items = query.count()
        processos = query.offset((page - 1) * per_page).limit(per_page).all()
        
         # Formatar os processos para JSON
        processos_json = []
        for processo in processos:
            processos_json.append({
                'codigo': processo.codigo,
                'classificacoes': [{'nome': c.nome} for c in processo.classificacoes],
                'partes': [{'nome': p.nome} for p in processo.partes],
                'status': processo.status
            })

        total_pages = (total_items + per_page - 1) // per_page  # Calcula o total de páginas

        return jsonify({
            'processos': processos_json,
            'page': page,
            'total_pages': total_pages
        })
            
    @app.route('/update_user/<int:user_id>', methods=['PUT'])
    def update_user_route(user_id):
        # Pegue a chave da API (você pode movê-la para uma variável de configuração)
        chave_api = '895a8p82-5k40-37w7-z595-99abxn8q4fgx'
        
        # Receber os dados da requisição (JSON)
        userData = request.json
        userData['id'] = user_id  # Adicione o ID ao userData
        
        # Chame a função update_user do api.py para realizar a operação
        resultado = update_user(chave_api, userData)
        
        if resultado:
            return jsonify({"status": "success", "data": resultado}), 200
        else:
            return jsonify({"status": "error", "message": "Erro ao atualizar usuário"}), 500
        
    @app.route('/add_user/', methods=['PUT'])
    def add_user_route():

        chave_api = '895a8p82-5k40-37w7-z595-99abxn8q4fgx'

        userData = request.json
        
        # Chame a função update_user do api.py para realizar a operação
        resultado = add_user(chave_api, userData)
        
        if resultado:
            return jsonify({"status": "success", "data": resultado}), 200
        else:
            return jsonify({"status": "error", "message": "Erro ao atualizar usuário"}), 500
        
    @app.route('/remove_user/<int:user_id>', methods=['DELETE'])
    def remove_user_route(user_id):

        chave_api = '895a8p82-5k40-37w7-z595-99abxn8q4fgx'

        userData = {'id': user_id}
        
        # Chame a função update_user do api.py para realizar a operação
        resultado = remove_user(chave_api, userData)
        
        if resultado:
            return jsonify({"status": "success", "data": resultado}), 200
        else:
            return jsonify({"status": "error", "message": "Erro ao atualizar usuário"}), 500
        
    @app.route('/get_user', methods=['GET'])
    def get_user():

        chave_api = '895a8p82-5k40-37w7-z595-99abxn8q4fgx'
        
        # Chame a função update_user do api.py para realizar a operação
        resultado = get_Users(chave_api)

        #print(resultado)
        
        if resultado and isinstance(resultado, dict) and 'users' in resultado:
            return jsonify({"status": "success", "users": resultado['users']}), 200
        else:
            return jsonify({"status": "error", "message": "Erro ao obter usuários"}), 500
    
    @app.route('/get_compromissos', methods=['GET'])
    def get_compromissos():

        chave_api = '895a8p82-5k40-37w7-z595-99abxn8q4fgx'

        user_id = session.get('user_id')
        
        # Chame a função update_user do api.py para realizar a operação
        resultado = get_Compromissos(chave_api, user_id)

        print(f"Resultado de get_Compromissos: {resultado}")

        
        if resultado and isinstance(resultado, dict) and 'compromissos' in resultado:
            return jsonify({"status": "success", "compromissos": resultado['compromissos']}), 200
        else:
            return jsonify({"status": "error", "message": "Erro ao obter Compromisso"}), 500
        
    @app.route('/add_compromisso/', methods=['PUT'])
    def add_compromisso_route():

        chave_api = '895a8p82-5k40-37w7-z595-99abxn8q4fgx'

        user_id = session.get('user_id')

        if not user_id:
            return jsonify({"status": "error", "message": "User not logged in"}), 401  # Retorna erro se não estiver logado

        CompromissoData = request.json
        
        # Adiciona o user_id aos dados do compromisso
        CompromissoData['id_user'] = user_id  # Presumindo que sua API espera esse campo

        # Chame a função add_compromisso para realizar a operação
        resultado = add_compromisso(chave_api, CompromissoData)

       
        
        if resultado:
            return jsonify({"status": "success", "data": resultado}), 200
        else:
            return jsonify({"status": "error", "message": "Erro ao atualizar usuário"}), 500
        
    @app.route('/remove_compromisso/<int:compromisso_id>', methods=['DELETE'])
    def remove_compromisso_route(compromisso_id):

        chave_api = '895a8p82-5k40-37w7-z595-99abxn8q4fgx'

        compromissoData = {'id': compromisso_id}
        
        # Chame a função update_user do api.py para realizar a operação
        resultado = remove_compromisso(chave_api, compromissoData)
        
        if resultado:
            return jsonify({"status": "success", "data": resultado}), 200
        else:
            return jsonify({"status": "error", "message": "Erro ao Remover compromisso"}), 500
        

    @app.route('/adicionar_responsavel', methods=['POST'])
    def adicionar_responsavel():
        try:

                # Obtém o perfil do usuário da sessão
            perfil = session.get('perfil')
        

            # Verifica se o perfil é de administrador
            if perfil != 'administrador':    
                session['notification_message'] = 'Você não tem acesso a essa pagina!'       
                return redirect(url_for('todos_processos'))
        
            # Obtém os dados da requisição
            dados = request.get_json()
            id_responsavel = dados.get('id_responsavel')
            processo_id = dados.get('id_processo')  # Processo agora é uma string

            # Verifica se os dados foram fornecidos
            if not id_responsavel or not processo_id:
                return jsonify({"error": "ID do responsável e do processo são obrigatórios"}), 400
            
            # Encontra o processo pela string response_id
            processo = Processo.query.filter_by(codigo=processo_id).first()

            if processo is None:
                return jsonify({"error": "Processo não encontrado."}), 404

            # Cria um novo registro na tabela Responsaveis_processos
            novo_responsavel = Responsavel_Processos(
                id_responsavel=id_responsavel,
                id_processo=processo.codigo  # Usar o ID do processo encontrado
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
            # Log: ID do processo recebido na requisição
            print(f"Processo ID recebido: {processo_id}")

            # Buscar o processo pelo código
            processo = Processo.query.filter_by(codigo=processo_id).first()

            # Log: Verificar se o processo foi encontrado
            if processo is None:
                print(f"Processo com código {processo_id} não encontrado.")
                return jsonify({"erro": "Processo não encontrado."}), 404
            print(f"Processo encontrado: ID = {processo.id}, Código = {processo.codigo}")

            # Buscar responsáveis relacionados ao processo
            responsaveis = db.session.query(Responsavel_Processos).join(User).filter(
                Responsavel_Processos.id_processo == processo.codigo  # Ajuste conforme necessário
            ).all()

            # Log: Mostrar os responsáveis encontrados
            if not responsaveis:
                print(f"Nenhum responsável encontrado para o processo {processo.codigo}.")
            else:
                print(f"Responsáveis encontrados para o processo {processo.codigo}:")
                for r in responsaveis:
                    print(f"  - ID: {r.user.id}, Nome: {r.user.username}")

            # Formatar resposta
            data = [{"id": r.user.id, "nome": r.user.username} for r in responsaveis]
            return jsonify({"responsaveis": data})
        
        except Exception as e:
            # Log: Erro geral
            print(f"Erro ao carregar responsáveis para o processo {processo_id}: {e}")
            return jsonify({"erro": str(e)}), 500
        
    @app.route('/remover_responsavel/<int:responsavel_id>', methods=['DELETE'])
    def remover_responsavel(responsavel_id):
        try:
                # Obtém o perfil do usuário da sessão
            perfil = session.get('perfil')
        

            # Verifica se o perfil é de administrador
            if perfil != 'administrador':    
                session['notification_message'] = 'Você não tem acesso a essa pagina!'       
                return redirect(url_for('todos_processos'))

            # Log para verificar o ID do responsável
            print(f"Tentando remover responsável com ID: {responsavel_id}")

            # Obtém o ID do processo da requisição
            dados = request.get_json()
            processo_id = dados.get('id_processo')

            # Log para verificar se o processo_id foi recebido corretamente
            print(f"ID do processo recebido: {processo_id}")

            if not processo_id:
                print("ID do processo não fornecido.")
                return jsonify({"error": "ID do processo é obrigatório"}), 400

            # Busca o responsável no banco de dados
            responsavel = Responsavel_Processos.query.filter_by(id_responsavel=responsavel_id, id_processo=processo_id).first()

            # Log para verificar se o responsável foi encontrado
            if responsavel:
                print(f"Responsável encontrado: {responsavel.id_responsavel}")
            else:
                print(f"Responsável com ID {responsavel_id} não encontrado para o processo {processo_id}")
                return jsonify({"error": "Responsável não encontrado para este processo"}), 404

            # Remove o responsável
            db.session.delete(responsavel)
            db.session.commit()

            # Log para confirmação de remoção
            print(f"Responsável com ID {responsavel_id} removido com sucesso do processo {processo_id}")

            return jsonify({"mensagem": "Responsável removido com sucesso"}), 200

        except Exception as e:
            db.session.rollback()
            print(f"Erro ao remover responsável: {str(e)}")
            return jsonify({"error": str(e)}), 500







   
    
