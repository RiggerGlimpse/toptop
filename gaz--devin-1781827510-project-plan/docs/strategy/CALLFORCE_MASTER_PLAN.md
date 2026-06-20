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
