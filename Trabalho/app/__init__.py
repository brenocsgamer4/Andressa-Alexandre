from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import click
from getpass import getpass
import os 

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'chave-super-secreta'
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    with app.app_context():
        from . import models  

    from .routes import main
    app.register_blueprint(main)

    @app.cli.command('create-admin')
    def create_admin_command():

        from .models import Usuario
        
        print("--- Criando Conta de Administrador Base ---")

        nome = click.prompt("Nome do Admin", type=str)
        email = click.prompt("Email do Admin", type=str)
        
        if Usuario.query.filter_by(email=email).first():
            print(f"Erro: O email '{email}' já existe.")
            return

        password_str = getpass("Senha: ")
        confirm_password_str = getpass("Confirme a Senha: ")

        if password_str != confirm_password_str:
            print("Erro: As senhas não conferem.")
            return

        try:
            hashed_password = bcrypt.generate_password_hash(password_str).decode('utf-8')
            admin_user = Usuario(
                nome=nome,
                email=email,
                senha_hash=hashed_password,
                role='Admin' 
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"\nSucesso! Administrador '{nome}' criado com o email '{email}'.")
        
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar admin: {e}")
    
    return app