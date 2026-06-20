from uuid import NAMESPACE_URL, UUID, uuid5

from app.rbac import Role
from app.schemas import (
    Agent,
    AgentStatus,
    ChatMessageRequest,
    KnowledgeSource,
    KnowledgeSourceStatus,
    Tenant,
    User,
)

DEMO_TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")
DEMO_OWNER_PASSWORD = "safe-local-password"
DEMO_OWNER_EMAIL = "owner@demo-pizza.example.com"


def demo_uuid(name: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"gaz-demo:{name}")


def build_demo_tenant(tenant_id: UUID = DEMO_TENANT_ID) -> Tenant:
    return Tenant(id=tenant_id, name="Demo Pizza", plan="pilot")


def build_demo_owner(tenant_id: UUID = DEMO_TENANT_ID) -> User:
    return User(
        id=demo_uuid("user:owner"),
        tenant_id=tenant_id,
        email=DEMO_OWNER_EMAIL,
        name="Demo Owner",
        role=Role.owner,
    )


def build_demo_agents(tenant_id: UUID = DEMO_TENANT_ID) -> list[Agent]:
    return [
        Agent(
            id=demo_uuid("agent:restaurant-support"),
            tenant_id=tenant_id,
            name="Demo Pizza AI Operator RU",
            prompt=(
                "Ты AI-оператор ресторана Demo Pizza для звонков, Telegram и сайта. "
                "Отвечай коротко и дружелюбно, используй только базу знаний и "
                "подключенные tools. Не выдумывай цены, сроки, наличие, статус "
                "заказа или скидки. Перед созданием, изменением или отменой заказа "
                "обязательно получи явное подтверждение клиента. Если клиент злится, "
                "просит человека, спрашивает про аллергию, корпоративный заказ, "
                "возврат денег или нестандартную ситуацию — передай оператору с резюме."
            ),
            status=AgentStatus.published,
            channel="telegram",
            version=1,
            voice_id="alloy",
            voice_language="ru",
            voice_speed=1.0,
            temperature=0.25,
            max_tokens=700,
            model_name="gpt-4o-mini",
        ),
        Agent(
            id=demo_uuid("agent:web-widget"),
            tenant_id=tenant_id,
            name="Demo Pizza Website Concierge",
            prompt=(
                "Помогай гостям сайта Demo Pizza выбрать пиццу, узнать доставку, "
                "условия оплаты, акции и статус простого заказа. Если для ответа "
                "нужны персональные данные, точный статус заказа или ручное решение, "
                "предложи перевод на оператора."
            ),
            status=AgentStatus.published,
            channel="web_widget",
            version=1,
            voice_id="alloy",
            voice_language="ru",
            voice_speed=1.0,
            temperature=0.25,
            max_tokens=700,
            model_name="gpt-4o-mini",
        ),
    ]


def build_demo_knowledge_sources(tenant_id: UUID = DEMO_TENANT_ID) -> list[KnowledgeSource]:
    return [
        KnowledgeSource(
            id=demo_uuid("knowledge:delivery-faq"),
            tenant_id=tenant_id,
            title="Demo Pizza: доставка и оплата",
            source_type="manual",
            content=(
                "Доставка Demo Pizza занимает 45-60 минут после подтверждения заказа. "
                "Бесплатная доставка доступна при заказе от 1000 рублей. Заказы меньше "
                "1000 рублей доставляются за 199 рублей. Оплата доступна картой на сайте, "
                "наличными курьеру или по ссылке YooKassa. Зона доставки: Центральный, "
                "Советский и Октябрьский районы. Заказы за пределы зоны доставки нужно "
                "передать оператору."
            ),
            status=KnowledgeSourceStatus.pending,
            chunk_count=0,
        ),
        KnowledgeSource(
            id=demo_uuid("knowledge:menu-faq"),
            tenant_id=tenant_id,
            title="Demo Pizza: меню и состав",
            source_type="manual",
            content=(
                "В меню есть пепперони 30 см за 690 рублей, маргарита 30 см за 590 "
                "рублей, вегетарианская пицца 30 см за 650 рублей и четыре сыра 30 см "
                "за 790 рублей. Острая пепперони содержит томаты, моцареллу и пепперони. "
                "Маргарита содержит томаты, моцареллу и базилик. Пиццы без глютена пока "
                "нет, такой запрос нужно передать оператору. Информацию по аллергенам "
                "нужно подтверждать у оператора."
            ),
            status=KnowledgeSourceStatus.pending,
            chunk_count=0,
        ),
        KnowledgeSource(
            id=demo_uuid("knowledge:order-policy"),
            tenant_id=tenant_id,
            title="Demo Pizza: правила заказов",
            source_type="manual",
            content=(
                "AI-оператор может собрать черновик заказа: позиции, количество, имя, "
                "телефон, адрес и способ оплаты. Перед созданием заказа AI обязан "
                "повторить состав, сумму, адрес и получить явное подтверждение клиента. "
                "Изменить или отменить заказ можно только до передачи на кухню. Точный "
                "статус заказа нельзя угадывать: его нужно проверять через систему заказов "
                "или передавать оператору."
            ),
            status=KnowledgeSourceStatus.pending,
            chunk_count=0,
        ),
        KnowledgeSource(
            id=demo_uuid("knowledge:handoff-policy"),
            tenant_id=tenant_id,
            title="Demo Pizza: правила передачи оператору",
            source_type="manual",
            content=(
                "Передача оператору обязательна, если клиент просит человека, злится, "
                "сообщает об аллергии, хочет возврат денег, жалуется на качество, просит "
                "корпоративный заказ больше 20 персон, находится вне зоны доставки или "
                "задает вопрос, которого нет в базе знаний. При передаче нужно кратко "
                "указать тему, что уже спросил клиент и какое действие требуется."
            ),
            status=KnowledgeSourceStatus.pending,
            chunk_count=0,
        ),
    ]


def build_demo_chat_requests(agent_id: UUID) -> list[ChatMessageRequest]:
    return [
        ChatMessageRequest(
            agent_id=agent_id,
            channel="telegram",
            message="Сколько занимает доставка и от какой суммы она бесплатная?",
        ),
        ChatMessageRequest(
            agent_id=agent_id,
            channel="web_widget",
            message="Есть ли пицца без глютена?",
        ),
        ChatMessageRequest(
            agent_id=agent_id,
            channel="web_widget",
            message="Хочу пепперони и маргариту, можно оформить заказ?",
        ),
        ChatMessageRequest(
            agent_id=agent_id,
            channel="telegram",
            message="Мой заказ опаздывает, где курьер?",
        ),
        ChatMessageRequest(
            agent_id=agent_id,
            channel="web_widget",
            message="Можно ли оформить корпоративный кейтеринг на 200 человек?",
        ),
    ]
