// Long-form help text, kept out of vue-i18n so it needs no message-syntax escaping.

export const QUICK_START = {
  en: {
    title: 'How to play in 5 steps',
    steps: [
      'Look at the plan first. Budget, Gantt and Team show who works on what. The plan is ready, but it has a few traps.',
      'Press Start clock. The week runs Monday to Friday, 8:00–19:00. People work 9:00–17:00.',
      'Read every mail and phone call. Some of them ask for a decision. Answer before the deadline, or someone else decides for you.',
      'When something goes wrong (someone falls sick, a task stops), pause the clock and reassign the work.',
      'Keep Cost, Schedule, Quality and Motivation close to 100% until Friday 19:00.',
    ],
    more: 'Full guide',
    hide: 'Hide',
  },
  ru: {
    title: 'Как играть: 5 шагов',
    steps: [
      'Сначала изучите план. «Бюджет», «Гант» и «Команда» показывают, кто над чем работает. План готов, но в нём есть ловушки.',
      'Нажмите «Запустить часы». Неделя идёт с понедельника по пятницу, с 8:00 до 19:00. Люди работают с 9:00 до 17:00.',
      'Читайте все письма и звонки. Некоторые требуют решения. Ответьте до срока, иначе решат за вас.',
      'Если что-то пошло не так (кто-то заболел, задача встала), поставьте часы на паузу и переназначьте работу.',
      'Держите стоимость, сроки, качество и мотивацию около 100% до пятницы, 19:00.',
    ],
    more: 'Полное руководство',
    hide: 'Скрыть',
  },
}

export const TEAM_GUIDE = {
  en: [
    { title: 'Read the grid', text: 'Each row is a person, each column is a project week. A number in a cell is the task that person is planned on that week. Click the number to open the task.' },
    { title: 'Check availability', text: 'The cell colour shows if the person can work: white - on the project, green - available to add (e.g. a freelancer), yellow - training, red - sick, blue - holiday, grey - busy on another project. Only white and green people actually work.' },
    { title: 'Find problems', text: 'A red frame means trouble: the person is unavailable, or booked for more than 100%. Their tasks stop or slow down, and overload lowers motivation and quality. All problems are listed in "Problems to fix".' },
    { title: 'Fix them', text: 'Pause the clock. Click a task number, then replace or add a person and press Save. Or press "Resource leveling" to get an automatic proposal that you can accept or cancel.' },
  ],
  ru: [
    { title: 'Как читать таблицу', text: 'Каждая строка - сотрудник, каждый столбец - неделя проекта. Число в ячейке - задача, на которую сотрудник назначен в эту неделю. Нажмите на число, чтобы открыть задачу.' },
    { title: 'Проверьте доступность', text: 'Цвет ячейки показывает, может ли человек работать: белый - в проекте, зелёный - доступен для подключения (например, фрилансер), жёлтый - обучение, красный - болеет, голубой - отпуск, серый - занят на другом проекте. Работают только «белые» и «зелёные».' },
    { title: 'Найдите проблемы', text: 'Красная рамка - проблема: человек недоступен или загружен больше чем на 100%. Его задачи встают или замедляются, а перегрузка снижает мотивацию и качество. Все проблемы собраны в блоке «Что нужно исправить».' },
    { title: 'Исправьте их', text: 'Поставьте часы на паузу. Нажмите на номер задачи, замените или добавьте человека и нажмите «Сохранить». Или нажмите «Выравнивание ресурсов» - система предложит изменения, которые можно принять или отклонить.' },
  ],
}

