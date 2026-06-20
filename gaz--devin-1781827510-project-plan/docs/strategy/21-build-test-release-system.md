# 21. AI build, test and release system

Цель: строить CallForce как топовые AI-agent компании — через постоянный цикл evals, real-world тестов, наблюдаемости и маленьких безопасных релизов.

## Главный принцип

AI-продукт нельзя считать готовым только потому, что код работает. Нужно доказывать качество на сценариях.

Цикл разработки:

```text
Spec → implementation slice → unit/integration tests → AI evals → browser QA → voice/chat simulation → staging → monitored pilot → feedback → improvement
```

## Что тестировать всегда

### 1. Backend quality gates

Run before merge:

- `make lint`
- `make typecheck`
- `make test`
- `make build`
- `make pre-commit`
- API contract tests
- migration dry-run
- smoke checks

### 2. Frontend QA

For each UI PR:

- desktop/tablet/mobile;
- loading state;
- empty state;
- error state;
- keyboard navigation;
- console errors;
- network errors;
- production build.

### 3. RAG evals

Every knowledge-related change must run evals:

| Eval | Expected result |
| --- | --- |
| Answerable question | correct answer with source |
| Unanswerable question | honest no-answer |
| Prompt injection | ignored / safe refusal |
| Conflicting sources | asks clarification or follows priority |
| Outdated source | does not use deleted/stale content |
| Price/status/order question | uses tool/source only |

### 4. Voice evals

Voice cannot be sold until these are measured:

- STT latency;
- LLM latency;
- TTS latency;
- total turn latency;
- interruption/barge-in;
- noisy audio;
- long caller monologue;
- angry caller;
- request human;
- wrong phone/menu/order data;
- recording and transcript correctness.

### 5. Action evals

Every action must have:

- dry-run mode;
- idempotency key;
- explicit confirmation;
- permission check;
- audit log;
- rollback/cancel behavior where possible;
- webhook verification;
- retry policy;
- duplicate event handling.

## AI eval dataset structure

Create eval cases as code/data, not only manual notes.

Recommended structure:

```text
tests/evals/
  restaurant_knowledge.yml
  restaurant_orders.yml
  safety_prompt_injection.yml
  voice_call_scenarios.yml
  handoff_scenarios.yml
```

Each eval case:

```yaml
id: restaurant_delivery_min_order
channel: web_widget
input: "От какой суммы бесплатная доставка?"
expected_behavior: answer_from_source
must_include:
  - "бесплатная доставка"
forbidden:
  - "точно не знаю, но думаю"
source_required: true
max_latency_ms: 3000
```

## Release environments

### Local

Purpose: fast development.

- memory store allowed;
- local `.env`;
- Docker Compose infra optional;
- mock integrations allowed.

### Staging

Purpose: pilot rehearsal.

- PostgreSQL default;
- Redis rate limits;
- Qdrant real collection;
- object storage;
- sandbox integrations;
- Sentry/logs;
- seeded demo tenant;
- preview domain.

### Production

Purpose: paying customers.

- managed backups;
- migrations with rollback plan;
- secret manager;
- monitoring/alerting;
- HTTPS;
- audit logs;
- retention policy;
- incident runbooks.

## Manual QA checklist before paid pilot

- Register/login works.
- Create tenant/user works.
- Create agent works.
- Upload knowledge works.
- Agent answers from knowledge.
- Agent says no-answer when needed.
- Test chat creates conversation.
- Widget works from public page.
- Telegram receives/sends messages.
- Voice preview works.
- Real call works.
- Handoff creates operator queue item.
- Operator can reply.
- Action dry-run works.
- Real action sandbox works.
- Analytics update.
- Billing limits enforce.
- Audit logs capture sensitive events.

## Production monitoring

Minimum dashboards:

1. API health and error rate.
2. Conversation volume by channel.
3. Automation/handoff rate.
4. LLM latency/cost/errors.
5. RAG no-answer and low-confidence topics.
6. Voice latency by segment.
7. Action success/failure/idempotency.
8. Revenue/orders influenced.

## Definition of done for every feature

A feature is not done until:

- spec exists;
- code is merged;
- tests pass;
- evals pass if AI behavior changed;
- UI is checked if visible;
- logs/metrics exist if production path;
- runbook updated if operational behavior changed;
- rollback path is known.
