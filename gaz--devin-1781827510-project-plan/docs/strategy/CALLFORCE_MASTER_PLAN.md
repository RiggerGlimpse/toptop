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

---

# 12. June 2026 deep competitor teardown and missing logic map

Этот раздел отвечает на вопрос: “точно ли мы учли всю логику, чтобы сделать лучший проект в мире?” Ответ: после дополнительного анализа нужно расширить план ещё сильнее. Лучшие платформы в 2026 году продают не просто chat/voice bot, а **Agent Operating System**: build -> simulate -> deploy -> monitor -> coach -> improve, with omnichannel memory, workflow/action governance, human workforce integration and measurable outcomes.

## 12.1 Источники benchmark, которые нужно держать в голове

Паттерны, которые нужно повторить или превзойти:

- Sierra Agent SDK / Agent Studio:
  - goals and guardrails;
  - composable skills;
  - workflows/journeys;
  - simulations;
  - traces of decisions/tool calls/responses;
  - real-time knowledge;
  - secure actions;
  - contact-center handoff with generated summary.
- Decagon:
  - Agent Operating Procedures in natural language;
  - build/optimize/scale lifecycle;
  - omnichannel chat/voice/email;
  - observability, experimentation, audit logging, proactive gap identification;
  - insights and reporting tied to business outcomes.
- PolyAI:
  - voice/chat platform;
  - test environments before production;
  - Git/native developer workflow;
  - handoff destinations;
  - SIP headers and handoff API for context;
  - QA analytics and large-scale conversation review.
- Parloa:
  - design/test/deploy/improve lifecycle;
  - simulations, evaluations, runtime guardrails;
  - natural low-latency conversations;
  - regulated environment compliance;
  - real-time performance, containment, sentiment and anomaly insights.
- Salesforce Agentforce:
  - subagents;
  - actions;
  - instructions;
  - grounding in CRM/knowledge data;
  - human handoff;
  - trust layer.
- Ada:
  - unified reasoning engine;
  - conversation hub across channels;
  - performance center;
  - playbooks;
  - action performance reports;
  - knowledge gap reports;
  - coaching loop.
- Genesys/NICE/Talkdesk:
  - agent assist;
  - real-time transcription;
  - next-best action;
  - routing;
  - workforce/performance management;
  - quality management scoring every interaction;
  - speech/text analytics;
  - topic spotting;
  - supervisor coaching.
- Bland/Vapi/Retell/ElevenLabs:
  - low-latency voice;
  - telephony portability;
  - warm/cold transfer;
  - tool/function calling;
  - post-call analysis;
  - monitoring by provider/tool/latency issue;
  - agent-to-agent transfer;
  - knowledge base attached to voice agents.

## 12.2 Главный недостающий концепт: CallForce Agent OS

CallForce должен стать не набором endpoints, а операционной системой для AI-операторов.

### Agent OS layers

```text
Tenant/business configuration
  -> Agent definitions
  -> Skills/subagents/playbooks
  -> Knowledge and guidance
  -> Tools/actions and permissions
  -> Channel adapters
  -> Runtime orchestrator
  -> Human workforce/inbox
  -> QA/eval lab
  -> Monitoring/analytics
  -> Billing/compliance/governance
```

### Agent OS must support two creation modes

1. **No-code Agent Studio** for business/admin/operator:
   - describe role;
   - select vertical preset;
   - import SOP/menu/FAQ;
   - define handoff rules;
   - connect channels;
   - run simulations;
   - publish.
2. **Developer SDK / config-as-code**:
   - agent config in versioned JSON/YAML;
   - playbooks/workflows as code;
   - test suites in repo;
   - promotion from draft -> staging -> production;
   - traces and evals tied to commit/version.

### Agent OS versioning

Every production answer must be traceable to:

- agent version;
- prompt version;
- playbook version;
- model config version;
- knowledge snapshot version;
- action schema version;
- channel adapter version;
- eval run before publish;
- release author;
- release timestamp.

Without this, impossible to debug “почему AI так ответил”.

## 12.3 Missing logic: subagents and specialist routing

Current plan mentions agents, but world-class platforms increasingly use specialized subagents. CallForce needs:

### Subagent types for restaurant vertical

- `RestaurantGreeterSubagent`
  - identifies intent;
  - handles greetings;
  - asks clarifying questions.
- `MenuExpertSubagent`
  - menu, ingredients, allergens, recommendations;
  - never invents price/availability.
- `DeliveryPolicySubagent`
  - delivery zones, minimum order, timing, fees.
- `OrderBuilderSubagent`
  - collects order draft;
  - validates required fields;
  - requests explicit confirmation.
- `OrderStatusSubagent`
  - reads POS/CRM status only;
  - no source/action result -> handoff.
- `ComplaintSubagent`
  - empathy;
  - collects details;
  - escalates to human.
- `PaymentSubagent`
  - creates payment link only through approved action;
  - handles failed payment fallback.
- `HumanHandoffSubagent`
  - prepares summary;
  - chooses queue/team;
  - creates SLA.
- `VoiceTransferSubagent`
  - cold/warm transfer;
  - operator briefing;
  - unavailable fallback.

### Subagent routing logic

```text
incoming_turn
  -> classify intent + risk + channel + customer state
  -> select subagent
  -> retrieve relevant context
  -> decide: answer / ask / action_draft / handoff / transfer
  -> validate decision against policy
  -> execute or respond
  -> store trace and outcome
```

### Subagent acceptance criteria

- each subagent has explicit allowed actions;
- each subagent has forbidden claims;
- each subagent has eval cases;
- subagent transfer is visible in trace;
- user never sees internal subagent names unless intentionally surfaced;
- operator can see which subagent failed or escalated.

## 12.4 Missing logic: conversation state machines

The current project has conversation statuses, but production needs precise state machines.

### Universal conversation state

```text
created
  -> active_ai
  -> waiting_customer
  -> needs_human
  -> active_human
  -> pending_external_action
  -> pending_customer_confirmation
  -> resolved
  -> reopened
  -> archived
  -> spam
  -> failed
```

Rules:

- `resolved` requires resolution actor: `ai`, `operator`, `system`, `external_action`.
- `needs_human` requires `handoff_reason` and `queue_id`.
- `pending_external_action` requires `action_run_id` and timeout.
- `pending_customer_confirmation` requires exact confirmation prompt.
- `failed` requires recoverable/non-recoverable reason.

### AI turn state

```text
received
  -> normalized
  -> classified
  -> context_retrieved
  -> decision_planned
  -> policy_checked
  -> action_required? -> action_drafted -> confirmation_required -> executed
  -> response_generated
  -> response_validated
  -> delivered
  -> observed
```

Failure branches:

- retrieval_failed -> safe no-answer/handoff;
- model_timeout -> fallback model or handoff;
- policy_violation -> block response;
- channel_send_failed -> retry/dead-letter/notify operator;
- action_failed -> operator handoff with action error.

### Handoff state

```text
created
  -> queued
  -> assigned
  -> opened_by_operator
  -> replied
  -> pending_customer
  -> resolved
  -> reopened
  -> escalated_to_supervisor
```

Required fields:

- reason;
- queue;
- priority;
- SLA deadline;
- summary;
- suggested reply;
- customer profile;
- channel callback capability;
- previous failures.

### Voice call state

```text
incoming_call
  -> consent_prompt
  -> listening
  -> transcribing
  -> thinking
  -> speaking
  -> interrupted
  -> action_pending
  -> transferring
  -> human_joined
  -> completed
  -> post_call_analysis
  -> archived
```

Failure branches:

- no_audio;
- STT_failed;
- TTS_failed;
- LLM_timeout;
- transfer_failed;
- customer_hung_up;
- provider_dropped;
- recording_failed.

### Order state

```text
none
  -> collecting_items
  -> collecting_contact
  -> collecting_address
  -> calculating_total
  -> awaiting_confirmation
  -> submitted_to_pos
  -> accepted
  -> rejected
  -> modified
  -> cancelled
  -> refunded
  -> escalated
```

Hard rule: no order leaves CallForce until customer explicitly confirms final order summary.

## 12.5 Missing logic: routing engine

A world-class product needs routing, not just “operator reply form”.

### Routing inputs

- channel;
- language;
- sentiment;
- urgency;
- topic;
- VIP/customer value;
- open order status;
- business hours;
- operator presence;
- team skills;
- SLA tier;
- integration failure reason;
- compliance risk.

### Routing outputs

- AI self-serve;
- assigned operator;
- queue;
- supervisor escalation;
- callback task;
- voice transfer number;
- after-hours autoresponse;
- blocked/spam.

### Routing examples

- refund complaint -> supervisor queue;
- allergy question -> human or strict knowledge source only;
- delivery late -> order status action, then human if unresolved;
- corporate order -> sales/catering queue;
- abusive message -> safe response + flag;
- VIP phone call -> priority human transfer.

## 12.6 Missing logic: same customer memory across channels

Competitors emphasize “same brain every channel”. CallForce needs identity stitching.

### Identity resolution

Sources:

- phone number;
- Telegram user id;
- WhatsApp user id;
- VK user id;
- web visitor cookie;
- email;
- CRM customer id;
- order phone;
- manual merge by operator.

Confidence levels:

- exact verified match;
- probable match;
- manual merge;
- conflict.

Rules:

- never auto-merge uncertain identities with sensitive data;
- operator can merge/split;
- every merge is audited;
- customer can request export/delete across identities.

### Memory types

- short-term conversation context;
- customer preferences: favorite order, language, allergies, delivery address;
- business-safe notes;
- consent flags;
- CRM history;
- unresolved issues;
- do-not-call/do-not-message flags.

### Memory safety

- allergies must be treated as safety-critical;
- do not infer sensitive categories unnecessarily;
- memory used in responses must be visible in trace;
- customer can delete memory.

## 12.7 Missing logic: workflow/playbook engine

A competitor-level AI product needs playbooks/AOPs, not prompt-only behavior.

### Playbook structure

```text
Playbook
  objective
  entry_conditions
  required_inputs
  steps
  allowed_actions
  confirmation_rules
  escalation_rules
  success_conditions
  failure_conditions
  eval_cases
```

### Restaurant playbooks

