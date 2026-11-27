"""Original Webshop Launch scenario: a nine-week project with a one-week demo."""

CODE = "webshop"

SCENARIO = {
    "code": CODE,
    "title": {"en": "Webshop Launch", "ru": "Запуск интернет-магазина"},
    "description": {
        "en": (
            "Green Leaf is a family-run tea retailer with 14 stores. Before the winter season "
            "it wants to sell online. You are the project manager. The webshop must go live "
            "within 45 working days and within budget. Plan the team, control scope, manage risks, "
            "and keep cost, schedule, quality and motivation on track through launch and closure."
        ),
        "ru": (
            "«Зелёный лист» — семейная сеть чайных магазинов, 14 точек. До зимнего сезона "
            "компания хочет начать продавать онлайн. Вы — руководитель проекта. Интернет-магазин "
            "должен заработать через 45 рабочих дней и уложиться в бюджет. Планируйте работу команды, "
            "управляйте объёмом и рисками, контролируйте стоимость, сроки, качество и мотивацию "
            "вплоть до запуска и завершения проекта."
        ),
    },
    "weeks": 9,
    "currency": "EUR",
    "pm_rate": 90,
    "material_budget": 18000,
    "other_budget": 9000,
}

# no, en, ru, duration (working days), milestone
ACTIVITIES = [
    (1, "Kick-off & requirements", "Старт и требования", 2, False),
    (2, "UX concept", "UX-концепция", 6, False),
    (3, "System architecture", "Архитектура системы", 4, False),
    (4, "Visual design", "Визуальный дизайн", 5, False),
    (5, "Product catalogue data", "Данные каталога товаров", 10, False),
    (6, "Hosting & infrastructure", "Хостинг и инфраструктура", 4, False),
    (7, "Backend development", "Разработка бэкенда", 12, False),
    (8, "Frontend development", "Разработка фронтенда", 14, False),
    (9, "Payment integration", "Интеграция платежей", 7, False),
    (10, "Delivery integration", "Интеграция доставки", 7, False),
    (11, "Content & photos", "Контент и фото", 8, False),
    (12, "Integration testing", "Интеграционное тестирование", 6, False),
    (13, "Staff training", "Обучение персонала", 3, False),
    (14, "Launch marketing", "Маркетинг запуска", 8, False),
    (15, "Go-live", "Запуск", 1, True),
    (16, "Data protection & compliance", "Защита данных и соответствие", 4, False),
    (17, "Accessibility design", "Проектирование доступности", 4, False),
    (18, "CRM & ERP integration", "Интеграция CRM и ERP", 8, False),
    (19, "Analytics & reporting", "Аналитика и отчётность", 6, False),
    (20, "Automated test suite", "Автоматизированные тесты", 8, False),
    (21, "Performance & security testing", "Нагрузочное тестирование и безопасность", 4, False),
    (22, "User acceptance testing", "Приёмочное тестирование", 2, False),
    (23, "Launch readiness & rollback rehearsal", "Готовность к запуску и откат", 1, True),
    (24, "Project closure & lessons learned", "Завершение и извлечённые уроки", 1, True),
    (25, "Stakeholder & communication plan", "План работы с заинтересованными сторонами", 2, False),
    (26, "Requirements traceability & backlog", "Трассируемость требований и бэклог", 3, False),
    (27, "Procurement & supplier contracting", "Закупки и договоры с поставщиками", 4, False),
    (28, "Customer interviews & journey validation", "Интервью с клиентами и проверка сценариев", 3, False),
    (29, "Design system & component library", "Дизайн-система и библиотека компонентов", 3, False),
    (30, "API specification & integration contracts", "Спецификация API и контракты интеграций", 2, False),
    (31, "Monitoring, logging & alerting", "Мониторинг, журналирование и оповещения", 3, False),
    (32, "Data migration mapping & cleansing", "Сопоставление и очистка данных миграции", 4, False),
    (33, "Product content translation", "Перевод товарного контента", 4, False),
    (34, "SEO & analytics tagging", "SEO и разметка аналитики", 3, False),
    (35, "Payment security certification", "Сертификация безопасности платежей", 3, False),
    (36, "Delivery exception workflows", "Сценарии исключений доставки", 3, False),
    (37, "CRM data validation", "Проверка данных CRM", 3, False),
    (38, "Support knowledge base", "База знаний поддержки", 4, False),
    (39, "Operational support handover", "Передача в операционную поддержку", 2, False),
    (40, "Benefits measurement plan", "План измерения выгод проекта", 2, False),
]

# activity -> predecessors
DEPENDENCIES = {
    2: [1], 3: [1], 5: [1], 4: [29], 6: [3], 7: [30], 8: [3, 4],
    9: [7], 10: [7], 11: [32], 12: [8, 9, 10, 35, 36], 13: [12], 14: [11],
    16: [30], 17: [4], 18: [7, 16], 19: [7], 20: [7],
    21: [12, 16, 18, 19, 20, 34, 37], 22: [21], 23: [13, 14, 22, 38, 39], 15: [23], 24: [15],
    25: [1], 26: [1], 27: [16], 28: [26], 29: [2], 30: [3], 31: [6], 32: [5],
    33: [11], 34: [19], 35: [9], 36: [10], 37: [18], 38: [33], 39: [13], 40: [19],
}

# no, name en, name ru, role en, role ru, hourly rate
RESOURCES = [
    (1, "Laura", "Лаура", "Business analyst", "Бизнес-аналитик", 70),
    (2, "Mark", "Марк", "Solution architect", "Архитектор решений", 95),
    (3, "Nina", "Нина", "UX designer", "UX-дизайнер", 75),
    (4, "Oscar", "Оскар", "Frontend developer", "Фронтенд-разработчик", 80),
    (5, "Priya", "Прия", "Backend developer", "Бэкенд-разработчик", 85),
    (6, "Ravi", "Рави", "Backend developer", "Бэкенд-разработчик", 80),
    (7, "Sofia", "София", "Content manager", "Контент-менеджер", 55),
    (8, "Tom", "Том", "QA engineer", "Инженер по тестированию", 65),
    (9, "Uma", "Ума", "Marketing specialist", "Маркетолог", 60),
    (10, "Victor", "Виктор", "DevOps engineer", "DevOps-инженер", 90),
    (11, "Wendy", "Венди", "Freelance developer", "Разработчик-фрилансер", 100),
]

# resource -> {week: state}; anything not listed is "payroll"
RESOURCE_WEEKS = {
    6: {1: "training"},
    3: {4: "holiday"},
    8: {w: "other" for w in range(1, 5)},
    9: {7: "holiday"},
    10: {1: "other", 2: "other"},
    11: {w: "available" for w in range(1, 10)},
}

# activity -> [(resource, percent)]
DEFAULT_ASSIGNMENTS = {
    1: [(1, 100), (2, 100)],
    2: [(3, 100)],
    3: [(2, 100)],
    4: [(3, 100)],
    5: [(7, 100)],
    6: [(10, 100)],
    7: [(5, 100), (6, 100)],
    8: [(4, 100)],
    9: [(5, 100)],
    10: [(6, 100)],
    11: [(7, 100)],
    12: [(8, 100), (1, 50)],
    13: [(1, 100)],
    14: [(9, 100)],
    15: [(10, 100), (2, 100)],
    16: [(2, 100)],
    17: [(3, 100)],
    18: [(11, 100)],
    19: [(1, 100)],
    20: [(8, 100)],
    21: [(8, 100), (2, 100)],
    22: [(1, 100), (8, 100)],
    23: [(10, 100), (2, 100)],
    24: [(1, 100)],
    25: [(1, 50)],
    26: [(1, 50)],
    27: [(2, 50)],
    28: [(1, 50)],
    29: [(3, 100)],
    30: [(2, 100)],
    31: [(10, 100)],
    32: [(7, 100)],
    33: [(7, 100)],
    34: [(1, 50)],
    35: [(5, 100)],
    36: [(6, 100)],
    37: [(11, 100)],
    38: [(7, 100)],
    39: [(10, 100)],
    40: [(1, 50)],
}

