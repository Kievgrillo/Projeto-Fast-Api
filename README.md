API de Pedidos — FastAPI

API REST para gerenciamento de pedidos de uma pizzaria, construída com FastAPI, SQLAlchemy e autenticação via JWT.

Projeto de estudo focado em backend Python: modelagem com ORM, migrations versionadas, autenticação com tokens e controle de níveis de acesso.

Stack
Camada	Tecnologia
Framework web	FastAPI
Servidor ASGI	Uvicorn
ORM	SQLAlchemy
Migrations	Alembic
Banco de dados	SQLite
Validação / serialização	Pydantic
Hash de senha	bcrypt (via pwdlib)
Tokens	PyJWT
Configuração	python-dotenv
Conceitos de API REST aplicados
O que é REST

REST é um estilo arquitetural para APIs baseado em recursos identificados por URLs. Cada recurso (/pedidos, /usuarios) é um substantivo, e a ação sobre ele é expressa pelo método HTTP, não pela URL. Por isso POST /pedidos em vez de /criarPedido.

Duas características centrais do estilo:

Stateless — o servidor não guarda sessão entre requisições. Toda requisição carrega o que é necessário para ser processada, incluindo a identidade de quem chama. É o que torna a API escalável horizontalmente, e é a razão de usarmos token em vez de sessão em memória.

Interface uniforme — os mesmos verbos e as mesmas convenções de status code valem para qualquer recurso. Quem já consumiu um endpoint sabe consumir os outros.

Métodos HTTP
Método	Uso	Idempotente
GET	Buscar recursos, sem efeito colateral	Sim
POST	Criar um recurso novo	Não
PUT	Substituir um recurso inteiro	Sim
PATCH	Atualizar parcialmente	Não
DELETE	Remover um recurso	Sim

Idempotente significa que repetir a mesma chamada produz o mesmo estado final. Chamar DELETE /pedidos/5 três vezes deixa o sistema igual a chamar uma vez — por isso o cliente pode fazer retry com segurança. Já POST /pedidos repetido cria três pedidos.

Status codes

O código de resposta é parte do contrato da API, não um detalhe.

Faixa	Significado	Exemplos usados aqui
2xx	Sucesso	200 OK, 201 Created
4xx	Erro do cliente	400, 401, 403, 404, 422
5xx	Erro do servidor	500

A distinção que mais confunde e mais importa:

401 Unauthorized — você não provou quem é. Token ausente, inválido ou expirado.
403 Forbidden — você provou quem é, mas não tem permissão. É o caso de um usuário comum tentando acessar rota de admin.
422 Unprocessable Entity — o corpo da requisição não passou na validação de schema. O FastAPI retorna isso automaticamente quando o JSON recebido não bate com o modelo Pydantic esperado.
JSON e serialização

JSON é o formato de troca de dados da API. O FastAPI cuida da conversão nas duas pontas: transforma o corpo da requisição em objeto Python validado, e transforma o retorno da função em JSON de resposta.

A validação não é opcional nem manual — ela vem do schema Pydantic declarado na assinatura da rota. Se o cliente enviar {"preco": "abc"} onde se espera um número, a requisição nem chega ao corpo da função: o FastAPI devolve 422 com a descrição exata do campo que falhou.

Schemas vs. Models

Separação deliberada, e uma das decisões mais importantes do projeto:

Model (models.py) — classe SQLAlchemy que representa uma tabela do banco. Define colunas, tipos e relacionamentos.
Schema (schemas.py) — classe Pydantic que representa o contrato da API. Define o que entra e o que sai em cada endpoint.

Manter os dois separados evita o vazamento acidental de campos sensíveis. O model Usuario tem a coluna senha; o schema de resposta não a inclui. Se fossem a mesma classe, todo GET /usuarios devolveria o hash da senha.

Autenticação com JWT

JWT (JSON Web Token) é uma string assinada composta por três partes separadas por ponto: header.payload.signature.

O payload carrega os dados da sessão (id do usuário, data de expiração). A assinatura é gerada com uma chave secreta que só o servidor conhece — qualquer alteração no payload invalida a assinatura, e o servidor rejeita o token.

O ponto importante: JWT não é criptografia, é assinatura. O payload é apenas Base64 e pode ser lido por qualquer um que tenha o token. Ele garante que o conteúdo não foi adulterado, não que seja secreto. Por isso nunca se coloca senha ou dado sensível dentro dele.

Fluxo implementado:

Cliente envia credenciais em POST /auth/login
Servidor verifica o hash com bcrypt e emite dois tokens
Access token — vida curta (minutos), enviado no header Authorization: Bearer <token> a cada requisição
Refresh token — vida longa (dias), usado só para obter um novo access token em POST /auth/refresh

A separação existe para limitar o dano de um token vazado: o access token expira rápido, e o refresh token trafega raramente.

Hash de senha com bcrypt

Senha nunca é armazenada — nem em texto puro, nem criptografada de forma reversível. O que se guarda é o hash, resultado de uma função de mão única.

O bcrypt tem duas propriedades que o tornam adequado a esse uso:

Salt automático — cada hash recebe um valor aleatório embutido, então duas contas com a mesma senha geram hashes diferentes. Isso inviabiliza ataques por rainbow table.
Custo configurável — o algoritmo é deliberadamente lento, e o custo pode ser aumentado conforme o hardware evolui. Isso encarece ataques de força bruta.

Na verificação, o servidor não descriptografa nada: ele aplica a mesma função à senha recebida e compara os hashes.

Níveis de acesso

O controle é feito por dependências do FastAPI (Depends), aplicadas em três granularidades:

Global — no APIRouter, protegendo todas as rotas daquele módulo de uma vez
Por rota — em endpoints específicos
Por regra de negócio — dentro da função, quando a permissão depende dos dados (ex.: um usuário comum pode ver apenas os próprios pedidos; admin vê todos)

A dependência de autenticação extrai o token do header, valida a assinatura, checa a expiração e devolve o usuário correspondente. Se qualquer etapa falhar, a requisição é interrompida antes de chegar ao corpo da rota.

Lazy Loading

Por padrão, o SQLAlchemy carrega relacionamentos sob demanda: ao buscar um Pedido, os ItemPedido associados não vêm junto — só são consultados no momento em que o código acessa o atributo.

Isso tem duas consequências práticas na API:

Serialização incompleta — se a resposta for montada fora do escopo da sessão do banco, os relacionamentos não carregados quebram ou vêm vazios.

Problema N+1 — listar 100 pedidos e acessar os itens de cada um dispara 1 consulta para os pedidos e mais 100 para os itens. A solução é carregamento antecipado (joinedload / selectinload), que traz tudo em uma única query.

Como rodar

Pré-requisitos: Python 3.11+

# clonar e entrar no diretório
git clone <url-do-repositorio>
cd ProjetoFastApi

# criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux / macOS

# instalar dependências
pip install -r requirements.txt

# criar o banco
alembic upgrade head

# subir o servidor
uvicorn main:app --reload

Variáveis de ambiente

Crie um arquivo .env na raiz:
SECRET_KEY=sua-chave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

Para gerar uma chave segura:
python -c "import secrets; print(secrets.token_hex(32))"
