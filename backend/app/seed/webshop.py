"""Original demo scenario: a tea retailer launches its first webshop in 12 weeks."""

CODE = "webshop"

SCENARIO = {
    "code": CODE,
    "title": {"en": "Webshop Launch", "ru": "Запуск интернет-магазина"},
    "description": {
        "en": (
            "Green Leaf is a family-run tea retailer with 14 stores. Before the winter season "
            "it wants to sell online. You are the project manager. The webshop must go live "
            "within 12 weeks and within budget. The plan is approved and the team is assigned. "
            "Keep cost, schedule, quality and team motivation on track, answer your mail and "
            "phone calls, and take decisions when they come up."
        ),
        "ru": (
            "«Зелёный лист» — семейная сеть чайных магазинов, 14 точек. До зимнего сезона "
            "компания хочет начать продавать онлайн. Вы — руководитель проекта. Интернет-магазин "
            "должен заработать через 12 недель и уложиться в бюджет. План утверждён, команда "
            "назначена. Держите под контролем стоимость, сроки, качество и мотивацию команды, "
            "отвечайте на письма и звонки и принимайте решения, когда они потребуются."
        ),
    },
    "weeks": 12,
    "currency": "EUR",
    "pm_rate": 90,
    "material_budget": 18000,
    "other_budget": 6000,
}

# no, en, ru, duration (working days), milestone
ACTIVITIES = [
    (1, "Kick-off & requirements", "Старт и требования", 2, False),
    (2, "UX concept", "UX-концепция", 10, False),
    (3, "System architecture", "Архитектура системы", 5, False),
    (4, "Visual design", "Визуальный дизайн", 10, False),
    (5, "Product catalogue data", "Данные каталога товаров", 15, False),
    (6, "Hosting & infrastructure", "Хостинг и инфраструктура", 5, False),
    (7, "Backend development", "Разработка бэкенда", 20, False),
    (8, "Frontend development", "Разработка фронтенда", 20, False),
    (9, "Payment integration", "Интеграция платежей", 10, False),
    (10, "Delivery integration", "Интеграция доставки", 10, False),
    (11, "Content & photos", "Контент и фото", 10, False),
    (12, "Integration testing", "Интеграционное тестирование", 8, False),
    (13, "Staff training", "Обучение персонала", 5, False),
    (14, "Launch marketing", "Маркетинг запуска", 10, False),
    (15, "Go-live", "Запуск", 1, True),
]

# activity -> predecessors
DEPENDENCIES = {
    2: [1], 3: [1], 5: [1], 4: [2], 6: [3], 7: [3], 8: [3, 4],
    9: [7], 10: [7], 11: [5], 12: [8, 9, 10], 13: [12], 14: [11], 15: [13, 14],
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
    8: {w: "other" for w in range(1, 7)},
    9: {10: "holiday"},
    10: {1: "other", 2: "other"},
    11: {w: "available" for w in range(1, 13)},
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
            "board expects the shop to go live in 12 weeks. Please keep me posted every Friday. "
            "— Helen",
            "Добро пожаловать в проект интернет-магазина! План утверждён, команда готова. Совет "
            "директоров ждёт запуска через 12 недель. Пожалуйста, держите меня в курсе каждую "
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

# Calendar beyond the demo week, so the 12-week calendar is not empty.
for _w in range(2, 13):
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
    "golive", 12, 2, 17, 2, "meeting", HELEN,
    t("Go-live party", "Праздник запуска"),
    t("Celebrate the launch with the whole team.", "Отмечаем запуск всей командой."),
    {}, None,
))
