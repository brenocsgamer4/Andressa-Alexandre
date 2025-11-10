from . import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='Torcedor')

    def __repr__(self):
        return f'<Usuario {self.nome} ({self.email})>'

campeonato_times = db.Table('campeonato_times',
    db.Column('time_id', db.Integer, db.ForeignKey('time.id'), primary_key=True),
    db.Column('campeonato_id', db.Integer, db.ForeignKey('campeonato.id'), primary_key=True)
)

class Time(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<Time {self.nome}>'

class Campeonato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    data_inicio = db.Column(db.Date, nullable=True) 
    data_fim = db.Column(db.Date, nullable=True) 
    regras = db.Column(db.Text, nullable=True) 

    jogos = db.relationship('Jogo', backref='campeonato', lazy=True)

    times = db.relationship('Time', secondary=campeonato_times, lazy='subquery',
        backref=db.backref('campeonatos', lazy=True))

    def __repr__(self):
        return f'<Campeonato {self.nome}>'

class Jogo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, nullable=False)
    placar_casa = db.Column(db.Integer, default=0)
    placar_visitante = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='Agendado') 

    time_casa_id = db.Column(db.Integer, db.ForeignKey('time.id'), nullable=False)
    time_visitante_id = db.Column(db.Integer, db.ForeignKey('time.id'), nullable=False)
    campeonato_id = db.Column(db.Integer, db.ForeignKey('campeonato.id'), nullable=False)

    time_casa = db.relationship('Time', foreign_keys=[time_casa_id])
    time_visitante = db.relationship('Time', foreign_keys=[time_visitante_id])