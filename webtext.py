"""Chat widget texts and legal pages in English, Russian and Armenian.

Rules for the website: plain, specific wording; no emoji icons; no em dashes;
no invented numbers or reviews. Facts come from henderson.am.
"""

# Texts for the chat widget (website rules: no emoji icons, no em dashes)
WT = {
    "title":     {"en": "Henderson assistant", "ru": "Помощник Henderson", "hy": "Henderson օգնական"},
    "open":      {"en": "Chat with us", "ru": "Написать нам", "hy": "Գրել մեզ"},
    "close":     {"en": "Close", "ru": "Закрыть", "hy": "Փակել"},
    "hello":     {"en": "Hello! I can help you find clothes, check prices, choose a size or reserve an item "
                        "in a Yerevan store. Ask a question or pick an option below.",
                  "ru": "Здравствуйте! Я помогу найти одежду, узнать цены, подобрать размер или забронировать "
                        "вещь в магазине в Ереване. Задайте вопрос или выберите вариант ниже.",
                  "hy": "Բարև։ Կօգնեմ գտնել հագուստ, իմանալ գները, ընտրել չափսը կամ ամրագրել ապրանքը "
                        "Երևանի խանութում։ Հարց տվեք կամ ընտրեք տարբերակ ներքևում։"},
    "placeholder": {"en": "Type a question", "ru": "Напишите вопрос", "hy": "Գրեք հարցը"},
    "send":      {"en": "Send", "ru": "Отправить", "hy": "Ուղարկել"},
    "catalog":   {"en": "Catalog", "ru": "Каталог", "hy": "Կատալոգ"},
    "stores":    {"en": "Stores", "ru": "Магазины", "hy": "Խանութներ"},
    "promos":    {"en": "Promotions", "ru": "Акции", "hy": "Ակցիաներ"},
    "menu":      {"en": "Main options", "ru": "Главное меню", "hy": "Գլխավոր մենյու"},
    "more":      {"en": "Show more", "ru": "Показать ещё", "hy": "Ցույց տալ ավելին"},
    "view":      {"en": "View", "ru": "Смотреть", "hy": "Դիտել"},
    "reserve":   {"en": "Order", "ru": "Заказать", "hy": "Պատվիրել"},
    "reserve_msg": {"en": "I'd like to order or reserve this item: {item}",
                    "ru": "Хочу заказать или забронировать этот товар: {item}",
                    "hy": "Ուզում եմ պատվիրել կամ ամրագրել այս ապրանքը՝ {item}"},
    "typing":    {"en": "Writing...", "ru": "Печатает...", "hy": "Գրում է..."},
    "privacy":   {"en": "Privacy", "ru": "Конфиденциальность", "hy": "Գաղտնիություն"},
    "offline":   {"en": "The assistant can't answer typed questions right now. Please use the options below "
                        "or call the store.",
                  "ru": "Помощник сейчас не может отвечать на вопросы. Воспользуйтесь кнопками ниже или "
                        "позвоните в магазин.",
                  "hy": "Օգնականն այժմ չի կարող պատասխանել հարցերին։ Օգտվեք ներքևի կոճակներից կամ "
                        "զանգահարեք խանութ։"},
    "busy":      {"en": "Too many messages. Please try again a bit later or call the store.",
                  "ru": "Слишком много сообщений. Попробуйте чуть позже или позвоните в магазин.",
                  "hy": "Չափազանց շատ հաղորդագրություններ։ Փորձեք քիչ անց կամ զանգահարեք խանութ։"},
    "error":     {"en": "Something went wrong. Please try again.", "ru": "Что-то пошло не так. Попробуйте ещё раз.",
                  "hy": "Ինչ-որ բան սխալ գնաց։ Փորձեք կրկին։"},
    "new_chat":  {"en": "This chat is long. Please start a new one.", "ru": "Чат слишком длинный. Начните новый.",
                  "hy": "Չաթը շատ երկար է։ Սկսեք նորը։"},
    "restart":   {"en": "New chat", "ru": "Новый чат", "hy": "Նոր չաթ"},
}

