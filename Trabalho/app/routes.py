from flask import render_template, redirect, url_for, flash, Blueprint, request
from .forms import TimeForm, CampeonatoForm, JogoForm, LoginForm, AdminUserCreationForm, InscreverTimeForm
from .models import Time, Campeonato, Jogo, Usuario
from flask_login import login_user, current_user, logout_user, login_required 
from collections import defaultdict
from . import db, bcrypt
from .decorators import admin_required

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/alguma-coisa')
@admin_required
def nome_da_rota():
    if current_user.role != 'Admin':
        flash('Você não tem permissão...', 'danger')
        return redirect(url_for('main.home'))

@main.route('/tabelas/<int:id>')
def ver_tabela_campeonato(id):
    campeonato = Campeonato.query.get_or_404(id)

    estatisticas = defaultdict(lambda: {
        'nome': '', 'pontos': 0, 'vitorias': 0, 'empates': 0, 'derrotas': 0,
        'gols_pro': 0, 'gols_contra': 0, 'saldo_gols': 0, 'jogos_disputados': 0
    })

    for time in campeonato.times:
        estatisticas[time.id]['nome'] = time.nome

    jogos_finalizados = Jogo.query.filter_by(status='Finalizado', campeonato_id=id).all()

    for jogo in jogos_finalizados:

        if jogo.time_casa_id in estatisticas and jogo.time_visitante_id in estatisticas:
            time_casa = estatisticas[jogo.time_casa_id]
            time_visitante = estatisticas[jogo.time_visitante_id]

            time_casa['jogos_disputados'] += 1
            time_visitante['jogos_disputados'] += 1
            
            time_casa['gols_pro'] += jogo.placar_casa
            time_casa['gols_contra'] += jogo.placar_visitante
            time_visitante['gols_pro'] += jogo.placar_visitante
            time_visitante['gols_contra'] += jogo.placar_casa

            if jogo.placar_casa > jogo.placar_visitante:
                time_casa['pontos'] += 3
                time_casa['vitorias'] += 1
                time_visitante['derrotas'] += 1
            elif jogo.placar_casa < jogo.placar_visitante:
                time_visitante['pontos'] += 3
                time_visitante['vitorias'] += 1
                time_casa['derrotas'] += 1
            else:
                time_casa['pontos'] += 1
                time_casa['empates'] += 1
                time_visitante['pontos'] += 1
                time_visitante['empates'] += 1

    tabela_classificacao = []
    for time_id, stats in estatisticas.items():
        stats['saldo_gols'] = stats['gols_pro'] - stats['gols_contra']
        tabela_classificacao.append(stats)

    tabela_ordenada = sorted(tabela_classificacao, 
                             key=lambda x: (x['pontos'], x['saldo_gols'], x['gols_pro']), 
                             reverse=True)
    
    return render_template('tabela_campeonato.html', 
                           tabela=tabela_ordenada, 
                           campeonato=campeonato)

@main.route('/times')
@admin_required
def times():
    if current_user.role != 'Admin':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.home'))
        
    todos_os_times = Time.query.all()
    return render_template('times.html', times=todos_os_times)

@main.route('/times/novo', methods=['GET', 'POST'])
@admin_required 
def novo_time():
    if current_user.role != 'Admin':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.home'))
        
    form = TimeForm()
    
    if form.validate_on_submit():
        nome_time = form.nome.data
        
        time = Time(nome=nome_time)
        
        db.session.add(time)
        db.session.commit()
        
        flash('Time cadastrado com sucesso!', 'success')
        return redirect(url_for('main.times'))

    return render_template('cadastrar_time.html', form=form)