- answer menu question;
- recommend pizza;
- create delivery order;
- create pickup order;
- change order;
- cancel order;
- check delivery status;
- handle complaint;
- handle allergy question;
- handle corporate/catering request;
- transfer to operator;
- after-hours response.

### Playbook controls

- deterministic steps for regulated/risky flows;
- flexible language for low-risk FAQ;
- approval for action execution;
- simulation before publish;
- metrics per playbook.

## 12.8 Missing logic: real-time operator copilot

CallForce should not only automate customers; it should help human operators.

### Operator copilot features

- live transcript summary;
- suggested reply;
- relevant knowledge snippets;
- customer/order context;
- sentiment and urgency;
- next best action;
- grammar/tone rewrite;
- auto-fill CRM/order fields;
- post-resolution summary;
- QA checklist.

### Voice live-assist

For transferred calls:

- real-time transcript;
- AI suggestions;
- customer profile screen-pop;
- order/action forms;
- compliance reminders;
- supervisor listen/whisper/barge later.

## 12.9 Missing logic: quality management and coaching

To beat contact-center platforms, CallForce needs QA for both AI and humans.

### Auto-QA scoring

Score every conversation/call for:

- correct answer;
- grounded source/action;
- tone;
- policy compliance;
- escalation correctness;
- resolution outcome;
- customer sentiment;
- operator response quality;
- action safety;
- missed upsell/order opportunity.

### Coaching loop

- low-score conversation -> QA review queue;
- supervisor labels issue;
- issue becomes prompt/source/playbook improvement;
- eval case generated automatically;
- future release must pass that regression.

### Quality dashboards

- AI quality by agent;
- operator quality by team;
- top policy violations;
- hallucination attempts;
- source gaps;
- failed actions;
- sentiment trends;
- CSAT by channel.

## 12.10 Missing logic: experimentation and safe rollout

World-class platforms do not push prompt changes directly to all users.

### Release lifecycle

```text
draft change
  -> local simulation
  -> eval suite
  -> staging agent
  -> internal test conversations/calls
  -> canary 5%
  -> monitor
  -> 25%
  -> 100%
  -> post-release review
```

### A/B experiments

- prompt variation;
- voice variation;
- handoff threshold;
- answer length;
- recommendation style;
- upsell strategy;
- playbook step order.

### Kill switches

- disable AI replies per tenant;
- disable specific agent;
- disable action execution;
- disable channel outbound;
- force all to human;
- fallback model/provider;
- pause outbound campaign.

## 12.11 Missing logic: provider abstraction and failover

Current stubs are useful, but production needs provider abstraction.

### Provider abstraction must cover

- LLM;
- embeddings;
- reranker;
- STT;
- TTS;
- telephony;
- SMS;
- WhatsApp;
- email;
- payments;
- POS/CRM;
- object storage;
- analytics/events.

### Failover policy examples

- primary LLM down -> fallback LLM with stricter no-answer;
- embeddings down -> lexical-only retrieval with lower confidence;
- TTS down -> transfer/handoff or SMS follow-up;
- POS down -> collect order draft and handoff;
- Telegram send failed -> retry then operator alert;
- recording storage failed -> continue call but flag compliance issue.

## 12.12 Missing logic: outbound campaigns

Voice AI competitors often support outbound campaigns. For restaurants, outbound should be careful, consent-based.

### Use cases

- missed-call callback;
- reservation confirmation;
- order status callback;
- delivery issue callback;
- reactivation campaign only with consent;
- catering lead follow-up.

### Required controls

- consent/do-not-call;
- quiet hours;
- frequency caps;
- campaign pacing;
- disposition tracking;
- retry policy;
- human takeover;
- script/playbook approval;
- campaign analytics.

## 12.13 Missing logic: multi-tenant enterprise governance

### Organization hierarchy

- platform owner;
- tenant owner;
- branch manager;
- supervisor;
- operator;
- billing admin;
- developer;
- read-only auditor.

### Branch/location support

Restaurants often have multiple locations. Need:

- branch-specific menu;
- branch-specific hours;
- branch-specific delivery zones;
- branch-specific phone/channel;
- branch-specific operators;
- aggregate analytics;
- customer chooses/infers branch.

### Approval policies

- who can publish agent;
- who can connect channel;
- who can enable voice;
- who can enable payments;
- who can export data;
- who can listen to recordings;
- who can change retention.

## 12.14 Missing logic: data ingestion beyond files

Knowledge is not only PDF/manual text.

### Sources needed

- website crawl;
- menu from iiko/r_keeper;
- Google Sheets;
- Notion/Confluence;
- CRM FAQs;
- help center;
- Telegram pinned messages;
- call transcripts;
- operator notes promoted to KB;
- unresolved topics.

### Source lifecycle

```text
connected
  -> syncing
  -> parsed
  -> chunked
  -> embedded
  -> evaluated
  -> active
  -> stale
  -> failed
  -> archived
```

### Freshness rules

- menu/prices must be fresh;
- delivery zones must be fresh;
- legal/policy docs versioned;
- stale source lowers confidence;
- source conflicts require admin resolution.

## 12.15 Missing logic: business outcome engine

To be better than competitors, CallForce must prove value.

### Outcome tracking

- conversation resolved by AI;
- order created;
- order influenced;
- missed call recovered;
- complaint prevented escalation;
- operator time saved;
- revenue assisted;
- cost saved;
- customer retained;
- appointment/booking created.

### Outcome pricing readiness

If later using outcome-based pricing:

- define billable outcome;
- prove attribution;
- exclude test conversations;
- dispute workflow;
- audit trail;
- customer-visible usage report.

## 12.16 Missing logic: mobile/operator app thinking

Restaurants may use phones/tablets.

Need responsive/operator mobile:

- inbox usable on phone;
- quick replies;
- push notifications later;
- accept/resolve handoff;
- call customer;
- view order/customer;
- mark unavailable;
- manager dashboard on tablet.

## 12.17 Missing logic: marketplace/templates later

Not first priority, but for “best in world” long-term:

- restaurant templates;
- clinic templates;
- e-commerce templates;
- service company templates;
- language packs;
- voice packs;
- integration recipes;
- eval packs;
- playbook packs.

Each template must include:

- prompt;
- playbooks;
- knowledge schema;
- actions;
- handoff rules;
- eval suite;
- dashboard defaults;
- onboarding checklist.

## 12.18 What CallForce can do better than US competitors specifically

### Russian/CIS moat

- native Russian speech and slang;
- Telegram/VK-first, not afterthought;
- WhatsApp local providers;
- iiko/r_keeper/1C/Bitrix24/AmoCRM;
- 152-ФЗ workflows;
- pricing in rubles;
- local telephony providers;
- restaurant/delivery preset;
- setup by real operator/business owner, not developer only.

### Product moat

- restaurant order engine built-in;
- operator inbox optimized for small businesses;
- AI safety visible in UI;
- no-hallucination as selling point;
- launch in one day;
- “missed calls saved” metric;
- “orders assisted” metric;
- Russian voice QA pack.

### Technical moat

- hybrid local/cloud model option later;
- provider abstraction;
- deterministic playbooks for risky actions;
- eval-generated unresolved topics;
- Git-like agent versioning;
- same runtime for chat and voice.

## 12.19 Revised P0/P1/P2 build plan

### P0: Must exist before first serious pilot

- operator inbox v1;
- real Telegram round-trip;
- production widget embed;
- customer profile basic;
- citations in transcript;
- unresolved topics;
- eval suite for restaurant/no-answer/prompt injection;
- order draft without POS submit;
- channel settings UI;
- basic analytics: automation/handoff/source gaps;
- CI checks;
- staging deploy;
- Sentry/logging;
- backup/migration runbooks verified;
- security pass: tenant isolation/RBAC/API keys/rate limits.

### P1: Must exist before paid production restaurants

- iiko/r_keeper sandbox order submit;
- WhatsApp provider;
- VK if target customers need it;
- voice real inbound pilot;
- recording/transcript;
- transfer/callback;
- billing/quota;
- onboarding wizard;
- SLA/assignment;
- audit export;
- data retention;
- mobile inbox;
- source performance analytics;
- action logs;
- customer export/delete.

### P2: Must exist before “best in world” claim

- low-latency streaming voice with barge-in;
- warm transfer;
- multi-agent/subagent studio;
- playbook builder;
- simulation lab;
- canary releases;
- A/B experiments;
- auto-QA for 100% conversations;
- workforce/supervisor dashboard;
- outcome-based pricing analytics;
- marketplace/templates;
- SSO/SAML;
- multi-region/data residency;
- enterprise incident/compliance portal;
- outbound campaigns with consent.

## 12.20 Final truth after deeper analysis

The previous plan was strong, but not yet “world-best blueprint” because it did not fully specify:

- Agent OS / lifecycle;
- subagents;
- exact state machines;
- routing engine;
- same-customer memory;
- playbook/AOP layer;
- operator copilot;
- QA/coaching loop;
- experimentation/canary releases;
- provider failover;
- outbound campaigns;
- branch/location hierarchy;
- ingestion from live systems;
- business outcome engine;
- P0/P1/P2 readiness tiers.

Now those pieces are included. The document is much closer to a complete blueprint for building CallForce into a world-class AI operator platform. The next step is no longer more planning by default; the next step should be execution, starting with **Operator Inbox v1**, because it unlocks real human fallback for every future channel and voice flow.

---

# 13. Production implementation blueprint: DB, onboarding, numbers, channels, infra

Этот раздел добавлен потому, что “лучший продукт в мире” — это не только AI-логика. Чтобы человек реально зашёл в кабинет, всё настроил, привязал номер/каналы и начал получать звонки/чаты, нужны production DB schema, миграции, provisioning, фоновые worker-процессы, credential vault, channel setup wizard, telephony onboarding, launch checklist and operations.

## 13.1 Текущая DB reality в проекте

Сейчас в коде уже есть SQLAlchemy-модели для базового MVP:

- `tenants`
- `users`
- `memberships`
- `auth_sessions`
- `audit_logs`
- `verification_tokens`
- `password_reset_tokens`
- `agents`
- `knowledge_sources`
- `knowledge_ingestion_jobs`
- `knowledge_chunks`
- `conversations`
- `messages`
- `api_keys`
- `billing_ledger`
- `webhook_subscriptions`

Что это значит:

