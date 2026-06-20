# CallForce Master Plan: текущий статус и путь до production-идеала

Дата анализа: 2026-06-20
Репозиторий: `RiggerGlimpse/toptop`
Цель: довести CallForce до уровня сильного коммерческого AI-оператора для звонков и чатов, сначала для ресторанов/доставки в РФ/СНГ.

## 1. Честный статус

CallForce уже является рабочим MVP-фундаментом, но ещё не полностью готовым production SaaS. Сейчас в проекте есть:

- FastAPI backend на Python 3.12;
- Next.js кабинет на TypeScript;
- multi-tenant модель;
- auth: register/login/refresh/logout/me/MFA/recovery/reset/verify-email;
- RBAC, sessions, API keys, audit events;
- agents: create/update/publish, prompt/channel/voice настройки;
- knowledge/RAG: sources, upload, parsers, ingestion jobs, chunks, Qdrant contract;
- RAG guardrails: relevance gate, prompt-injection detector, no-answer escalation;
- conversations: list/detail, transcript, sources, statuses;
- первый operator handoff: `needs_human` -> operator reply -> `resolved`;
- web widget endpoint and widget UI;
- Telegram webhook/adapter skeleton;
- voice session state machine, preview-turn, audio endpoint, WebSocket route, Twilio webhook/outbound skeleton;
- integration contracts/local adapters: iiko, Telegram outbound, YooKassa, webhook signatures;
- billing ledger/status/usage;
- analytics overview/agents;
- seeded Demo Pizza tenant as restaurant scenario;
- backend test suite: 83 tests passed locally;
- `make lint`, `make typecheck`, `make test`, `make build`, `make pre-commit`.

Главный вывод: проект уже демонстрирует правильную архитектуру и ключевые MVP-потоки, но многие коммерческие блоки пока `local_stub`, skeleton или preview. До “идеала” нужно закрыть реальные каналы, voice production, operator inbox, action/order engine, observability, deploy, billing, security/compliance и полный UI/QA-polish.

## 2. Правильное позиционирование

Не строить абстрактного чатбота “для всех”. Первый сильный продукт:

> **CallForce — AI-оператор для ресторанов и доставки: отвечает на звонки, Telegram/WhatsApp/VK и сайт-чат, знает меню/доставку/акции, принимает и уточняет заказы, подключается к iiko/r_keeper/1C/CRM, а сложные случаи передаёт оператору с полной историей.**

Почему рестораны первыми:

1. Быстрый ROI: меньше пропущенных звонков, быстрее ответы, больше заказов.
2. У проекта уже есть Demo Pizza preset, menu/delivery/order/handoff policy.
3. Локальные интеграции iiko/r_keeper/Telegram/WhatsApp/voice нужны именно этому рынку.
4. Российскому бизнесу важны рубли, русский голос, 152-ФЗ, локальные каналы и понятный запуск.

## 3. Как всё должно работать в идеале

### 3.1 Chat flow

1. Клиент пишет в Telegram/WhatsApp/VK/web-widget.
2. Channel adapter нормализует входящее сообщение в `Conversation` + `Message`.
3. Orchestrator получает tenant, agent, channel, историю и текст клиента.
4. RAG ищет только релевантные источники.
5. Если источник найден и запрос безопасен — AI отвечает по базе знаний.
6. Если источник не найден, запрос опасный или требует человека — conversation становится `needs_human`.
7. Operator inbox показывает диалог, reason, summary, suggested reply, customer card и SLA.
8. Оператор отвечает вручную или через AI-draft.
9. Ответ уходит в тот же канал, transcript обновляется.
10. Analytics считает automation rate, unresolved topics, cost, conversion, SLA.

### 3.2 Voice flow

1. Клиент звонит на номер.
2. Telephony provider/SIP/Twilio-compatible gateway подключает streaming audio.
3. STT распознаёт речь потоково.
4. Voice activity detection понимает паузы и перебивания.
5. Orchestrator отвечает с RAG/action context.
6. TTS генерирует натуральный русский голос.
7. AI умеет barge-in, transfer to human, fallback, consent phrase.
8. После звонка сохраняются recording, transcript, summary, outcome, QA score.

### 3.3 Restaurant order flow

1. Клиент спрашивает меню/доставку/акции.
2. AI отвечает только из menu/delivery/order policy.
3. Клиент выбирает позиции.
4. AI собирает order draft: items, quantity, modifiers, address, phone, time, payment.
5. AI обязательно подтверждает итог: состав, цена, адрес, время.
6. Только после явного подтверждения создаётся order action.
7. iiko/r_keeper/CRM получает заказ с idempotency key.
8. Клиент получает order number/status.
9. Любой конфликт, аллерген, неизвестная позиция или изменение заказа — handoff.

## 4. Что уже работает по слоям

### Backend/API

Есть routes для auth, tenants, agents, knowledge, conversations, widget, Telegram webhook, integrations, voice, billing, API keys, team, analytics, health/readiness. Самые зрелые пути: auth, agents, knowledge ingestion, RAG no-answer, conversations, operator reply, demo dashboard. Менее зрелые: real Telegram/WhatsApp/VK, production voice, real iiko/r_keeper/CRM actions, production billing.

### Frontend/UI

Есть страницы: landing, login/register/MFA/reset, dashboard, agents, knowledge, conversations, test-console, widget, analytics, onboarding, settings, docs/privacy/terms. Самые живые пользовательские потоки: demo login, dashboard, agent create/update/publish, knowledge source, Test Console chat, RAG escalation, conversation detail, operator reply, voice preview.

### RAG/no-hallucination

Сейчас есть chunking, retrieval, Qdrant contract, relevance filter, prompt-injection detection, no-answer escalation and regression tests. Нужно добавить production embeddings per tenant, citations in UI, eval dataset, coverage audit, unresolved topics workflow, reranker/confidence and merge-blocking hallucination evals.

### Operator handoff

