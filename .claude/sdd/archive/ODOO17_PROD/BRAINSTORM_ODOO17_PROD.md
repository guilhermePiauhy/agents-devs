# BRAINSTORM: Odoo 17 Produção com PostgreSQL e Nginx

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | ODOO17_PROD |
| **Date** | 2026-03-30 |
| **Author** | brainstorm-agent |
| **Status** | Ready for Define |

---

## Initial Idea

**Raw Input:** "Criar projeto odoo 17 com postgree e proxyreverso"

**Context Gathered:**
- Ambiente de produção self-hosted (não dev/POC)
- Sem configuração existente — projeto do zero
- Sem módulos customizados definidos ainda

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Orquestração | Docker Compose (single server) | Um `docker-compose.yml` com 3 serviços |
| Reverse Proxy | Nginx | Config manual, SSL por certificado ou certbot |
| Banco de Dados | PostgreSQL 15 | Não exposto externamente — rede interna Docker |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Qual o objetivo do ambiente? | Produção self-hosted | Configurações de segurança e performance necessárias |
| 2 | Qual reverse proxy? | Nginx | Config manual em `conf.d/odoo.conf` |
| 3 | Como orquestrar os serviços? | Docker Compose | Single `docker-compose.yml`, sem Swarm/K8s |
| 4 | Samples ou restrições existentes? | Nenhum — do zero | Estrutura padrão sem necessidade de migração |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | N/A | 0 | Projeto do zero |
| Output examples | N/A | 0 | — |
| Ground truth | N/A | 0 | — |
| Related code | N/A | 0 | — |

---

## Approaches Explored

### Approach A: Docker Compose multi-service com Nginx dedicado ⭐ Recommended

**Description:** Três serviços isolados no Compose (`db`, `odoo`, `nginx`) com volumes persistentes e `.env` para configuração sensível.

**Pros:**
- Isolamento claro entre serviços
- Fácil substituição/atualização de componentes individualmente
- Nginx controla SSL, gzip e headers de segurança
- Padrão amplamente documentado para Odoo em produção

**Cons:**
- Requer configuração manual do SSL
- Mais arquivos para gerenciar

**Why Recommended:** Melhor controle, mais claro, padrão de mercado para Odoo self-hosted em produção.

---

### Approach B: nginx-proxy + acme-companion (SSL automático)

**Description:** Usa `nginxproxy/nginx-proxy` + `nginxproxy/acme-companion` para SSL automático via Let's Encrypt sem configuração manual do Nginx.

**Pros:**
- SSL automático com renovação zero-config
- Menos configuração manual

**Cons:**
- Requer domínio com DNS apontado (não funciona offline)
- Menos controle sobre config do Nginx
- Difícil de debugar

---

### Approach C: Nginx no host (sem container)

**Description:** Nginx instalado diretamente no SO do servidor, fazendo proxy para containers Odoo/Postgres.

**Pros:**
- Ligeira vantagem de performance de rede

**Cons:**
- Mistura infra de host com containers
- Difícil de replicar e versionar

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-03-30 |
| **Reasoning** | Mais controle, estrutura clara, padrão de produção |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | PostgreSQL não exposto externamente | Segurança — acesso apenas via rede interna Docker | Expor porta 5432 ao host |
| 2 | Odoo acessível apenas via Nginx | SSL termination e headers de segurança centralizados | Expor 8069 diretamente |
| 3 | `.env` para variáveis sensíveis | Evitar senhas hardcoded no `docker-compose.yml` | Secrets hardcoded |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Redis/Celery para tarefas assíncronas | Não necessário no MVP | Yes |
| Monitoramento (Prometheus/Grafana) | Fora do escopo inicial | Yes |
| Multi-instância Odoo com load balancing | Desnecessário para single server | Yes |
| Backup automatizado (pgdump cron) | Pode ser adicionado após setup inicial | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Estrutura do projeto e serviços Docker | ✅ | Confirmado ("estamos alinhados") | No |
| Fluxo de rede e exposição de portas | ✅ | Confirmado ("s") | No |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
Criar um ambiente de produção self-hosted para Odoo 17, com PostgreSQL 15 como banco de dados e Nginx como reverse proxy, orquestrado via Docker Compose em servidor único.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Administrador do servidor | Precisa de ambiente Odoo estável, seguro e fácil de manter em produção |
| Usuários de negócio | Precisam acessar o Odoo via HTTPS de forma confiável |

### Success Criteria (Draft)
- [ ] Odoo 17 acessível via Nginx (HTTP/HTTPS)
- [ ] PostgreSQL acessível apenas internamente (porta não exposta)
- [ ] Dados persistentes entre restarts (`docker compose down` / `up`)
- [ ] Configuração sensível (senhas, domínio) em `.env`
- [ ] Nginx configurado com proxy_pass, headers de segurança e gzip

### Constraints Identified
- Single server (não cluster)
- Docker Compose como orquestrador
- Nginx como reverse proxy (não Traefik/Caddy)

### Out of Scope (Confirmed)
- SSL automático via acme-companion
- Redis/Celery
- Monitoramento e observabilidade
- Backup automatizado
- Multi-instância / load balancing

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 4 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 4 |
| Validations Completed | 2 |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_ODOO17_PROD.md`