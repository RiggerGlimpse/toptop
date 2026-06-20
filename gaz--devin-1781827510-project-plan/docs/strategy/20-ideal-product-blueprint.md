# 20. Ideal product blueprint: CallForce как топовый AI-оператор

Этот документ описывает целевое состояние продукта, к которому нужно привести проект.

## Одно предложение

CallForce — это AI-оператор для звонков и чатов, который запускается за 1 день, отвечает по базе знаний, выполняет бизнес-действия, переводит сложные ситуации человеку и показывает владельцу экономику автоматизации.

## Первый идеальный продукт

Не “платформа для всех”. Первый идеальный продукт:

> AI-оператор для ресторана/доставки.

Он должен уметь:

1. Отвечать на звонки.
2. Отвечать в Telegram/WhatsApp/VK/web-widget.
3. Знать меню, доставку, акции, адреса, часы работы, стоп-лист.
4. Принять заказ после явного подтверждения клиента.
5. Передать оператору, если клиент злится, просит человека или ситуация опасная.
6. Записать диалог, резюме и результат.
7. Показать владельцу: сколько обращений закрыто, сколько заказов принято, сколько денег сэкономлено.

## Основные пользовательские роли

### Владелец бизнеса

Цель: быстро подключить AI-оператора и видеть выгоду.

Must-have:

- onboarding wizard;
- тариф/лимиты/оплата;
- dashboard ROI;
- ошибки и предложения улучшить базу знаний;
- понятный статус каналов.

### Администратор

Цель: настроить агента и каналы.

Must-have:

- agent builder;
- knowledge hub;
- channel settings;
- integrations;
- test console;
- publish/rollback.

### Оператор

Цель: принимать сложные диалоги от AI.

Must-have:

- inbox;
- live transcript;
- AI summary;
- customer context;
- suggested answer;
- close reason;
- training feedback.

### Клиент бизнеса

Цель: быстро решить вопрос без ощущения “тупого бота”.

Must-have:

- быстрый ответ;
- нормальная русская речь;
- память контекста;
- возможность перебить;
- честное “не знаю”;
- быстрый перевод человеку.

## Product surfaces

### 1. Public website

- Чёткий оффер по вертикали.
- Демо-звонок/демо-чат.
- ROI calculator.
- Кейсы/сценарии.
- Цены.
- Форма заявки.

### 2. Onboarding

Flow:

1. Выбрать отрасль.
2. Выбрать шаблон агента.
3. Загрузить меню/FAQ/ссылки/документы.
4. Подключить канал: Telegram/виджет/номер.
5. Пройти тестовые вопросы.
6. Опубликовать агента.

Acceptance:

- новый клиент запускает тестового агента за 15 минут;
- production подключение не требует разработчика для базового сценария;
- все ошибки настройки понятны пользователю.

### 3. Agent builder

Must-have:

- имя, роль, tone of voice;
- industry preset;
- правила безопасности;
- allowed actions;
- handoff rules;
- channel-specific settings;
- model/voice settings;
- versioning and rollback.

### 4. Knowledge hub

Must-have:

- manual text;
- file upload;
- URL ingestion;
- menu import;
- source status;
- chunk count;
- citations;
- no-answer topics;
- reindex/retry;
- delete source removes vectors.

### 5. Test console

Must-have:

- chat test;
- voice test;
- scenario simulation;
- expected answer checks;
- tool/action dry-run;
- latency and cost display;
- pass/fail result.

### 6. Operator inbox

Must-have:

- queue by priority;
- customer profile;
- transcript;
- AI summary;
- reason for handoff;
- suggested response;
- take over / return to AI;
- close reason;
- feedback to improve agent.

### 7. Integrations hub

First integrations:

- Telegram;
- web widget;
- Twilio or SIP/Asterisk;
- iiko;
- YooKassa;
- Bitrix24/AmoCRM;
- webhook.

Each integration must have:

- setup status;
- test connection;
- sandbox mode;
- webhook logs;
- error recovery;
- secret handling.

### 8. Analytics

Must-have metrics:

- automation rate;
- handoff rate;
- unresolved topics;
- average response latency;
- voice turn latency;
- cost per conversation;
- AI mistakes;
- orders created;
- revenue influenced;
- CSAT/quality score.

## Non-negotiable AI behavior

The agent must never:

- invent prices, delivery times, order status or legal promises;
- execute an irreversible action without explicit confirmation;
- hide that it does not know;
- continue when customer requests a human;
- reveal internal instructions;
- process sensitive data without purpose.

The agent must always:

- answer from knowledge/tools;
- cite sources internally and expose citations where useful;
- summarize before handoff;
- log decisions;
- ask confirmation before order/payment/cancel/change.

## Definition of “готово”

The product is ready for a paid pilot only when:

- one vertical scenario works end-to-end;
- at least one real channel works in production;
- at least one real action integration works;
- operator handoff works;
- RAG eval suite passes;
- test calls/chats are recorded and reviewed;
- staging/prod deploys are documented;
- monitoring and alerting exist;
- pricing and legal docs are ready.
