from app import db
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'users'  
    __table_args__ = {"schema": "homolog", "extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

class Processo(db.Model):
    __tablename__ = 'processos'
    __table_args__ = {"schema": "homolog", "extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.String(255), unique=True)
    request_id = db.Column(db.String(255))
    codigo = db.Column(db.String(255), unique=True)
    instancia = db.Column(db.Integer)
    nome = db.Column(db.String(512))
    nivel_sigilo = db.Column(db.Integer)
    tribunal_acronimo = db.Column(db.String(255))
    data_distribuicao = db.Column(db.DateTime)
    valor = db.Column(db.Numeric)
    estado = db.Column(db.String(255))
    fase = db.Column(db.String(255))
    ultima_atualizacao = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    status = db.Column(db.String(50))
    fase_processo = db.Column(db.String(50))
    justice = db.Column(db.Integer)
    tribunal = db.Column(db.Integer)
    county = db.Column(db.String(255))
    free_justice = db.Column(db.Boolean)
    judge = db.Column(db.String(50))
    situation = db.Column(db.String(255))

    classificacoes = db.relationship('Classificacao', backref='processo', lazy=True)
    tribunais = db.relationship('Tribunal', backref='processo', lazy=True)
    partes = db.relationship('Parte', backref='processo', lazy=True)
    assuntos = db.relationship('Assunto', backref='processo', lazy=True)
    etapas = db.relationship('Etapa', backref='processo', lazy=True)
    passos = db.relationship('Passos', backref='processo', lazy=True)
    acoes = db.relationship('Acao', backref='processo', lazy=True)  

class Acao(db.Model):
    __tablename__ = 'acoes'
    __table_args__ = {"schema": "homolog", "extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date)
    comentario = db.Column(db.String(500))
    status = db.Column(db.String(50))
    processo_id = db.Column(db.Integer, db.ForeignKey('homolog.processos.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)    
    id_responsavel = db.Column(db.Integer, db.ForeignKey('homolog.users.id'))
    tipo = db.Column(db.String(255))

    responsavel = db.relationship('User', backref='acoes', lazy=True)

class Classificacao(db.Model):
    __tablename__ = 'classificacoes'
    __table_args__ = {"schema": "homolog", "extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50))
    nome = db.Column(db.String(512))
    processo_id = db.Column(db.Integer, db.ForeignKey('homolog.processos.id'))

class Tribunal(db.Model):
    __tablename__ = 'tribunais'
    __table_args__ = {"schema": "homolog", "extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(512))
    processo_id = db.Column(db.Integer, db.ForeignKey('homolog.processos.id'))

class Parte(db.Model):
    __tablename__ = 'partes'
    __table_args__ = {"schema": "homolog", "extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(512))
    documento_principal = db.Column(db.String(20))
    entity_id = db.Column(db.String(36))
    entity_type = db.Column(db.String(20))
    tipo_pessoa = db.Column(db.String(50))
    lado = db.Column(db.String(50))
    processo_id = db.Column(db.Integer, db.ForeignKey('homolog.processos.id'))
    advogados = db.relationship('Advogado', backref='parte', lazy=True)

class Advogado(db.Model):
    __tablename__ = 'advogados'
    __table_args__ = {"schema": "homolog", "extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(512))
    documento_principal = db.Column(db.String(20))
    entity_type = db.Column(db.String(20))
    document = db.Column(db.String(20))
    document_type = db.Column(db.String(20))
    parte_id = db.Column(db.Integer, db.ForeignKey('homolog.partes.id'))

class Assunto(db.Model):
    __tablename__ = 'assuntos'
    __table_args__ = {"schema": "homolog", "extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50))
    nome = db.Column(db.String(512))
    processo_id = db.Column(db.Integer, db.ForeignKey('homolog.processos.id'))

class Etapa(db.Model):
    __tablename__ = 'etapas'
    __table_args__ = {"schema": "homolog", "extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    etapa_id = db.Column(db.String(255))
    data_etapa = db.Column(db.DateTime)
    conteudo = db.Column(db.Text)
    quantidade_etapas = db.Column(db.Integer)
    lawsuit_cnj = db.Column(db.String(255))
    lawsuit_instance = db.Column(db.Integer)
    private = db.Column(db.Boolean)
    processo_id = db.Column(db.Integer, db.ForeignKey('homolog.processos.id'))

class Passos(db.Model):
    __tablename__ = 'passos'
    __table_args__ = {"schema": "homolog", "extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    step_id = db.Column(db.String(255))
    nome = db.Column(db.String(5000))
    step_date = db.Column(db.DateTime)
    lawsuit_cnj = db.Column(db.String(255))
    lawsuit_instance = db.Column(db.Integer)
    private = db.Column(db.Boolean)
    processo_id = db.Column(db.Integer, db.ForeignKey('homolog.processos.id'))

class Request(db.Model):
    __tablename__ = 'request'
    __table_args__ = {"schema": "homolog", "extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(255))
    nome = db.Column(db.String(255))
    cnpj = db.Column(db.String(255))
    db.create_all()

class Compromissos(db.Model):
    __tablename__ = 'Compromissos'
    __table_args__ = {"schema": "homolog", "extend_existing": True}
    id_compromisso = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255))
    Inicio = db.Column(db.String(255))
    Fim = db.Column(db.String(255))
    id_user = db.Column(db.Integer, db.ForeignKey('homolog.users.id'))
    db.create_all()

class Documentos(db.Model):
    __tablename__ = 'Documentos'
    __table_args__ = {"schema": "homolog", "extend_existing": True}
    
    id_documento = db.Column(db.Integer, primary_key=True)
    acoes_id = db.Column(db.Integer, db.ForeignKey('homolog.acoes.id'), nullable=False)
    nome_arq = db.Column(db.String(255), nullable=False)
    conteudo_arq = db.Column(db.LargeBinary) 
    db.create_all()

class Responsavel_Processos(db.Model):
    __tablename__ = 'Responsaveis_processos'
    __table_args__ = {"schema": "homolog", "extend_existing": True}
    
    id = db.Column(db.Integer, primary_key=True)
    id_responsavel = db.Column(db.Integer, db.ForeignKey('homolog.users.id'), nullable=False)
    id_processo = db.Column(db.String(255), db.ForeignKey('homolog.processos.id'), nullable=False)
    user = db.relationship('User', backref='responsavel_processos', lazy=True)
    db.create_all()




