# 🏆 SIGTO - Sistema de Gerenciamento de Torneios

SIGTO é uma aplicação web completa construída em **Python (Flask)** para gerir **campeonatos de futebol**.  
Ela permite o **cálculo automático de tabelas de classificação**, além da **gestão de times, jogos e inscrições**.

O sistema oferece:
- Uma **vista pública estilizada** para visitantes;
- Uma **vista administrativa funcional ("seca")** para gestores e administradores.

---

## 📋 1. Requisitos do Sistema

O **SIGTO** é um projeto **leve e multiplataforma**, projetado para funcionar em qualquer computador moderno.

- **Sistema Operacional:** Windows, macOS ou Linux  
- **Hardware:** Sem exigências elevadas; usa **Flask** e **SQLite**

---

## ⚙️ 2. Instalação (Como Executar)

Siga estes passos para configurar o ambiente e executar o projeto pela primeira vez.

### 🧩 Passo 1: Criar o Ambiente Virtual

No terminal, dentro da pasta do projeto:

```bash
# 1. Criar o ambiente virtual
python3 -m venv venv

# 2. Ativar o venv (Windows)
.env\Scriptsctivate

# OU

# 2. Ativar o venv (Linux/macOS)
source venv/bin/activate
```

---

### 📦 Passo 2: Instalar as Bibliotecas

Com o ambiente virtual ativado, instale as dependências:

```bash
pip install -r requirements.txt
```

---

### 🗄️ Passo 3: Criar o Banco de Dados e o Administrador Supremo

Se for a primeira execução (ou se o arquivo `app/site.db` foi apagado), é necessário criar as tabelas e o primeiro administrador.

#### 1️⃣ Criar as tabelas do banco:

```bash
flask shell
```

Dentro do shell do Flask:

```python
>>> from app import db
>>> db.create_all()
>>> exit()
```

#### 2️⃣ Criar o Administrador Supremo (ID 1):

```bash
flask create-admin
```

Siga as instruções no terminal para definir o **nome**, **email** e **senha** do administrador principal.

---

## 🌐 3. Como Colocar o Site "no Ar" (Em Rede Local)

### 💻 Para Desenvolvimento (Apenas no seu PC)

Execute o site em modo de desenvolvimento (recarrega automaticamente a cada alteração):

```bash
# Certifique-se de que o venv está ativado
python run.py
```

Acesse o site em:  
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

### 🏠 Para Produção (Na sua Rede Local)

Para permitir que outros dispositivos (computadores ou celulares) na mesma rede acessem o site, use o servidor **Waitress**.

#### 🔍 Passo 1: Descubra seu IP Interno

- **Windows:**  
  Abra o **CMD** e digite:
  ```bash
  ipconfig
  ```
  Procure o campo **"Endereço IPv4"** (ex: `192.168.1.10`)

- **Linux/macOS:**  
  ```bash
  ip addr show
  ```
  Procure pelo IP na interface **eth0** ou **wlan0** (ex: `inet 192.168.1.10/24`)

---

#### 🔒 Passo 2: Configurar o Firewall

##### No Windows:
1. Abra **"Firewall do Windows com Segurança Avançada"**  
2. Vá em **"Regras de Entrada" → "Nova Regra..."**  
3. Selecione:
   - Tipo: **Porta**
   - Protocolo: **TCP**
   - Portas locais específicas: **5000**
4. Escolha **"Permitir a ligação"**  
5. Dê um nome à regra (ex: “Servidor Flask”)

##### No Linux (com `ufw`):
```bash
sudo ufw allow 5000/tcp
```

---

#### 🚀 Passo 3: Iniciar o Servidor de Produção

Com o ambiente virtual ativo, execute:

```bash
waitress-serve --host=0.0.0.0 --port=5000 run:app
```

> **--host=0.0.0.0** → aceita conexões de qualquer IP  
> **run:app** → indica que o Waitress deve procurar `app` dentro de `run.py`

---

#### 🌍 Passo 4: Acessar o Site

Enquanto o servidor estiver rodando, qualquer pessoa na sua rede local pode acessar o site no navegador digitando:

```
http://192.168.1.10:5000
```

*(Substitua `192.168.1.10` pelo seu IP interno do Passo 1)*

---

## 📘 Licença

Este projeto é distribuído sob a licença **MIT**.  
Sinta-se à vontade para usar, modificar e contribuir com melhorias.

---

💡 **SIGTO** — Simplificando a gestão de torneios com Python e Flask ⚽