HELEN = {"en": "Helen Berg, CEO", "ru": "Елена Берг, генеральный директор"}


def t(en: str, ru: str) -> dict:
    return {"en": en, "ru": ru}


DECISIONS = [
    {
        "key": "scope",
        "default_option": "a",
        "prompt": t(
            "At the end of the kick-off Helen asks to add a loyalty program (points and member "
            "prices) to the first release. \"It should be small,\" she says. What do you do?",
            "В конце стартовой встречи Елена просит добавить в первый релиз программу "
            "лояльности (баллы и цены для участников). «Это ведь немного», — говорит она. "
            "Что вы сделаете?",
        ),
        "options": [
            {
                "key": "a",
                "label": t("Accept it into the current plan", "Принять в текущий план"),
                "feedback": t(
                    "The team takes on the extra work with the same dates. Backend and frontend "
                    "effort grows by 72 hours. Uncontrolled scope growth is one of the most "
                    "common reasons projects slip.",
                    "Команда берёт дополнительную работу при тех же сроках. Трудоёмкость бэкенда "
                    "и фронтенда растёт на 72 часа. Неконтролируемый рост объёма — одна из самых "
                    "частых причин срыва сроков.",
                ),
                "effects": {"effort": {"7": 48, "8": 24}, "motivation": -3},
                "learning_point": t(
                    "Never accept a scope change before you know its impact on time and cost.",
                    "Не принимайте изменение объёма, пока не оценили его влияние на сроки и стоимость.",
                ),
            },
            {
                "key": "b",
                "label": t(
                    "Ask for a change request with impact analysis",
                    "Оформить запрос на изменение с анализом влияния",
                ),
                "feedback": t(
                    "Laura and Mark spend half a day estimating. Helen sees the numbers and moves "
                    "the loyalty program to release 2. The baseline stays intact.",
                    "Лаура и Марк полдня делают оценку. Увидев цифры, Елена переносит программу "
                    "лояльности во второй релиз. Базовый план не меняется.",
                ),
                "effects": {"cost": 400, "quality": 3},
                "learning_point": t(
                    "Handle scope changes through a formal change request with an impact analysis.",
                    "Проводите изменения объёма через формальный запрос на изменение с анализом влияния.",
                ),
            },
            {
                "key": "c",
                "label": t("Refuse — it is out of scope", "Отказать — это вне рамок проекта"),
                "feedback": t(
                    "Helen accepts, but she is visibly unhappy. You will need the sponsor's support "
                    "later in the project.",
                    "Елена соглашается, но явно недовольна. Поддержка спонсора понадобится вам "
                    "позже в проекте.",
                ),
                "effects": {"motivation": -2},
                "learning_point": t(
                    "Saying no is legitimate. Explain the trade-off so the sponsor stays on board.",
                    "Отказать можно, но объясните компромисс, чтобы сохранить поддержку спонсора.",
                ),
            },
        ],
    },
    {
        "key": "remote",
        "default_option": "b",
        "prompt": t(
            "Nina asks to work from home two days a week while she focuses on the UX concept. "
            "She says the open office is too noisy for concentrated design work.",
            "Нина просит работать из дома два дня в неделю, пока она занимается UX-концепцией. "
            "По её словам, в открытом офисе слишком шумно для сосредоточенной работы.",
        ),
        "options": [
            {
                "key": "a",
                "label": t("Approve", "Согласовать"),
                "feedback": t(
                    "Nina is pleased and productive. The rest of the team notices that requests "
                    "are taken seriously.",
                    "Нина довольна и работает продуктивно. Команда видит, что к просьбам относятся серьёзно.",
                ),
                "effects": {"motivation": 5, "quality": 1},
                "learning_point": t(
                    "Adapting the work environment to the task is a cheap motivation lever.",
                    "Подстроить условия работы под задачу — дешёвый способ поддержать мотивацию.",
                ),
            },
            {
                "key": "b",
                "label": t("Refuse — the team must sit together", "Отказать — команда должна сидеть вместе"),
                "feedback": t(
                    "Nina accepts, but she is frustrated. Motivation drops a little across the team.",
                    "Нина соглашается, но расстроена. Мотивация команды немного снижается.",
                ),
                "effects": {"motivation": -6},
                "learning_point": t(
                    "A refusal without a reason costs motivation. Explain, or offer an alternative.",
                    "Отказ без объяснения снижает мотивацию. Объясните причину или предложите альтернативу.",
                ),
            },
            {
                "key": "c",
                "label": t("Approve, with a short daily check-in", "Согласовать, с короткой ежедневной синхронизацией"),
                "feedback": t(
                    "Nina works from home and joins a 15-minute call each morning. Issues surface "
                    "early, which helps quality.",
                    "Нина работает из дома и каждое утро подключается к 15-минутному созвону. "
                    "Проблемы всплывают рано, что помогает качеству.",
                ),
                "effects": {"motivation": 4, "quality": 3, "cost": 150},
                "learning_point": t(
                    "Flexibility plus a light communication routine keeps both motivation and quality.",
                    "Гибкость вместе с лёгким ритмом коммуникации сохраняет и мотивацию, и качество.",
                ),
            },
        ],
    },
    {
        "key": "teamevent",
        "default_option": "b",
        "prompt": t(
            "Laura suggests a small team dinner on Thursday so that everyone gets to know each "
            "other. It would cost about €600.",
            "Лаура предлагает в четверг небольшой командный ужин, чтобы все познакомились. "
            "Это обойдётся примерно в 600 €.",
        ),
        "options": [
            {
                "key": "a",
                "label": t("Yes, organise it", "Да, организуйте"),
                "feedback": t(
                    "The dinner is a success. People who had never worked together now talk freely.",
                    "Ужин удался. Люди, которые раньше не работали вместе, теперь легко общаются.",
                ),
                "effects": {"cost": 600, "motivation": 6},
                "learning_point": t(
                    "Investing early in team building pays off when the pressure rises.",
                    "Вложения в сплочение команды в начале окупаются, когда растёт нагрузка.",
                ),
            },
            {
                "key": "b",
                "label": t("Not now, maybe later", "Не сейчас, может быть позже"),
                "feedback": t(
                    "The team is a bit disappointed. The idea does not come back.",
                    "Команда немного разочарована. К идее больше не возвращаются.",
                ),
                "effects": {"motivation": -2},
                "learning_point": None,
            },
            {
                "key": "c",
                "label": t("Coffee and cake in the office instead", "Вместо этого — кофе с тортом в офисе"),
                "feedback": t(
                    "A short, friendly break. Cheaper, and still appreciated.",
                    "Короткий дружеский перерыв. Дешевле, и всё равно приятно.",
                ),
                "effects": {"cost": 120, "motivation": 3},
                "learning_point": t(
                    "Small gestures matter. Team building does not have to be expensive.",
                    "Мелочи важны. Сплочение команды не обязательно должно быть дорогим.",
                ),
            },
        ],
    },
    {
        "key": "photos",
        "default_option": "b",
        "prompt": t(
            "PhotoPro studio calls. They offer to shoot all 400 product photos for €3,200. That "
            "would remove most of the photo work from \"Content & photos\".",
            "Звонят из фотостудии PhotoPro. Они предлагают снять все 400 товаров за 3 200 €. "
            "Это сняло бы большую часть фоторабот с задачи «Контент и фото».",
        ),
        "options": [
            {
                "key": "a",
                "label": t("Buy the service", "Купить услугу"),
                "feedback": t(
                    "Professional photos, delivered on time. Content & photos needs 40 hours less.",
                    "Профессиональные фото, сданные вовремя. «Контенту и фото» нужно на 40 часов меньше.",
                ),
                "effects": {"cost": 3200, "effort": {"11": -40}, "quality": 2},
                "learning_point": t(
                    "Buying a service can free scarce people, but it moves cost into the budget now.",
                    "Покупка услуги освобождает дефицитных людей, но переносит затраты в бюджет сразу.",
                ),
            },
            {
                "key": "b",
                "label": t("Decline — we do it in-house", "Отказаться — сделаем сами"),
                "feedback": t(
                    "No extra cost. Sofia keeps the full photo workload.",
                    "Без лишних затрат. София сохраняет всю нагрузку по фото.",
                ),
                "effects": {},
                "learning_point": None,
            },
            {
                "key": "c",
                "label": t("Negotiate half the catalogue", "Договориться на половину каталога"),
                "feedback": t(
                    "PhotoPro agrees to shoot the 200 best sellers for €1,800. A balanced trade.",
                    "PhotoPro соглашается снять 200 самых продаваемых товаров за 1 800 €. Разумный компромисс.",
                ),
                "effects": {"cost": 1800, "effort": {"11": -20}, "quality": 1},
                "learning_point": t(
                    "Make-or-buy is rarely all or nothing. Negotiate the split.",
                    "«Делать или покупать» — редко выбор «всё или ничего». Договаривайтесь о доле.",
                ),
            },
        ],
    },
]