Сейчас работает минимальный loop: AI создаёт `needs_human`, оператор на detail page вводит reply, backend сохраняет `operator` message and marks conversation `resolved`. Нужно сделать полноценный inbox: очередь, фильтры, assignment, SLA, notes, reopen, channel outbound, supervisor view, audit.

### Voice

Сейчас есть state machine, preview-turn, WebSocket/audio/Twilio skeleton. Нужно production STT/TTS streaming, barge-in, recording, transfer, DTMF, provider hardening, latency monitoring, call evals, real phone numbers.

### Integrations/actions

Сейчас есть local contracts for iiko menu/order, Telegram outbound, YooKassa payment, webhook signing. Нужно real credentials, sandbox/live toggles, retries, persistent idempotency, order state machine, CRM lookup, Bitrix24/AmoCRM/1C/r_keeper, visible action logs.

## 5. Что заменено в документации

Старые разрозненные strategy `.md` заменены этим единым master plan, чтобы не держать 20+ документов с пересекающимися roadmap. Essential docs нужно оставить:

- `README.md` — быстрый старт и обзор;
- `AGENTS.md` — правила разработки;
- `DEPLOYMENT.md` — deployment context;
- `SKILLS.md` — skills context;
- `apps/api/README.md` — API setup;
- `docs/runbooks/*` — operational runbooks;
- `docs/architecture/overview.md` — architecture reference;
- `docs/INDEX.md` — индекс актуальной документации.

## 6. Roadmap до 10000%

### Phase 0 — Documentation and setup cleanup

Задачи:

- держать один master plan вместо множества старых roadmap;
- обновить README and docs index links;
- принять suggested `.agents/skills/testing-callforce-runtime/SKILL.md`;
- добавить repo blueprint для future setup if approved;
- проверить docs links;
- добавить release notes/changelog.

Acceptance criteria:

- новый разработчик понимает, что реально работает, а что stub;
- setup/test/build commands documented;
- нет противоречивых roadmap-документов.

### Phase 1 — Operator Inbox v1

Почему первым: RAG уже создаёт `needs_human`, значит бизнесу нужна нормальная очередь операторов.

Задачи:

- route `/inbox` или major upgrade `/conversations`;
- filters: needs_human/open/resolved/channel/agent/date/assigned_to;
- counters by status;
- sorting by SLA/updated_at;
- customer card;
- assignment: unassigned/me/team;
- reply composer;
- internal notes;
- close/reopen/escalate;
- suggested AI reply;
- audit log;
- tests and browser runtime test.

Acceptance criteria:

- оператор видит все `needs_human` без ручного поиска;
- can assign/reply/close/reopen;
- state persists after reload;
- SLA/assignment visible.

### Phase 2 — Real messaging channels

#### Telegram

- webhook setup/verification;
- per-tenant bot token settings/secrets;
- inbound normalization;
- AI/operator outbound replies;
- duplicate update handling;
- attachments policy;
- typing indicator;
- retries/error logs.

#### WhatsApp

- choose provider: Meta Cloud API/360dialog/Wazzup/Green API;
- webhook validation;
- template/session-window rules;
- inbound/outbound text;
- media support;
- pricing/limits;
- tenant setup UI.

#### VK

- group token setup;
- callback confirmation;
- inbound/outbound;
- duplicate handling;
- attachments.

Acceptance criteria:

- real customer message reaches CallForce;
- AI answer or operator answer returns to same channel;
- transcript matches external channel history;
- duplicates are ignored.

### Phase 3 — Production web widget

Задачи:

- embeddable script;
- public widget config endpoint;
- CORS/domain allowlist;
- visitor session id;
- message persistence after reload;
- loading/offline/error states;
- mobile layout;
- unread badge;
- theme customization;
- privacy/consent copy;
- abuse/rate limit.

Acceptance criteria:

- business can install widget on site;
- desktop/mobile work;
- handoff works;
- no tenant data leak.

### Phase 4 — Voice production

Задачи:

- choose provider for РФ/СНГ: SIP/Twilio alternative/UIS/Mango/Novofon/MCN/Asterisk;
- real inbound and outbound calls;
- streaming STT;
- streaming TTS;
- interruption/barge-in;
- silence timeout;
- transfer to human;
- call recording;
- consent phrase;
- transcript timestamps;
- latency/WER/dropped call metrics;
- fallback if provider/STT/TTS fails;
- load tests for concurrent calls.

Acceptance criteria:

- 20+ real test calls pass golden scenarios;
- p95 latency target is measured;
- caller can interrupt AI;
- transfer works;
- recording/transcript saved.

### Phase 5 — Restaurant Action Engine

Задачи:

- order draft model;
- order state machine: collecting -> confirming -> submitted -> accepted/rejected/cancelled;
- menu item matching;
- modifiers/allergens/stop-list;
- delivery address validation;
- working hours;
- delivery zone/price/min order;
- payment method;
- explicit confirmation before creating order;
- iiko/r_keeper real adapter/sandbox;
- idempotency/retry;
- action logs;
- operator approval for risky actions;
- CRM customer lookup/create;
- order status lookup.

Acceptance criteria:

- AI creates real/sandbox order only after explicit confirmation;
- no duplicate orders on retry;
- ambiguous items escalate;
- order appears in POS/CRM;
- transcript includes action result.

### Phase 6 — RAG evals and citations

Задачи:

- benchmark dataset: menu, delivery, allergens, order status, unknown topics, prompt injection;
- automated eval runner;
- source coverage report;
- answer faithfulness scoring;
- strict policy: prices/status/orders only from source/action result;
- citations visible in UI;
- unresolved topic creation;
- admin flow to add source from unresolved topic;
- per-tenant RAG metrics;
- CI gate for hallucination regressions.

Acceptance criteria:

- eval suite blocks bad merges;
- unknown topics become `needs_human`;
- grounded answers show sources;
- unresolved topics improve KB.

### Phase 7 — UI/UX polish every pixel

Задачи для всех critical pages:

- desktop/tablet/mobile pass;
- keyboard navigation;
- focus states;
- empty/loading/error states;
- consistent spacing/typography;
- forms validation;
- accessible labels;
- skeletons instead of layout jumps;
- no weak contrast;
- no fake data in live mode without label;
- responsive sidebar/header;
- toast consistency;
- Russian microcopy polish.

