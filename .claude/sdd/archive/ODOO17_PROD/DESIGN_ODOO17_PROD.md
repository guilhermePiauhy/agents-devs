# DESIGN: Odoo 17 Produção com PostgreSQL e Nginx

> Especificação técnica para ambiente de produção self-hosted: Odoo 17 + PostgreSQL 15 + Nginx via Docker Compose

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | ODOO17_PROD |
| **Date** | 2026-03-30 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_ODOO17_PROD.md](./DEFINE_ODOO17_PROD.md) |
| **Status** | ✅ Shipped |

---

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────┐
│                     HOST SERVER                                  │
│                                                                  │
│   Porta 80 ──→ ┌─────────────┐                                  │
│   Porta 443 ──→│    nginx    │ (container)                      │
│                │  :80 / :443 │                                   │
│                └──────┬──────┘                                   │
│                       │ proxy_pass http://odoo:8069              │
│                       ▼                                          │
│                ┌─────────────┐      ┌──────────────────┐        │
│                │    odoo     │─────→│       db         │        │
│                │   :8069     │      │  PostgreSQL 15   │        │
│                │ (container) │      │    :5432         │        │
│                └─────────────┘      │  (sem porta      │        │
│                       │             │  exposta ao host)│        │
│                       │             └──────────────────┘        │
│                       │                      │                   │
│              ┌────────▼──────────────────────▼──────────┐       │
│              │           odoo_network (bridge)           │       │
│              └──────────────────────────────────────────┘       │
│                                                                  │
│  Volumes:  odoo_data (filestore)   pg_data (postgres)           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

| Component | Purpose | Technology | Imagem Docker |
|-----------|---------|------------|---------------|
| `nginx` | Reverse proxy — SSL termination, gzip, headers de segurança | Nginx | `nginx:1.25-alpine` |
| `odoo` | Aplicação ERP | Odoo 17 (Python) | `odoo:17` |
| `db` | Banco de dados relacional | PostgreSQL 15 | `postgres:15-alpine` |

---

## Key Decisions

### Decision 1: PostgreSQL sem porta exposta ao host

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-03-30 |

**Context:** Em produção, expor a porta 5432 ao host aumenta a superfície de ataque sem benefício operacional quando Odoo acessa o banco pela rede interna Docker.

**Choice:** Não declarar `ports` para o serviço `db` no `docker-compose.yml`. Comunicação apenas via rede interna `odoo_network`.

**Rationale:** Reduz ataque externo a zero — mesmo que o firewall do host esteja mal configurado, a porta não existe no host.

**Alternatives Rejected:**
1. `ports: "5432:5432"` com firewall — rejeitado porque depende de config correta de iptables (fora do controle deste projeto)
2. `ports: "127.0.0.1:5432:5432"` — rejeitado porque ainda expõe no loopback e não é necessário

**Consequences:**
- Acesso ao banco via `docker exec` ou `docker compose exec db psql` para manutenção
- Backups executados dentro do container ou via `docker compose exec`

---

### Decision 2: Odoo sem porta exposta ao host

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-03-30 |

**Context:** Todo tráfego externo deve passar pelo Nginx para garantir headers de segurança, gzip e SSL centralizados.

**Choice:** Não declarar `ports` para o serviço `odoo`. Nginx acessa via `http://odoo:8069` na rede interna.

**Rationale:** Nginx é o único ponto de entrada externo — simplifica SSL e evita bypass de segurança.

**Alternatives Rejected:**
1. Expor 8069 diretamente — rejeitado porque bypassa SSL termination no Nginx

**Consequences:**
- Debug local requer `docker compose exec odoo` ou port-forward temporário via `docker compose port`

---

### Decision 3: `.env` para toda configuração sensível

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-03-30 |

**Context:** Hardcodar senhas no `docker-compose.yml` impede versionar o arquivo com segurança.

**Choice:** Todas as variáveis sensíveis (senhas, domínio) em `.env`, com `.env.example` versionado para documentação.

**Rationale:** `.env` listado no `.gitignore`; `.env.example` serve como documentação viva das variáveis necessárias.

**Alternatives Rejected:**
1. Docker Secrets (Swarm) — rejeitado porque está fora do escopo (single server, Compose only)

**Consequences:**
- `.env` nunca vai para o repositório — operador é responsável por criar a partir do `.env.example`

---

### Decision 4: Nginx com HTTP → HTTPS redirect + SSL manual

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-03-30 |

**Context:** SSL automático (acme-companion) foi descartado no brainstorm. SysAdmin providencia o certificado.

