# 22. Execution roadmap до идеального CallForce

Этот документ — практический порядок разработки. Его цель: превратить большой проект в последовательность маленьких PR, каждый из которых можно проверить.

## Правило фокуса

Пока первый вертикальный сценарий не работает end-to-end, не распыляться на все отрасли.

Первый сценарий:

> Ресторан/доставка: клиент пишет или звонит → AI отвечает по меню/FAQ → принимает заказ после подтверждения → при проблеме переводит оператору → владелец видит результат.

## Phase 0: стабилизировать фундамент

### P0.0 Project hygiene

- [ ] Закрыть все baseline CI/typecheck/lint failures.
- [ ] Убедиться, что blueprint устанавливает зависимости и pre-commit.
- [ ] Добавить `docs/strategy/22-execution-roadmap-to-ideal.md` как источник порядка работ.
- [ ] Убедиться, что `make test`, `make lint`, `make typecheck`, `make build`, `make pre-commit` проходят.

Acceptance:

- любой новый PR стартует с зелёного baseline;
- README/local-development дают воспроизводимый запуск.

### P0.1 Demo tenant and restaurant preset

- [ ] Обновить demo tenant под ресторан.
- [ ] Добавить готового агента “AI-оператор ресторана”.
- [ ] Добавить меню/FAQ/доставку/адреса/акции.
- [ ] Добавить 30-50 тестовых вопросов.

Acceptance:

- новый пользователь может открыть демо и сразу тестировать ресторанного агента.

## Phase 1: production chat MVP

### P1.1 Knowledge/RAG production path

- [ ] Проверить реальный Qdrant upsert/search/delete.
- [ ] Сделать source-only answer mode.
- [ ] Добавить no-answer behavior.
- [ ] Добавить RAG eval dataset.
- [ ] Показывать unresolved topics.

Acceptance:

- агент не выдумывает ответы;
- удалённый source не используется;
- evals проходят.

### P1.2 Web widget production install

- [ ] Виджет получает public config.
- [ ] Есть install snippet.
- [ ] Есть session persistence.
- [ ] Есть rate limiting и abuse protection.
- [ ] Есть widget analytics.

Acceptance:

- виджет можно вставить в внешний HTML и провести диалог.

### P1.3 Telegram production channel

- [ ] Настройка bot token без утечки секрета.
- [ ] Webhook verify/setup.
- [ ] Message dedupe.
- [ ] Error logs.
- [ ] Conversation continuity.

Acceptance:

- Telegram message creates/continues conversation and gets AI answer.

## Phase 2: operator handoff

### P2.1 Operator inbox

- [ ] Queue page.
- [ ] Conversation details.
- [ ] AI summary.
- [ ] Handoff reason.
- [ ] Take over/release.
- [ ] Close reason.

Acceptance:

- AI can escalate and operator can continue conversation with context.

### P2.2 Quality feedback loop

- [ ] Operator marks answer good/bad.
- [ ] Add correction note.
- [ ] Create unresolved topic.
- [ ] Suggest knowledge update.

Acceptance:

- every bad answer becomes an actionable improvement item.

## Phase 3: action engine and restaurant orders

### P3.1 Tool registry

- [ ] Tool definitions stored per tenant/agent.
- [ ] Permission model.
- [ ] Dry-run.
- [ ] Audit logs.
- [ ] Idempotency.

Acceptance:

- LLM cannot call unknown or unauthorized tools.

### P3.2 Restaurant order flow

- [ ] Menu lookup.
- [ ] Cart draft.
- [ ] Customer confirmation.
- [ ] Order creation sandbox.
- [ ] Duplicate prevention.
- [ ] Failure fallback to operator.

Acceptance:

- AI creates sandbox order only after explicit confirmation.

### P3.3 iiko/r_keeper path

- [ ] Sandbox adapter.
- [ ] Menu sync.
- [ ] Order create.
- [ ] Webhook/status.
- [ ] Error mapping.

Acceptance:

- demo restaurant order can be pushed to sandbox adapter.

## Phase 4: production voice

### P4.1 Choose telephony path

Decision needed:

- Twilio: fastest global demo.
- SIP/Asterisk: more realistic for RF/local telephony.

Acceptance:

- one path is officially selected for MVP; the other remains later.

### P4.2 Streaming speech loop

- [ ] Streaming STT.
- [ ] Turn detection.
- [ ] LLM streaming.
- [ ] TTS streaming.
- [ ] Barge-in.
- [ ] Latency metrics.

Acceptance:

- real voice call can complete 10 scripted scenarios.

### P4.3 Voice compliance

- [ ] Consent phrase.
- [ ] Recording storage.
- [ ] Transcript timestamps.
- [ ] Retention/delete policy.
- [ ] Sensitive data masking where needed.

Acceptance:

- recordings and transcripts are safe to store and review.

## Phase 5: SaaS polish and payments

- [ ] Onboarding wizard.
- [ ] Pricing page and billing status.
- [ ] Usage limits.
- [ ] ЮKassa sandbox/live flow.
- [ ] Team invites and roles polished.
- [ ] API keys and webhooks polished.

Acceptance:

- paying pilot can self-serve basic setup.

## Phase 6: analytics and growth

- [ ] ROI calculator.
- [ ] Automation rate dashboard.
- [ ] Cost dashboard.
- [ ] Quality dashboard.
- [ ] Pilot report generator.
- [ ] Sales demo script.

Acceptance:

- after pilot, owner sees business value in numbers.

## First 10 implementation PRs

1. Baseline quality fix: all checks green.
2. Restaurant demo tenant and agent preset.
3. RAG eval dataset and no-answer tests.
4. Knowledge source delete/reindex correctness.
5. Widget install snippet and public config endpoint.
6. Telegram webhook hardening and dedupe.
7. Operator inbox data model and API.
8. Operator inbox UI.
9. Action Engine tool registry and dry-run audit.
10. Restaurant order sandbox flow.

## When project can be called “ready”

Ready for demo:

- restaurant agent answers in test console and widget;
- knowledge upload works;
- basic analytics show conversations.

Ready for paid pilot:

- real Telegram/widget;
- operator handoff;
- one real/sandbox business action;
- staging deployment;
- evals and monitoring.

Ready to claim top competitor level:

- real voice calls;
- barge-in and latency metrics;
- production action integrations;
- quality dashboard;
- multiple paying pilots;
- documented reliability and safety.