- базовая multi-tenant/auth/agent/knowledge/conversation структура уже есть;
- есть audit/API keys/billing ledger foundations;
- knowledge chunks can store embeddings/Qdrant payload;
- conversations/messages support current demo and handoff;
- но это ещё не production SaaS schema.

Критичный DB gap:

- `apps/api/alembic/versions/b7917ceca4f4_initial_migration.py` сейчас фактически empty `pass` migration;
- для production нужны реальные Alembic migrations, иначе чистая production DB не поднимет таблицы воспроизводимо;
- нельзя считать проект production-ready, пока schema не создаётся migration-командами в staging/prod.

## 13.2 Target production data architecture

Production CallForce должен использовать несколько типов хранения, а не только Postgres.

### Operational PostgreSQL

Хранит truth state:

- tenants/users/roles;
- agents/versions/playbooks;
- customers/identities;
- conversations/messages/inbox;
- actions/orders/payments;
- channel connections;
- phone numbers/SIP trunks;
- knowledge metadata;
- evals/releases;
- billing/audit/compliance.

Requirements:

- real Alembic migrations;
- tenant-scoped indexes;
- foreign keys where safe;
- JSONB only for flexible metadata, not core query fields;
- soft-delete/archival for customer data where needed;
- row-level tenant isolation tests;
- PITR backups;
- restore drill.

### Redis

Needed for:

- rate limits;
- short-lived idempotency locks;
- webhook duplicate suppression;
- job queues if using RQ/Celery/Arq;
- online operator presence;
- voice session ephemeral state;
- typing indicators;
- websocket fanout.

### Qdrant/vector DB

Needed for:

- tenant knowledge vectors;
- source/chunk metadata;
- knowledge snapshot versioning;
- hybrid retrieval payload filters;
- future semantic conversation search.

Rules:

- each vector payload must include `tenant_id`, `source_id`, `chunk_id`, `source_version`, `visibility`, `updated_at`;
- retrieval must filter by tenant and active source version;
- stale/deleted source vectors must be removed or excluded.

### Object storage

Needed for:

- uploaded knowledge files;
- parsed originals;
- call recordings;
- exported audit archives;
- screenshots/attachments;
- generated reports.

Requirements:

- tenant-scoped paths;
- signed URLs;
- retention policies;
- encryption at rest;
- audit on download/playback;
- malware/file type validation for uploads.

### Analytics/event store

Postgres may be enough initially, but world-class analytics eventually needs event storage:

- conversation events;
- AI turn events;
- tool-call events;
- channel delivery events;
- voice latency events;
- billing usage events;
- QA labels;
- operator activity.

Options:

- start with append-only `events` table in Postgres;
- later move heavy analytics to ClickHouse/BigQuery/warehouse;
- dashboards should read aggregates, not scan huge transcript tables.

## 13.3 Production DB schema: tables that must be added

### Tenant, team, branches

```text
tenants
branches
business_hours
holiday_hours
teams
team_memberships
operator_presence
roles
permissions
```

`branches` fields:

- `id`
- `tenant_id`
- `name`
- `address`
- `timezone`
- `phone_public`
- `delivery_zones`
- `pickup_enabled`
- `delivery_enabled`
- `pos_external_id`
- `status`

Why: restaurants are often multi-location. Voice/chat/order logic must know branch-specific menu, hours, delivery rules and operator team.

### Customers and identity stitching

```text
customers
customer_identities
customer_addresses
customer_preferences
customer_consents
customer_tags
customer_merge_events
customer_timeline_events
```

Must support:

- phone -> customer;
- Telegram -> customer;
- WhatsApp -> customer;
- VK -> customer;
- web visitor -> customer;
- CRM/POS external id -> customer;
- manual merge/split;
- GDPR/152-ФЗ export/delete.

### Agent OS

```text
agent_versions
prompt_versions
model_config_versions
subagents
agent_skills
playbooks
playbook_versions
playbook_steps
guardrail_rules
escalation_rules
agent_release_channels
agent_release_events
```

Must support:

- draft/staging/production versions;
- simulation before publish;
- rollback to previous version;
- trace every answer to exact version.

### Knowledge

Existing:

- `knowledge_sources`
- `knowledge_ingestion_jobs`
- `knowledge_chunks`

Needed:

```text
knowledge_source_versions
knowledge_connectors
knowledge_sync_runs
knowledge_guidance_rules
knowledge_conflicts
unresolved_topics
source_performance_daily
chunk_feedback
```

Why:

- menu/prices/delivery zones change;
- source conflicts must be explicit;
- AI must know which source to use for which topic;
- unresolved questions should become actionable knowledge tasks.

### Inbox and conversations

Existing:

- `conversations`
- `messages`

Needed:

```text
inbox_threads
thread_participants
assignments
queues
sla_policies
sla_events
internal_notes
message_delivery_attempts
conversation_summaries
handoff_packages
operator_drafts
saved_replies
```

Why:

- current conversation detail form is not enough;
- real support needs queue, assignment, SLA, notes, delivery tracking and reopen/snooze.

### Channels

```text
channel_connections
channel_credentials
channel_webhooks
channel_events
channel_delivery_logs
widget_installations
allowed_widget_domains
telegram_bots
whatsapp_business_accounts
vk_communities
email_inboxes
sms_numbers
```

Credential rules:

- store encrypted secret references, not plaintext;
- never show token after save;
- rotate/reconnect flow;
- validate webhook signatures;
- log last inbound/outbound event.

### Voice and telephony

```text
telephony_providers
sip_trunks
phone_numbers
phone_number_assignments
voice_agents
call_sessions
call_legs
call_recordings
transcript_segments
voice_latency_events
call_transfers
callback_requests
outbound_campaigns
outbound_campaign_recipients
do_not_call_entries
```

Must support:

- buy/import number;
- BYO Twilio;
- BYO SIP trunk;
- local provider such as Zadarma/Mango/UIS-like SIP;
- inbound/outbound routing;
- warm/cold transfer;
- recordings/transcripts;
- callback fallback;
- consent and retention.

### Actions, orders, POS/CRM

```text
action_definitions
action_runs
action_approvals
action_idempotency_keys
integration_connections
integration_credentials
integration_sync_runs
menu_catalogs
menu_categories
menu_items
menu_modifiers
menu_availability
order_drafts
orders
order_items
order_status_events
payment_links
refund_requests
crm_links
```

Hard rules:

- no order submit without explicit confirmation;
- no payment without provider callback verification;
- POS unavailable -> collect draft + handoff;
- duplicate webhook/action must be idempotent.

### QA, evals, monitoring

```text
eval_suites
eval_cases
eval_runs
eval_results
simulation_runs
ai_turn_traces
llm_calls
tool_calls
retrieval_traces
qa_reviews
qa_scorecards
monitor_definitions
monitor_alerts
incident_events
```

Why:

- top competitors expose traces, simulations, QA and proactive gap insights;
- CallForce must catch failures before customers do.

### Billing and commercial readiness

Existing:

- `billing_ledger`

Needed:

```text
plans
subscriptions
usage_events
usage_aggregates
invoices
payment_methods
billing_entitlements
quota_events
trial_events
outcome_events
billing_disputes
```

Must track:

- messages;
- calls/minutes;
- AI resolutions;
- operator seats;
- channels;
- integrations;
- storage/recordings;
- outcome-based metrics later.

## 13.4 Migration and DB operations plan

### Migration requirements

- Replace empty initial migration with real schema migration.
- Add migrations in small batches:
  1. current MVP schema baseline;
  2. customers/identities;
  3. inbox/queues/SLA;
  4. channel connections;
  5. telephony/calls;
  6. actions/orders/integrations;
  7. evals/monitoring;
  8. billing/subscriptions.
- Every migration must have downgrade or explicit irreversible note.
- CI must run migration upgrade against empty DB.
- CI must run app tests against migrated DB, not only in-memory store.

### DB indexes that matter

- `tenant_id, created_at` on almost every tenant table;
- `tenant_id, status` for inbox/actions/orders;
- `tenant_id, channel, external_message_id` for webhook idempotency;
- `tenant_id, phone_e164` for customers/phone;
- `tenant_id, provider_call_id` for calls;
- `tenant_id, idempotency_key` for action runs;
- `tenant_id, source_id, source_version` for chunks;
- `conversation_id, created_at` for messages;
- `thread_id, created_at` for timeline.

### Backup/restore

- daily automatic backups minimum;
- PITR for production Postgres;
- monthly restore test;
- object storage lifecycle retention;
- Qdrant backup or rebuild-from-source plan;
- runbook: restore tenant, restore full system, restore deleted source.

## 13.5 Full onboarding: user enters and launches real product

The onboarding must be an activation wizard. Goal: owner can launch first working AI operator without developer help.

### Step 0: Create account and tenant

User does:

- register;
- verify email;
- create company;
- choose business type: restaurant/delivery first;
- choose language/timezone/currency.

System creates:

- tenant;
- owner user;
- default roles;
- default branch;
- demo agent draft;
- onboarding checklist;
- trial subscription.

### Step 1: Business profile

User fills:

- restaurant name;
- public phone;
- address;
- working hours;
- delivery/pickup enabled;
- delivery zones;
- average delivery time;
- payment methods;
- operator hours;
- handoff phone/chat.

System validates:

- timezone;
- E.164 phone;
- required fields;
- branch completeness.

### Step 2: Import menu and knowledge

Options:

1. Upload file: PDF/DOCX/CSV/XLSX/TXT.
2. Paste text/FAQ.
3. Crawl website/menu URL.
4. Connect Google Sheets.
5. Connect iiko/r_keeper later.
6. Use Demo Pizza template.

System does:

- parse;
- extract menu items/prices/modifiers/allergens;
- detect conflicts/missing prices;
- chunk/embed;
- run coverage check;
- ask owner to confirm critical facts.

Activation gate:

- cannot launch restaurant agent if menu has no prices and policy says prices are required;
- cannot answer allergy questions unless allergen info exists or handoff rule is enabled;
- stale/failed source blocks launch or forces safe handoff mode.

### Step 3: Configure AI operator

User chooses:

- agent name;
- tone;
- language;
- channels;
- allowed tasks;
- forbidden topics;
- handoff rules;
- whether AI can draft orders;
- whether AI can submit orders;
- voice persona later.

System creates:

