# DEFINE: Odoo 17 Produção com PostgreSQL e Nginx

> Ambiente de produção self-hosted para Odoo 17, orquestrado via Docker Compose com PostgreSQL 15 e Nginx como reverse proxy.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | ODOO17_PROD |
| **Date** | 2026-03-30 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 14/15 |
| **Source** | BRAINSTORM_ODOO17_PROD.md |

---

## Problem Statement

O time precisa de um ambiente de produção Odoo 17 self-hosted, estável e seguro, sem exposição direta do banco de dados ou da aplicação à internet. A ausência de um setup padronizado aumenta o risco de configurações inseguras e dificulta a manutenção do ambiente ao longo do tempo.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Administrador do servidor | DevOps / SysAdmin | Precisa de ambiente reproduzível, seguro e fácil de manter |
| Usuários de negócio | Operadores do Odoo | Precisam acessar o Odoo via HTTPS de forma confiável e estável |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | Odoo 17 acessível via Nginx (HTTP redireciona para HTTPS) |
| **MUST** | PostgreSQL 15 acessível apenas internamente (sem porta exposta ao host) |
| **MUST** | Dados persistentes entre restarts (`docker compose down` / `up`) |
| **MUST** | Configuração sensível (senhas, domínio) isolada em arquivo `.env` |
| **MUST** | Nginx configurado com proxy_pass, headers de segurança e compressão gzip |
| **SHOULD** | Estrutura de diretórios clara para adicionar addons customizados |
| **COULD** | Backup manual documentado (dump do PostgreSQL) |

---

## Success Criteria

- [ ] `docker compose up -d` sobe todos os serviços sem erros
- [ ] Odoo 17 responde na porta 80 e/ou 443 via Nginx
- [ ] Acesso direto às portas 8069 (Odoo) e 5432 (Postgres) bloqueado externamente
- [ ] Dados do Odoo e do PostgreSQL persistem após `docker compose down && docker compose up`
- [ ] Arquivo `.env` centraliza todas as variáveis sensíveis (sem senhas hardcoded no `docker-compose.yml`)
- [ ] Diretório `odoo/addons/` pronto para receber módulos customizados

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Subida dos serviços | Arquivo `.env` configurado corretamente | `docker compose up -d` executado | Todos os 3 serviços (`db`, `odoo`, `nginx`) em status `running` |
| AT-002 | Acesso via Nginx | Serviços rodando | Browser acessa `http://<IP-do-servidor>` | Odoo 17 carrega (ou redireciona para HTTPS) |
| AT-003 | Isolamento do banco | Serviços rodando | Tentativa de conexão à porta 5432 do host | Conexão recusada (porta não exposta) |
| AT-004 | Persistência de dados | Odoo configurado e com dados | `docker compose down && docker compose up -d` | Dados e configurações do Odoo preservados |
| AT-005 | Configuração via .env | `.env` com valores customizados | `docker compose up -d` | Odoo usa banco e senha definidos no `.env` |
| AT-006 | Addons customizados | Módulo copiado para `odoo/addons/` | Reiniciar container Odoo | Módulo aparece disponível no Odoo |

---

## Out of Scope

- SSL automático via Let's Encrypt / acme-companion (pode ser adicionado após MVP)
- Redis / Celery para tarefas assíncronas
- Monitoramento e observabilidade (Prometheus, Grafana)
- Backup automatizado (pgdump cron job)
- Multi-instância Odoo com load balancing
- Configuração de firewall / iptables (responsabilidade do SysAdmin)
- Módulos ou customizações específicas do Odoo

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Docker Compose como único orquestrador | Sem Swarm, K8s ou equivalente |
| Technical | Nginx como reverse proxy (não Traefik/Caddy) | Config manual em `conf.d/odoo.conf` |
| Infrastructure | Single server (não cluster) | Todos os serviços no mesmo host |
| Security | PostgreSQL e Odoo sem portas expostas ao host | Acesso apenas via Nginx e rede interna Docker |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | Raiz do projeto (`./`) | `docker-compose.yml`, `.env`, `nginx/`, `odoo/` |
| **KB Domains** | `aws` (containers), `python` (Odoo config), `terraform` (N/A) | Padrões de containerização e config |
| **IaC Impact** | Novos recursos (Docker Compose) | Nenhuma infra cloud envolvida |

**Estrutura de arquivos esperada:**

```text
odoo-projeto/
├── docker-compose.yml
├── .env
├── nginx/
│   └── conf.d/
│       └── odoo.conf
├── odoo/
│   ├── config/
│   │   └── odoo.conf
│   └── addons/
```

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Docker e Docker Compose estão instalados no servidor | Necessário instalar antes do setup | [ ] |
| A-002 | Servidor tem acesso à internet para pull das imagens Docker | Necessário mirror local ou imagens pré-baixadas | [ ] |
| A-003 | SSL será configurado manualmente pelo SysAdmin após o setup (certbot ou certificado próprio) | HTTPS não funcionará sem ação manual | [x] Confirmado no brainstorm |
| A-004 | Portas 80 e 443 estão liberadas no firewall do servidor | Odoo não ficará acessível externamente | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Claro, específico, acionável |
| Users | 2 | Identificados mas pain points parcialmente detalhados |
| Goals | 3 | Priorizados com MUST/SHOULD/COULD |
| Success | 3 | Critérios testáveis e mensuráveis |
| Scope | 3 | In/out scope explícito |
| **Total** | **14/15** | Acima do mínimo de 12 |

---

## Open Questions

Nenhuma — pronto para Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-30 | define-agent | Versão inicial baseada em BRAINSTORM_ODOO17_PROD.md |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_ODOO17_PROD.md`