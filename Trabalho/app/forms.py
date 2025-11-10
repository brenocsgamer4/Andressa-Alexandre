from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField, DateTimeField, IntegerField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from .models import Usuario, Time, Campeonato
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField    
from wtforms.widgets import ListWidget, CheckboxInput

def get_campeonatos():
    return Campeonato.query.all()

def get_times():
    return Time.query.all()

class TimeForm(FlaskForm):
    nome = StringField('Nome do Time', 
                       validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Cadastrar Time')

class InscreverTimeForm(FlaskForm):
    times = QuerySelectMultipleField(
        'Selecionar Times para Inscrever',
        get_label='nome',
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput()
    )
    submit_inscricao = SubmitField('Inscrever Times Selecionados')

    def __init__(self, campeonato_id, *args, **kwargs):
        super(InscreverTimeForm, self).__init__(*args, **kwargs)

        campeonato = Campeonato.query.get(campeonato_id)
        times_inscritos_ids = [time.id for time in campeonato.times]

        self.times.query_factory = lambda: Time.query.filter(
            Time.id.notin_(times_inscritos_ids)
        ).order_by(Time.nome).all()

class CampeonatoForm(FlaskForm):
    nome = StringField('Nome do Campeonato', 
                       validators=[DataRequired(), Length(min=3, max=150)])
    data_inicio = DateField('Data de Início', format='%Y-%m-%d',
                            validators=[DataRequired()])
    data_fim = DateField('Data de Fim', format='%Y-%m-%d',
                         validators=[DataRequired()])
    regras = TextAreaField('Regras (opcional)')
    submit_campeonato = SubmitField('Salvar Alterações do Campeonato')

class JogoForm(FlaskForm):
    campeonato = QuerySelectField(
        'Campeonato',
        query_factory=get_campeonatos,
        get_label='nome',
        allow_blank=False,
        validators=[DataRequired()]
    )
    
    time_casa = QuerySelectField(
        'Time da Casa',
        query_factory=get_times,
        get_label='nome',
        allow_blank=False,
        validators=[DataRequired()]
    )
    
    time_visitante = QuerySelectField(
        'Time Visitante',
        query_factory=get_times,
        get_label='nome',
        allow_blank=False,
        validators=[DataRequired()]
    )
    
    data_hora = DateTimeField('Data e Hora', format='%Y-%m-%dT%H:%M',
                              validators=[DataRequired()])
    placar_casa = IntegerField('Placar Time da Casa', default=0)
    placar_visitante = IntegerField('Placar Time Visitante', default=0)
    
    status = SelectField('Status', 
                         choices=[('Agendado', 'Agendado'), 
                                  ('Em Andamento', 'Em Andamento'), 
                                  ('Finalizado', 'Finalizado')],
                         validators=[DataRequired()])
    
    submit = SubmitField('Salvar Jogo')

class AdminUserCreationForm(FlaskForm):
    nome = StringField('Nome',
                           validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Senha',
                                     validators=[DataRequired(), EqualTo('password', message='As senhas não conferem.')])
    submit = SubmitField('Criar Conta')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Este email já está cadastrado.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Login')