Critical screens:

- landing;
- register/login/MFA/reset;
- onboarding;
- dashboard;
- agents list/detail/create;
- knowledge;
- test-console;
- inbox/conversations/detail;
- widget;
- analytics;
- channel settings;
- team/security/API keys;
- billing.

Acceptance criteria:

- browser recording per critical flow;
- no relevant console errors;
- no broken critical requests;
- mobile screenshots pass;
- forms cannot silently fail.

### Phase 8 — Security and compliance РФ

Задачи:

- secrets management;
- no secrets in logs;
- tenant isolation tests;
- RBAC matrix tests;
- audit log UI/export;
- data retention policy;
- customer/conversation export/delete;
- consent for call recording;
- 152-ФЗ docs/process;
- rate limits;
- webhook signatures;
- API key scopes;
- MFA enforcement option;
- security headers/CSP;
- dependency audit/SBOM;
- backup encryption;
- incident runbook.

Acceptance criteria:

- tenant A cannot read tenant B;
- permissions are enforced;
- sensitive actions audited;
- customer data export/delete works;
- public endpoints rate-limited.

### Phase 9 — Billing and commercial packaging

Задачи:

- tariffs in DB;
- usage metering: messages, call minutes, STT/TTS cost, actions;
- quota enforcement;
- YooKassa checkout;
- invoices/receipts;
- trial mode;
- overage rules;
- plan upgrade/downgrade;
- billing UI;
- admin override;
- unit economics dashboard.

Acceptance criteria:

- quota limits work;
- payment updates plan;
- usage reconciles with conversations/calls;
- billing failures do not delete data.

### Phase 10 — Observability, CI/CD, deploy

Задачи:

- GitHub Actions CI for lint/typecheck/test/build;
- preview deploy per PR;
- staging environment;
- production deploy;
- Sentry frontend/backend;
- structured logs;
- OpenTelemetry traces;
- metrics dashboards;
- alerts: error rate, latency, failed webhooks, voice failures, queue SLA;
- smoke checks after deploy;
- backup/restore drill scheduled;
- migration dry-run in CI;
- load tests.

Acceptance criteria:

- PR cannot merge with failing checks;
- every PR has preview URL;
- deploy has smoke check;
- failures are diagnosable.

### Phase 11 — Onboarding and sales launch

Задачи:

- restaurant onboarding wizard;
- upload menu/FAQ/docs;
- choose preset;
- configure channels;
- test bot checklist;
- invite team;
- install widget;
- connect Telegram/WhatsApp/phone;
- connect iiko/CRM;
- launch readiness score;
- demo scripts;
- pilot checklist;
- success metrics dashboard.

Acceptance criteria:

- new restaurant setup in 30-60 minutes;
- launch readiness visible;
- after launch, dashboard shows automation rate, saved missed calls, assisted orders.

## 7. Следующие PR по приоритету

1. **Operator Inbox v1** — очередь, фильтры, assignment, SLA, notes, reopen.
2. **Telegram real round-trip** — real inbound/outbound with same transcript.
3. **Production Web Widget** — embed script, sessions, mobile, allowlist.
4. **RAG evals/citations** — automated no-hallucination quality gate.
5. **Restaurant Order Engine** — order draft, confirmation, iiko/r_keeper sandbox.
6. **Voice production spike** — provider decision, real call prototype, latency.
7. **Security/compliance pack** — tenant isolation, audit UI, export/delete, 152-ФЗ.
8. **CI/CD/preview/staging** — required checks and deploy safety.
9. **Billing UI/YooKassa live flow** — real tariffs/usage/quota.
10. **Every-pixel UI QA** — critical pages desktop/tablet/mobile.

## 8. Definition of Done for the whole product

### Product DoD

- AI answers real chats and calls;
- restaurant preset handles menu/FAQ/order/handoff;
- operator inbox closes complex cases;
- customer launches without developer;
- billing works;
- analytics shows business value.

### Engineering DoD

- lint/typecheck/tests/build/pre-commit pass;
- CI is required;
- preview/staging/prod exist;
- migrations safe;
- backups/restores work;
- logs/metrics/traces/Sentry exist;
- load tests cover calls/messages.

### AI Quality DoD

- RAG evals pass;
- prompt injection does not leak instructions;
- AI does not invent prices/statuses/delivery/order facts;
- unknown topics go to operator;
- sources are visible;
- regressions block merge.

### Voice DoD

- real inbound/outbound calls;
- streaming STT/TTS;
- barge-in;
- transfer;
- recording/transcript;
- measured latency;
- provider failure fallback.

### Security DoD

- tenant isolation tested;
- RBAC tested;
- audit logs visible/exportable;
- customer data export/delete;
- secrets protected;
- rate limits;
- webhook signatures;
- 152-ФЗ/privacy/terms ready.

### UX DoD

- every critical page checked desktop/tablet/mobile;
- no relevant console errors;
- no broken critical requests;
- accessible labels/focus;
- loading/empty/error states;
- Russian copy polished;
- onboarding understandable.

## 9. Основные риски

| Риск | Почему опасно | Как закрыть |
| --- | --- | --- |
| Voice latency | Звонок ощущается плохим | streaming STT/TTS, barge-in, latency dashboard |
| Hallucination | Неверные цены/сроки/статусы | RAG evals, citations, action-only status/order answers |
| Каналы только stub | Нельзя продавать без real Telegram/WhatsApp/voice | real channel adapters |
| Нет operator inbox | `needs_human` не превращается в процесс | inbox, assignment, SLA, notifications |
| Нет order actions | Ресторану мало FAQ | order engine + iiko/r_keeper |
| Нет monitoring | Ошибки не видны | Sentry, metrics, alerts, smoke checks |
| UI выглядит MVP | Клиент не доверяет продукту | visual QA and polish |
| Compliance не закрыт | Риск для звонков/персональных данных | 152-ФЗ, audit, retention, export/delete |