# Legal pages. [COMPANY] and [EMAIL] must be replaced with the real details before going public.
LEGAL = {
    "privacy": {
        "en": [
            ("What we collect", "When you send a request on this site we receive the name and phone number you "
             "enter, the item, size, store and message you choose. We do not ask for payment details."),
            ("Why", "Only to answer your request: store staff use it to call you about the order, reservation "
             "or service you asked for."),
            ("Who sees it", "Your request is delivered to Henderson store staff through Telegram. We do not sell "
             "or share it with anyone else."),
            ("How long", "Requests are kept in the staff's Telegram chat for as long as needed to handle them. "
             "This site does not keep a copy."),
            ("Cookies", "We use one cookie to remember your language. There are no advertising or tracking cookies."),
            ("Your rights", "You can ask us to delete your data or tell you what we have. Contact: [EMAIL], "
             "hotline 8248."),
            ("Who we are", "This site is run by [COMPANY], Yerevan, Armenia."),
        ],
        "ru": [
            ("Какие данные мы получаем", "Когда вы отправляете заявку на сайте, мы получаем имя и номер телефона, "
             "которые вы указали, а также выбранный товар, размер, магазин и сообщение. Платёжные данные мы не "
             "запрашиваем."),
            ("Зачем", "Только чтобы ответить на заявку: сотрудники магазина звонят вам по поводу заказа, брони или "
             "услуги."),
            ("Кто их видит", "Заявка передаётся сотрудникам магазинов Henderson через Telegram. Мы не продаём и не "
             "передаём её третьим лицам."),
            ("Как долго", "Заявки хранятся в Telegram-чате сотрудников столько, сколько нужно для их обработки. "
             "Сам сайт копию не хранит."),
            ("Cookie", "Мы используем один cookie, чтобы запомнить язык. Рекламных и отслеживающих cookie нет."),
            ("Ваши права", "Вы можете попросить удалить ваши данные или узнать, какие данные у нас есть. "
             "Контакт: [EMAIL], горячая линия 8248."),
            ("Кто мы", "Сайт работает от имени [COMPANY], Ереван, Армения."),
        ],
        "hy": [
            ("Ինչ ենք ստանում", "Երբ կայքում հայտ եք ուղարկում, մենք ստանում ենք ձեր նշած անունը և "
             "հեռախոսահամարը, ինչպես նաև ընտրված ապրանքը, չափսը, խանութը և հաղորդագրությունը։ Վճարման "
             "տվյալներ չենք պահանջում։"),
            ("Ինչու", "Միայն ձեր հայտին պատասխանելու համար. խանութի աշխատակիցները զանգում են ձեզ պատվերի, "
             "ամրագրման կամ ծառայության վերաբերյալ։"),
            ("Ով է տեսնում", "Հայտը Telegram-ի միջոցով փոխանցվում է Henderson խանութների աշխատակիցներին։ Մենք "
             "այն չենք վաճառում և չենք փոխանցում այլ անձանց։"),
            ("Որքան ժամանակ", "Հայտերը պահվում են աշխատակիցների Telegram չաթում այնքան, որքան անհրաժեշտ է "
             "դրանք մշակելու համար։ Կայքն ինքը պատճեն չի պահում։"),
            ("Cookie", "Մենք օգտագործում ենք մեկ cookie՝ լեզուն հիշելու համար։ Գովազդային կամ հետևող cookie-ներ չկան։"),
            ("Ձեր իրավունքները", "Կարող եք խնդրել ջնջել ձեր տվյալները կամ իմանալ, թե ինչ տվյալներ ունենք։ "
             "Կապ՝ [EMAIL], թեժ գիծ 8248։"),
            ("Ովքեր ենք մենք", "Կայքը գործում է [COMPANY]-ի անունից, Երևան, Հայաստան։"),
        ],
    },
    "terms": {
        "en": [
            ("About this site", "This site shows the Henderson catalog with prices taken from henderson.am and "
             "lets you send an order or reservation request to a store in Yerevan."),
            ("Prices and stock", "Prices are in Armenian dram. USD and RUB amounts are approximate. Prices, sizes "
             "and stock can change; the store confirms the final price and availability by phone."),
            ("Requests", "Sending a request is not a purchase and you pay nothing on this site. The store calls "
             "you to confirm, and you pay in the store."),
            ("Reservations", "A reserved item is held in the chosen store for the time the store tells you on "
             "the phone."),
            ("Returns and guarantee", "Returns, exchanges and the guarantee follow Henderson's rules in Armenia, "
             "described on the Delivery and returns page."),
            ("Contact", "[COMPANY], Yerevan, Armenia. [EMAIL], hotline 8248."),
        ],
        "ru": [
            ("О сайте", "Сайт показывает каталог Henderson с ценами с henderson.am и позволяет отправить заявку "
             "на заказ или бронь в магазин в Ереване."),
            ("Цены и наличие", "Цены указаны в армянских драмах. Суммы в USD и RUB примерные. Цены, размеры и "
             "наличие могут меняться; окончательную цену и наличие магазин подтверждает по телефону."),
            ("Заявки", "Заявка не является покупкой, на сайте вы ничего не оплачиваете. Магазин звонит вам для "
             "подтверждения, оплата происходит в магазине."),
            ("Бронь", "Забронированная вещь хранится в выбранном магазине в течение срока, который вам назовут по "
             "телефону."),
            ("Возврат и гарантия", "Возврат, обмен и гарантия действуют по правилам Henderson в Армении, "
             "описанным на странице «Доставка и возврат»."),
            ("Контакты", "[COMPANY], Ереван, Армения. [EMAIL], горячая линия 8248."),
        ],
        "hy": [
            ("Կայքի մասին", "Կայքը ցույց է տալիս Henderson-ի կատալոգը henderson.am-ի գներով և թույլ է տալիս "
             "պատվերի կամ ամրագրման հայտ ուղարկել Երևանի խանութ։"),
            ("Գներ և առկայություն", "Գները նշված են հայկական դրամով։ USD և RUB գումարները մոտավոր են։ Գները, "
             "չափսերը և առկայությունը կարող են փոխվել. վերջնական գինը և առկայությունը խանութը հաստատում է հեռախոսով։"),
            ("Հայտեր", "Հայտն ուղարկելը գնում չէ, կայքում ոչինչ չեք վճարում։ Խանութը զանգում է հաստատելու "
             "համար, վճարումը կատարվում է խանութում։"),
            ("Ամրագրում", "Ամրագրված ապրանքը պահվում է ընտրված խանութում այն ժամկետով, որը կասեն ձեզ հեռախոսով։"),
            ("Վերադարձ և երաշխիք", "Վերադարձը, փոխանակումը և երաշխիքը գործում են Հայաստանում Henderson-ի "
             "կանոններով, որոնք նկարագրված են «Առաքում և վերադարձ» էջում։"),
            ("Կապ", "[COMPANY], Երևան, Հայաստան։ [EMAIL], թեժ գիծ 8248։"),
        ],
    },
}