export const GUIDE = {
  en: {
    title: 'How to play',
    intro: 'You are the project manager of a 12-week project. The demo plays the first week. Your job is to keep the project on budget, on time, at good quality and with a motivated team - while events keep happening.',
    sections: [
      {
        title: '1. Before you start the clock',
        items: [
          'Open Reports → Project description to read what the project is about.',
          'Open Budget: every task, its planned cost and the people assigned to it.',
          'Open Gantt: when each task is planned. Red bars are on the critical path - if they are late, the whole project is late.',
          'Open Team: check who is available each week. Red frames show conflicts in the plan. Fix the ones in the first weeks now - it is free while the clock is stopped.',
        ],
      },
      {
        title: '2. Run the week',
        items: [
          'Press Start clock (top right). One project week is Monday to Friday, 8:00–19:00. People work 9:00–17:00.',
          'At Demo speed one week takes 15 minutes. Test and Fast speeds are shorter.',
          'You can pause and resume at any time. Pausing does not cost anything.',
        ],
      },
      {
        title: '3. Mail, phone calls and decisions',
        items: [
          'New messages appear in the inbox (envelope icon). A blinking phone means a new call.',
          'Some messages ask for a decision. A window opens with 2–3 options and a deadline.',
          'After you choose, you see what happened and what it changed. Some choices add a learning point.',
          '"Later this week" postpones a decision once, until Friday 12:00.',
          'If nobody decides before the deadline, the decision is made for you - usually not in your favour.',
        ],
      },
      {
        title: '4. React to problems',
        items: [
          'Things change during the week: someone falls sick, extra work is added, people get overloaded.',
          'Pause the clock first - assignments can only be changed while it is stopped.',
          'Click any task in Budget, Gantt or Team to open it. Add or remove people and set their share (25–100%). Press Save.',
          'A task only starts when all tasks before it are finished. People assigned to a waiting task do nothing yet.',
          'Resource leveling (on the Team page) suggests who can take over work from unavailable or overloaded people.',
        ],
      },
      {
        title: '5. The four scores',
        items: [
          'Schedule - work done compared with work planned by now. Below 100% means you are behind.',
          'Cost - total budget compared with the current forecast. Extra spending and extra work lower it.',
          'Quality - goes down when people are overloaded and with some decisions; careful choices raise it.',
          'Motivation - moved by decisions and overload. Low motivation makes everybody work slower.',
          'Green is 97% and above, amber 90–97%, red below 90%.',
        ],
      },
      {
        title: '6. End of the demo',
        items: [
          'The clock stops on Friday at 19:00. You see your final scores, your decisions and your learning points.',
          'Close the summary to look around the results, or start a new simulation with other settings.',
          'Reports show how each score moved during the week.',
        ],
      },
    ],
  },
  ru: {
    title: 'Как играть',
    intro: 'Вы - руководитель 12-недельного проекта. В демо играется первая неделя. Ваша задача - удержать проект в бюджете и сроках, с хорошим качеством и мотивированной командой, пока вокруг всё время что-то происходит.',
    sections: [
      {
        title: '1. Перед запуском часов',
        items: [
          'Откройте «Отчёты» → «Описание проекта» и прочитайте, о чём проект.',
          'Откройте «Бюджет»: все задачи, их плановая стоимость и назначенные люди.',
          'Откройте «Гант»: когда запланирована каждая задача. Красные полосы - критический путь: если они опаздывают, опаздывает весь проект.',
          'Откройте «Команду»: проверьте, кто доступен в каждую неделю. Красные рамки - конфликты в плане. Исправьте те, что в первых неделях, сейчас - пока часы стоят, это бесплатно.',
        ],
      },
      {
        title: '2. Запустите неделю',
        items: [
          'Нажмите «Запустить часы» (справа вверху). Проектная неделя - с понедельника по пятницу, 8:00–19:00. Люди работают с 9:00 до 17:00.',
          'На скорости «Демо» неделя длится 15 минут. «Тест» и «Быстро» - короче.',
          'Ставить на паузу и продолжать можно в любой момент. Пауза ничего не стоит.',
        ],
      },
      {
        title: '3. Письма, звонки и решения',
        items: [
          'Новые сообщения появляются во входящих (значок конверта). Мигающий телефон - новый звонок.',
          'Некоторые сообщения требуют решения. Откроется окно с 2–3 вариантами и сроком.',
          'После выбора вы увидите, что произошло и что изменилось. Некоторые решения дают вывод для обучения.',
          '«Позже на этой неделе» один раз откладывает решение - до пятницы, 12:00.',
          'Если до срока никто не решит, решение примут за вас - обычно не в вашу пользу.',
        ],
      },
      {
        title: '4. Реагируйте на проблемы',
        items: [
          'В течение недели всё меняется: кто-то заболевает, добавляется работа, люди перегружаются.',
          'Сначала поставьте часы на паузу - назначения можно менять только когда часы стоят.',
          'Нажмите на любую задачу в «Бюджете», «Ганте» или «Команде». Добавьте или уберите людей и задайте долю (25–100%). Нажмите «Сохранить».',
          'Задача начинается, только когда завершены все предшествующие. Люди, назначенные на ожидающую задачу, пока ничего не делают.',
          '«Выравнивание ресурсов» (на странице «Команда») подскажет, кто может забрать работу у недоступных или перегруженных людей.',
        ],
      },
      {
        title: '5. Четыре показателя',
        items: [
          'Сроки - сделанная работа по сравнению с запланированной на текущий момент. Ниже 100% - вы отстаёте.',
          'Стоимость - бюджет по сравнению с текущим прогнозом. Дополнительные траты и работа снижают показатель.',
          'Качество - падает при перегрузке людей и после некоторых решений; продуманные решения его повышают.',
          'Мотивация - зависит от решений и перегрузки. При низкой мотивации все работают медленнее.',
          'Зелёный - от 97%, жёлтый - 90–97%, красный - ниже 90%.',
        ],
      },
      {
        title: '6. Конец демо',
        items: [
          'Часы останавливаются в пятницу в 19:00. Вы увидите итоговые показатели, свои решения и выводы.',
          'Закройте итог, чтобы изучить результаты, или начните новую симуляцию с другими настройками.',
          'В «Отчётах» видно, как менялся каждый показатель в течение недели.',
        ],
      },
    ],
  },
}