## 10. Итог

Текущий проект — хороший рабочий MVP-фундамент. Он уже показывает правильный путь: agents, knowledge, RAG guardrails, restaurant demo, Test Console, conversations, first operator handoff, voice/integration skeletons.

Но “идеальный коммерческий продукт” появится только после последовательного закрытия production-блоков: operator inbox, real channels, production widget, voice calls, restaurant order engine, RAG evals/citations, UI polish, security/compliance, billing, observability/deploy, onboarding/sales.

Рекомендованный следующий PR: **Operator Inbox v1**, потому что RAG уже создаёт `needs_human`, а операторский процесс должен стать полноценным, быстрым и видимым.

---

# 11. Дополнение: ultra-detailed production blueprint до “10000%”

Этот раздел добавлен после повторного анализа текущего кода и открытых feature-паттернов лидеров рынка voice/support AI. Он не заменяет roadmap выше, а делает его более детальным: что именно должно существовать в продукте, backend, frontend, данных, QA, безопасности, продажах и операциях, чтобы CallForce можно было считать готовым лучше конкурентов.

## 11.1 Что делают лидеры и что CallForce должен закрыть

Наблюдения по рынку:

- Bland AI делает упор на sub-second/sub-200ms voice, same memory across voice/SMS/chat, telephony portability, voice cloning, pathways, compliance, audit trails, retention, redaction, SSO/RBAC/MFA, data residency, incident response and warm transfer.
- Intercom Fin делает упор на knowledge guidance, source/content performance, escalation reporting, AI involvement/resolution metrics and continuous training.
- Zendesk AI agents делают упор на omnichannel support, trusted knowledge, generative procedures, authorized actions, analytics, QA, workforce/contact-center ecosystem.
- Vapi делает упор на low-latency voice, provider fallback, monitoring by issue type, technical/infrastructure monitoring, logs, analytics, structured outputs, enterprise reliability.
- Retell делает упор на turn-taking, low-latency voice, real-time function calling, transfer, post-call analysis, dashboards, batch campaigns and conversion tracking.

Вывод для CallForce:

| Competitor strength | Что это значит практически | Что нужно в CallForce |
| --- | --- | --- |
| Same memory across channels | Клиент начал в Telegram, продолжил звонком, оператор видит всё | unified customer profile, cross-channel conversation stitching, channel identity map |
| Low-latency voice | Голос не должен звучать как “бот с паузами” | streaming STT/TTS, barge-in, p95 latency metrics, provider failover |
| Warm transfer | Оператор получает briefing до соединения | warm transfer flow, operator briefing prompt, hold music, unavailable fallback |
| Guided knowledge | AI выбирает правильные источники по policy | knowledge guidance rules, source priority, source performance analytics |
| Authorized actions | AI делает действия только с правами/approval | action permissions, confirmation gates, idempotency, audit, rollback/fallback |
| Monitoring | Владелец видит, что ломается и почему | issue monitors, alerts, traces, failed tool-call dashboard |
| QA/evals | Нельзя выпускать плохого агента | eval lab, simulation runs, red-team cases, regression gate |
| Compliance | Enterprise покупает только с безопасностью | SSO/SAML, audit export, retention, redaction, data residency, incident runbooks |
| Analytics | Бизнес покупает результат, не “AI” | automation rate, containment, revenue assisted, missed calls saved, cost per resolution |

## 11.2 Product principles для “лучше конкурентов”

1. **Vertical-first, not generic-first**: ресторанный оператор должен быть готовым продуктом, а не набором API.
2. **Grounded by default**: AI отвечает только из источника или результата action; иначе handoff.
3. **Human handoff is a feature, not failure**: оператор получает summary, reason, recommended reply, customer card, SLA, channel context.
4. **Voice must feel real-time**: latency, interruption, turn-taking and transfer are product features.
5. **Actions require governance**: любые заказы/оплаты/изменения статуса идут через confirmations, permissions, audit, idempotency.
6. **Every answer improves the system**: unresolved topics, content performance and QA labels feed back into knowledge and prompts.
7. **One customer, many channels**: один профиль клиента across phone/Telegram/WhatsApp/VK/web.
8. **Sell outcomes**: показывать saved calls, assisted orders, automation rate, revenue, SLA, CSAT.
9. **No black box**: sources, tool calls, prompt version, model version, costs and traces visible to admins.
10. **Launch safely**: sandbox -> pilot -> limited production -> full rollout, with kill switches.

## 11.3 Полная domain model, которой не хватает

Сейчас есть базовые tenants/users/agents/knowledge/conversations/messages/api keys/billing. Для production нужны новые сущности.

### Customer and identity

- `CustomerProfile`
  - `id`
  - `tenant_id`
  - `display_name`
  - `phone_e164`
  - `telegram_user_id`
  - `whatsapp_user_id`
  - `vk_user_id`
  - `web_visitor_id`
  - `email`
  - `crm_external_id`
  - `first_seen_at`
  - `last_seen_at`
  - `tags`
  - `consent_flags`
  - `metadata`
- `ChannelIdentity`
  - links one customer to multiple channel-specific identities;
  - prevents duplicate customer records;
  - stores verification confidence.

### Inbox and operations

- `InboxThread`
  - canonical thread across one or multiple conversations;
  - status: `open`, `needs_human`, `pending_customer`, `pending_external`, `resolved`, `spam`, `archived`.
- `Assignment`
  - `assignee_user_id`
  - `team_id`
  - `assigned_at`
  - `assignment_reason`
- `SlaPolicy`
  - first response target;
  - resolution target;
  - business hours;
  - escalation ladder.
- `InternalNote`
  - private operator/supervisor notes;
  - never sent to customer.
- `OperatorPresence`
  - online/offline/busy;
  - capacity;
  - routing availability.

### Actions and orders

- `ActionRun`
  - `action_type`: `create_order`, `lookup_order`, `cancel_order`, `book_table`, `create_payment`, `crm_update`;
  - input/output JSON;
  - status: `draft`, `needs_confirmation`, `approved`, `running`, `succeeded`, `failed`, `rolled_back`;
  - idempotency key;
  - approvals;
  - trace id.
