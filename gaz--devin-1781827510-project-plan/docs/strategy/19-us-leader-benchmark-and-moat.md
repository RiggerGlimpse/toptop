# 19. Benchmark топовых AI-agent компаний и moat для CallForce

Date checked: 2026-06-20.

Цель документа: зафиксировать, какие зарубежные проекты считаются топовыми, почему инвесторы дают им сотни миллионов долларов, и какой moat должен построить CallForce, чтобы быть не копией, а сильным локальным продуктом для РФ/СНГ.

## Главный вывод

CallForce должен строиться не как “ещё один chatbot”, а как вертикальный AI-оператор:

> AI-оператор для ресторанов, доставки и сервисного бизнеса: отвечает на звонки и сообщения, знает базу знаний, принимает заказы, подключается к iiko/r_keeper/1C/CRM, переводит сложное человеку и показывает владельцу экономику автоматизации.

Лучшее позиционирование: **Bland AI + Intercom Fin + локальные интеграции РФ/СНГ**.

## Компании-ориентиры

| Компания | Сильная сторона | Что важно скопировать | Как CallForce может быть лучше локально |
| --- | --- | --- | --- |
| Bland AI | Сложные телефонные разговоры, own voice models, 3.5M+ calls/week, >$100M raised | Voice-first reliability, long calls, interruption handling, production call monitoring | Русский голос, SIP/локальные телефония-провайдеры, рестораны/доставка, 152-ФЗ |
| Sierra | Enterprise customer agents, complex workflows, huge enterprise trust | Agent platform, workflow execution, premium UX, enterprise governance | Дешевле, быстрее запуск, локальные каналы и CRM |
| Decagon | AI concierge across voice/chat/email/SMS, operational procedures | Omnichannel concierge, safe procedures, enterprise rollout | Шаблоны под РФ-бизнес, Telegram/VK/WhatsApp, iiko/1C |
| Vapi | Developer-first voice agent platform, fast deployment, simulations | Voice infrastructure, API-first design, simulations, call testing | No-code cabinet + готовые вертикальные шаблоны, не только API |
| Retell AI | Build/test/deploy/monitor loop for voice agents | Voice test console, deployment lifecycle, call logs | Русские сценарии, локальные телефония/каналы |
| PolyAI / Parloa | Enterprise call-center voice agents | Voice quality, contact-center integration, responsible AI | Mid-market SaaS, fast onboarding, local integrations |
| Intercom Fin | AI support agent + helpdesk + human handoff | Knowledge-grounded answers, operator inbox, resolution metrics | Русский рынок, cheaper support automation, Telegram-first |
| Zendesk AI / Ada | Mature support automation platforms | Knowledge, workflows, analytics, escalation | Вертикальные packages, локальная цена, быстрый pilot |
| ElevenLabs | Best-in-class voice models and agents | Natural voice, turn-taking, expressiveness | Use best provider first, then add local/fallback models |

## Что у топовых проектов общее

1. Они не продают “бота”; они продают **business outcome**: меньше операторов, больше продаж, быстрее ответы, выше CSAT.
2. У них есть полный цикл: build → test → deploy → monitor → improve.
3. Они выбирают одну сильную категорию: voice agents, customer agents, helpdesk agents, concierge agents.
4. Они показывают качество: resolution rate, containment rate, latency, cost, failures, handoff reasons.
5. Они не боятся человека: operator handoff — часть продукта, а не ошибка.
6. Они делают workflow actions: возврат, заказ, бронь, оплата, изменение заявки, статус.
7. Они строят доверие: guardrails, audit, permissions, human approval, privacy.

## Где CallForce может выиграть

### 1. Локализация лучше глобальных игроков

- русский язык по умолчанию;
- локальные каналы: Telegram, VK, WhatsApp Business через доступных провайдеров;
- локальные интеграции: iiko, r_keeper, 1C, Bitrix24, AmoCRM, ЮKassa;
- локальная правовая рамка: 152-ФЗ, согласие на запись, хранение данных;
- цена в рублях и понятные пакеты.

### 2. Вертикальная упаковка

Глобальные платформы часто универсальны. CallForce должен продавать готовый результат:

- ресторан: меню, доставка, бронь, заказ, статусы, акции;
- клиника: запись, перенос, FAQ, напоминания;
- e-commerce: наличие, доставка, возвраты, трекинг;
- сервис: заявки, диагностика, расписание мастера.

Первый фокус: **рестораны/доставка**.

### 3. Кабинет, а не только API

Bland/Vapi сильны как API/platform. Для SMB в РФ нужен кабинет:

- создать агента;
- загрузить меню/FAQ;
- протестировать звонок/чат;
- подключить Telegram/номер/виджет;
- видеть экономику и ошибки;
- передавать диалоги оператору.

## Product moat CallForce

CallForce должен иметь 5 защитных слоёв:

1. **Vertical data moat**: шаблоны, промпты, eval-наборы и сценарии под каждую отрасль.
2. **Integration moat**: iiko/r_keeper/1C/CRM/телефония, которые сложно быстро повторить зарубежным игрокам.
3. **Voice quality moat**: русская речь, перебивания, паузы, шум, разные акценты, latency.
4. **Operational moat**: запуск клиента за 1-3 дня, playbooks, мониторинг, ручная проверка качества.
5. **Trust moat**: аудит, роли, безопасность, хранение, согласие на запись, human approval.

## Minimum “top competitor parity”

Нельзя говорить “лучше Bland/Intercom”, пока нет:

- 10-20 реальных тестовых звонков с логами и записями;
- стабильного chat/widget/Telegram production flow;
- operator inbox с handoff summary;
- RAG evals и no-answer policy;
- production deployment/staging;
- метрик качества и стоимости;
- реальной интеграции хотя бы с одним бизнес-действием.

## North Star

Один показатель должен быть главным:

> Доля обращений, решённых AI без участия человека, без нарушения правил и с подтверждённой пользой для бизнеса.

Для первого платного пилота целевой минимум:

- 50-60% automation rate на FAQ/простых заказах;
- < 5% опасных/неправильных ответов на eval-наборе;
- < 3 секунды latency для chat;
- < 2.5 секунды perceived turn latency для voice после окончания фразы;
- 100% сложных/опасных случаев уходят в handoff.