# key, week, weekday (0=Mon), hour, duration_h, channel, sender, subject, body, effects, decision
EVENTS = [
    (
        "welcome", 1, 0, 8, 0, "mail", HELEN,
        t("Welcome aboard", "Добро пожаловать"),
        t(
            "Welcome to the webshop project! The plan is approved and the team is ready. The "
            "board expects the shop to go live in 45 working days. Please keep me posted every Friday. "
            "— Helen",
            "Добро пожаловать в проект интернет-магазина! План утверждён, команда готова. Совет "
            "директоров ждёт запуска через 45 рабочих дней. Пожалуйста, держите меня в курсе каждую "
            "пятницу. — Елена",
        ),
        {}, None,
    ),
    (
        "kickoff", 1, 0, 9, 2, "meeting", HELEN,
        t("Kick-off meeting", "Стартовая встреча"),
        t("Whole team, meeting room 2. Catering ordered.", "Вся команда, переговорная 2. Заказан кейтеринг."),
        {"cost": 300}, None,
    ),
    (
        "scope", 1, 0, 11, 0, "mail", HELEN,
        t("Loyalty program for release 1?", "Программа лояльности в первый релиз?"),
        DECISIONS[0]["prompt"], {}, "scope",
    ),
    (
        "remote", 1, 1, 10, 0, "mail", t("Nina, UX designer", "Нина, UX-дизайнер"),
        t("Working from home", "Работа из дома"),
        DECISIONS[1]["prompt"], {}, "remote",
    ),
    (
        "hosting", 1, 1, 15, 0, "phone", t("Mark, architect", "Марк, архитектор"),
        t("Server region", "Регион серверов"),
        t(
            "Mark: the hosting provider wants us to confirm the server region by Friday. Victor "
            "will take care of it when he is back from the other project.",
            "Марк: хостинг-провайдер просит подтвердить регион серверов до пятницы. Виктор "
            "займётся этим, когда вернётся с другого проекта.",
        ),
        {}, None,
    ),
    (
        "sick", 1, 2, 11, 0, "phone", t("Sofia, content manager", "София, контент-менеджер"),
        t("Calling in sick", "Больничный"),
        t(
            "Sofia has a fever and will be away for the rest of the week. Work on the product "
            "catalogue stops unless someone else takes it over. You can reassign people while "
            "the clock is paused.",
            "У Софии температура, до конца недели её не будет. Работа над каталогом товаров "
            "остановится, если её никто не подхватит. Переназначить людей можно, поставив "
            "часы на паузу.",
        ),
        {"resource": {"no": 7, "week": 1, "state": "sick"}}, None,
    ),
    (
        "lunch", 1, 2, 13, 1, "meeting", HELEN,
        t("Lunch with the sponsor", "Обед со спонсором"),
        t("Informal update with Helen.", "Неформальная встреча с Еленой."),
        {}, None,
    ),
    (
        "teamevent", 1, 2, 14, 0, "mail", t("Laura, business analyst", "Лаура, бизнес-аналитик"),
        t("Team dinner?", "Командный ужин?"),
        DECISIONS[2]["prompt"], {}, "teamevent",
    ),
    (
        "photos", 1, 3, 9, 0, "phone", t("PhotoPro studio", "Фотостудия PhotoPro"),
        t("Product photo offer", "Предложение по фото товаров"),
        DECISIONS[3]["prompt"], {}, "photos",
    ),
    (
        "steering1", 1, 3, 15, 1, "meeting", HELEN,
        t("Steering committee", "Управляющий комитет"),
        t("Monthly steering committee with the board.", "Ежемесячный управляющий комитет с советом директоров."),
        {}, None,
    ),
    (
        "statusdue", 1, 4, 10, 0, "mail", HELEN,
        t("Status at 16:00", "Статус в 16:00"),
        t(
            "Please present the project status at 16:00 today. I would like to see the cost and "
            "schedule indexes and what you plan for next week.",
            "Пожалуйста, представьте статус проекта сегодня в 16:00. Хочу увидеть индексы "
            "стоимости и сроков и ваш план на следующую неделю.",
        ),
        {}, None,
    ),
    (
        "status1", 1, 4, 16, 1, "meeting", HELEN,
        t("Weekly status meeting", "Еженедельный статус"),
        t("Status report to the sponsor.", "Отчёт о статусе спонсору."),
        {}, None,
    ),
]

# Recurring project-management ceremonies for the full nine-week game.
for _w in range(2, 10):
    EVENTS.append((
        f"status{_w}", _w, 4, 16, 1, "meeting", HELEN,
        t("Weekly status meeting", "Еженедельный статус"),
        t("Status report to the sponsor.", "Отчёт о статусе спонсору."),
        {}, None,
    ))
    EVENTS.append((
        f"standup{_w}", _w, 0, 9, 0.5, "meeting", t("Team", "Команда"),
        t("Weekly planning", "Планирование недели"),
        t("Team planning for the week.", "Планирование работы команды на неделю."),
        {}, None,
    ))
for _w in (5, 9):
    EVENTS.append((
        f"steering{_w}", _w, 3, 15, 1, "meeting", HELEN,
        t("Steering committee", "Управляющий комитет"),
        t("Monthly steering committee with the board.", "Ежемесячный управляющий комитет с советом директоров."),
        {}, None,
    ))
EVENTS.append((
    "golive", 9, 4, 14, 2, "meeting", HELEN,
    t("Go-live and project closure", "Запуск и завершение проекта"),
    t("Confirm the launch, hand over operations and capture lessons learned.", "Подтвердите запуск, передайте проект в эксплуатацию и зафиксируйте извлечённые уроки."),
    {}, None,
))