- `OrderDraft`
  - items, modifiers, quantities;
  - customer contact;
  - delivery/pickup;
  - address;
  - payment method;
  - confirmation text shown to customer;
  - external order id.
- `MenuCatalog`
  - normalized menu items from knowledge/iiko/r_keeper;
  - availability/stop-list;
  - prices;
  - allergens;
  - modifiers.

### Voice

- `CallSession`
  - call id, provider call id, direction, phone numbers;
  - status: ringing/active/on_hold/transferring/completed/failed;
  - recording URL;
  - transcript segments;
  - latency metrics;
  - transfer data;
  - consent recorded.
- `TranscriptSegment`
  - speaker;
  - start/end time;
  - confidence;
  - text;
  - interrupted flag.
- `VoiceMetric`
  - STT latency;
  - LLM latency;
  - TTS latency;
  - turn latency;
  - WER proxy;
  - barge-in count;
  - silence timeout.

### Knowledge and quality

- `KnowledgeGuidanceRule`
  - if condition -> required/preferred sources;
  - escalation rule;
  - answer format.
- `UnresolvedTopic`
  - question;
  - conversation id;
  - category;
  - suggested source;
  - status: new/triaged/fixed/ignored.
- `EvalSuite`
  - restaurant FAQ;
  - unknown topics;
  - prompt injection;
  - order policy;
  - channel-specific cases;
  - voice turn-taking cases.
- `EvalRun`
  - prompt version;
  - model version;
  - knowledge version;
  - pass/fail;
  - traces.

### Observability and governance

- `PromptVersion`
  - agent id;
  - prompt text;
  - changelog;
  - author;
  - eval result before publish.
- `ModelConfigVersion`
  - provider;
  - model;
  - temperature;
  - fallback chain;
  - cost assumptions.
- `AuditExportJob`
  - compliance export for tenant/admin.
- `RetentionPolicy`
  - transcript retention;
  - recording retention;
  - PII redaction policy.

## 11.4 Backend modules to build or expand

### Core orchestration

Needed:

- `ConversationOrchestrator` should become channel-agnostic and support:
  - chat input;
  - voice turn input;
  - operator reply;
  - action callbacks;
  - scheduled follow-ups;
  - idempotency;
  - trace propagation.
- Add deterministic decision step:
  - `answer_with_rag`;
  - `ask_clarifying_question`;
  - `draft_action`;
  - `request_confirmation`;
  - `handoff_to_human`;
  - `close_as_resolved`.
- Store `decision_reason` and `confidence` for every AI turn.

### Channel adapters

Every channel adapter must implement a common interface:

```text
receive(raw_event) -> NormalizedInboundMessage
send(thread_id, outbound_message) -> DeliveryResult
mark_read(thread_id) -> DeliveryResult
send_typing(thread_id) -> DeliveryResult
validate_signature(raw_event) -> bool
```

Adapters needed:

- web widget;
- Telegram;
- WhatsApp;
- VK;
- SMS;
- voice;
- email later.

### Action engine

Needed interfaces:

```text
validate(action_draft) -> ValidationResult
require_confirmation(action_draft) -> ConfirmationPrompt
execute(action_draft, idempotency_key) -> ActionResult
rollback(action_run) -> RollbackResult | NotSupported
```

Rules:

- no order/payment/cancellation without explicit customer confirmation;
- no destructive action without approval policy;
- no duplicate action on retry;
- every external call has timeout, retry policy, idempotency, audit.

### RAG service

Needed:

- tenant-scoped collections;
- source priority/guidance rules;
- hybrid search: lexical + vector + reranker;
- citations with chunk ids;
- stale source detection;
- coverage score by topic;
- source performance metrics;
- answer faithfulness evaluator;
- prompt injection red-team tests;
- KB change versioning.

### Billing service

Needed:

- usage events emitted from all channels/actions;
- pricing calculator;
- plan limits;
- quota enforcement;
- payment provider webhooks;
- invoices/receipts;
- trial and grace periods;
- admin override;
- dunning/failed payment flow.

### Notification service

Needed:

- operator assignment notification;
- SLA breach warning;
- failed channel delivery;
- failed integration action;
- billing limit warning;
- weekly performance report;
- new unresolved topic digest.

Delivery options:

- in-app;
- email;
- Telegram internal admin bot;
- webhook;
- Slack later.

## 11.5 API surface needed for production

### Inbox

```text
GET    /api/v1/inbox/threads
GET    /api/v1/inbox/threads/{thread_id}
POST   /api/v1/inbox/threads/{thread_id}/assign
POST   /api/v1/inbox/threads/{thread_id}/reply
POST   /api/v1/inbox/threads/{thread_id}/notes
POST   /api/v1/inbox/threads/{thread_id}/close
POST   /api/v1/inbox/threads/{thread_id}/reopen
POST   /api/v1/inbox/threads/{thread_id}/snooze
GET    /api/v1/inbox/counters
GET    /api/v1/inbox/sla
```

### Customers

```text
GET    /api/v1/customers
GET    /api/v1/customers/{customer_id}
PATCH  /api/v1/customers/{customer_id}
GET    /api/v1/customers/{customer_id}/timeline
POST   /api/v1/customers/{customer_id}/merge
POST   /api/v1/customers/{customer_id}/export
DELETE /api/v1/customers/{customer_id}
```

### Channels

```text
GET    /api/v1/channels
POST   /api/v1/channels/telegram/connect
POST   /api/v1/channels/telegram/test
POST   /api/v1/channels/whatsapp/connect
POST   /api/v1/channels/whatsapp/test
POST   /api/v1/channels/vk/connect
POST   /api/v1/channels/vk/test
POST   /api/v1/channels/widget/domains
POST   /api/v1/channels/voice/numbers
POST   /api/v1/channels/voice/test-call
```

### Actions/orders