- agent draft;
- prompt version;
- restaurant playbooks;
- subagent config;
- eval suite;
- test questions.

### Step 4: Configure human fallback

User sets:

- operator users;
- teams/queues;
- business hours;
- SLA;
- handoff destinations;
- after-hours message;
- transfer phone numbers.

System validates:

- at least one fallback exists before real voice launch;
- if no operator online, callback/off-hours flow exists;
- escalation reasons mapped to queue/team.

### Step 5: Connect web widget

User does:

- adds allowed domain;
- copies embed script;
- customizes color/logo/greeting;
- sends test message.

System does:

- creates `widget_installation`;
- validates domain allowlist;
- shows installation status;
- records first inbound/outbound test;
- warns if CORS/domain invalid.

Non-MVP requirement:

- widget must support visitor identity, transcript persistence, handoff, operator reply, offline form, rate limit, spam protection, mobile layout.

### Step 6: Connect Telegram

User does:

- creates bot through BotFather;
- pastes bot token into CallForce;
- CallForce calls Telegram `setWebhook`;
- user sends test message to bot.

System stores:

- encrypted token reference;
- bot username;
- webhook secret;
- last webhook status;
- last update id.

System validates:

- HTTPS webhook reachable;
- token valid;
- duplicate updates ignored;
- outbound `sendMessage` works;
- operator replies route back to Telegram.

### Step 7: Connect WhatsApp

User flow depends on provider.

Option A: Meta WhatsApp Cloud API:

- connect Meta business;
- add/verify business phone number;
- register phone number;
- configure webhook;
- create/approve templates for outbound beyond 24h window;
- send test inbound and outbound.

Option B: local WhatsApp BSP/provider:

- OAuth/API key;
- select phone;
- webhook URL;
- template sync;
- delivery receipts.

System must track:

- WABA id;
- phone number id;
- display phone;
- template status;
- webhook verify token;
- message status events;
- 24-hour customer service window;
- template fallback if window closed.

### Step 8: Connect VK

User does:

- creates/uses community;
- creates group access token;
- copies confirmation string;
- sets Callback API server URL;
- enables incoming/outgoing message events;
- sends test message.

System validates:

- confirmation callback returns correct string;
- secret key matches;
- inbound `message_new` works;
- outbound community message works;
- duplicate events ignored.

### Step 9: Connect phone number / voice

User should see three paths.

#### Path A: Buy a new number inside CallForce

Best UX:

- user chooses country/city;
- selects number;
- pays/activates;
- assigns to agent/branch;
- tests inbound call.

Requires CallForce to integrate telephony provider inventory/billing.

#### Path B: Bring existing Twilio/Telnyx/Plivo-like number

Flow:

- user enters provider credentials or OAuth;
- imports phone number;
- CallForce configures webhook/SIP routing;
- user runs test call.

Competitor pattern:

- Vapi imports Twilio number after user provides Account SID/Auth Token;
- Bland supports BYOT encrypted key and imported inbound numbers;
- Retell imports phone numbers with E.164 number and SIP termination URI.

#### Path C: Bring your own SIP trunk / local provider

Flow:

- user enters SIP host;
- username/password or IP auth;
- DID/phone number in E.164;
- region;
- transport UDP/TCP/TLS;
- media/RTP port requirements;
- inbound origination URI;
- outbound termination URI;
- test inbound;
- test outbound;
- test transfer.

Must support local/CIS reality:

- Zadarma-like SIP credentials;
- Mango/UIS/CoMagic-like SIP or webhook providers if APIs support it;
- existing PBX forwarding;
- call transfer to restaurant manager.

Voice activation gate:

- number verified;
- provider health ok;
- inbound call test passed;
- outbound test passed if outbound enabled;
- recording consent configured;
- transfer/callback fallback configured;
- latency smoke test passed;
- operator fallback exists.

### Step 10: Run launch simulation

System runs:

- 20 restaurant FAQ evals;
- 10 unknown/no-answer evals;
- prompt injection tests;
- order draft simulation;
- handoff simulation;
- channel send/receive tests;
- voice test call if number enabled.

Launch readiness result:

```text
Ready
Needs fixes
Blocked
```

User sees exact reasons, not generic failure.

### Step 11: Go live

User clicks launch.

System:

- publishes agent version;
- enables selected channels;
- starts monitoring;
- creates first launch report;
- schedules 24h review;
- enables emergency kill switch.

## 13.6 What must happen when a real customer writes/calls

### Real chat path

```text
Customer message
  -> channel webhook signature validation
  -> duplicate/idempotency check
  -> normalize channel payload
  -> identify/create customer
  -> attach to inbox thread
  -> load agent/version/branch/customer/context
  -> classify intent/risk/language
  -> choose playbook/subagent
  -> retrieve knowledge/action context
  -> policy check
  -> answer OR ask clarification OR draft action OR handoff
  -> send via channel adapter
  -> store delivery result
  -> emit analytics/usage/trace events
```

### Real voice path

```text
Incoming call
  -> telephony webhook/SIP event
  -> identify phone number -> tenant/branch/agent
  -> create call session and conversation
  -> play consent/greeting
  -> stream audio to STT
  -> handle partial transcripts and barge-in
  -> choose playbook/subagent
  -> retrieve knowledge/action context
  -> respond with streaming TTS
  -> if human needed: warm/cold transfer or callback
  -> save recording/transcript/latency/cost
  -> post-call summary and QA
```

### Real order path

```text
Customer wants order
  -> OrderBuilderSubagent
  -> collect items/modifiers
  -> check menu/availability
  -> collect delivery/pickup/contact
  -> calculate total/delivery fee
  -> show exact confirmation summary
  -> wait for explicit yes
  -> submit to POS or create internal order
  -> send order number/status
  -> monitor status events
  -> handoff on failure/complaint/change/refund
```

## 13.7 Channel setup screens that must exist

### Channels overview

Cards:

- Widget: connected / needs install / error.
- Telegram: connected / webhook failed / token expired.
- WhatsApp: connected / templates pending / phone unverified.
- VK: connected / confirmation needed / event error.
- Voice: no number / test failed / live.
- Email/SMS later.

Each card shows:

- last inbound;
- last outbound;
- error count;
- setup progress;
- test button;
- disconnect/rotate credentials.

### Phone numbers screen

Must show:

- phone number;
- provider;
- assigned branch;
- assigned agent;
- inbound enabled;
- outbound enabled;
- recording enabled;
- transfer target;
- last call;
- health status;
- test call button;
- setup instructions.

### Provider credential screen

Must show:

- provider name;
- credential status;
- scopes/capabilities;
- last verified;
- rotate/reconnect;
- never show secret value.

## 13.8 Background workers and scheduled jobs

Needed worker types:

- knowledge ingestion worker;
- channel delivery retry worker;
- webhook dead-letter reprocessor;
- voice post-call analysis worker;
- eval/simulation worker;
- analytics aggregation worker;
- billing usage aggregation worker;
- integration sync worker;
- cleanup/retention worker;
- notification worker.

Critical queues:

```text
critical-webhooks
channel-outbound
voice-events
knowledge-ingestion
actions
analytics
billing
notifications
low-priority-reports
```

Rules:

- critical webhook ack must be fast;
- heavy AI/eval/post-call work async;
- retries exponential with max attempts;
- dead-letter queue visible in Ops UI;
- idempotency keys prevent duplicated orders/messages.

## 13.9 Secrets and credentials

Production cannot store raw provider tokens in JSON settings.

Need:

- encrypted credential store;
- secret references in DB;
- per-tenant credential ownership;
- rotation;
- last-used timestamp;
- audit on use;
- masked UI display;
- provider capability validation;
- revoke/disconnect flow.

Credential types:

- Telegram bot token;
- WhatsApp access token;
- VK group token;
- Twilio SID/token;
- SIP username/password;
- iiko/r_keeper credentials;
- YooKassa shop/secret;
- SMTP/email provider;
- Sentry/monitoring keys;
- LLM provider keys if tenant brings own.

## 13.10 Non-MVP production services

### API service

- public REST API;
- auth/RBAC;
- tenant isolation;
- channel settings;
- inbox;
- actions;
- billing;
- admin.

### Websocket/realtime service

- inbox updates;
- typing;
- live call transcript;
- operator presence;
- channel status.

### Voice media service

- handles low-latency audio streams;
- separate from normal API if needed;
- optimized for WebSocket/SIP media;
- records latency metrics.

### Worker service

- async jobs;
- retries;
- dead-letter.

### Scheduler

- sync jobs;
- billing aggregation;
- reports;
- retention cleanup;
- SLA breach checks.

### Admin/Ops service or screens

- provider health;
- incidents;
- tenant overrides;
- queue backlogs;
- failed webhooks/actions;
- cost anomalies.

## 13.11 Production readiness launch checklist

The product is not MVP anymore only when all items below are true.

### Owner can self-serve

- register;
- create restaurant;
- upload menu/FAQ;
- configure agent;
- connect widget;
- connect Telegram;
- invite operator;
- run tests;
- launch.

### Voice can be launched

- add/import number;
- configure provider/SIP;
- verify inbound;
- verify outbound if enabled;
- configure recording consent;
- configure transfer/callback;
- pass latency smoke test;
- see call log and transcript.

### Channels are real

- Telegram real inbound/outbound;
- widget real inbound/outbound;
- WhatsApp real inbound/outbound with templates/window logic;
- VK real inbound/outbound if supported;
- delivery failures visible;
- retries/idempotency working.

### Operators can work all day

- inbox queue;
- assignment;
- SLA;
- notes;
- customer profile;
- AI summary;
- suggested reply;
- reply to original channel;
- close/reopen;
- mobile usable.

### AI is safe

- no-answer/handoff;
- prompt-injection block;
- citations;
- eval suite;
- source performance;
- unresolved topics;
- action confirmation;
- traces.

### Business can see value

- missed calls saved;
- conversations resolved;
- orders assisted;
- revenue assisted;
- operator time saved;
- handoff reasons;
- top missing knowledge;
- costs.

### Engineering can operate

- real migrations;
- CI;
- staging;
- production deploy;
- backups;
- monitoring;
- alerting;
- logs/traces;
- incident runbooks;
- rollback.

## 13.12 Exact next implementation order to stop being MVP

This is the recommended sequence from current repo state.

### PR A: Real DB baseline and migrations