@main.route('/times/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_time(id):

    if current_user.role != 'Admin':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.home'))
    time = Time.query.get_or_404(id)
    form = TimeForm()
    
    if form.validate_on_submit():
        time.nome = form.nome.data  
        db.session.commit()         
        flash('Time atualizado com sucesso!', 'success')
        return redirect(url_for('main.times'))
    
    elif request.method == 'GET':
        form.nome.data = time.nome  

    return render_template('editar_time.html', form=form, time=time)

@main.route('/times/<int:id>/deletar', methods=['POST'])
@admin_required
def deletar_time(id):

    if current_user.role != 'Admin':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.home'))
    time = Time.query.get_or_404(id)
    db.session.delete(time)
    db.session.commit()
    flash('Time removido com sucesso!', 'danger')
    return redirect(url_for('main.times'))

@main.route('/campeonatos')
def campeonatos():

    todos_os_campeonatos = Campeonato.query.all()
    return render_template('campeonatos.html', campeonatos=todos_os_campeonatos)

@main.route('/campeonatos/novo', methods=['GET', 'POST'])
@admin_required
def novo_campeonato():

    if current_user.role != 'Admin':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.home'))
    form = CampeonatoForm()
    if form.validate_on_submit():

        campeonato = Campeonato(
            nome=form.nome.data,
            data_inicio=form.data_inicio.data,
            data_fim=form.data_fim.data,
            regras=form.regras.data
        )
        db.session.add(campeonato)
        db.session.commit()
        flash('Campeonato cadastrado com sucesso!', 'success')
        return redirect(url_for('main.campeonatos'))
    
    return render_template('cadastrar_campeonato.html', form=form)

@main.route('/campeonatos/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_campeonato(id):
    campeonato = Campeonato.query.get_or_404(id)
    form_campeonato = CampeonatoForm()
    
    form_inscricao = InscreverTimeForm(campeonato_id=id)

    if form_campeonato.validate_on_submit() and form_campeonato.submit_campeonato.data:
        flash('Dados do campeonato atualizados!', 'success')
        return redirect(url_for('main.editar_campeonato', id=id))
    
    if form_inscricao.validate_on_submit() and form_inscricao.submit_inscricao.data:
        
        times_para_inscrever = form_inscricao.times.data
        
        inscritos_count = 0
        for time in times_para_inscrever:
            campeonato.times.append(time)
            inscritos_count += 1
        
        if inscritos_count > 0:
            db.session.commit()
            flash(f'{inscritos_count} time(s) inscritos com sucesso!', 'success')
        else:
            flash('Nenhum time novo foi selecionado.', 'info')
        
        return redirect(url_for('main.editar_campeonato', id=id))

    times_inscritos = campeonato.times
    
    return render_template('editar_campeonato.html', 
                           form_campeonato=form_campeonato,
                           form_inscricao=form_inscricao,
                           campeonato=campeonato,
                           times_inscritos=times_inscritos)

@main.route('/campeonatos/<int:campeonato_id>/remover-time/<int:time_id>', methods=['POST'])
@admin_required
def remover_time_campeonato(campeonato_id, time_id):
    campeonato = Campeonato.query.get_or_404(campeonato_id)
    time_para_remover = Time.query.get_or_404(time_id)

    if time_para_remover in campeonato.times:
        campeonato.times.remove(time_para_remover)
        db.session.commit()
        flash(f'Time "{time_para_remover.nome}" removido do campeonato.', 'success')
    else:
        flash(f'O time "{time_para_remover.nome}" não estava neste campeonato.', 'warning')
    
    return redirect(url_for('main.editar_campeonato', id=campeonato_id))

@main.route('/campeonatos/<int:id>/deletar', methods=['POST'])
@admin_required
def deletar_campeonato(id):

    if current_user.role != 'Admin':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.home'))
    campeonato = Campeonato.query.get_or_404(id)
    db.session.delete(campeonato)
    db.session.commit()
    flash('Campeonato removido com sucesso!', 'danger')
    return redirect(url_for('main.campeonatos'))

@main.route('/jogos')
def jogos():
    todos_os_jogos = Jogo.query.order_by(Jogo.data_hora.desc()).all()
    return render_template('jogos.html', jogos=todos_os_jogos)

@main.route('/jogos/novo', methods=['GET', 'POST'])
@admin_required
def novo_jogo():

    if current_user.role != 'Admin':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.home'))
    form = JogoForm()
    
    if form.validate_on_submit():

        jogo = Jogo(
            campeonato_id=form.campeonato.data.id, 
            time_casa_id=form.time_casa.data.id,
            time_visitante_id=form.time_visitante.data.id,
            data_hora=form.data_hora.data,
            placar_casa=form.placar_casa.data,
            placar_visitante=form.placar_visitante.data,
            status=form.status.data
        )
        db.session.add(jogo)
        db.session.commit()
        flash('Jogo cadastrado com sucesso!', 'success')
        return redirect(url_for('main.jogos'))
    
    return render_template('cadastrar_jogo.html', form=form)

@main.route('/jogos/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_jogo(id):

    if current_user.role != 'Admin':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.home'))
    jogo = Jogo.query.get_or_404(id)
    form = JogoForm()
    
    if form.validate_on_submit():
        jogo.campeonato_id = form.campeonato.data.id
        jogo.time_casa_id = form.time_casa.data.id
        jogo.time_visitante_id = form.time_visitante.data.id
        jogo.data_hora = form.data_hora.data
        jogo.placar_casa = form.placar_casa.data
        jogo.placar_visitante = form.placar_visitante.data
        jogo.status = form.status.data
        
        db.session.commit()
        flash('Jogo atualizado com sucesso!', 'success')
        return redirect(url_for('main.jogos'))
    
    elif request.method == 'GET':

        form.campeonato.data = jogo.campeonato
        form.time_casa.data = jogo.time_casa
        form.time_visitante.data = jogo.time_visitante
        form.data_hora.data = jogo.data_hora
        form.placar_casa.data = jogo.placar_casa
        form.placar_visitante.data = jogo.placar_visitante
        form.status.data = jogo.status
    
    return render_template('editar_jogo.html', form=form, jogo=jogo)

@main.route('/jogos/<int:id>/deletar', methods=['POST'])
@admin_required
def deletar_jogo(id):

    if current_user.role != 'Admin':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('main.home'))
    jogo = Jogo.query.get_or_404(id)
    db.session.delete(jogo)
    db.session.commit()
    flash('Jogo removido com sucesso!', 'danger')
    return redirect(url_for('main.jogos'))

@main.route('/admin/usuarios')
@login_required
def gerenciar_usuarios():

    if current_user.id != 1:
        flash('Apenas o Administrador Supremo pode aceder a esta página.', 'danger')
        return redirect(url_for('main.home'))
    
    usuarios = Usuario.query.all()
    
    return render_template('gerenciar_usuarios.html', usuarios=usuarios)

@main.route('/admin/usuarios/<int:id>/deletar', methods=['POST'])
@login_required
def deletar_usuario(id):

    if current_user.id != 1:
        flash('Apenas o Administrador Supremo pode remover utilizadores.', 'danger')
        return redirect(url_for('main.home'))

    if id == 1:
        flash('O Administrador "Supremo" (ID 1) não pode ser removido.', 'danger')
        return redirect(url_for('main.gerenciar_usuarios'))

    usuario_para_deletar = Usuario.query.get_or_404(id)

    db.session.delete(usuario_para_deletar)
    db.session.commit()
    flash('Utilizador removido com sucesso.', 'success')
    return redirect(url_for('main.gerenciar_usuarios'))

@main.route('/admin/usuarios/novo', methods=['GET', 'POST'])
@login_required
def novo_usuario_admin():

    if current_user.id != 1:
        flash('Apenas o Administrador Supremo pode aceder a esta página.', 'danger')
        return redirect(url_for('main.home'))

    form = AdminUserCreationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        usuario = Usuario(nome=form.nome.data, 
                        email=form.email.data, 
                        senha_hash=hashed_password, 
                        role='Admin')
        db.session.commit()
        flash('Novo usuário criado com sucesso!', 'success')
        return redirect(url_for('main.gerenciar_usuarios'))

    return render_template('criar_usuario_admin.html', title='Criar Usuário', form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()

        if usuario and bcrypt.check_password_hash(usuario.senha_hash, form.password.data):
            login_user(usuario)
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Login falhou. Por favor, verifique o email e a senha.', 'danger')
            
    return render_template('login.html', title='Login', form=form)


@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

