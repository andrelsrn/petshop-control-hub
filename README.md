# 🐾 Pet Control Hub  
**Plataforma de Gestão Integrada para Pet Shops**

O **Pet Control Hub** é uma plataforma de gestão e **Business Intelligence (BI)** para pet shops modernos.  
Ela simula operações diárias como **vendas, agendamentos e novos clientes**, processa eventos em tempo real e gera **insights acionáveis** para apoiar a tomada de decisões.

---

## 🚀 Tecnologias Utilizadas
- **Backend (API):** FastAPI com Python  
- **Banco de Dados:** SQLite  
- **ORM:** SQLAlchemy  
- **Simulação de Eventos:** httpx  

---

## ⚙️ Como Executar o Projeto

### Pré-requisitos
- Python **3.8+** instalado

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/andrelsrn/petshop-control-hub.git
cd petshop-control-hub

# 2. Crie e ative o ambiente virtual
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute o servidor da API (em um terminal)
uvicorn app.main:app --reload

# 5. Execute o simulador de eventos (em outro terminal)
python simulador.py

---

📊 Uso

O simulador começará a enviar eventos automaticamente para a API.

Os dados serão salvos no banco SQLite do projeto.

Acesse a documentação interativa da API em:
http://127.0.0.1:8000/docs

---

🔜 Próximas melhorias

Dashboards visuais e relatórios em tempo real

Autenticação e autorização (JWT)

Integração com serviços externos (pagamentos, email)

Contêinerização com Docker e deploy CI/CD

---

👨‍💻 Autor

Projeto desenvolvido por André Nunes