```text
POST   /api/v1/actions/draft
POST   /api/v1/actions/{action_id}/confirm
POST   /api/v1/actions/{action_id}/execute
GET    /api/v1/actions/{action_id}
GET    /api/v1/orders
GET    /api/v1/orders/{order_id}
POST   /api/v1/orders/{order_id}/cancel
GET    /api/v1/menu
POST   /api/v1/menu/sync
```

### Quality/evals

```text
GET    /api/v1/evals/suites
POST   /api/v1/evals/suites
POST   /api/v1/evals/suites/{suite_id}/run
GET    /api/v1/evals/runs/{run_id}
GET    /api/v1/quality/unresolved-topics
POST   /api/v1/quality/unresolved-topics/{topic_id}/resolve
GET    /api/v1/quality/answer-samples
POST   /api/v1/quality/answer-samples/{sample_id}/label
```

### Observability/admin

```text
GET    /api/v1/ops/health/deep
GET    /api/v1/ops/incidents
GET    /api/v1/ops/provider-status
GET    /api/v1/ops/costs
GET    /api/v1/audit/events
POST   /api/v1/audit/export
GET    /api/v1/admin/tenants
PATCH  /api/v1/admin/tenants/{tenant_id}
```

## 11.6 Frontend information architecture

Final navigation should be:

1. **Overview**
   - business KPIs;
   - launch status;
   - today’s conversations/calls/orders;
   - critical alerts.
2. **Inbox**
   - human queue;
   - filters;
   - assignment;
   - SLA;
   - reply composer;
   - notes;
   - customer card.
3. **AI Agents**
   - agents list;
   - agent detail;
   - prompt/policy;
   - model settings;
   - voice settings;
   - tools/actions permissions;
   - eval before publish.
4. **Knowledge**
   - sources;
   - ingestion;
   - chunks/citations;
   - unresolved topics;
   - source performance;
   - coverage audit.
5. **Channels**
   - web widget;
   - Telegram;
   - WhatsApp;
   - VK;
   - phone numbers;
   - test each channel.
6. **Voice**
   - numbers;
   - call logs;
   - recordings;
   - latency;
   - transfer rules;
   - outbound campaigns.
7. **Actions & Orders**
   - orders;
   - menu sync;
   - integrations;
   - action logs;
   - approval rules.
8. **Analytics**
   - automation;
   - resolution;
   - revenue;
   - costs;
   - quality;
   - source performance;
   - operator performance.
9. **QA Lab**
   - eval suites;
   - simulation runs;
   - red-team tests;
   - release gate.
10. **Settings**
   - team;
   - roles;
   - API keys;
   - billing;
   - security;
   - audit;
   - data retention.

## 11.7 Exact UI requirements by screen

### Overview

Must show:

- live status: API, channels, voice, integrations;
- automation rate;
- conversations today;
- calls today;
- orders assisted;
- revenue assisted;
- unresolved queue count;
- SLA breaches;
- cost today/month;
- top unresolved topics;
- quick launch checklist.

States:

- empty tenant before setup;
- demo tenant;
- live tenant;
- degraded provider;
- quota exceeded.

### Inbox

Must show:

- left thread list;
- center transcript;
- right customer/context panel;
- status pill;
- assignment dropdown;
- SLA timer;
- source/action trace;
- AI summary;
- handoff reason;
- suggested reply;
- composer;
- internal notes toggle;
- close/reopen controls.

Keyboard:

- `j/k` next/previous thread optional;
- `r` focus reply optional;
- `cmd/ctrl+enter` send;
- escape closes modals.

### Agent builder

Must show:

- name/status/channel;
- business role;
- system instructions;
- tone;
- allowed sources;
- forbidden claims;
- action permissions;
- escalation rules;
- voice profile;
- test panel;
- eval result before publish;
- version history.

Publish guard:

- cannot publish if required evals fail;
- cannot publish without at least one source or explicit no-source mode;
- cannot enable actions without confirmation policy.

### Knowledge

Must show:

- upload/add URL/manual source;
- ingestion status;
- chunk count;
- last updated;
- source health;
- used in conversations;
- resolved conversations by source;
- failed/no-answer topics;
- reingest button;
- delete/archive;
- citations preview.

### Channel settings

Must show per channel:

- connected/disconnected;
- credentials status without showing secrets;
- webhook URL;
- verification status;
- last inbound event;
- last outbound event;
- test message;
- error logs;
- rate limits;
- setup instructions.

### Voice

Must show:

- phone numbers;
- provider status;
- inbound/outbound rules;
- voice persona;
- STT/TTS provider;
- transfer phone numbers;
- business hours;
- call logs;
- recordings;
- transcripts;
- latency waterfall;
- failed call reason.

### Analytics

Must show:

- automation rate;
- containment rate;
- escalation rate;
- human resolution time;
- first response time;
- cost per resolution;
- AI cost breakdown;
- call latency;
- top intents;
- top unresolved topics;
- content performance;
- channel performance;
- operator performance;
- orders/revenue assisted.

### Onboarding

Must be wizard, not a static checklist:

1. Business type.
2. Restaurant info.
3. Upload menu/FAQ.
4. Configure agent persona.
5. Connect first channel.
6. Run test questions.
7. Invite operator.
8. Set handoff hours.
9. Install widget/connect Telegram.
10. Launch readiness review.

## 11.8 Voice production details

### Latency budget

Target values must be explicit:

- STT partial result: p50 < 200ms, p95 < 500ms after speech chunk;
- LLM first token/decision: p50 < 300ms, p95 < 800ms;
- TTS first audio: p50 < 250ms, p95 < 600ms;
- full turn first audible response: p50 < 700ms, p95 < 1200ms for MVP production;
- long-term competitive target: sub-500ms perceived latency.

### Turn-taking

Must handle:

- user interrupts while AI speaks;
- user pauses mid-sentence;
- background noise;
- short confirmations: “да”, “нет”, “ага”;
- repeated question;
- silence timeout;
- “соедините с оператором”.

### Transfer types

- cold transfer: immediately transfer to human number;
- warm transfer: AI calls/brings operator, briefs them, then connects;
- callback: if operator unavailable, collect phone/time and create task;
- voicemail fallback;
- after-hours policy.