- turn current SQLAlchemy schema into real Alembic migration;
- add migration test in CI/local;
- ensure app can boot against empty Postgres;
- document DB setup.

Why first: without reproducible DB, production does not exist.

### PR B: Customer profile + channel identity

- add customers/customer_identities;
- attach conversations to customer;
- resolve by phone/Telegram/web visitor;
- UI customer panel.

Why: omnichannel memory depends on this.

### PR C: Operator Inbox v1

- threads/queues/assignments/SLA/notes;
- filters and counters;
- reply to current internal channel;
- prepare for external outbound.

Why: every real failure must have human process.

### PR D: Widget production channel

- domain allowlist;
- visitor identity;
- real outbound operator/AI replies;
- offline form;
- spam/rate limits;
- embed docs.

Why: easiest real channel to fully control.

### PR E: Telegram real setup wizard

- encrypted bot token;
- setWebhook;
- inbound/outbound;
- delivery logs;
- duplicate update handling;
- setup UI.

Why: fastest local/CIS channel.

### PR F: Knowledge production and eval lab

- source versions;
- guidance;
- unresolved topics;
- citations UI;
- eval suites before publish.

Why: trust and no hallucinations.

### PR G: Order draft engine

- menu catalog;
- order draft;
- confirmation;
- internal order storage;
- handoff on submit.

Why: business value before deep POS integration.

### PR H: POS/iiko integration

- sync menu;
- stop-list;
- submit order;
- status events;
- idempotency.

Why: converts AI chats into real orders.

### PR I: Voice provider spike

- choose provider path;
- phone number model;
- SIP/Twilio/Zadarma-like setup;
- inbound test call;
- transcript/call log.

Why: voice must be proven with real telephony early.

### PR J: Voice production pilot

- streaming STT/TTS;
- barge-in;
- transfer;
- recording;
- latency dashboard;
- 20-call QA.

### PR K: WhatsApp/VK

- WhatsApp Cloud/BSP setup;
- templates/window logic;
- VK callback;
- channel health screens.

### PR L: Billing/security/ops hardening

- subscriptions/usage;
- quota;
- audit export;
- retention;
- monitoring;
- incident runbooks;
- staging/prod deploy.

## 13.13 “User walked in and launched” acceptance test

A product owner should be able to record this full test without engineer help:

1. Open CallForce.
2. Register account.
3. Choose “restaurant/delivery”.
4. Add restaurant name, hours, delivery rules.
5. Upload menu PDF or paste menu.
6. Confirm extracted menu facts.
7. Create AI operator from template.
8. Invite one operator.
9. Connect web widget and send test message.
10. Connect Telegram bot and send real Telegram message.
11. AI answers known menu question with source.
12. AI escalates unknown/refund/allergy question.
13. Operator sees thread, summary, customer, source, reason.
14. Operator replies; customer receives reply in Telegram/widget.
15. Owner sees analytics updated.
16. Owner adds/imports phone number.
17. Owner runs test call.
18. Call transcript/recording appears.
19. AI transfers/callbacks when needed.
20. Owner clicks “Go live”.

If any step requires developer console/manual DB edit/manual secret placement outside UI, project is still not self-serve production.

## 13.14 Final deeper conclusion

To make CallForce not MVP, the next work must shift from “AI demo features” to **production activation system**:

- reproducible database;
- real onboarding;
- real channel provisioning;
- real phone number/SIP setup;
- real customer identity;
- real operator inbox;
- real delivery/outbound logs;
- real eval/release gate;
- real monitoring and billing.

The current code has the right foundation, but the biggest missing layer is now clear: **self-serve production operations**. The user must be able to connect knowledge, operators, channels and numbers from the UI, pass launch tests, and go live without engineering help.

---

# 14. Final completeness pass: ideal non-MVP product specification

Этот раздел — финальная контрольная матрица. Его цель: убрать последние серые зоны и зафиксировать, что именно должно быть построено, чтобы CallForce был не MVP, а полноценный production SaaS/contact-center/voice-AI продукт, который владелец ресторана может сам настроить и запустить.

Важно: “идеальность” в software означает не бесконечный список желаний, а проверяемое состояние. Поэтому ниже всё сформулировано как **acceptance checks**: если чек не проходит, продукт ещё не production-ready.

## 14.1 Как понять, что документ теперь полный

Документ считается полным blueprint, потому что покрывает все уровни системы:

| Layer | Покрыто в плане | Почему это обязательно |
| --- | --- | --- |
| Market/category | конкуренты, positioning, локальный moat | чтобы не строить generic chatbot |
| Product flows | chat, voice, orders, handoff, onboarding | чтобы было понятно, как работает бизнес-сценарий end-to-end |
| Agent logic | Agent OS, subagents, playbooks, state machines | чтобы AI был управляемым, а не prompt-only |
| Data model | current DB, missing tables, migrations | чтобы production state был воспроизводимым |
| Channels | widget, Telegram, WhatsApp, VK, voice | чтобы клиент реально мог писать/звонить |
| Telephony | numbers, SIP, BYOT, transfer, recordings | чтобы звонки были production, не preview |
| Human ops | inbox, queues, SLA, assignment, copilot | чтобы AI-failure превращался в рабочий процесс |
| Knowledge/RAG | sources, versions, guidance, evals | чтобы AI не выдумывал |
| Actions | orders, payments, POS/CRM, idempotency | чтобы AI выполнял полезную работу безопасно |
| Security | tenant isolation, secrets, audit, retention | чтобы можно было продавать бизнесу |
| Infra | Postgres, Redis, Qdrant, storage, workers | чтобы система выдерживала реальную эксплуатацию |
| QA | tests, evals, simulations, load, voice QA | чтобы релизы не ломали AI поведение |
| Analytics | business/AI/voice/operator outcomes | чтобы клиент видел ROI |
| Billing | plans, usage, quotas, invoices | чтобы это был SaaS |
| Launch/Ops | staging/prod, monitoring, runbooks, incident | чтобы можно было поддерживать live customers |

## 14.2 Final competitor checklist: что именно нужно превзойти

### Voice AI leaders: Bland, Vapi, Retell, ElevenLabs

CallForce должен иметь:

- real inbound calls;
- real outbound calls only with consent and controls;
- import/buy phone number;
- BYO Twilio/SIP trunk;
- local SIP provider support;
- streaming STT/TTS;
- barge-in/interruption;
- call transfer;
- warm transfer with human briefing;
- call recordings;
- transcript segments;
- post-call analysis;
- latency dashboard;
- provider failover;
- call outcome/disposition;
- voice eval suite.

Better-than-competitor angle:

- Russian/CIS telephony and language quality;
- restaurant-specific order/complaint/delivery flows;
- local channels and POS integrations;
- owner-friendly setup, not developer-only API.

### AI support leaders: Intercom Fin, Ada, Decagon, Sierra, Zendesk

CallForce должен иметь:

- knowledge source management;
- content/source performance;
- guided knowledge rules;
- AI behavior guidance;
- playbooks/procedures/AOPs;
- simulations before publish;
- traces of decisions/tool calls;
- human handoff with summary;
- agent assist/copilot;
- analytics by deflection/resolution/content;
- continuous improvement loop.

Better-than-competitor angle:

- no-hallucination policy visible in every transcript;
- unresolved topics automatically become knowledge tasks;
- restaurant launch wizard;
- “orders assisted / missed calls saved” ROI dashboard.

### Contact-center leaders: Genesys, NICE, Talkdesk, Twilio Flex, Amazon Connect

CallForce должен иметь:

- queues;
- routing;
- assignment;
- operator presence;
- SLA;
- supervisor view;
- real-time transcript;
- suggested replies;
- wrap-up notes;
- quality scoring;
- topic spotting;
- workforce basics;
- historical and real-time dashboards;
- incident/health monitoring.

Better-than-competitor angle:

- simpler than enterprise contact center;
- built for small/medium restaurant owners;
- AI + operator + local channels in one setup;
- launch without consultants.

## 14.3 The “no hidden manual work” rule

CallForce is not non-MVP if launch requires any of these hidden manual steps:

- developer manually edits DB;
- developer manually inserts secrets into `.env` for a tenant;
- developer manually configures webhook outside documented UI/setup flow;
- developer manually creates vector collection;
- developer manually connects phone number;
- developer manually runs SQL to fix onboarding;
- developer manually changes prompt in code;
- developer manually restarts worker for a normal tenant action;
- developer manually reads logs to tell owner what failed;
- customer cannot see why setup is blocked.

Every setup action must be either:

1. done inside CallForce UI;
2. done by the user in an external provider console with exact guided steps;
3. automatically verified by CallForce.

## 14.4 Final product surfaces that must exist

### Public website

Must have:

- clear restaurant/delivery positioning;
- demo video;
- pricing;
- “book demo”;
- “start free trial”;
- security/compliance page;
- integrations page;
- docs link;
- terms/privacy;
- status page link.

### SaaS app

Must have:

- onboarding wizard;
- dashboard;
- inbox;
- agents;
- knowledge;
- channels;
- phone/voice;
- orders/actions;
- analytics;
- QA lab;
- billing;
- settings;
- team/roles;
- audit/security;
- support/help.

### Widget

Must have:

- embed script;
- domain allowlist;
- visitor identity;
- AI replies;
- operator replies;
- offline form;
- transcript history;
- mobile design;
- rate limit/spam controls;
- custom branding;
- handoff state visible to customer.

### Operator workspace

Must have:

- queue list;
- filters;
- assignment;
- transcript;
- reply composer;
- internal notes;
- AI summary;
- sources;
- customer card;
- order/action card;
- SLA timer;
- close/reopen;
- suggested reply;
- mobile/tablet usability.

### Admin/Ops workspace

Must have:

- tenant health;
- provider health;
- queue backlogs;
- failed webhooks;
- failed channel sends;
- failed actions;
- model/provider errors;
- cost anomalies;
- incident log;
- audit export;
- support impersonation with audit, if ever added.

## 14.5 Final backend service map

```text
api-web
  auth, tenants, agents, knowledge, inbox, channels, voice config, billing

realtime-gateway
  inbox live updates, operator presence, live call transcript

channel-webhooks
  Telegram, WhatsApp, VK, widget, external webhooks

voice-gateway
  Twilio/SIP/media streams, STT/TTS loop, transfer events

worker-critical
  channel sends, action execution, webhook retries

worker-ai
  ingestion, evals, post-call analysis, summaries

scheduler
  SLA checks, billing aggregation, reports, retention cleanup

admin-ops
  provider status, incidents, internal support tools
```