RISK_SPECS = [
    {
        "key": "vendor", "name": t("Hosting supplier delay", "Задержка поставщика хостинга"),
        "category": t("Supplier", "Поставщик"), "probability": 0.45,
        "description": t(
            "The hosting supplier has a capacity shortage. Environment delivery may be late and delay infrastructure work.",
            "У поставщика хостинга не хватает мощностей. Среда может быть предоставлена позже и задержать инфраструктурные работы.",
        ),
        "impact": {"effort": {"6": 16}, "cost": 1000},
        "identify": (2, 0, 9), "occur": (3, 3, 10),
        "mitigate": t("Reserve a second supplier and confirm capacity weekly", "Зарезервировать второго поставщика и еженедельно подтверждать мощности"),
        "transfer": t("Buy guaranteed capacity with a service-level penalty", "Купить гарантированные мощности со штрафом за нарушение SLA"),
        "costs": (500, 1400),
    },
    {
        "key": "scope", "name": t("Uncontrolled scope growth", "Неконтролируемый рост объёма"),
        "category": t("Scope", "Объём"), "probability": 0.35,
        "description": t(
            "Store managers are proposing extra release-one features directly to developers.",
            "Менеджеры магазинов предлагают разработчикам дополнительные функции первого релиза напрямую.",
        ),
        "impact": {"effort": {"7": 24, "8": 16}, "motivation": -3},
        "identify": (2, 1, 10), "occur": (4, 0, 11),
        "mitigate": t("Run change control and a weekly requirements review", "Ввести управление изменениями и еженедельный обзор требований"),
        "transfer": t("Agree a fixed release-one scope with the sponsor", "Согласовать со спонсором фиксированный объём первого релиза"),
        "costs": (400, 800),
    },
    {
        "key": "staffing", "name": t("Key developer leaves", "Уход ключевого разработчика"),
        "category": t("People", "Команда"), "probability": 0.25,
        "description": t(
            "A key developer has another offer. Losing context would disrupt backend delivery and team morale.",
            "Ключевой разработчик рассматривает другое предложение. Потеря знаний нарушит разработку и снизит мораль команды.",
        ),
        "impact": {"effort": {"7": 16}, "motivation": -8},
        "identify": (3, 0, 10), "occur": (4, 1, 11),
        "mitigate": t("Pair developers and document critical decisions", "Организовать парную работу и документировать ключевые решения"),
        "transfer": t("Retain an experienced freelancer as backup", "Привлечь опытного фрилансера как резерв"),
        "costs": (300, 1600),
    },
    {
        "key": "data", "name": t("Poor product data quality", "Низкое качество данных каталога"),
        "category": t("Data", "Данные"), "probability": 0.40,
        "description": t(
            "Legacy product records contain missing attributes and inconsistent stock units.",
            "В старых карточках товаров отсутствуют атрибуты и используются разные единицы остатков.",
        ),
        "impact": {"effort": {"5": 24}, "quality": -4},
        "identify": (3, 2, 9), "occur": (5, 1, 10),
        "mitigate": t("Profile and cleanse a representative data sample now", "Проанализировать и очистить репрезентативную выборку данных"),
        "transfer": t("Contract a specialist data-cleansing team", "Привлечь специалистов по очистке данных"),
        "costs": (600, 1800),
    },
    {
        "key": "privacy", "name": t("Privacy compliance gap", "Нарушение требований приватности"),
        "category": t("Compliance", "Соответствие"), "probability": 0.30,
        "description": t(
            "Customer consent and retention rules may not cover the new analytics and CRM flows.",
            "Правила согласия и хранения данных могут не покрывать новые процессы аналитики и CRM.",
        ),
        "impact": {"effort": {"16": 16}, "cost": 2500, "quality": -6},
        "identify": (4, 0, 9), "occur": (6, 2, 11),
        "mitigate": t("Run a privacy review and add consent checks", "Провести проверку приватности и добавить контроль согласий"),
        "transfer": t("Obtain an external legal and security audit", "Заказать внешний юридический аудит и аудит безопасности"),
        "costs": (700, 2000),
    },
    {
        "key": "payment", "name": t("Payment certification delay", "Задержка сертификации платежей"),
        "category": t("Supplier", "Поставщик"), "probability": 0.40,
        "description": t(
            "The payment provider has limited certification slots and may reject the first test submission.",
            "У платёжного провайдера мало окон сертификации, и первая заявка может быть отклонена.",
        ),
        "impact": {"effort": {"9": 24}, "cost": 800},
        "identify": (4, 1, 10), "occur": (6, 3, 10),
        "mitigate": t("Book a slot and run an early certification checklist", "Забронировать окно и заранее выполнить контрольный список сертификации"),
        "transfer": t("Purchase priority certification support", "Купить приоритетную поддержку сертификации"),
        "costs": (500, 1500),
    },
    {
        "key": "performance", "name": t("Storefront performance failure", "Недостаточная производительность магазина"),
        "category": t("Technical", "Технический"), "probability": 0.35,
        "description": t(
            "Peak-season traffic may exceed the capacity assumed for the storefront and integrations.",
            "Пиковый сезонный трафик может превысить расчётную мощность магазина и интеграций.",
        ),
        "impact": {"effort": {"8": 24}, "quality": -5},
        "identify": (5, 0, 9), "occur": (7, 1, 10),
        "mitigate": t("Create realistic load profiles and test early", "Подготовить реалистичные профили нагрузки и провести ранние тесты"),
        "transfer": t("Reserve scalable infrastructure and specialist support", "Зарезервировать масштабируемую инфраструктуру и поддержку специалистов"),
        "costs": (700, 1700),
    },
    {
        "key": "accessibility", "name": t("Accessibility non-compliance", "Несоответствие требованиям доступности"),
        "category": t("Compliance", "Соответствие"), "probability": 0.30,
        "description": t(
            "Keyboard navigation and contrast have not been checked against the agreed accessibility standard.",
            "Навигация с клавиатуры и контрастность ещё не проверены по согласованному стандарту доступности.",
        ),
        "impact": {"effort": {"4": 16}, "cost": 1200, "quality": -4},
        "identify": (5, 1, 10), "occur": (7, 2, 9),
        "mitigate": t("Add accessibility checks to design and testing", "Добавить проверки доступности в дизайн и тестирование"),
        "transfer": t("Commission an independent accessibility audit", "Заказать независимый аудит доступности"),
        "costs": (500, 1300),
    },
    {
        "key": "defects", "name": t("Critical defects escape testing", "Критические дефекты пропущены"),
        "category": t("Quality", "Качество"), "probability": 0.40,
        "description": t(
            "Integration coverage is incomplete, so critical order-flow defects may reach acceptance testing.",
            "Покрытие интеграционных тестов неполное, поэтому критические дефекты заказов могут попасть в приёмку.",
        ),
        "impact": {"effort": {"12": 24}, "quality": -6},
        "identify": (6, 0, 10), "occur": (7, 3, 11),
        "mitigate": t("Trace critical requirements to automated regression tests", "Связать критические требования с автоматическими регрессионными тестами"),
        "transfer": t("Add independent exploratory testing", "Привлечь независимых специалистов для исследовательского тестирования"),
        "costs": (600, 1600),
    },
    {
        "key": "infrastructure", "name": t("Infrastructure cost overrun", "Превышение расходов на инфраструктуру"),
        "category": t("Financial", "Финансовый"), "probability": 0.30,
        "description": t(
            "Traffic estimates and data-transfer charges may make the selected hosting plan too expensive.",
            "Оценки трафика и плата за передачу данных могут сделать выбранный хостинг слишком дорогим.",
        ),
        "impact": {"cost": 3500},
        "identify": (6, 1, 11), "occur": (8, 1, 10),
        "mitigate": t("Set budget alerts and load-test capacity assumptions", "Настроить бюджетные оповещения и проверить мощности нагрузочными тестами"),
        "transfer": t("Negotiate a capped-price hosting contract", "Согласовать контракт на хостинг с фиксированным пределом цены"),
        "costs": (400, 1200),
    },
    {
        "key": "burnout", "name": t("Team burnout", "Выгорание команды"),
        "category": t("People", "Команда"), "probability": 0.35,
        "description": t(
            "Sustained integration pressure and overlapping deadlines may exhaust the core team.",
            "Постоянное давление интеграции и совпадающие сроки могут истощить основную команду.",
        ),
        "impact": {"effort": {"12": 16}, "motivation": -10, "quality": -3},
        "identify": (7, 1, 10), "occur": (8, 3, 11),
        "mitigate": t("Rebalance work and protect focused recovery time", "Перераспределить работу и выделить время на восстановление"),
        "transfer": t("Bring in temporary integration support", "Привлечь временную поддержку для интеграции"),
        "costs": (500, 1800),
    },
    {
        "key": "readiness", "name": t("Operational launch unreadiness", "Операционная неготовность к запуску"),
        "category": t("Operational", "Операционный"), "probability": 0.30,
        "description": t(
            "Support procedures, monitoring, or rollback ownership may be incomplete at cutover.",
            "К переключению могут быть не готовы процедуры поддержки, мониторинг или ответственность за откат.",
        ),
        "impact": {"effort": {"23": 8}, "quality": -5},
        "identify": (7, 0, 9), "occur": (9, 1, 10),
        "mitigate": t("Run a readiness checklist and named-owner rehearsal", "Выполнить контрольный список готовности и репетицию с назначенными владельцами"),
        "transfer": t("Purchase launch-day operational support", "Купить операционную поддержку на день запуска"),
        "costs": (600, 1500),
    },
]