### Call records

Every call should store:

- channel/provider call id;
- direction;
- caller/callee;
- agent id;
- status;
- start/end/duration;
- recording URL;
- consent flag;
- transcript;
- summary;
- handoff reason;
- action runs;
- latency metrics;
- cost;
- QA score.

## 11.9 RAG/no-hallucination production standard

### Answer policy

AI may answer only when one is true:

1. Answer is grounded in active tenant knowledge source.
2. Answer is grounded in external action result, such as order status from POS/CRM.
3. Answer is generic safe operational text explicitly allowed by policy, e.g. “передам оператору”.

AI must not invent:

- prices;
- discounts;
- delivery time;
- delivery areas;
- order status;
- allergens;
- legal/medical/financial advice;
- working hours;
- availability/stop-list;
- refunds;
- promises about manager callback unless workflow created it.

### Eval categories

- menu exact facts;
- delivery exact facts;
- order policy;
- allergen safety;
- unknown non-restaurant questions;
- prompt injection RU;
- prompt injection EN;
- source conflict;
- stale source;
- channel-specific wording;
- tone and brevity;
- action confirmation;
- refusal quality;
- handoff quality.

### Metrics

- grounded answer rate;
- false answer rate;
- source attribution rate;
- escalation correctness;
- retrieval precision;
- retrieval recall proxy;
- prompt injection block rate;
- unresolved topic closure time;
- knowledge freshness.

## 11.10 Operator workflow in full detail

### Inbox lifecycle

```text
new inbound -> AI processing -> resolved_by_ai
                         -> needs_human -> assigned -> operator_replied -> pending_customer
                                                 -> resolved
                                                 -> reopened
                                                 -> escalated_to_supervisor
```

### Handoff package

Every handoff must include:

- customer question;
- AI summary;
- handoff reason;
- failed sources or no-source reason;
- recommended reply;
- customer profile;
- channel;
- previous interactions;
- relevant sources;
- pending action draft if any;
- SLA timer;
- sentiment/urgency.

### Operator controls

- reply;
- internal note;
- assign;
- transfer to another operator;
- mark spam;
- close;
- reopen;
- snooze;
- create follow-up;
- create/update customer tag;
- approve/reject AI action;
- send payment/order link.

### Supervisor controls

- view team queue;
- reassign;
- monitor SLA;
- QA sample conversations;
- coach operator;
- inspect AI failures;
- export reports.

## 11.11 Restaurant-specific product depth

### Menu intelligence

Must understand:

- categories;
- sizes;
- modifiers;
- toppings;
- combos;
- drinks;
- allergens;
- calories optional;
- spicy/vegetarian/halal/lenten tags;
- availability/stop-list;
- price changes by branch;
- delivery-only items.

### Order intelligence

Must handle:

- “как обычно” repeat order;
- “без лука” modifier;
- “самовывоз через 20 минут”;
- delivery address ambiguity;
- apartment/entrance/floor/intercom;
- min order;
- delivery fee;
- promo code;
- payment method;
- change/cancel order;
- courier late;
- complaint/refund handoff.

### Handoff triggers for restaurants

Always handoff when:

- allergy risk is unclear;
- customer asks for refund/complaint;
- order modification after submission;
- payment failed;
- VIP/corporate order;
- abusive customer;
- legal threat;
- no source for answer;
- POS/CRM unavailable;
- delivery conflict;
- AI confidence low.

## 11.12 Analytics that must exist

### Business analytics

- missed calls saved;
- orders assisted;
- revenue assisted;
- conversion from conversation to order;
- average order value;
- automation rate;
- human handoff rate;
- operator resolution time;
- channel breakdown;
- campaign performance;
- cost per conversation/call/order.

### AI quality analytics

- AI resolved;
- AI escalated;
- wrong-answer reports;
- low confidence answers;
- hallucination eval failures;
- prompt injection attempts;
- source usage;
- top missing knowledge;
- answer rating;
- model/provider latency;
- token/cost usage.

### Voice analytics

- calls answered;
- calls missed;
- average duration;
- transfer rate;
- silence timeout;
- barge-in count;
- STT/TTS/LLM latency;
- dropped calls;
- provider errors;
- recordings with QA flags;
- post-call outcome.

### Operator analytics

- assigned conversations;
- first response time;
- resolution time;
- reopened rate;
- CSAT if available;
- QA score;
- SLA breaches;
- workload by hour.

## 11.13 Security, privacy, compliance deeper checklist

### Tenant isolation

- every query scoped by tenant;
- integration credentials scoped by tenant;
- vector collections scoped by tenant;
- object storage paths scoped by tenant;
- tests attempt cross-tenant reads/writes.

### PII and call data

- transcript redaction option;
- recording retention;
- export/delete customer data;
- data processing agreement;
- privacy policy;
- consent phrase for recording;
- role-based access to recordings;
- audit every recording playback/download.

### Auth and access

- MFA enforcement per tenant;
- password policy;
- session revocation;
- device/session list;
- SSO/SAML later;
- API key scopes;
- IP allowlist for enterprise;
- least privilege roles.

### Public endpoint hardening

- webhook signature validation;
- rate limits;
- replay protection;
- request size limits;
- schema validation;
- bot/spam protection;
- CORS/domain allowlist;
- abuse monitoring.

### Incident readiness

- security contact;
- incident runbook;
- audit export;
- backup restore drill;
- provider outage fallback;
- postmortem template.

## 11.14 Reliability and infrastructure

### Environments

- local;
- preview per PR;
- staging;
- production;
- demo/sales sandbox.

### Required services

- PostgreSQL;
- Redis;
- Qdrant;
- object storage for recordings/uploads;
- email provider;
- telephony provider;
- channel providers;
- payment provider;
- monitoring stack.

### Deployment requirements

- migrations before app deploy;
- smoke checks after deploy;
- rollback plan;
- zero-downtime where possible;
- health/readiness probes;
- secret rotation;
- backup verification;
- disaster recovery RTO/RPO defined.