Minimum production can start with fewer deployable processes if the codebase is small, but the responsibilities must be separated in architecture and queues so scaling is possible.

## 14.6 Final external provider decisions to make before implementation

Some decisions cannot be “documented into existence”; they must be chosen before building production adapters.

### Telephony provider

Decision needed:

- Twilio-style global provider;
- Vapi/Retell-like voice platform;
- direct SIP with local CIS provider;
- hybrid provider abstraction.

Recommendation:

- build abstraction first;
- pilot with the fastest reliable provider;
- keep BYO SIP/Twilio path in schema;
- keep local provider path for Russian/CIS moat.

### WhatsApp provider

Decision needed:

- Meta Cloud API directly;
- Business Solution Provider;
- local aggregator.

Must support:

- verified business phone;
- templates;
- template quality/status webhooks;
- 24-hour customer service window;
- delivery/read statuses;
- webhook signatures;
- opt-in/opt-out.

### POS provider

Decision needed:

- iiko first;
- r_keeper second;
- internal order draft before POS submit.

Recommendation:

- build internal order draft/confirmation first;
- then iiko sandbox;
- then production POS submit/status/stop-list.

### LLM/STT/TTS providers

Decision needed:

- default platform keys;
- tenant BYO keys later;
- fallback chain.

Must support:

- latency requirements;
- Russian quality;
- cost monitoring;
- safe degradation;
- no customer data training terms.

## 14.7 Final DB acceptance checklist

Production DB is ready only if:

- real Alembic migrations exist;
- empty database can be migrated from zero;
- app boots using migrated schema;
- tests run against migrated DB;
- every tenant table has tenant isolation;
- all webhook/action/order operations are idempotent;
- customer identity is modeled;
- channel connections are modeled;
- phone numbers and SIP trunks are modeled;
- call sessions/recordings/transcripts are modeled;
- orders/actions/payments are modeled;
- audit events cover sensitive actions;
- retention/export/delete can be implemented from schema;
- backups and restore test exist.

## 14.8 Final onboarding acceptance checklist

Self-serve onboarding is ready only if a restaurant owner can:

- create account;
- verify email;
- create restaurant profile;
- add branch/hours/delivery rules;
- upload or paste menu;
- confirm extracted facts;
- create AI operator from restaurant template;
- configure handoff;
- invite operator;
- install widget;
- connect Telegram;
- connect WhatsApp if approved/available;
- connect VK if enabled;
- add/import phone number;
- run test chat;
- run test call;
- see readiness report;
- fix blocked items;
- click Go Live;
- see first live conversation/call/order in dashboard.

## 14.9 Final channel acceptance checklist

### Widget

- embed works on allowed domain;
- blocked on unapproved domain;
- mobile layout works;
- visitor id persists;
- AI answer delivered;
- operator answer delivered;
- offline mode works;
- spam/rate limit works;
- transcript stored;
- delivery failures visible.

### Telegram

- token saved encrypted;
- webhook set automatically;
- webhook secret validated;
- duplicate updates ignored;
- inbound message creates/continues thread;
- AI reply sends to Telegram;
- operator reply sends to Telegram;
- send failure retried and visible;
- disconnect/rotate token works.

### WhatsApp

- business/phone status visible;
- webhook configured;
- templates synced;
- template status/quality webhooks handled;
- 24-hour service window respected;
- inbound/outbound text works;
- opt-out respected;
- delivery/read statuses stored;
- failed template or rejected message visible.

### VK

- confirmation callback works;
- secret validation works;
- inbound community message works;
- outbound reply works;
- duplicate events ignored;
- setup errors visible.

### Voice

- number assigned to tenant/branch/agent;
- inbound call reaches CallForce;
- greeting/consent plays;
- transcript starts;
- AI replies with acceptable latency;
- interruption works;
- transfer/callback works;
- recording stored;
- post-call summary generated;
- failed provider events visible.

## 14.10 Final AI safety acceptance checklist

AI can be enabled in production only if:

- known menu question answered with source;
- unknown question escalates;
- prompt injection blocked;
- source conflict escalates or asks admin;
- stale source reduces confidence;
- allergen uncertainty escalates;
- refund/complaint escalates;
- order submit requires explicit confirmation;
- action result, not model imagination, drives order status;
- every AI answer has trace;
- eval suite runs before publish;
- failed eval blocks production publish.

## 14.11 Final voice acceptance checklist

Voice is production-ready only if:

- p95 first audible response is acceptable for pilot;
- p95 STT/LLM/TTS latencies are measured separately;
- user interruption stops/adjusts AI speech;
- silence timeout works;
- background noise does not crash flow;
- customer can request operator;
- transfer has fallback;
- recording consent configured;
- call recording stored securely;
- transcript segments have timestamps;
- post-call summary/disposition generated;
- call cost recorded;
- call failure reason is visible;
- 20+ real pilot calls reviewed and scored.

## 14.12 Final order/POS acceptance checklist

Restaurant order flow is production-ready only if:

- menu catalog exists;
- modifiers/sizes supported;
- stop-list/availability supported;
- delivery/pickup supported;
- customer contact collected;
- address fields collected;
- final summary shown;
- explicit confirmation required;
- order idempotency works;
- POS submit success stored;
- POS failure creates handoff;
- order status lookup works;
- cancel/change routes correctly;
- payment link flow has webhook verification;
- refund/complaint escalates.

## 14.13 Final security/compliance acceptance checklist

Production security is ready only if:

- RBAC enforced;
- MFA works and can be required;
- API key scopes enforced;
- tenant isolation tests pass;
- webhook signatures validated;
- rate limits exist;
- secrets encrypted;
- secrets rotated/disconnected;
- recordings protected by signed URL/access checks;
- audit logs cover sensitive actions;
- customer export works;
- customer delete/anonymize works;
- retention policy works;
- privacy/terms updated;
- incident response runbook exists;
- backup restore tested.

## 14.14 Final observability acceptance checklist

Operations is ready only if dashboards/alerts cover:

- API errors;
- webhook errors;
- channel send failures;
- queue backlog;
- worker failures;
- dead-letter jobs;
- LLM/STT/TTS latency;
- telephony provider errors;
- call drops;
- failed action runs;
- POS/CRM errors;
- billing webhook failures;
- cost spikes;
- eval failures;
- SLA breaches;
- storage/DB/Qdrant health.

Every alert must have:

- owner;
- severity;
- runbook;
- customer impact definition;
- mitigation;
- postmortem path.

## 14.15 Final UI/UX acceptance checklist

Every production page must pass:

- desktop layout;
- tablet layout;
- mobile layout;
- loading state;
- empty state;
- error state;
- permission denied state;
- destructive action confirmation;
- keyboard basics;
- visible focus states;
- form validation;
- no fake data in live mode;
- no console errors;
- no broken critical network requests;
- consistent spacing/type/buttons;
- Russian copy quality;
- user can understand next action.

## 14.16 Final business readiness checklist

CallForce can be sold only if:

- pricing page exists;
- plan limits exist;
- trial exists;
- billing works;
- invoices/receipts work;
- support contact exists;
- onboarding docs exist;
- demo script exists;
- pilot contract/checklist exists;
- success metrics defined;
- customer feedback process exists;
- churn/cancel flow exists;
- status page or incident comms exists.

## 14.17 Final release pipeline acceptance checklist

A release is allowed only if:

- branch has PR;
- PR description explains impact;
- lint passes;
- typecheck passes;
- backend tests pass;
- frontend build passes;
- migration test passes;
- AI evals pass;
- critical browser E2E passes;
- channel smoke tests pass in staging;
- voice smoke passes if voice changed;
- security checks pass;
- staging deploy succeeds;
- rollback plan known;
- release notes written.

## 14.18 Final “day in the life” proof tests

### Owner proof

Owner can launch restaurant without engineer help.

Acceptance:

- record full setup from empty account to live widget/Telegram;
- no DB/manual secret/manual CLI required;
- readiness report explains every issue.

### Customer proof

Customer can ask:

- “Какие пиццы есть?”
- “Сколько доставка?”
- “Хочу заказать пепперони без лука”
- “Где мой заказ?”
- “У меня аллергия, что можно?”
- “Хочу вернуть деньги”

Acceptance:

- safe known answers;
- order draft/confirmation;
- status via action or handoff;
- allergy/refund escalates;
- transcript correct.

### Operator proof

Operator can:

- see escalated thread;
- understand reason;
- read AI summary;
- inspect sources;
- reply to original channel;
- close/reopen;
- add note;
- handle mobile if needed.

### Manager proof

Manager can see:

- conversations;
- calls;
- handoffs;
- missed calls saved;
- orders assisted;
- unresolved topics;
- operator SLA;
- AI failures;
- cost.

### Engineer/Ops proof

Engineer can:

- deploy staging;
- run migrations;
- inspect traces;
- replay failed webhook;
- see dead-letter job;
- rotate secret;
- rollback release;
- restore backup.

## 14.19 Final sequencing: what to build first, without more planning

After this document, the correct next step is execution. The first PRs should be:

1. Real Alembic migration baseline.
2. Customer profile and channel identity.
3. Operator Inbox v1.
4. Widget production outbound.
5. Telegram production setup wizard.
6. Knowledge source versions, citations, unresolved topics and eval lab.
7. Order draft engine.
8. iiko/r_keeper integration.
9. Phone number/SIP/voice provider spike.
10. Voice production pilot.
11. WhatsApp/VK production channels.
12. Billing/security/ops hardening.

Why this order is final:

- DB/migrations must come before production features;
- identity must come before omnichannel memory;
- inbox must come before real channels/voice, otherwise escalations have nowhere to go;
- widget/Telegram are fastest real launch channels;
- evals must guard AI before more automation;
- order draft creates business value before POS complexity;
- voice is expensive/risky and should be piloted after fallback/inbox exists.

## 14.20 Final answer: what “идеальный документ” means here

This document is now intended to be the authoritative build blueprint. It includes:

- current state;
- ideal state;
- competitor benchmark;
- missing architecture;
- DB schema direction;
- infra direction;
- onboarding direction;
- channel/number setup;
- AI logic;
- voice logic;
- operator workflow;
- testing;
- security;
- analytics;
- billing;
- launch;
- exact execution order.

The project itself is not yet ideal until the checklist is implemented. But the plan now defines what “ideal” means in a testable way: if every acceptance checklist above passes, CallForce is no longer an MVP and can operate as a real production AI-operator SaaS.

---

# 15. Client-first setup blueprint: how the product feels from first click to live operations

Этот раздел закрывает главный UX-вопрос: **как сделать так, чтобы клиент не “разбирался в платформе”, а быстро получил работающего AI-оператора**. Техническая архитектура выше отвечает “что построить”. Этот раздел отвечает “как человек реально проходит путь от нуля до live”.

Core principle: CallForce must feel like **guided launch**, not like a developer console.

## 15.1 Product promise for the customer

Пользователь должен понимать продукт за 30 секунд:

```text
CallForce подключается к вашим звонкам и сообщениям, знает меню/правила доставки,
сам отвечает клиентам, помогает принимать заказы и переводит сложное оператору.
Запуск: загрузите меню, выберите каналы, протестируйте, нажмите Go Live.
```

What this means in UX:

- never start with empty dashboard;
- always show next best action;
- every technical setup has a human-language explanation;
- every external provider step has copy-paste values;
- every connection has a test button;
- every failed test explains exact fix;
- advanced settings are hidden until needed;
- restaurant template should make the product usable before deep customization.

## 15.2 Two setup modes: quick launch and pro setup

### Quick launch: 15-30 minutes

For a restaurant owner who wants speed.

Includes:

- restaurant profile;
- menu upload/paste;
- AI operator template;
- widget setup;
- Telegram setup;
- one human fallback operator;
- test conversation;
- Go Live for chat.

Does not require:

- phone/SIP;
- POS integration;
- advanced prompt editing;
- billing customization;
- custom workflows.

### Pro setup: 1-3 days

For full production.

Adds:

- phone number/SIP;
- WhatsApp/VK;
- iiko/r_keeper;
- order automation;
- payments;
- SLA/teams;
- detailed analytics;
- QA/evals;
- compliance/retention;
- custom playbooks.

UX rule:

- Quick launch must not be blocked by Pro setup;
- Pro setup should appear as “Improve your AI operator” milestones after first live success.

## 15.3 First screen after registration

The first screen should not be a generic dashboard. It should be an activation cockpit.

Header:

```text
Запустим AI-оператора для вашего ресторана
Шаг 1 из 6: расскажите о бизнесе. Обычно запуск занимает 15-30 минут.
```

Left side:

- progress checklist;
- estimated time per step;
- status: not started / needs attention / testing / done;
- “continue where you left off”.

Right side:

- preview of what customer will see/hear;
- live readiness score;
- help card;
- “book setup help” optional.

Primary CTA:

```text
Начать настройку
```

Secondary CTA:

```text
Посмотреть демо-ресторан
```

## 15.4 Wizard overview: the six-step quick launch

```text
1. Business profile
2. Menu and knowledge
3. AI operator behavior
4. Human fallback
5. Channels
6. Test and Go Live
```

Rules:

- user can leave and resume;
- every step autosaves;
- every step has “why we need this” explanation;
- every step has “skip for now” only if safe;
- launch is blocked only for truly critical missing items;
- blocked state must say exactly what to fix.

## 15.5 Step 1: Business profile UX

Fields:

- restaurant name;
- city/timezone;
- address;
- phone shown to customers;
- opening hours;
- delivery hours;
- pickup/delivery enabled;
- delivery radius/zones;
- average preparation/delivery time;
- payment methods;
- cuisine type;
- branches if more than one.

Smart defaults:

- timezone from browser/IP but user confirms;
- currency based on country;
- default language Russian;
- default channel greeting generated from restaurant name;
- default after-hours message generated from hours.

Validation:

- phone must be E.164 internally but shown naturally;
- hours cannot overlap incorrectly;
- delivery enabled requires delivery rules;
- branch without address must be marked pickup-disabled or incomplete.

Good UX copy:

```text
Эти данные AI будет использовать в ответах клиентам: когда вы открыты, куда доставляете, как с вами связаться.
```

Failure state:

```text
Не можем запустить доставку: не указаны зоны или радиус. AI может принимать только самовывоз, пока вы это не заполните.
```

## 15.6 Step 2: Menu and knowledge UX

User options:

- upload menu PDF/photo/document;
- paste menu text;
- import from website;
- import from Google Sheets;
- connect POS later;
- start with template.

After upload, UI should show extracted structured data:

```text
Мы нашли:
- 34 блюда
- 8 категорий
- 12 модификаторов
- 5 аллергенов
- 3 возможных проблемы
```

Review screen:

- menu table;
- missing prices highlighted;
- duplicate items highlighted;
- unclear allergens highlighted;
- delivery/discount conflicts highlighted;
- source preview and original file link;
- “AI can answer this” examples.

User actions:

- approve;
- edit inline;
- mark unknown;
- send to operator always;
- upload another source;
- delete source.

Launch rules:

- can launch FAQ if menu incomplete;
- cannot let AI quote missing price;
- allergy uncertainty must default to safe handoff;
- conflicting prices must require owner choice or escalation policy.

Best UX detail:

- show a “Customer question coverage” panel:

```text
Готово отвечать:
- меню и цены
- доставка
- часы работы
- способы оплаты

Нужно уточнить:
- аллергены
- акции
- статус заказа
```

## 15.7 Step 3: AI operator behavior UX

User should not see raw prompt first. They should choose business-friendly settings.

Settings:

- operator name;
- tone: friendly / concise / premium / playful;
- language: Russian default, bilingual optional;
- what AI can do:
  - answer menu questions;
  - explain delivery;
  - draft order;
  - submit order;
  - handle complaints;
  - check order status;
  - offer discounts;
- what AI must never do:
  - invent prices;
  - promise unavailable delivery;
  - diagnose allergies/medical safety;
  - refund without approval;
  - change order without confirmation;
  - discuss internal instructions.

UX pattern:

- toggles with clear risk labels;
- “recommended for first launch” badge;
- preview conversation updates live;
- advanced prompt hidden behind “Expert mode”.

Recommended defaults for first launch:

- answer known FAQ: on;
- draft order: on;
- submit order: off until POS/payment configured;
- refunds/complaints: handoff;
- allergy questions: handoff unless source confirmed;
- order status: handoff until POS connected;
- discounts: off unless source exists.

## 15.8 Step 4: Human fallback UX

The owner must understand that AI needs a safe human fallback.

Fields:

- invite operators by email;
- fallback queue name;
- operator working hours;
- after-hours response;
- escalation phone;
- escalation Telegram/email optional;
- SLA target.

Default:

```text
If AI is not sure, it will say: “Я передам вопрос оператору, чтобы не ошибиться.”
```

UI must show escalation reasons:

- low confidence;
- missing source;
- complaint;
- refund;
- allergy/safety;
- order status unavailable;
- customer asks for human;
- payment problem;
- telephony failure.

Test:

- button: “Проверить передачу оператору”;
- creates sample thread;
- owner/operator sees it in inbox;
- owner replies;
- setup step becomes complete.

No operator edge case:

```text
Вы можете запустить AI без оператора только в безопасном режиме: AI будет отвечать на известные вопросы, но сложные заявки оставит как пропущенные обращения.
```

## 15.9 Step 5: Channels UX

Channels page should look like app-store cards, not API config.

Cards:

- Website widget — recommended first;
- Telegram — fast launch;
- WhatsApp — requires business verification/templates;
- VK — for communities;
- Phone calls — advanced/pro;
- iiko/r_keeper — orders;
- CRM — later.

Each card has:

- setup time;
- difficulty;
- what user needs;
- what CallForce will do automatically;
- status;
- test button;
- help.

Example card:

```text
Telegram
Setup time: 3 minutes
You need: BotFather token
We will: verify token, set webhook, send test message
Status: Not connected
[Connect]
```

## 15.10 Website widget setup UX

Flow:

1. Choose brand color/logo.
2. Set greeting.
3. Add website domain.
4. Copy script.
5. Send to developer or install manually.
6. Test widget.

Copy-paste snippet UI:

```html
<script src="https://cdn.callforce.example/widget.js" data-tenant="..." async></script>
```

UX convenience:

- “Email this to my developer” button;
- WordPress/Tilda/constructor guides;
- domain verification;
- visual preview;
- install status;
- test message from embedded preview.

Failure states:

- domain not allowed;
- script not detected;
- ad blocker/browser blocked;
- API unreachable;
- tenant disabled;
- no published agent.

## 15.11 Telegram setup UX

Flow:

1. UI explains: “Create bot in BotFather”.
2. Shows exact steps:
   - open Telegram;
   - message `@BotFather`;
   - `/newbot`;
   - choose name;
   - copy token.
3. User pastes token.
4. CallForce verifies token.
5. CallForce sets webhook.
6. UI shows bot username.
7. User clicks “Send test”.
8. User sends message to bot.
9. CallForce marks connected.

UX must show:

- token masked after save;
- rotate token;
- disconnect;
- last webhook event;
- last send result;
- bot deep link.

Perfect success state:

```text
Telegram подключён. Клиенты могут писать вашему AI-оператору: https://t.me/your_bot
```

## 15.12 WhatsApp setup UX

WhatsApp is harder, so UX must be honest.

Modes:

- “I already have WhatsApp Business API”;
- “Help me connect Meta Cloud API”;
- “Use partner/BSP”;
- “Skip for now”.

The UI should explain:

- WhatsApp requires business verification for production;
- outbound first messages require approved templates;
- normal replies work inside 24-hour customer service window;
- template quality can affect deliverability;
- approval can take time.

Setup steps:

1. connect Meta/BSP;
2. select business account;
3. select phone number;
4. configure webhook;
5. sync templates;
6. send inbound test;
7. send template test if needed;
8. show production readiness.

Failure states:

- phone not verified;
- token missing permission;
- webhook verification failed;
- template rejected;
- template disabled/quality issue;
- 24-hour window closed;
- message delivery failed.

## 15.13 VK setup UX

Flow:

1. User selects VK community.
2. Creates/copies group token.
3. Copies confirmation string.
4. CallForce gives callback URL.
5. User enables message events.
6. User confirms server.
7. Sends test message.

UI must provide:

- callback URL copy button;
- secret key copy button;
- confirmation code instructions;
- event types checklist;
- troubleshooting for HTTPS/domain errors.

## 15.14 Phone/voice setup UX

Voice must be treated as advanced but guided.

Entry screen:

```text
Подключите звонки
Выберите способ:
1. Купить новый номер
2. Подключить существующий номер
3. Подключить SIP-транк
4. Настроить переадресацию на CallForce
```

### Buy number

UX:

- choose country/city;
- search numbers;
- select number;
- show monthly price;
- confirm;
- assign to branch/agent;
- call test.

### Existing provider/Twilio-like

UX:

- choose provider;
- paste credentials or OAuth;
- select/import number;
- CallForce configures webhook/SIP where possible;
- test inbound/outbound.

### SIP trunk

UX fields:

- provider name;
- SIP host;
- username;
- password;
- DID/phone number;
- region;
- transport;
- inbound/outbound enabled;
- transfer target;
- recording setting.

UI must explain technical terms simply:

```text
SIP host — адрес вашего телефонного провайдера, например sip.provider.ru.
DID — номер, на который звонят клиенты.
```

Test sequence:

- verify credentials;
- test inbound signaling;
- test media/audio;
- test AI greeting;
- test operator transfer;
- test recording/transcript;
- show latency.

Voice cannot go live unless:

- consent text set;
- fallback transfer/callback set;
- test call passed;
- phone assigned to published agent;
- recording/retention policy configured;
- emergency disable button exists.

## 15.15 POS/order setup UX

The owner must not be forced to connect POS on day one.

Stages:

### Stage 1: Internal order draft

- AI collects order;
- shows summary;
- asks confirmation;
- sends to operator/inbox;
- operator manually enters POS.

### Stage 2: POS connected

- sync menu;
- sync stop-list;
- submit order;
- receive status;
- handle errors.

### Stage 3: Payment/order automation

- payment links;
- status updates;
- cancel/change flows;
- refund handoff.

UX for iiko/r_keeper:

- choose provider;
- enter credentials;
- select organization/terminal;
- import menu preview;
- map delivery/payment types;
- run test order in sandbox/test mode;
- enable real submit.

Launch rule:

- never submit live POS order without explicit owner enabling and successful test order.

## 15.16 Readiness score UX

Dashboard should always show readiness in plain language.

Example:

```text
Launch readiness: 82%
Ready for: website chat, Telegram FAQ
Not ready for: phone calls, WhatsApp, automatic POS orders
```

Checklist groups:

- Business info;
- Knowledge;
- AI safety;
- Human fallback;
- Channels;
- Voice;
- Orders/POS;
- Billing;
- Monitoring.

Each item:

- status;
- why it matters;
- fix button;
- estimated time;
- can skip? yes/no;
- risk if skipped.

## 15.17 Test center UX before Go Live

Before Go Live, user enters Test Center.

Test categories:

- menu questions;
- delivery questions;
- unknown questions;
- allergy/safety;
- complaint/refund;
- order draft;
- operator handoff;
- channel delivery;
- phone call if configured.

UI shows:

- passed/failed;
- transcript;
- source used;
- why AI escalated;
- what to fix;
- rerun test.

Go Live button remains disabled if critical tests fail.

## 15.18 Go Live UX

Final confirmation modal:

```text
Вы готовы запустить AI-оператора
Будет включено:
- Website widget
- Telegram
- AI answers for menu/delivery/FAQ
- Human handoff to Operators queue

Не будет включено пока:
- Phone calls
- WhatsApp
- Automatic POS order submit
```

User must confirm:

- AI scope;
- fallback;
- channels;
- recording consent if voice;
- billing/trial.

After launch:

- show live status;
- show share links;
- show next recommended improvements;
- schedule 24-hour review;
- show emergency pause.

## 15.19 First 24 hours UX

The first day should be actively guided.

Dashboard shows:

- live conversations;
- AI answers;
- escalations;
- unresolved topics;
- failed deliveries;
- operator response time;
- customer satisfaction if collected;
- suggested fixes.

Smart nudges:

- “5 customers asked about delivery minimum — add it to knowledge?”
- “AI escalated 3 allergy questions — add allergen info or keep safe handoff.”
- “Telegram is working; connect website widget next.”
- “No operator online during lunch peak — adjust schedule.”

## 15.20 Daily owner workflow

Owner should not manage prompts daily. They should see business actions.

Morning:

- yesterday summary;
- missed opportunities;
- unresolved topics;
- failed channel sends;
- order/call stats.

During day:

- live alerts only for important problems;
- “operator needed” notifications;
- channel/voice incidents.

Evening:

- ROI report;
- top questions;
- AI mistakes;
- suggested knowledge updates;
- operator performance.

## 15.21 Operator daily workflow

Operator opens Inbox.

They see:

- assigned threads;
- unassigned queue;
- SLA timers;
- AI summary;
- customer details;
- sources AI used;
- suggested reply;
- order draft;
- internal notes.

Operator actions:

- reply;
- assign;
- snooze;
- transfer;
- close;
- mark AI wrong;
- add knowledge gap;
- create order manually;
- request manager approval.

UX must prevent mistakes:

- clear channel badge;
- “reply visible to customer” vs internal note;
- confirmation for refunds/discounts;
- warning if customer waited too long;
- mobile-friendly composer.

## 15.22 End-customer experience

The restaurant customer should feel they are talking to a competent operator.

AI should:

- greet naturally;
- answer quickly;
- ask one clarification at a time;
- not expose system internals;
- not say “based on vector database/source chunk”;
- use restaurant tone;
- admit uncertainty;
- offer human help;
- remember context within conversation;
- confirm order details before action.

Customer handoff message:

```text
Чтобы не ошибиться, передам этот вопрос оператору. Он увидит весь диалог и ответит здесь.
```

Customer should see:

- typing/processing state;
- operator joined state;
- after-hours expectation;
- order summary;
- confirmation request;
- status updates.

## 15.23 Error and recovery UX

Every error must answer four questions:

1. What happened?
2. Does it affect customers?
3. What should I do?
4. Can CallForce fix/retry automatically?

Examples:

### Telegram webhook failed

```text
Telegram не может доставить сообщения в CallForce.
Клиенты пока не получат ответы в Telegram.
Мы попробуем переподключить webhook автоматически. Если ошибка останется, нажмите “Переподключить”.
```

### Knowledge source failed

```text
Меню не обработалось: файл слишком размытый.
Загрузите PDF/текст или вставьте меню вручную. AI пока не будет отвечать по этому меню.
```

### Voice provider down

```text
Провайдер звонков недоступен.
Новые звонки будут переведены на резервный номер, если он настроен. Записи и транскрипты могут появиться позже.
```

### POS submit failed

```text
Заказ не отправился в POS.
Мы создали задачу оператору, чтобы заказ не потерялся. Повторная отправка доступна после проверки.
```

## 15.24 Defaults that make setup fast

The system should pre-create:

- restaurant AI template;
- default greeting;
- default safe handoff rules;
- default operator queue;
- default SLA;
- default no-answer policy;
- default analytics dashboard;
- default eval suite;
- default widget theme;
- default Telegram instructions;
- default launch checklist;
- default after-hours behavior.

The owner should customize only what is necessary.

## 15.25 Help, docs and support inside setup

Every setup step needs:

- short explanation;
- visual example;
- provider-specific instructions;
- copy buttons;
- test button;
- troubleshooting;
- “send to developer/operator” link;
- support chat/contact.

Docs should be contextual:

- not one huge docs page;
- small guides opened from the step;
- “what you need before starting” checklist;
- screenshots/GIFs for external provider consoles.

## 15.26 UX metrics that prove setup is good

Track:

- registration -> first source uploaded;
- source uploaded -> first test answer;
- first test answer -> first connected channel;
- first connected channel -> Go Live;
- time to first live customer message;
- time to first operator handoff resolved;
- setup drop-off by step;
- most common setup errors;
- support requests per setup;
- activation by channel.

Targets:

- quick launch first channel within 30 minutes;
- widget install under 10 minutes if user controls site;
- Telegram connect under 5 minutes;
- first test answer under 10 minutes after menu upload;
- no manual developer intervention for standard setup.

## 15.27 What must never happen in ideal UX

- empty dashboard after signup;
- raw JSON/API keys as the first experience;
- “contact support” without explanation;
- silent webhook failure;
- AI live without fallback policy;
- voice live without test call;
- POS live without test order;
- WhatsApp outbound without template/window explanation;
- customer messages disappear without thread/log;
- operator cannot tell if message is public or internal;
- owner cannot pause AI quickly;
- setup progress lost after refresh.

## 15.28 End-to-end walkthrough: ideal restaurant launch

```text
Owner opens landing
  -> clicks Start
  -> registers
  -> verifies email
  -> sees activation cockpit
  -> chooses Restaurant/Delivery
  -> fills business profile
  -> uploads menu
  -> reviews extracted menu issues
  -> approves safe knowledge
  -> chooses AI behavior defaults
  -> invites operator
  -> tests handoff
  -> connects Telegram
  -> sends test Telegram message
  -> installs widget or sends snippet to developer
  -> runs Test Center
  -> sees readiness score
  -> clicks Go Live for widget/Telegram
  -> receives first real customer message
  -> AI answers known question with source
  -> AI escalates unknown/refund/allergy safely
  -> operator replies from Inbox
  -> owner sees analytics and unresolved topics
  -> later connects phone number/SIP
  -> runs test call
  -> later connects POS
  -> enables order submit after test order
```

If this exact flow works without developer help, the product feels premium and self-serve.

## 15.29 Final UX conclusion

To be better than top platforms, CallForce must not only have more features. It must make a hard technical product feel simple:

- owner sees a guided launch cockpit;
- AI is preconfigured for restaurant reality;
- every setup step has defaults, tests and recovery;
- technical provider setup is translated into clear human steps;
- launch is gated by safety checks;
- daily operation shows business outcomes, not technical noise;
- operator workflow prevents missed customers;
- owner can pause, fix and improve the AI without engineering.

This is the practical UX bar for “клиент зашёл, быстро всё настроил, и всё работает удобно”.