**Choice:** Config Nginx com dois `server` blocks: porta 80 redireciona para 443; porta 443 serve com `ssl_certificate` apontando para paths configuráveis via variável.

**Rationale:** Flexível para qualquer certificado (Let's Encrypt manual, auto-assinado, corporativo).

**Alternatives Rejected:**
1. acme-companion — rejeitado (requer DNS apontado, difícil debugar, fora do escopo)
2. Nginx sem SSL — rejeitado porque produção requer HTTPS

**Consequences:**
- SysAdmin deve gerar/copiar certificados antes de ativar HTTPS
- Para MVP sem SSL ainda, config Nginx inicia apenas com HTTP (porta 80)

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `docker-compose.yml` | Create | Orquestração dos 3 serviços com volumes e rede isolada | @shell-script-specialist | 2, 3 |
| 2 | `.env.example` | Create | Template documentado de todas as variáveis de ambiente | (general) | None |
| 3 | `.env` | Create (local, não versionar) | Variáveis sensíveis preenchidas para o ambiente | (general) | 2 |
| 4 | `nginx/conf.d/odoo.conf` | Create | Config Nginx: proxy_pass, gzip, headers, redirect HTTP→HTTPS | @shell-script-specialist | None |
| 5 | `odoo/config/odoo.conf` | Create | Config Odoo: db_host, workers, proxy_mode, addons_path | (general) | None |
| 6 | `odoo/addons/.gitkeep` | Create | Mantém diretório versionado para módulos customizados | (general) | None |
| 7 | `.gitignore` | Create | Exclui `.env`, `odoo/filestore/`, `pg_data/` do git | (general) | None |

**Total Files:** 7

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @shell-script-specialist | 1, 4 | Docker Compose YAML e Nginx conf são arquivos de infraestrutura/config com sintaxe específica e boas práticas de produção |
| (general) | 2, 3, 5, 6, 7 | Arquivos simples de configuração — sem especialização necessária |

---

## Code Patterns

### Pattern 1: Docker Compose — Estrutura dos 3 serviços

```yaml
# docker-compose.yml
version: "3.9"

services:
  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pg_data:/var/lib/postgresql/data
    networks:
      - odoo_network
    # SEM ports: — banco não exposto ao host

  odoo:
    image: odoo:17
    restart: unless-stopped
    depends_on:
      - db
    environment:
      HOST: db
      PORT: 5432
      USER: ${POSTGRES_USER}
      PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - odoo_data:/var/lib/odoo
      - ./odoo/config/odoo.conf:/etc/odoo/odoo.conf:ro
      - ./odoo/addons:/mnt/extra-addons:ro
    networks:
      - odoo_network
    # SEM ports: — acesso apenas via Nginx

  nginx:
    image: nginx:1.25-alpine
    restart: unless-stopped
    depends_on:
      - odoo
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/certs:/etc/nginx/certs:ro   # certificados SSL
    networks:
      - odoo_network

volumes:
  pg_data:
  odoo_data:

networks:
  odoo_network:
    driver: bridge
```

### Pattern 2: `.env.example` — Variáveis documentadas

```bash
# .env.example — Copie para .env e preencha os valores reais
# NUNCA versionar o .env com senhas reais

# PostgreSQL
POSTGRES_DB=odoo
POSTGRES_USER=odoo
POSTGRES_PASSWORD=CHANGE_ME_strong_password_here

# Domínio (usado no Nginx para server_name e redirect HTTPS)
ODOO_DOMAIN=erp.minha-empresa.com.br
```

### Pattern 3: Nginx config — HTTP→HTTPS redirect + proxy_pass

```nginx
# nginx/conf.d/odoo.conf

# Redirect HTTP → HTTPS
server {
    listen 80;
    server_name ${ODOO_DOMAIN};
    return 301 https://$host$request_uri;
}

# HTTPS — SSL termination + proxy para Odoo
server {
    listen 443 ssl;
    server_name ${ODOO_DOMAIN};

    ssl_certificate     /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    # Headers de segurança
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    # Proxy para Odoo
    location / {
        proxy_pass         http://odoo:8069;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 720s;
        proxy_connect_timeout 720s;
        proxy_send_timeout 720s;
    }

    # Longpolling (chat, notificações)
    location /longpolling {
        proxy_pass http://odoo:8072;
    }

    # Limitar acesso ao manager de banco de dados
    location /web/database/manager {
        deny all;
        return 403;
    }

    client_max_body_size 200m;
}
```

### Pattern 4: Odoo config

```ini
# odoo/config/odoo.conf
[options]
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
db_host = db
db_port = 5432
db_user = odoo
db_password = False   ; será sobrescrito pela variável de ambiente PASSWORD
proxy_mode = True     ; obrigatório quando Odoo está atrás de Nginx
workers = 2           ; ajustar conforme CPUs disponíveis
max_cron_threads = 1
logfile = /var/log/odoo/odoo.log
log_level = warn
```

---

## Data Flow

```text
1. Usuário acessa http://<domínio>
   │
   ▼
2. Nginx (porta 80) → redirect 301 para https://<domínio>
   │
   ▼
3. Nginx (porta 443) → SSL termination → proxy_pass http://odoo:8069
   │  Headers injetados: X-Forwarded-For, X-Forwarded-Proto
   ▼
4. Odoo processa requisição (proxy_mode=True para ler headers corretos)
   │
   ▼
5. Odoo consulta PostgreSQL via rede interna odoo_network (host=db, porta=5432)
   │
   ▼
6. Resposta retorna pelo mesmo caminho → cliente
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| PostgreSQL (container `db`) | TCP interno Docker, protocolo PostgreSQL | Usuário/senha via `.env` |
| Certificados SSL | Volume mount (`./nginx/certs/`) | N/A — arquivos no sistema de arquivos |
| Módulos customizados | Volume mount (`./odoo/addons/`) | N/A — arquivos locais |

---

## Testing Strategy

| Test Type | Scope | Procedure | Coverage Goal |
|-----------|-------|-----------|---------------|
| Smoke test | Todos os 3 containers em `running` | `docker compose ps` após `up -d` | AT-001 |
| Functional | Nginx serve Odoo via HTTP | `curl -L http://<IP>` retorna HTML do Odoo | AT-002 |
| Security | Porta 5432 não acessível externamente | `nc -zv <IP> 5432` deve falhar (connection refused) | AT-003 |
| Persistência | Dados sobrevivem restart | Criar database Odoo → `down` → `up` → database existe | AT-004 |
| Env vars | `.env` customizado é aplicado | Subir com credenciais custom → Odoo usa banco correto | AT-005 |
| Addons | Módulo em `odoo/addons/` detectado | Copiar módulo → restart odoo → aparece no menu | AT-006 |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| `db` não pronto quando `odoo` sobe | `depends_on: db` + Odoo faz retry automático de conexão | Sim (Odoo built-in) |
| Certificado SSL ausente | Nginx falha ao subir — verificar logs com `docker compose logs nginx` | Não — requer ação manual |
| `.env` ausente | `docker compose up` falha com variável não definida — copiar `.env.example` | Não — requer ação manual |
| Volume corrompido | Restaurar backup do pgdump; recriar volume | Não — requer intervenção |

---

## Configuration

| Config Key | Tipo | Exemplo | Descrição |
|------------|------|---------|-----------|
| `POSTGRES_DB` | string | `odoo` | Nome do banco PostgreSQL |
| `POSTGRES_USER` | string | `odoo` | Usuário do banco |
| `POSTGRES_PASSWORD` | string | `S3cur3P@ss` | Senha do banco (nunca commitar) |
| `ODOO_DOMAIN` | string | `erp.empresa.com` | Domínio para `server_name` no Nginx |
| `workers` (odoo.conf) | int | `2` | Workers Odoo (recomendado: 2×CPUs) |
| `client_max_body_size` (nginx) | string | `200m` | Tamanho máximo de upload |

---

## Security Considerations

- `db` e `odoo` sem portas expostas ao host — acesso externo impossível mesmo com firewall mal configurado
- `/web/database/manager` bloqueado no Nginx (`deny all`) — evita exposição do manager de bancos em produção
- Headers HTTP de segurança: `X-Frame-Options`, `X-Content-Type-Options`, `HSTS`, `X-XSS-Protection`
- `.env` com senhas no `.gitignore` — nunca versionar
- `proxy_mode = True` no Odoo — garante que logs e sessões usam IP real do cliente, não o IP do Nginx
- SSL com TLSv1.2 mínimo — TLSv1.0 e TLSv1.1 desabilitados

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logs Odoo | `docker compose logs odoo` / arquivo `/var/log/odoo/odoo.log` no container |
| Logs Nginx | `docker compose logs nginx` — access.log + error.log |
| Logs PostgreSQL | `docker compose logs db` |
| Health check | `docker compose ps` — coluna `Status` mostra `Up` ou `Exit` |
| Backup manual | `docker compose exec db pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql` |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-30 | design-agent | Versão inicial baseada em DEFINE_ODOO17_PROD.md |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_ODOO17_PROD.md`