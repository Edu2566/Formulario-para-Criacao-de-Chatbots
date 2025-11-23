# Formulário de Chatbots (Flask + Banco de Dados)

Aplicação Flask para criar e editar chatbots, registrar mensagens e subopções em árvore (profundidade ilimitada), com visualização escrita, “mapa mental” e exportação em PDF. Interface em três páginas (lista, mapas e construtor), navegação por setas e botões `+` para adicionar mensagens/subopções, colapso de nós para não poluir a tela e campos multiline (textarea) para as mensagens. Persistência em banco MySQL via SQLAlchemy.

## Rodando com Docker (recomendado)

1. Duplique `.env.example` para `.env` e ajuste as variáveis conforme desejar (valores padrões são apenas para desenvolvimento).
2. Suba os serviços:
   ```bash
   docker compose up --build
   ```
3. A aplicação estará em `http://localhost:5000` e o MySQL exposto na porta `3306` (se quiser conectar externamente).

`docker-compose.yml` sobe dois serviços:
- `app`: Flask + Gunicorn, aguardando o MySQL ficar disponível e criando as tabelas automaticamente.
- `db`: MySQL 8.0 com volume persistente `db_data`.

## Rodando localmente (sem Docker)

Requisitos: Python 3.10+ e MySQL acessível.

```bash
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
pip install -r requirements.txt
# Ajuste as variáveis de ambiente (veja .env.example). Exemplo:
export MYSQL_DATABASE_URL="mysql://chatbot:chatbotpass@localhost:3306/chatbots"
python app.py  # roda em http://127.0.0.1:5000
```

Para exportar PDF é usada a biblioteca WeasyPrint; pode ser necessário ter dependências de sistema (Cairo/ffi/Pango) instaladas no SO.

## Estrutura (MVT simples)

- `app.py`: factory que configura Flask/SQLAlchemy e registra os blueprints.
- `extensions.py`: instancia `db`.
- `models.py`: `Chatbot` e `BotMessage` (relacionamento pai/filhos).
- `services/chatbot_service.py`: regras de negócio (validar árvore, persistir, buscar chatbots, exportar PDF).
- `views/`: blueprints (`main` para lista/mapas, `builder` para criar/editar/deletar, `export` para PDF).
- `templates/`: `base.html` com navegação, `list.html` (visão escrita), `maps.html` (mapa mental), `form.html` (criar/editar) e `map_pdf.html` (print-friendly do PDF).
- `static/js/form.js`: lógica de etapas, validações, construtor/edição da árvore de mensagens (subopções ilimitadas), colapso/expansão de nós e textareas para mensagens multilinha.

## Notas

- Front-end impede avanço sem nome ou mensagens; back-end valida novamente.
- Para editar um chatbot, clique em “Editar” no card. As mensagens existentes são carregadas no formulário; ao salvar, a árvore é substituída.
- Para excluir, use “Deletar” no card. Remover mensagens específicas pode ser feito na edição (apagando nós do mapa) e salvando.
- As listagens mostram a visão escrita e a página de mapas traz um “mapa mental” das mensagens/subopções.
- Use “Colapsar todas” ou os botões de colapso por nó no construtor para lidar melhor com árvores muito profundas.
- Para exportar o mapa mental em PDF, clique em “Exportar PDF” no card do chatbot (lista ou mapas).