RISKS = []
for _r in RISK_SPECS:
    _decision_key = f"risk_{_r['key']}"
    _identify_key = f"risk_{_r['key']}_id"
    _occur_key = f"risk_{_r['key']}_occur"
    RISKS.append({
        "key": _r["key"], "name": _r["name"], "description": _r["description"],
        "category": _r["category"], "probability": _r["probability"], "impact": _r["impact"],
        "identify_event_key": _identify_key, "occurrence_event_key": _occur_key, "decision_key": _decision_key,
    })
    DECISIONS.append({
        "key": _decision_key, "default_option": "a", "deadline_hours": 8,
        "prompt": _r["description"],
        "options": [
            {
                "key": "a", "label": t("Accept the risk and monitor it", "Принять риск и наблюдать за ним"),
                "feedback": t("No response cost is incurred; the original probability and impact remain.", "Затрат на реагирование нет; исходные вероятность и влияние сохраняются."),
                "effects": {"risk_response": {"probability": 1.0, "impact": 1.0}},
                "learning_point": t("Acceptance is a deliberate response when exposure is low; monitoring is still required.", "Принятие подходит при низком риске, но наблюдение всё равно необходимо."),
            },
            {
                "key": "b", "label": _r["mitigate"],
                "feedback": t("The response reduces both the chance and the potential impact.", "Реагирование снижает и вероятность, и возможное влияние."),
                "effects": {"cost": _r["costs"][0], "risk_response": {"probability": 0.45, "impact": 0.70}},
                "learning_point": t("Early mitigation usually costs less than unmanaged impact.", "Раннее смягчение обычно дешевле последствий неуправляемого риска."),
            },
            {
                "key": "c", "label": _r["transfer"],
                "feedback": t("Specialist or contractual protection greatly reduces impact, but leaves some exposure.", "Поддержка специалистов или договорная защита сильно снижает влияние, но не устраняет риск полностью."),
                "effects": {"cost": _r["costs"][1], "risk_response": {"probability": 0.80, "impact": 0.35}},
                "learning_point": t("Transfer or specialist support reduces exposure; it does not remove the need to monitor.", "Передача риска или поддержка специалистов снижает влияние, но наблюдение остаётся необходимым."),
            },
        ],
    })
    _iw, _id, _ih = _r["identify"]
    _ow, _od, _oh = _r["occur"]
    EVENTS.extend([
        (
            _identify_key, _iw, _id, _ih, 0, "mail", t("PMO risk register", "Реестр рисков PMO"),
            t(f"Risk identified: {_r['name']['en']}", f"Выявлен риск: {_r['name']['ru']}"),
            _r["description"], {}, _decision_key,
        ),
        (
            _occur_key, _ow, _od, _oh, 0, "phone", t("PMO risk register", "Реестр рисков PMO"),
            t(f"Risk review: {_r['name']['en']}", f"Проверка риска: {_r['name']['ru']}"),
            t("The trigger review is complete. See the risk register for the outcome.", "Проверка триггера завершена. Результат доступен в реестре рисков."),
            {}, None,
        ),
    ])


def _o(key, label, feedback, effects, learning):
    return {
        "key": key, "label": t(*label), "feedback": t(*feedback), "effects": effects,
        "learning_point": t(*learning),
    }


def _d(key, prompt, options, default="a"):
    return {"key": key, "prompt": t(*prompt), "default_option": default, "options": options}