### Provider fallback

- LLM primary/fallback;
- embeddings fallback or degraded no-answer mode;
- STT fallback;
- TTS fallback;
- channel delivery retry;
- POS/CRM unavailable -> human handoff.

## 11.15 Testing matrix for “10000%” readiness

### Unit tests

- schemas;
- RBAC;
- stores;
- RAG relevance;
- prompt injection;
- action validation;
- billing calculator;
- channel parsers;
- voice state machine.

### Integration tests

- auth session flow;
- create/publish agent;
- upload/ingest source;
- chat -> RAG answer;
- chat -> no-answer -> handoff;
- operator reply -> channel outbound;
- Telegram webhook duplicate;
- iiko order idempotency;
- YooKassa webhook;
- voice preview turn;
- backup/migration scripts.

### E2E/browser tests

- registration/login/MFA;
- onboarding;
- dashboard;
- agent builder;
- knowledge upload;
- test-console;
- inbox reply;
- widget visitor flow;
- channel setup;
- billing upgrade;
- mobile layout.

### Voice tests

- inbound call happy path;
- interruption;
- silence;
- transfer;
- unavailable operator;
- noisy audio;
- long customer speech;
- action during call;
- dropped provider;
- recording/transcript saved.

### AI evals

- restaurant FAQ;
- order confirmation;
- unknown topic;
- prompt injection;
- malicious instruction;
- source conflict;
- stale data;
- tone;
- refusal;
- action safety.

### Load tests

- concurrent chats;
- concurrent widget visitors;
- Telegram webhook burst;
- concurrent calls;
- ingestion batch;
- vector retrieval latency;
- dashboard analytics queries.

### Release gate

No production release unless:

- lint passes;
- typecheck passes;
- unit/integration tests pass;
- frontend build passes;
- migrations dry-run passes;
- smoke check passes;
- AI eval pass threshold met;
- no critical security findings;
- preview/staging tested;
- rollback plan exists.

## 11.16 Concrete MVP-to-production milestones

### Milestone 1: “Reliable human fallback”

- operator inbox;
- assignment;
- notes;
- close/reopen;
- SLA;
- outbound reply to widget/Telegram;
- tests.

### Milestone 2: “Real messaging launch”

- Telegram real round-trip;
- production widget embed;
- channel settings UI;
- channel error logs;
- abuse limits.

### Milestone 3: “No-hallucination restaurant AI”

- eval lab;
- citations UI;
- unresolved topics;
- knowledge guidance;
- source performance.

### Milestone 4: “Orders and integrations”

- order draft;
- confirmation;
- iiko/r_keeper sandbox;
- order status;
- CRM customer profile;
- action audit.

### Milestone 5: “Voice pilot”

- provider selected;
- real inbound calls;
- STT/TTS streaming;
- transfer;
- recording;
- latency dashboard;
- 20-call QA report.

### Milestone 6: “Commercial SaaS”

- billing;
- quotas;
- onboarding wizard;
- security/compliance;
- monitoring;
- staging/prod;
- sales demo package.

## 11.17 What not to build yet

To avoid wasting time, do not prioritize:

- marketplace of templates before one vertical works;
- complex visual workflow builder before operator/channel/order basics;
- multi-language beyond RU/EN before Russian restaurant flow is strong;
- enterprise SAML before first paying pilots, unless demanded;
- deep workforce management before inbox/SLA basics;
- custom voice cloning before real low-latency calls;
- many CRM integrations before one POS/order path works.

## 11.18 “Better than competitors” acceptance bar

CallForce is not better than competitors until it can prove:

1. A restaurant launches in one day.
2. AI answers real Telegram/widget questions from verified knowledge.
3. AI refuses/escalates unknown questions instead of hallucinating.
4. Operator sees a full queue with context and can reply back to the same channel.
5. AI can take or draft a restaurant order with explicit confirmation.
6. Real voice calls feel natural enough for a customer not to hang up.
7. Owner sees saved missed calls, assisted orders and automation rate.
8. Every critical action is auditable.
9. Every release is tested with AI evals and browser checks.
10. Production failures are visible through alerts and dashboards.

## 11.19 Master backlog by domain

### Product

- restaurant positioning;
- demo script;
- pricing;
- onboarding;
- pilot checklist;
- sales deck;
- success metrics;
- customer feedback loop.

### Backend

- inbox models;
- customers;
- channel adapters;
- action engine;
- orders;
- voice sessions;
- eval service;
- billing quotas;
- audit export;
- monitoring endpoints.

### Frontend

- inbox;
- customer profile;
- channel setup;
- voice logs;
- order/action screens;
- QA lab;
- billing;
- analytics deep dashboards;
- mobile pass.

### AI

- prompt versioning;
- RAG guidance;
- eval datasets;
- red-team tests;
- source citations;
- action planning;
- confidence scoring;
- unresolved topic learning.

### DevOps

- CI;
- preview deploy;
- staging;
- production;
- migrations;
- backups;
- monitoring;
- alerting;
- load tests.

### Security/legal

- retention;
- export/delete;
- audit logs;
- MFA enforcement;
- webhook signatures;
- 152-ФЗ docs;
- incident response;
- provider DPAs.

## 11.20 Final recommended execution order

The fastest path to a sellable product:

1. **Operator Inbox v1** — because current RAG already produces `needs_human`.
2. **Widget outbound + Telegram real outbound** — so handoff reaches customer.
3. **Customer profile + unified timeline** — so cross-channel memory exists.
4. **RAG citations + eval lab** — so answers are trusted.
5. **Restaurant order draft + confirmation** — so product creates business value.
6. **iiko/r_keeper sandbox integration** — so orders become real.
7. **Voice provider spike** — choose stack and prove real call quality.
8. **Voice production pilot** — recordings, transfer, latency, QA.
9. **Billing/quota/onboarding** — turn into SaaS.
10. **Observability/security/deploy hardening** — scale safely.

If only one next thing can be built, build **Operator Inbox v1**. It turns AI failure into a controlled business process, which is required before real channels and voice can be trusted.