CORE_DECISIONS = [
    _d("requirements_signoff", (
        "Store managers disagree about the requirements baseline. Helen wants development to start without another workshop.",
        "Менеджеры магазинов не согласовали базовые требования. Елена хочет начать разработку без дополнительного совещания.",
    ), [
        _o("a", ("Start with the current requirements", "Начать с текущих требований"),
           ("Development starts immediately, but ambiguity is left in the UX work.", "Разработка начинается сразу, но неопределённость остаётся в UX-работе."),
           {"effort": {"2": 8}, "quality": -4},
           ("Starting fast does not remove uncertainty; it moves its cost into later work.", "Быстрый старт не устраняет неопределённость, а переносит её стоимость на следующие этапы.")),
        _o("b", ("Hold a focused requirements workshop", "Провести тематический семинар по требованиям"),
           ("The baseline is agreed after a short workshop. Rework falls and Laura's analysis costs increase.", "После короткого семинара базовые требования согласованы. Доработки сокращаются, но затраты на анализ растут."),
           {"cost": 400, "effort": {"1": 4, "2": -4}, "quality": 3},
           ("A short alignment workshop is cheaper than discovering conflicting requirements in testing.", "Короткое согласование дешевле обнаружения противоречивых требований при тестировании.")),
        _o("c", ("Document assumptions and validate them in the prototype", "Зафиксировать допущения и проверить их на прототипе"),
           ("Work continues with visible assumptions and a planned validation point.", "Работа продолжается, допущения зафиксированы, а проверка запланирована."),
           {"cost": 150, "quality": 1},
           ("Explicit assumptions are useful only when the team validates them at a concrete checkpoint.", "Допущения полезны, только если команда проверяет их в конкретной контрольной точке.")),
    ]),
    _d("hosting_choice", (
        "Three hosting options are available: a cheap shared service, a managed platform, or internal infrastructure.",
        "Доступны три варианта хостинга: дешёвый shared-хостинг, управляемая платформа или собственная инфраструктура.",
    ), [
        _o("a", ("Choose the cheap shared service", "Выбрать дешёвый shared-хостинг"),
           ("Material cost falls, but capacity limits add infrastructure work.", "Материальные затраты снижаются, но ограничения мощности добавляют инфраструктурную работу."),
           {"cost": -1000, "effort": {"6": 8}, "quality": -4},
           ("The lowest purchase price can have the highest total cost of ownership.", "Самая низкая цена покупки может означать самую высокую совокупную стоимость владения.")),
        _o("b", ("Choose the managed platform", "Выбрать управляемую платформу"),
           ("The supplier takes over routine operations, reducing infrastructure effort and improving resilience.", "Поставщик берёт на себя эксплуатацию, сокращая инфраструктурную работу и повышая надёжность."),
           {"cost": 2500, "effort": {"6": -8}, "quality": 3},
           ("Evaluate supplier cost against internal effort, resilience, and operational risk.", "Сравнивайте стоимость поставщика с внутренними работами, надёжностью и операционными рисками.")),
        _o("c", ("Use the internal infrastructure team", "Использовать внутреннюю инфраструктурную команду"),
           ("There is no supplier premium, but Victor must spend more time on setup.", "Нет наценки поставщика, но Виктору потребуется больше времени на настройку."),
           {"effort": {"6": 16}, "motivation": -2},
           ("Internal does not mean free; include scarce-team capacity in procurement decisions.", "Внутренние ресурсы не бесплатны: учитывайте ограниченную мощность команды при закупках.")),
    ]),
    _d("prototype_findings", (
        "Usability sessions show that new customers cannot find delivery information before checkout.",
        "Тестирование прототипа показало: новые клиенты не могут найти информацию о доставке до оформления заказа.",
    ), [
        _o("a", ("Keep the design and add help text later", "Оставить дизайн и позже добавить справку"),
           ("The visual plan stays unchanged, but the underlying navigation problem remains.", "Визуальный план сохранён, но проблема навигации остаётся."),
           {"effort": {"8": 16}, "quality": -6},
           ("Help text rarely repairs a flawed user journey.", "Справка редко исправляет ошибочный пользовательский сценарий.")),
        _o("b", ("Revise the prototype and retest it", "Доработать прототип и повторить тест"),
           ("Nina updates the journey and Oscar receives a clearer design.", "Нина обновляет сценарий, а Оскар получает более ясный дизайн."),
           {"cost": 600, "effort": {"2": 8, "4": 8}, "quality": 5},
           ("Prototype findings are cheapest to fix before development is complete.", "Замечания по прототипу дешевле всего исправлять до завершения разработки.")),
    ]),
    _d("accessibility_scope", (
        "Nina recommends meeting the accessibility standard in release one rather than retrofitting it after launch.",
        "Нина рекомендует выполнить стандарт доступности в первом релизе, а не после запуска.",
    ), [
        _o("a", ("Defer accessibility to a later release", "Перенести доступность на следующий релиз"),
           ("No design effort is added now, but compliance and customer-experience debt remain.", "Сейчас дополнительных дизайн-работ нет, но остаётся долг по соответствию и клиентскому опыту."),
           {"quality": -5},
           ("Deferring compliance work creates both product and regulatory exposure.", "Перенос работ по соответствию создаёт продуктовые и регуляторные риски.")),
        _o("b", ("Include accessibility in the current design", "Включить доступность в текущий дизайн"),
           ("The accessibility activity receives explicit analysis time and acceptance criteria.", "Работа по доступности получает время на анализ и критерии приёмки."),
           {"cost": 800, "effort": {"17": 16}, "quality": 4},
           ("Build accessibility into design and acceptance criteria instead of inspecting it at the end.", "Встраивайте доступность в дизайн и критерии приёмки, а не проверяйте только в конце.")),
    ]),
    _d("discount_scope", (
        "Helen asks for complex mix-and-match discounts after seeing a competitor's promotion.",
        "Увидев акцию конкурента, Елена просит добавить сложные комбинированные скидки.",
    ), [
        _o("a", ("Accept the feature to protect the sponsor relationship", "Принять функцию, чтобы сохранить отношения со спонсором"),
           ("Backend and frontend teams absorb the new rules without a baseline change.", "Команды бэкенда и фронтенда принимают новые правила без изменения базового плана."),
           {"effort": {"7": 24, "8": 16}, "motivation": -3},
           ("Sponsor support does not require bypassing scope control.", "Поддержка спонсора не требует отказа от управления объёмом.")),
        _o("b", ("Assess a formal change request", "Оценить официальный запрос на изменение"),
           ("The impact is made visible and Helen chooses a simpler promotion within the baseline.", "Влияние становится прозрачным, и Елена выбирает более простую акцию в рамках плана."),
           {"cost": 300, "quality": 2},
           ("Impact analysis turns an emotional scope debate into a business trade-off.", "Анализ влияния превращает спор об объёме в обоснованный бизнес-выбор.")),
        _o("c", ("Move the feature to the post-launch backlog", "Перенести функцию в бэклог после запуска"),
           ("Release scope is protected, though the sponsor is disappointed by the delay.", "Объём релиза защищён, но спонсор разочарован отсрочкой."),
           {"motivation": -1},
           ("A sequenced roadmap can protect the release without rejecting the business need.", "Дорожная карта позволяет защитить релиз, не отвергая потребность бизнеса.")),
    ]),
    _d("overtime_request", (
        "Backend progress is under pressure. Priya proposes weekend overtime, while Laura suggests using the freelancer.",
        "Разработка бэкенда отстаёт. Прия предлагает работу в выходные, а Лаура — привлечение фрилансера.",
    ), [
        _o("a", ("Approve weekend overtime", "Согласовать работу в выходные"),
           ("Some remaining work is completed immediately, at a visible cost to motivation and quality.", "Часть оставшейся работы выполняется сразу, но мотивация и качество снижаются."),
           {"cost": 800, "effort": {"7": -16}, "motivation": -8, "quality": -3},
           ("Overtime can buy short-term output while reducing future productivity.", "Сверхурочные дают краткосрочный результат, но могут снизить будущую производительность.")),
        _o("b", ("Buy focused freelancer support", "Привлечь фрилансера для конкретной работы"),
           ("Wendy takes a defined package and the core team keeps a sustainable pace.", "Венди берёт отдельный пакет работ, а основная команда сохраняет устойчивый темп."),
           {"cost": 1200, "effort": {"7": -16}, "motivation": 2},
           ("Adding help works best with a bounded work package and clear ownership.", "Дополнительные люди эффективны при чётко ограниченном пакете работ и ответственности.")),
        _o("c", ("Keep the pace and reforecast the remaining work", "Сохранить темп и пересмотреть прогноз"),
           ("No immediate cost is added; the schedule indexes reveal the shortfall.", "Немедленных затрат нет, а индексы сроков показывают отставание."),
           {},
           ("A forecast is a management signal, not a commitment to hide unfavourable news.", "Прогноз — это управленческий сигнал, а не способ скрыть неприятные новости.")),
    ]),
    _d("api_change", (
        "The delivery supplier releases a breaking API change. The current version will be retired before launch.",
        "Поставщик доставки выпускает несовместимую версию API. Текущая версия будет отключена до запуска.",
    ), [
        _o("a", ("Patch calls directly wherever they are used", "Исправить вызовы напрямую во всех местах"),
           ("The change is quick to start, but duplicated integration logic adds rework.", "Исправления начинаются быстро, но дублирование интеграционной логики добавляет работу."),
           {"effort": {"10": 16}, "quality": -3},
           ("A fast patch can create long-lived integration debt.", "Быстрое исправление может создать долгосрочный интеграционный долг.")),
        _o("b", ("Add an anti-corruption adapter", "Добавить изолирующий адаптер"),
           ("The adapter isolates supplier changes with moderate integration effort.", "Адаптер изолирует изменения поставщика при умеренном объёме интеграционных работ."),
           {"cost": 400, "effort": {"18": 16}, "quality": 2},
           ("An adapter protects the core system from external interface volatility.", "Адаптер защищает основную систему от изменений внешних интерфейсов.")),
        _o("c", ("Upgrade to the supplier's new managed connector", "Перейти на новый управляемый коннектор поставщика"),
           ("The supplier handles mapping updates, but certification must be repeated.", "Поставщик отвечает за обновления соответствий, но сертификацию придётся повторить."),
           {"cost": 900, "effort": {"10": 24}, "quality": 5},
           ("Managed integration shifts work to a supplier but introduces its own certification dependency.", "Управляемая интеграция передаёт работу поставщику, но добавляет зависимость от сертификации.")),
    ]),
    _d("test_automation", (
        "Tom proposes automating the order-flow regression suite instead of repeating all tests manually.",
        "Том предлагает автоматизировать регрессионные тесты заказов вместо повторных ручных проверок.",
    ), [
        _o("a", ("Continue with manual regression only", "Продолжить только ручное регрессионное тестирование"),
           ("There is no automation investment, but repetitive integration testing grows.", "Нет инвестиций в автоматизацию, но объём повторяющегося интеграционного тестирования растёт."),
           {"effort": {"12": 16}, "quality": -2},
           ("Manual-only regression becomes slower and less consistent as scope grows.", "Ручная регрессия становится медленнее и менее стабильной по мере роста объёма.")),
        _o("b", ("Automate the complete order flow", "Автоматизировать весь сценарий заказа"),
           ("A substantial test suite is built, improving repeatability and defect detection.", "Создаётся значительный набор тестов, повышающий повторяемость и обнаружение дефектов."),
           {"cost": 1000, "effort": {"20": 24}, "quality": 5},
           ("Automation has an upfront cost; prioritise stable, high-value journeys.", "Автоматизация требует вложений; выбирайте стабильные и наиболее ценные сценарии.")),
        _o("c", ("Automate only critical checkout paths", "Автоматизировать только критические сценарии оформления заказа"),
           ("A focused suite protects the highest-risk journeys with less effort.", "Небольшой набор тестов защищает самые рискованные сценарии с меньшими трудозатратами."),
           {"cost": 300, "effort": {"20": 8}, "quality": 2},
           ("Risk-based testing concentrates limited effort where failure matters most.", "Риск-ориентированное тестирование направляет ограниченные ресурсы на самые важные сбои.")),
    ]),
    _d("defect_triage", (
        "Integration testing finds two critical checkout defects and twelve cosmetic issues.",
        "Интеграционное тестирование выявило два критических дефекта оформления заказа и двенадцать косметических замечаний.",
    ), [
        _o("a", ("Fix every defect before continuing", "Исправить все дефекты до продолжения"),
           ("All findings are addressed, including low-value cosmetic work.", "Исправляются все замечания, включая малозначимые косметические работы."),
           {"effort": {"12": 32}, "quality": 6, "motivation": -3},
           ("Treating every defect equally can consume time needed for critical risks.", "Одинаковый приоритет всех дефектов может отнять время у критических рисков.")),
        _o("b", ("Fix critical defects and schedule cosmetic work", "Исправить критические дефекты и запланировать косметические"),
           ("Critical flows are repaired and lower-severity findings remain visible in the backlog.", "Критические сценарии исправлены, а менее серьёзные замечания остаются в бэклоге."),
           {"effort": {"12": 12}, "quality": 2},
           ("Triage by severity and business impact, not by the order in which defects arrived.", "Распределяйте дефекты по серьёзности и влиянию на бизнес, а не по порядку поступления.")),
        _o("c", ("Accept the defects to protect the date", "Принять дефекты ради соблюдения срока"),
           ("Testing finishes with known order-flow failures still present.", "Тестирование завершается с известными сбоями в оформлении заказа."),
           {"quality": -8},
           ("Schedule pressure does not change the customer impact of a critical defect.", "Давление сроков не меняет влияние критического дефекта на клиента.")),
    ]),
    _d("emergency_change", (
        "A store director asks Oscar to add a last-minute store-locator feature as a personal favour.",
        "Директор магазина просит Оскара внепланово добавить карту магазинов как личную услугу.",
    ), [
        _o("a", ("Let Oscar implement it between other tasks", "Позволить Оскару сделать это между задачами"),
           ("Unrecorded work interrupts frontend delivery and bypasses acceptance criteria.", "Неучтённая работа прерывает фронтенд и обходит критерии приёмки."),
           {"effort": {"8": 16}, "quality": -3},
           ("Invisible work destroys forecast accuracy and accountability.", "Невидимая работа разрушает точность прогноза и ответственность.")),
        _o("b", ("Require a change request and product-owner decision", "Требовать запрос на изменение и решение владельца продукта"),
           ("The request is evaluated openly and deferred until its value justifies the impact.", "Запрос оценивается открыто и откладывается, пока его ценность не оправдает влияние."),
           {"cost": 300, "effort": {"1": 4}, "quality": 2},
           ("All work should pass through the same governance regardless of the requester's seniority.", "Вся работа должна проходить единый процесс управления независимо от статуса инициатора.")),
    ]),
    _d("release_scope", (
        "Testing is taking longer than expected. The team must choose what to protect before the launch gate.",
        "Тестирование занимает больше времени. Перед контролем запуска нужно выбрать, что важнее защитить.",
    ), [
        _o("a", ("Protect the full scope and compress testing", "Сохранить весь объём и сократить тестирование"),
           ("The feature list stays intact while verification coverage is reduced.", "Список функций сохранён, но покрытие проверок сокращено."),
           {"effort": {"12": 16}, "quality": -4},
           ("Keeping all scope by cutting verification hides risk rather than removing it.", "Сохранение объёма за счёт проверок скрывает риск, а не устраняет его.")),
        _o("b", ("Release must-have journeys and defer optional features", "Выпустить основные сценарии и перенести дополнительные функции"),
           ("The release is simplified around customer and operational essentials.", "Релиз упрощён до основных клиентских и операционных сценариев."),
           {"effort": {"12": -16}, "quality": 3},
           ("Scope is often the most effective lever when both time and quality matter.", "Объём часто является самым эффективным рычагом, когда важны и сроки, и качество.")),
        _o("c", ("Add targeted test support", "Привлечь дополнительную тестовую поддержку"),
           ("Specialists cover the highest-risk integrations without removing features.", "Специалисты проверяют самые рискованные интеграции без исключения функций."),
           {"cost": 1000, "effort": {"12": 8}, "quality": 2},
           ("Additional testing capacity should target the remaining risk, not simply add activity.", "Дополнительные мощности тестирования должны закрывать оставшиеся риски, а не просто увеличивать активность.")),
    ]),
    _d("training_format", (
        "Store staff need training, but managers cannot release everyone for a full classroom session.",
        "Персоналу магазинов нужно обучение, но менеджеры не могут отпустить всех на полный очный курс.",
    ), [
        _o("a", ("Run compulsory after-hours classroom sessions", "Провести обязательные очные занятия после работы"),
           ("Everyone attends, but the extra hours reduce motivation.", "Все посещают занятия, но дополнительные часы снижают мотивацию."),
           {"cost": 400, "motivation": -4, "quality": 2},
           ("Training logistics are part of stakeholder and team management.", "Организация обучения — часть управления заинтересованными сторонами и командой.")),
        _o("b", ("Run short role-based sessions with local champions", "Провести короткие ролевые занятия с локальными наставниками"),
           ("Preparation takes more analysis time, while staff receive relevant hands-on practice.", "Подготовка требует больше анализа, но сотрудники получают практику по своим ролям."),
           {"effort": {"13": 8}, "quality": 5},
           ("Role-based practice and local support improve operational adoption.", "Ролевые занятия и локальная поддержка улучшают внедрение в эксплуатацию.")),
        _o("c", ("Publish a short self-service e-learning course", "Опубликовать короткий курс для самостоятельного обучения"),
           ("The course is cheap and flexible, with less individual support.", "Курс дешёв и гибок, но индивидуальной поддержки меньше."),
           {"cost": 200, "quality": 1},
           ("Match training format to task complexity and available learner support.", "Формат обучения должен соответствовать сложности задач и доступной поддержке.")),
    ]),
    _d("uat_signoff", (
        "Business users found one critical return-order defect during UAT. Helen asks you to sign anyway.",
        "Пользователи нашли критический дефект возврата заказа. Елена просит всё равно подписать приёмку.",
    ), [
        _o("a", ("Sign UAT and fix the defect after launch", "Подписать приёмку и исправить дефект после запуска"),
           ("The gate is signed, but a known critical customer issue moves into production.", "Контроль пройден, но известная критическая клиентская проблема переходит в эксплуатацию."),
           {"quality": -8},
           ("A signature does not transfer accountability for a known critical defect.", "Подпись не снимает ответственность за известный критический дефект.")),
        _o("b", ("Fix the defect and rerun the affected acceptance cases", "Исправить дефект и повторить связанные приёмочные тесты"),
           ("UAT is extended for the defect and targeted confirmation.", "Приёмка продлевается для исправления и точечной проверки."),
           {"cost": 400, "quality": 4},
           ("Retest the fix and its affected business journey before acceptance.", "До приёмки проверьте исправление и связанный бизнес-сценарий.")),
        _o("c", ("Run a full regression with business representatives", "Провести полную регрессию с представителями бизнеса"),
           ("All acceptance journeys are repeated with additional support cost.", "Все приёмочные сценарии повторяются с дополнительными затратами на поддержку."),
           {"cost": 600, "effort": {"21": 16}, "quality": 6},
           ("Full regression increases confidence but should be weighed against the change's blast radius.", "Полная регрессия повышает уверенность, но её объём должен соответствовать области влияния изменения.")),
    ]),
    _d("launch_budget", (
        "Uma can increase launch reach with paid advertising, focus on loyal customers, or retain the reserve.",
        "Ума может увеличить охват запуска платной рекламой, сосредоточиться на постоянных клиентах или сохранить резерв.",
    ), [
        _o("a", ("Fund a broad paid campaign", "Профинансировать широкую платную кампанию"),
           ("Reach increases substantially, consuming contingency before opening demand is proven.", "Охват значительно растёт, а резерв расходуется до подтверждения спроса."),
           {"cost": 2000, "motivation": 2},
           ("Marketing commitments should match launch capacity and validated demand.", "Маркетинговые обязательства должны соответствовать мощностям запуска и подтверждённому спросу.")),
        _o("b", ("Run a targeted loyalty campaign", "Провести кампанию для постоянных клиентов"),
           ("A smaller campaign targets customers most likely to try the new channel.", "Небольшая кампания нацелена на клиентов, которые вероятнее попробуют новый канал."),
           {"cost": 600, "quality": 1},
           ("A focused launch can provide useful feedback with controlled exposure.", "Адресный запуск даёт полезную обратную связь при контролируемом влиянии.")),
        _o("c", ("Cancel discretionary launch promotion", "Отменить необязательное продвижение запуска"),
           ("Reserve is retained, but the team loses an opportunity to build early adoption.", "Резерв сохранён, но команда теряет возможность стимулировать раннее внедрение."),
           {"cost": -500, "motivation": -2},
           ("Cost control includes assessing the value lost by cancelling an activity.", "Контроль затрат включает оценку ценности, потерянной при отмене работы.")),
    ]),
    _d("go_no_go", (
        "The readiness review shows a failed rollback rehearsal. Operations asks for a decision before tomorrow's launch.",
        "Проверка готовности выявила неудачную репетицию отката. Эксплуатации нужно решение перед завтрашним запуском.",
    ), [
        _o("a", ("Launch as planned and handle a rollback if needed", "Запуститься по плану и при необходимости выполнить откат"),
           ("The date is protected despite an untested recovery path.", "Дата соблюдена, несмотря на непроверенный путь восстановления."),
           {"quality": -10, "cost": 1000},
           ("Go-live readiness includes the ability to recover, not only the ability to deploy.", "Готовность к запуску включает способность восстановиться, а не только развернуть систему.")),
        _o("b", ("Use contingency to repeat the rollback rehearsal", "Использовать резерв на повторную репетицию отката"),
           ("Specialist support completes the rehearsal within the launch window.", "При поддержке специалистов репетиция завершается в пределах окна запуска."),
           {"cost": 600, "quality": 4},
           ("A failed critical rehearsal is evidence that must change the launch decision.", "Неудачная критическая репетиция — доказательство, которое должно изменить решение о запуске.")),
        _o("c", ("Use a limited launch with enhanced operational support", "Выполнить ограниченный запуск с усиленной операционной поддержкой"),
           ("Exposure is limited and specialists remain available during cutover.", "Влияние ограничено, а специалисты доступны во время переключения."),
           {"cost": 800, "quality": 1, "motivation": -2},
           ("A controlled release can reduce exposure, but it does not replace a viable rollback.", "Контролируемый релиз снижает влияние, но не заменяет работоспособный откат.")),
    ]),
    _d("hypercare", (
        "The sponsor wants normal staffing immediately after launch; operations recommends a two-week hypercare period.",
        "Спонсор хочет вернуть обычную загрузку сразу после запуска; эксплуатация рекомендует двухнедельный период усиленной поддержки.",
    ), [
        _o("a", ("Contract supplier-led hypercare", "Заказать усиленную поддержку поставщика"),
           ("Specialists monitor the launch while the internal team returns to normal work.", "Специалисты сопровождают запуск, а внутренняя команда возвращается к обычной работе."),
           {"cost": 1500, "quality": 5, "motivation": 2},
           ("Transition planning should include early-life support capacity and ownership.", "План перехода должен включать мощности и ответственность на период начальной эксплуатации.")),
        _o("b", ("Ask the core team to cover hypercare overtime", "Попросить основную команду поддерживать запуск сверхурочно"),
           ("Knowledge stays in the team, but the extended push affects motivation.", "Знания остаются в команде, но продолжительное напряжение влияет на мотивацию."),
           {"motivation": -6, "quality": 3},
           ("Using the same experts for delivery and hypercare can prolong overload.", "Использование одних экспертов для разработки и поддержки может продлить перегрузку.")),
        _o("c", ("Move directly to normal support", "Сразу перейти к обычной поддержке"),
           ("No extra cost is incurred, but operational response capacity is limited.", "Дополнительных затрат нет, но мощности операционной поддержки ограничены."),
           {"quality": -4},
           ("Project closure should follow a verified operational handover, not merely the deployment date.", "Завершение проекта должно следовать за подтверждённой передачей в эксплуатацию, а не только за датой развертывания.")),
    ]),
]
DECISIONS.extend(CORE_DECISIONS)
_CORE_BY_KEY = {d["key"]: d for d in CORE_DECISIONS}
TEAM = t("Project team", "Проектная команда")
CORE_EVENTS = [
    ("requirements_signoff", 2, 0, 11, "meeting", HELEN, t("Requirements baseline", "Базовые требования")),
    ("hosting_choice", 2, 2, 14, "phone", t("Victor, DevOps", "Виктор, DevOps"), t("Hosting procurement decision", "Решение о закупке хостинга")),
    ("prototype_findings", 3, 1, 10, "meeting", t("Nina, UX designer", "Нина, UX-дизайнер"), t("Prototype usability review", "Обзор удобства прототипа")),
    ("accessibility_scope", 3, 3, 11, "mail", t("Nina, UX designer", "Нина, UX-дизайнер"), t("Accessibility in release one", "Доступность в первом релизе")),
    ("discount_scope", 4, 1, 14, "mail", HELEN, t("Competitor promotion", "Акция конкурента")),
    ("overtime_request", 4, 3, 15, "phone", t("Priya, backend developer", "Прия, бэкенд-разработчик"), t("Backend recovery options", "Варианты восстановления бэкенда")),
    ("api_change", 5, 1, 11, "phone", t("Delivery supplier", "Поставщик доставки"), t("Breaking delivery API change", "Несовместимое изменение API доставки")),
    ("test_automation", 5, 3, 10, "mail", t("Tom, QA engineer", "Том, инженер по тестированию"), t("Regression automation proposal", "Предложение по автоматизации регрессии")),
    ("defect_triage", 6, 1, 14, "meeting", t("Tom, QA engineer", "Том, инженер по тестированию"), t("Defect triage", "Разбор дефектов")),
    ("emergency_change", 6, 3, 11, "phone", t("Oscar, frontend developer", "Оскар, фронтенд-разработчик"), t("Unofficial store-locator request", "Неофициальный запрос на карту магазинов")),
    ("release_scope", 7, 1, 14, "meeting", HELEN, t("Release scope checkpoint", "Контроль объёма релиза")),
    ("training_format", 7, 3, 10, "mail", t("Laura, business analyst", "Лаура, бизнес-аналитик"), t("Store training logistics", "Организация обучения магазинов")),
    ("uat_signoff", 8, 1, 15, "meeting", HELEN, t("UAT sign-off", "Подписание приёмки")),
    ("launch_budget", 8, 3, 10, "mail", t("Uma, marketing specialist", "Ума, маркетолог"), t("Launch campaign budget", "Бюджет кампании запуска")),
    ("go_no_go", 9, 0, 15, "meeting", HELEN, t("Go / no-go decision", "Решение о запуске")),
    ("hypercare", 9, 2, 14, "phone", t("Operations manager", "Руководитель эксплуатации"), t("Post-launch support model", "Модель поддержки после запуска")),
]
for _key, _w, _dow, _h, _channel, _sender, _subject in CORE_EVENTS:
    EVENTS.append((
        _key, _w, _dow, _h, 1 if _channel == "meeting" else 0, _channel, _sender, _subject,
        _CORE_BY_KEY[_key]["prompt"], {}, _key,
    ))
