"""Bot texts in English, Russian and Armenian.

The site is only in Russian, so Russian category names come from the site,
and English/Armenian ones from CATEGORY_NAMES below (matched by link).
"""

LANGS = {"en": "English", "ru": "Русский", "hy": "Հայերեն"}

UI = {
    "choose_lang": {"en": "🌐 Choose a language\nВыберите язык\nԸնտրեք լեզուն"},
    "welcome":     {"en": "Welcome to *HENDERSON* 🎩\nClothing, shoes and accessories.\n\nHow can we help? 👇",
                    "ru": "Добро пожаловать в *HENDERSON* 🎩\nОдежда, обувь и аксессуары.\n\nЧем можем помочь? 👇",
                    "hy": "Բարի գալուստ *HENDERSON* 🎩\nՀագուստ, կոշիկներ և աքսեսուարներ։\n\nԻնչո՞վ կարող ենք օգնել 👇"},
    "back":        {"en": "⬅️ Back", "ru": "⬅️ Назад", "hy": "⬅️ Հետ"},
    "menu":        {"en": "🏠 Menu", "ru": "🏠 Меню", "hy": "🏠 Մենյու"},
    "all":         {"en": "🛍 All", "ru": "🛍 Все", "hy": "🛍 Բոլորը"},
    "close":       {"en": "✖️ Close", "ru": "✖️ Закрыть", "hy": "✖️ Փակել"},
    "no_products": {"en": "No products 😔", "ru": "Нет товаров 😔", "hy": "Ապրանքներ չկան 😔"},
    "language":    {"en": "🌐 Language", "ru": "🌐 Язык", "hy": "🌐 Լեզու"},
    "error":       {"en": "⚠️ Site not responding. Try again.",
                    "ru": "⚠️ Сайт не отвечает. Попробуйте ещё раз.",
                    "hy": "⚠️ Կայքը չի պատասխանում։ Փորձեք կրկին։"},
}

LANG_BUTTONS = {"en": "🇬🇧 English", "ru": "🇷🇺 Русский", "hy": "🇦🇲 Հայերեն"}

GROUP_ICONS = {
    "Suits & formal wear": "🤵", "Winter clothes": "🧥", "Shirts & polos": "👔", "Trousers & jeans": "👖",
    "Sportswear": "🏃", "Shoes": "👞", "Bags": "💼", "Accessories": "🎩",
    "Home & underwear": "🏠", "Gifts": "🎁", "Unisex": "👜", "Other": "🧺",
}

# Big sections (keys are the names used in GROUPS in bot.py)
GROUP_NAMES = {
    "Suits & formal wear": {"ru": "Костюмы и классика", "hy": "Կոստյումներ և դասական հագուստ"},
    "Winter clothes":   {"ru": "Зимняя одежда", "hy": "Ձմեռային հագուստ"},
    "Shirts & polos":   {"ru": "Рубашки и поло", "hy": "Վերնաշապիկներ և պոլոներ"},
    "Trousers & jeans": {"ru": "Брюки и джинсы", "hy": "Տաբատներ և ջինսեր"},
    "Sportswear":       {"ru": "Спортивная одежда", "hy": "Սպորտային հագուստ"},
    "Shoes":            {"ru": "Обувь", "hy": "Կոշիկներ"},
    "Bags":             {"ru": "Сумки", "hy": "Պայուսակներ"},
    "Accessories":      {"ru": "Аксессуары", "hy": "Աքսեսուարներ"},
    "Home & underwear": {"ru": "Дом и бельё", "hy": "Տնային հագուստ և ներքնազգեստ"},
    "Gifts":            {"ru": "Подарки", "hy": "Նվերներ"},
    "Unisex":           {"ru": "Унисекс", "hy": "Ունիսեքս"},
    "Other":            {"ru": "Другое", "hy": "Այլ"},
}

# Site category link (after /catalog/) -> (English, Armenian)
CATEGORY_NAMES = {
    "apparel": ("Clothing", "Հագուստ"),
    "shirts": ("Shirts", "Վերնաշապիկներ"),
    "knitted-shirts": ("Knitted", "Տրիկոտաժե"),
    "straight-shirts": ("Straight fit", "Ուղիղ կտրվածքի"),
    "albini-shirts": ("Albini fabric", "Albini գործվածքից"),
    "noniron-stretch": ("Non-Iron & Stretch", "Non-Iron և Stretch"),
    "suit-separates": ("Suits", "Կոստյումներ"),
    "formal-trousers": ("Formal trousers", "Դասական տաբատներ"),
    "suit-trousers-2": ("Suit trousers", "Կոստյումի տաբատներ"),
    "polos": ("Polos", "Պոլոներ"),
    "polo-s-korotkim-rukavom": ("Short sleeve", "Կարճ թևքով"),
    "polo-s-dlinnym-rukavom": ("Long sleeve", "Երկար թևքով"),
    "t-shirts": ("T-shirts", "Շապիկներ"),
    "futbolki-s-korotkim-rukavom": ("Short sleeve", "Կարճ թևքով"),
    "futbolki-s-dlinnym-rukavom": ("Long sleeve", "Երկար թևքով"),
    "jeans": ("Jeans", "Ջինսեր"),
    "prjamye": ("Straight", "Ուղիղ"),
    "zauzhennye": ("Slim", "Նեղ"),
    "shorts": ("Shorts", "Շորտեր"),
    "plavatelnye": ("Swim", "Լողալու"),
    "kargo": ("Cargo", "Կարգո"),
    "dzhinsovye": ("Denim", "Ջինսե"),
    "knitwear": ("Knitwear", "Տրիկոտաժ"),
    "pullovers": ("Pullovers", "Պուլովերներ"),
    "turtlenecks": ("Turtlenecks", "Գոլֆեր"),
    "cardigans": ("Cardigans", "Կարդիգաններ"),
    "knitted-vests": ("Vests", "Ժիլետներ"),
    "sweatshirt": ("Sweatshirts", "Սվիտշոտներ"),
    "outerwear": ("Outerwear", "Վերնահագուստ"),
    "formal-vests-2": ("Classic", "Դասական"),
    "casual-vests": ("Casual", "Քեժուալ"),
    "blazers": ("Casual blazers", "Առօրյա պիջակներ"),
    "vests": ("Vests", "Ժիլետներ"),
    "muzhskie-bruki": ("Casual trousers", "Առօրյա տաբատներ"),
    "muzhskaya-sportivnaya-odezhda": ("Casual sport", "Առօրյա սպորտ"),
    "tolstovki-sportivnye": ("Sweatshirts", "Սվիտշոտներ"),
    "futbilki-sportivnye": ("T-shirts", "Շապիկներ"),
    "kurtki-sportivnye": ("Jackets", "Բաճկոններ"),
    "zhilety-sportivnye": ("Vests", "Ժիլետներ"),
    "domashnyya-odejda": ("Homewear", "Տնային հագուստ"),
    "futbolki-pizhamnye": ("Pyjama T-shirts", "Պիժամայի շապիկներ"),
    "brjuki-pizhamnye": ("Pyjama trousers", "Պիժամայի տաբատներ"),
    "pijamy": ("Pyjamas", "Պիժամաներ"),
    "thermal-underwear": ("Thermal underwear", "Ջերմային ներքնազգեստ"),
    "termofutbolki": ("Thermal T-shirts", "Ջերմային շապիկներ"),
    "termokalsony": ("Thermal long johns", "Ջերմային ներքնատաբատներ"),
    "muzhskoe-nizhnee-belyo": ("Underwear", "Ներքնազգեստ"),
    "majki-belevye": ("Tank tops", "Մայկաներ"),
    "futbolki-belevye": ("Undershirts", "Ներքնաշապիկներ"),
    "boxers-knit": ("Knit boxers", "Տրիկոտաժե բոքսերներ"),
    "boxers-chintz": ("Cotton boxers", "Բամբակյա բոքսերներ"),
    "boxers": ("Boxers", "Բոքսերներ"),
    "briefs": ("Briefs", "Բրիֆներ"),
    "kalsony": ("Long johns", "Ներքնատաբատներ"),
    "trusy": ("Underpants", "Վարտիքներ"),
    "kits": ("Sets", "Հավաքածուներ"),
    "socks": ("Socks", "Գուլպաներ"),
    "noski-klassicheskie": ("Classic", "Դասական"),
    "noski-sportivnye": ("Sport", "Սպորտային"),
    "chehly": ("Garment covers", "Հագուստի պատյաններ"),
    "other-accessories": ("Laundry bag", "Լվացքի տոպրակ"),
    "garment-care": ("Garment care", "Հագուստի խնամք"),
    "footwear": ("Shoes", "Կոշիկներ"),
    "muzhskie-tufli": ("Dress shoes", "Դասական կոշիկներ"),
    "derbi": ("Derby", "Դերբի"),
    "lofery": ("Loafers", "Լոֆերներ"),
    "oksfordy": ("Oxfords", "Օքսֆորդներ"),
    "monki": ("Monk straps", "Մոնքեր"),
    "brogi": ("Brogues", "Բրոգներ"),
    "krossovki": ("Trainers", "Կրոսովկաներ"),
    "slipony": ("Slip-ons", "Սլիպոններ"),
    "snikersy": ("Sneakers", "Սնիքերսներ"),
    "muzhskie-sandalii-i-shlepancy": ("Sandals & slides", "Սանդալներ և հողաթափեր"),
    "sandalii": ("Sandals", "Սանդալներ"),
    "shlepancy": ("Slides", "Հողաթափեր"),
    "muzhskie-botinki-i-sapogi": ("Boots", "Ճտքակոշիկներ"),
    "home-shoes": ("Slippers", "Տնային հողաթափեր"),
    "related-products": ("Shoe care", "Կոշիկի խնամք"),
    "sumki": ("Bags", "Պայուսակներ"),
    "briefcase": ("Briefcases", "Պորտֆելներ"),
    "rjukzaki": ("Backpacks", "Ուսապարկեր"),
    "messenger": ("Messenger bags", "Մեսենջեր պայուսակներ"),
    "roadbags": ("Travel bags", "Ճամփորդական պայուսակներ"),
    "suitcase": ("Suitcases", "Ճամպրուկներ"),
    "accessories": ("Accessories", "Աքսեսուարներ"),
    "fragrance": ("Fragrance", "Օծանելիք"),
    "ties": ("Ties", "Փողկապներ"),
    "bow-ties": ("Bow ties", "Թիթեռնիկներ"),
    "muzhskie-platki": ("Handkerchiefs", "Թաշկինակներ"),
    "pocket-squares": ("Pocket squares", "Կրծքագրպանի թաշկինակներ"),
    "cuff-links-tie-clips": ("Cufflinks & tie clips", "Թևքակոճակներ և սեղմիչներ"),
    "tie-clips": ("Tie clips", "Փողկապի սեղմիչներ"),
    "cuff-links": ("Cufflinks", "Թևքակոճակներ"),
    "bracelets": ("Bracelets", "Ապարանջաններ"),
    "glasses": ("Glasses", "Ակնոցներ"),
    "suspenders": ("Suspenders", "Տաբատակալներ"),
    "muzhskie-kluchnicy-vizitnicy-oblozhki": ("Key & card holders", "Բանալու և քարտի պատյաններ"),
    "key-holders": ("Key holders", "Բանալու պատյաններ"),
    "card-holders": ("Card holders", "Քարտապանակներ"),
    "covers": ("Document covers", "Փաստաթղթերի կազմեր"),
    "muzhskie-koshelki-portmone-i-zazhimy": ("Wallets", "Դրամապանակներ"),
    "porte-monnaie": ("Billfolds", "Պորտմոնեներ"),
    "wallets": ("Wallets", "Դրամապանակներ"),
    "portmone-dlja-dokumentov": ("Document wallets", "Փաստաթղթերի պորտմոնեներ"),
    "hats": ("Hats", "Գլխարկներ"),
    "warm-hats": ("Beanies", "Տաք գլխարկներ"),
    "kepki": ("Caps", "Կեպիներ"),
    "baseball-cap": ("Baseball caps", "Բեյսբոլկաներ"),
    "panamy": ("Bucket hats", "Պանամաներ"),
    "gloves": ("Gloves", "Ձեռնոցներ"),
    "kozhanye": ("Leather", "Կաշվե"),
    "trikotazhnye": ("Knitted", "Տրիկոտաժե"),
    "kombinirovannye": ("Mixed", "Համակցված"),
    "scarves": ("Scarves", "Շարֆեր"),
    "tolstye": ("Thick", "Հաստ"),
    "tonkie": ("Thin", "Բարակ"),
    "srednie": ("Medium", "Միջին"),
    "umbrellas": ("Umbrellas", "Անձրևանոցներ"),
    "gift-cards-am": ("Gift cards", "Նվեր քարտեր"),
    "gift-box": ("Gift wrapping", "Նվերի փաթեթավորում"),
    "malaja": ("Small", "Փոքր"),
    "srednjaja": ("Medium", "Միջին"),
    "bolshaja": ("Large", "Մեծ"),
}

# ---------- start menu ----------

MENU_BUTTONS = {
    "catalog":  {"en": "🛍 Catalog", "ru": "🛍 Каталог", "hy": "🛍 Կատալոգ"},
    "sizes":    {"en": "📏 Sizes & measuring", "ru": "📏 Размеры и замеры", "hy": "📏 Չափսեր և չափումներ"},
    "tailor":   {"en": "✂️ Tailoring & fitting", "ru": "✂️ Ателье и подгонка", "hy": "✂️ Դերձակ և հարմարեցում"},
    "mtm":      {"en": "🧵 Made-to-measure", "ru": "🧵 Пошив на заказ", "hy": "🧵 Անհատական կարում"},
    "stores":   {"en": "📍 Stores & contacts", "ru": "📍 Магазины и контакты", "hy": "📍 Խանութներ և կապ"},
    "delivery": {"en": "🚚 Delivery & returns", "ru": "🚚 Доставка и возврат", "hy": "🚚 Առաքում և վերադարձ"},
    "promo":    {"en": "🏷 Promotions", "ru": "🏷 Акции", "hy": "🏷 Ակցիաներ"},
    "search":   {"en": "🔍 Search", "ru": "🔍 Поиск", "hy": "🔍 Որոնում"},
}

# Size table is the same in every language (HTML <pre> = monospace)
SIZE_TABLE = """<pre>
RU   INT   Chest  Waist
46   S     92     80
48   M     96     84
50   L     100    88
52   XL    104    92
54   XXL   108    96
56   3XL   112    102
58   4XL   116    108
</pre>"""

# Info pages (HTML). Facts from henderson.am; size table and measuring tips are a general guide.
INFO = {
    "sizes": {
        "en": "<b>📏 Sizes & measuring</b>\n\n"
              "<b>How to measure yourself</b> (use a soft tape, over a thin shirt):\n"
              "• <b>Chest</b> – around the fullest part, under the arms\n"
              "• <b>Waist</b> – around your natural waistline\n"
              "• <b>Hips</b> – around the fullest part\n"
              "• <b>Neck</b> – around the base of the neck, plus one finger\n"
              "• <b>Sleeve</b> – from the shoulder seam to the wrist bone\n"
              "• <b>Inseam</b> – from the crotch to the ankle\n\n"
              "<b>Size table</b> (cm, approximate):" + SIZE_TABLE +
              "Not sure? Staff in any store will measure you 👌",
        "ru": "<b>📏 Размеры и замеры</b>\n\n"
              "<b>Как снять мерки</b> (мягкой лентой, поверх тонкой рубашки):\n"
              "• <b>Грудь</b> – по самой широкой части, под мышками\n"
              "• <b>Талия</b> – по естественной линии талии\n"
              "• <b>Бёдра</b> – по самой широкой части\n"
              "• <b>Шея</b> – у основания шеи, плюс один палец\n"
              "• <b>Рукав</b> – от плечевого шва до косточки запястья\n"
              "• <b>Шаговый шов</b> – от паха до щиколотки\n\n"
              "<b>Таблица размеров</b> (см, примерно):" + SIZE_TABLE +
              "Сомневаетесь? В любом салоне вас измерят 👌",
        "hy": "<b>📏 Չափսեր և չափումներ</b>\n\n"
              "<b>Ինչպես չափել</b> (փափուկ ժապավենով, բարակ վերնաշապիկի վրայից).\n"
              "• <b>Կուրծք</b> – ամենալայն մասով, թևատակերի տակով\n"
              "• <b>Գոտկատեղ</b> – բնական գոտկագծով\n"
              "• <b>Ազդրեր</b> – ամենալայն մասով\n"
              "• <b>Վիզ</b> – վզի հիմքով, գումարած մեկ մատ\n"
              "• <b>Թևք</b> – ուսի կարից մինչև դաստակի ոսկորը\n"
              "• <b>Ներքին կար</b> – աճուկից մինչև կոճը\n\n"
              "<b>Չափսերի աղյուսակ</b> (սմ, մոտավոր).\n" + SIZE_TABLE +
              "Վստահ չե՞ք։ Ցանկացած խանութում ձեզ կչափեն 👌",
    },
    "tailor": {
        "en": "<b>✂️ Tailoring & fitting</b>\n\n"
              "✅ <b>Free</b> within 30 days of purchase – with the receipt, item unworn, tags on.\n"
              "⏱ Ready in 24 hours to 7 days.\n\n"
              "<b>Services:</b>\n"
              "• hemming trousers\n• taking in / letting out the waist\n• tapering trousers\n"
              "• taking in the back (jacket, shirt)\n• lengthening or shortening sleeves\n"
              "• shortening a jacket\n• hemming a coat or raincoat\n"
              "• sewing buttons, moving a buttonhole\n• short sleeves from long (shirts)\n\n"
              "Some items have limits – ask the store staff.\n"
              "💰 Price after 30 days: ask in store.",
        "ru": "<b>✂️ Ателье и подгонка</b>\n\n"
              "✅ <b>Бесплатно</b> в течение 30 дней после покупки – с чеком, изделие не ношено, ярлыки сохранены.\n"
              "⏱ Срок: от 24 часов до 7 дней.\n\n"
              "<b>Услуги:</b>\n"
              "• подшив брюк\n• ушив / распуск брюк по талии\n• сужение брюк\n"
              "• ушив по спинке (пиджак, рубашка)\n• удлинение или укорачивание рукавов\n"
              "• укорачивание пиджака\n• подшив низа пальто или плаща\n"
              "• пришив пуговиц, перенос петли\n• короткий рукав из длинного (рубашки)\n\n"
              "У некоторых изделий есть ограничения – уточняйте в салоне.\n"
              "💰 Цена после 30 дней: уточняйте в салоне.",
        "hy": "<b>✂️ Դերձակ և հարմարեցում</b>\n\n"
              "✅ <b>Անվճար</b> գնումից 30 օրվա ընթացքում – կտրոնով, չկրած, պիտակներով։\n"
              "⏱ Պատրաստ է 24 ժամից մինչև 7 օրում։\n\n"
              "<b>Ծառայություններ.</b>\n"
              "• տաբատի ծալքի կարում\n• գոտկատեղի նեղացում / լայնացում\n• տաբատի նեղացում\n"
              "• մեջքի նեղացում (պիջակ, վերնաշապիկ)\n• թևքերի երկարացում կամ կարճացում\n"
              "• պիջակի կարճացում\n• վերարկուի կամ անձրևանոցի ծալքի կարում\n"
              "• կոճակների կարում, օղակի տեղափոխում\n• կարճ թևք երկարից (վերնաշապիկներ)\n\n"
              "Որոշ ապրանքներ ունեն սահմանափակումներ – հարցրեք խանութում։\n"
              "💰 Գինը 30 օրից հետո՝ հարցրեք խանութում։",
    },
    "mtm": {
        "en": "<b>🧵 Made-to-measure – HENDERSON Su Misura</b>\n\n"
              "Suits and shirts tailored to your measurements, from the fabric and fit you choose.\n"
              "👩 Women's made-to-measure shirts too.\n\n"
              "💰 Price and timing: ask in store.\n"
              "📞 8248 · +374 98 99 82 48",
        "ru": "<b>🧵 Пошив на заказ – HENDERSON Su Misura</b>\n\n"
              "Костюмы и рубашки по вашим меркам, из выбранной ткани и с нужной посадкой.\n"
              "👩 Также женские рубашки на заказ.\n\n"
              "💰 Цена и сроки: уточняйте в салоне.\n"
              "📞 8248 · +374 98 99 82 48",
        "hy": "<b>🧵 Անհատական կարում – HENDERSON Su Misura</b>\n\n"
              "Կոստյումներ և վերնաշապիկներ ձեր չափսերով, ձեր ընտրած գործվածքից և կտրվածքով։\n"
              "👩 Նաև կանացի վերնաշապիկներ՝ պատվերով։\n\n"
              "💰 Գինը և ժամկետը՝ հարցրեք խանութում։\n"
              "📞 8248 · +374 98 99 82 48",
    },
    "stores": {
        "en": "<b>📍 Stores in Yerevan</b>\n🕙 Daily 10:00–22:00\n\n"
              "<b>Rio Mall</b>\n8 Vahram Papazyan St, 1st floor\n📞 +37412457547\n\n"
              "<b>Sayat-Nova Avenue</b>\n8 Sayat-Nova Ave, 1st floor\n📞 +37412457548\n\n"
              "<b>Dalma Garden Mall</b>\n3 Tsitsernakaberd Hwy, 1st floor\n📞 +37412457546\n\n"
              "☎️ Hotline: 8248 · +374 98 99 82 48",
        "ru": "<b>📍 Салоны в Ереване</b>\n🕙 Ежедневно 10:00–22:00\n\n"
              "<b>ТРЦ Rio Mall</b>\nул. Ваграма Папазяна 8, 1 этаж\n📞 +37412457547\n\n"
              "<b>Проспект Саят-Нова</b>\nпр. Саят-Нова 8, 1 этаж\n📞 +37412457548\n\n"
              "<b>ТРЦ Dalma Garden Mall</b>\nЦицернакабердское шоссе 3, 1 этаж\n📞 +37412457546\n\n"
              "☎️ Горячая линия: 8248 · +374 98 99 82 48",
        "hy": "<b>📍 Խանութներ Երևանում</b>\n🕙 Ամեն օր 10:00–22:00\n\n"
              "<b>Ռիո Մոլ</b>\nՎահրամ Փափազյան փ. 8, 1-ին հարկ\n📞 +37412457547\n\n"
              "<b>Սայաթ-Նովա պողոտա</b>\nՍայաթ-Նովա պող. 8, 1-ին հարկ\n📞 +37412457548\n\n"
              "<b>Դալմա Գարդեն Մոլ</b>\nԾիծեռնակաբերդի խճ. 3, 1-ին հարկ\n📞 +37412457546\n\n"
              "☎️ Թեժ գիծ՝ 8248 · +374 98 99 82 48",
    },
    "delivery": {
        "en": "<b>🚚 Delivery & returns</b>\n\n"
              "<b>Delivery</b>\n• Free delivery of any order to Henderson stores in Armenia\n\n"
              "<b>Returns</b>\n• Within 30 days of purchase, at any store in Armenia\n"
              "• Item unworn, with tags and the receipt\n"
              "• Underwear, pyjamas and socks – only if defective\n\n"
              "<b>Guarantee</b>\n• 24 months for privilege club members (shoes – 1 year)\n"
              "• Defect in the first 30 days – return or exchange",
        "ru": "<b>🚚 Доставка и возврат</b>\n\n"
              "<b>Доставка</b>\n• Бесплатная доставка любого заказа в салоны Армении\n\n"
              "<b>Возврат</b>\n• В течение 30 дней после покупки, в любом салоне Армении\n"
              "• Изделие не ношено, с ярлыками и чеком\n"
              "• Бельё, пижамы и носки – только при браке\n\n"
              "<b>Гарантия</b>\n• 24 месяца для участников клуба привилегий (обувь – 1 год)\n"
              "• Брак в первые 30 дней – возврат или обмен",
        "hy": "<b>🚚 Առաքում և վերադարձ</b>\n\n"
              "<b>Առաքում</b>\n• Ցանկացած պատվերի անվճար առաքում Հայաստանի Henderson խանութներ\n\n"
              "<b>Վերադարձ</b>\n• Գնումից 30 օրվա ընթացքում, Հայաստանի ցանկացած խանութում\n"
              "• Չկրած, պիտակներով և կտրոնով\n"
              "• Ներքնազգեստ, պիժամաներ և գուլպաներ – միայն թերության դեպքում\n\n"
              "<b>Երաշխիք</b>\n• 24 ամիս արտոնյալ ակումբի անդամների համար (կոշիկներ – 1 տարի)\n"
              "• Թերություն առաջին 30 օրում – վերադարձ կամ փոխանակում",
    },
    "promo": {
        "en": "<b>🎁 Promotions</b>\n\n"
              "🏷 Up to 25% off when you buy 3 or more items\n"
              "👔 Oxford garment bag for 100 ֏\n\n"
              "Offers change – check details in store.",
        "ru": "<b>🎁 Акции</b>\n\n"
              "🏷 Скидка до 25% при покупке от трёх изделий\n"
              "👔 Чехол Oxford за 100 ֏\n\n"
              "Акции меняются – уточняйте условия в салоне.",
        "hy": "<b>🎁 Ակցիաներ</b>\n\n"
              "🏷 Մինչև 25% զեղչ՝ 3 և ավելի ապրանք գնելիս\n"
              "👔 Oxford պատյան՝ 100 ֏\n\n"
              "Ակցիաները փոխվում են – մանրամասները ճշտեք խանութում։",
    },
}

# ---------- ordering, reserving and calling ----------

STORES = {
    "en": ["Rio Mall", "Sayat-Nova Ave 8", "Dalma Garden Mall"],
    "ru": ["ТРЦ Rio Mall", "пр. Саят-Нова 8", "ТРЦ Dalma Garden Mall"],
    "hy": ["Ռիո Մոլ", "Սայաթ-Նովա պող. 8", "Դալմա Գարդեն Մոլ"],
}

ORDER = {
    "order_btn":   {"en": "📩 Order / Reserve", "ru": "📩 Заказать / Забронировать", "hy": "📩 Պատվիրել / Ամրագրել"},
    "call_btn":    {"en": "📞 Call", "ru": "📞 Позвонить", "hy": "📞 Զանգել"},
    "contact_btn": {"en": "📩 Contact us", "ru": "📩 Связаться с нами", "hy": "📩 Կապվել մեզ հետ"},
    "call_store":  {"en": "📞 Call the store", "ru": "📞 Позвонить в салон", "hy": "📞 Զանգել խանութ"},
    "cancel":      {"en": "✖️ Cancel", "ru": "✖️ Отмена", "hy": "✖️ Չեղարկել"},
    "ask_type":    {"en": "📩 What would you like?", "ru": "📩 Что вы хотите?", "hy": "📩 Ի՞նչ եք ցանկանում"},
    "t_order":     {"en": "🛒 Order", "ru": "🛒 Заказать", "hy": "🛒 Պատվիրել"},
    "t_reserve":   {"en": "📌 Reserve to try on", "ru": "📌 Забронировать на примерку", "hy": "📌 Ամրագրել փորձելու համար"},
    "t_fitting":   {"en": "✂️ Fitting / tailoring", "ru": "✂️ Подгонка / ателье", "hy": "✂️ Հարմարեցում / դերձակ"},
    "t_mtm":       {"en": "🧵 Made-to-measure", "ru": "🧵 Пошив на заказ", "hy": "🧵 Անհատական կարում"},
    "t_other":     {"en": "❓ Other question", "ru": "❓ Другой вопрос", "hy": "❓ Այլ հարց"},
    "ask_store":   {"en": "📍 Which store?", "ru": "📍 Какой салон?", "hy": "📍 Ո՞ր խանութը"},
    "ask_size":    {"en": "📏 Write your size (for example 50, L or 42).\nNot sure? Send -",
                    "ru": "📏 Напишите ваш размер (например 50, L или 42).\nНе знаете? Отправьте -",
                    "hy": "📏 Գրեք ձեր չափսը (օրինակ՝ 50, L կամ 42)։\nՎստահ չե՞ք։ Ուղարկեք -"},
    "ask_note":    {"en": "✍️ Write a short message (what you need, a good time to call).\nNothing to add? Send -",
                    "ru": "✍️ Напишите коротко, что нужно и когда удобно позвонить.\nНечего добавить? Отправьте -",
                    "hy": "✍️ Գրեք կարճ, ինչ է պետք և երբ է հարմար զանգել։\nԱվելացնելու բան չկա՞։ Ուղարկեք -"},
    "ask_phone":   {"en": "📱 Share your phone number with the button below, or type it.",
                    "ru": "📱 Отправьте номер телефона кнопкой ниже или напишите его.",
                    "hy": "📱 Ուղարկեք ձեր հեռախոսահամարը ներքևի կոճակով կամ գրեք այն։"},
    "share_phone": {"en": "📱 Share my phone", "ru": "📱 Отправить мой номер", "hy": "📱 Ուղարկել իմ համարը"},
    "bad_phone":   {"en": "Please send a phone number 🙏", "ru": "Пожалуйста, отправьте номер телефона 🙏",
                    "hy": "Խնդրում ենք ուղարկել հեռախոսահամար 🙏"},
    "sent":        {"en": "✅ Thank you! Your request has been sent.\nThe store will call you soon.",
                    "ru": "✅ Спасибо! Ваша заявка отправлена.\nСалон скоро вам позвонит.",
                    "hy": "✅ Շնորհակալություն։ Ձեր հայտն ուղարկված է։\nԽանութը շուտով կզանգի ձեզ։"},
    "not_sent":    {"en": "⚠️ Sorry, we couldn't send your request. Please call us:",
                    "ru": "⚠️ Не удалось отправить заявку. Пожалуйста, позвоните нам:",
                    "hy": "⚠️ Չհաջողվեց ուղարկել հայտը։ Խնդրում ենք զանգահարել մեզ."},
    "call_text":   {"en": "<b>📞 Call us</b>\n🕙 Daily 10:00–22:00\n\n"
                          "Rio Mall – +37412457547\nSayat-Nova Ave 8 – +37412457548\n"
                          "Dalma Garden Mall – +37412457546\n\n☎️ Hotline: 8248 · +374 98 99 82 48",
                    "ru": "<b>📞 Позвоните нам</b>\n🕙 Ежедневно 10:00–22:00\n\n"
                          "ТРЦ Rio Mall – +37412457547\nпр. Саят-Нова 8 – +37412457548\n"
                          "ТРЦ Dalma Garden Mall – +37412457546\n\n☎️ Горячая линия: 8248 · +374 98 99 82 48",
                    "hy": "<b>📞 Զանգահարեք մեզ</b>\n🕙 Ամեն օր 10:00–22:00\n\n"
                          "Ռիո Մոլ – +37412457547\nՍայաթ-Նովա պող. 8 – +37412457548\n"
                          "Դալմա Գարդեն Մոլ – +37412457546\n\n☎️ Թեժ գիծ՝ 8248 · +374 98 99 82 48"},
    # messages for the shop owner (admin)
    "admin_set":   {"en": "✅ Done. Order and reservation requests will come to this chat.",
                    "ru": "✅ Готово. Заявки на заказ и бронь будут приходить в этот чат.",
                    "hy": "✅ Պատրաստ է։ Պատվերի և ամրագրման հայտերը կգան այս չաթ։"},
    "admin_taken": {"en": "⛔️ Only an admin can add new admins. Ask an admin to send you an invite link.",
                    "ru": "⛔️ Добавлять админов может только админ. Попросите админа прислать вам ссылку-приглашение.",
                    "hy": "⛔️ Նոր ադմիններ կարող է ավելացնել միայն ադմինը։ Խնդրեք ադմինին ուղարկել հրավերի հղում։"},
    "new_request": {"en": "📩 New request", "ru": "📩 Новая заявка", "hy": "📩 Նոր հայտ"},
    "f_type":      {"en": "Type", "ru": "Тип", "hy": "Տեսակ"},
    "f_item":      {"en": "Item", "ru": "Товар", "hy": "Ապրանք"},
    "f_size":      {"en": "Size", "ru": "Размер", "hy": "Չափս"},
    "f_note":      {"en": "Message", "ru": "Сообщение", "hy": "Հաղորդագրություն"},
    "f_store":     {"en": "Store", "ru": "Салон", "hy": "Խանութ"},
    "f_client":    {"en": "Customer", "ru": "Клиент", "hy": "Հաճախորդ"},
    "f_phone":     {"en": "Phone", "ru": "Телефон", "hy": "Հեռախոս"},
}


# ---------- search ----------

SEARCH = {
    "prompt":  {"en": "🔍 Type what you're looking for.\nFor example: coat, jeans, belt, պայուսակ, пальто",
                "ru": "🔍 Напишите, что вы ищете.\nНапример: пальто, джинсы, ремень, coat, պայուսակ",
                "hy": "🔍 Գրեք, թե ինչ եք փնտրում։\nՕրինակ՝ վերարկու, ջինս, գոտի, coat, пальто"},
    "none":    {"en": "😔 Nothing found for “{q}”.\nTry another word or open the catalog.",
                "ru": "😔 По запросу «{q}» ничего не найдено.\nПопробуйте другое слово или откройте каталог.",
                "hy": "😔 «{q}» հարցմամբ ոչինչ չի գտնվել։\nՓորձեք այլ բառ կամ բացեք կատալոգը։"},
    "wait":    {"en": "⏳ Search is getting ready (a few minutes after a restart). Try again soon, or use the catalog.",
                "ru": "⏳ Поиск готовится (несколько минут после перезапуска). Попробуйте чуть позже или откройте каталог.",
                "hy": "⏳ Որոնումը պատրաստվում է (վերագործարկումից մի քանի րոպե անց)։ Փորձեք քիչ անց կամ բացեք կատալոգը։"},
    "again":   {"en": "🔍 New search", "ru": "🔍 Новый поиск", "hy": "🔍 Նոր որոնում"},
}

# English and Armenian words -> Russian word starts used in product names on the site
SEARCH_WORDS = {
    "coat": ["пальто", "плащ"], "raincoat": ["плащ"], "jacket": ["куртк", "пиджак"], "blazer": ["пиджак"],
    "parka": ["парк"], "down": ["пухов"], "shirt": ["рубаш"], "suit": ["костюм"], "tuxedo": ["смокинг"],
    "trousers": ["брюк"], "pants": ["брюк"], "chinos": ["чинос"], "jeans": ["джинс"], "shorts": ["шорт"],
    "t-shirt": ["футболк"], "tshirt": ["футболк"], "polo": ["поло"], "sweater": ["свитер", "пуловер", "джемпер"],
    "pullover": ["пуловер"], "jumper": ["джемпер"], "cardigan": ["кардиган"], "hoodie": ["толстовк", "худи"],
    "sweatshirt": ["толстовк", "свитшот"], "turtleneck": ["водолазк"], "vest": ["жилет"],
    "shoes": ["туфл", "обув"], "sneakers": ["кроссов", "кед", "сникер"], "trainers": ["кроссов"],
    "boots": ["ботин"], "loafers": ["лофер"], "sandals": ["сандал"], "slippers": ["тапоч", "шлепан"],
    "belt": ["ремен", "ремн"], "tie": ["галстук"], "bow tie": ["бабочк"], "socks": ["носк"],
    "underwear": ["трус", "боксер", "белье", "бельё"], "boxers": ["боксер"], "pyjamas": ["пижам"],
    "pajamas": ["пижам"], "bag": ["сумк", "портфел", "рюкзак"], "backpack": ["рюкзак"],
    "briefcase": ["портфел"], "suitcase": ["чемодан"], "wallet": ["кошел", "портмоне"],
    "scarf": ["шарф"], "gloves": ["перчат"], "hat": ["шапк", "кепк", "бейсболк", "панам"], "cap": ["кепк", "бейсболк"],
    "beanie": ["шапк"], "glasses": ["очк"], "sunglasses": ["очк"], "umbrella": ["зонт"],
    "perfume": ["парфюм", "туалетн", "вода"], "fragrance": ["парфюм", "туалетн"], "cufflinks": ["запонк"],
    "bracelet": ["браслет"], "gift card": ["подарочн"],
    "վերարկու": ["пальто"], "անձրևանոց": ["плащ", "зонт"], "բաճկոն": ["куртк"], "պիջակ": ["пиджак"],
    "վերնաշապիկ": ["рубаш"], "կոստյում": ["костюм"], "տաբատ": ["брюк"], "ջինս": ["джинс"], "շորտ": ["шорт"],
    "շապիկ": ["футболк"], "պոլո": ["поло"], "սվիտեր": ["свитер", "пуловер", "джемпер"], "ժիլետ": ["жилет"],
    "կոշիկ": ["туфл", "обув", "ботин"], "կրոսովկա": ["кроссов"], "գոտի": ["ремен", "ремн"],
    "փողկապ": ["галстук"], "գուլպա": ["носк"], "պայուսակ": ["сумк", "портфел"], "ուսապարկ": ["рюкзак"],
    "ճամպրուկ": ["чемодан"], "դրամապանակ": ["кошел", "портмоне"], "շարֆ": ["шарф"], "ձեռնոց": ["перчат"],
    "գլխարկ": ["шапк", "кепк"], "ակնոց": ["очк"], "օծանելիք": ["парфюм", "туалетн"], "պիժամա": ["пижам"],
    "black": ["black"], "white": ["white"], "navy": ["navy"], "blue": ["blue", "navy"], "grey": ["grey"],
    "gray": ["grey"], "brown": ["brown"], "beige": ["beige"], "green": ["green", "olive"],
    "red": ["red"], "burgundy": ["bordo", "burgundy"], "khaki": ["khaki"],
    # colours in Russian (word stems: "черные", "черный" and "чёрная" all start with "черн") and Armenian
    "черн": ["black"], "бел": ["white"], "син": ["navy", "blue"], "голуб": ["blue"], "сер": ["grey"],
    "коричн": ["brown"], "беж": ["beige"], "зелен": ["green", "olive"], "красн": ["red"],
    "бордо": ["bordo", "burgundy"], "хаки": ["khaki"],
    "սև": ["black"], "սպիտակ": ["white"], "կապույտ": ["navy", "blue"], "մոխրագույն": ["grey"],
    "շագանակագույն": ["brown"], "բեժ": ["beige"], "կանաչ": ["green", "olive"], "կարմիր": ["red"],
}

# ---------- live promotions ----------

PROMO = {
    "title": {"en": "🏷 Promotions", "ru": "🏷 Акции", "hy": "🏷 Ակցիաներ"},
    "until": {"en": "until", "ru": "до", "hy": "մինչև"},
    "note":  {"en": "Details in store.", "ru": "Подробности в салоне.", "hy": "Մանրամասները՝ խանութում։"},
}

# Known offers (by link on henderson.am/offers/) -> (English, Armenian). New offers show the site's Russian title.
PROMO_NAMES = {
    "discount-3pcs": ("Up to 25% off when you buy 3 or more items", "Մինչև 25% զեղչ՝ 3 և ավելի ապրանք գնելիս"),
    "welcome-coupon-am": ("7 000 ֏ gift for registering", "7 000 ֏ նվեր գրանցվելու համար"),
    "discount-socks-am": ("Up to 20% off when you buy 3+ pairs of socks",
                          "Մինչև 20% զեղչ՝ 3 և ավելի զույգ գուլպա գնելիս"),
    "garment-bag-sp": ("Oxford garment bag for 100 ֏", "Oxford պատյան՝ 100 ֏"),
}

# ---------- admins and reminders ----------

ADMIN = {
    "panel":      {"en": "👥 <b>Admins</b> – they receive all order and reservation requests:",
                   "ru": "👥 <b>Админы</b> – получают все заявки на заказ и бронь:",
                   "hy": "👥 <b>Ադմիններ</b> – ստանում են պատվերի և ամրագրման բոլոր հայտերը."},
    "invite_btn": {"en": "➕ Invite admin", "ru": "➕ Пригласить админа", "hy": "➕ Հրավիրել ադմին"},
    "leave_btn":  {"en": "🚪 Stop being admin", "ru": "🚪 Перестать быть админом", "hy": "🚪 Դադարել ադմին լինել"},
    "invite":     {"en": "➕ Send this link to the new admin. It works once, for 24 hours:\n{link}\n\n"
                         "To hand over: after they join, tap 🚪 Stop being admin.",
                   "ru": "➕ Отправьте эту ссылку новому админу. Она работает один раз, 24 часа:\n{link}\n\n"
                         "Чтобы передать права: после того как он присоединится, нажмите 🚪 Перестать быть админом.",
                   "hy": "➕ Ուղարկեք այս հղումը նոր ադմինին։ Այն գործում է մեկ անգամ, 24 ժամ.\n{link}\n\n"
                         "Իրավունքները փոխանցելու համար՝ նրա միանալուց հետո սեղմեք 🚪 Դադարել ադմին լինել։"},
    "bad_invite": {"en": "⛔️ This invite link is used or expired. Ask an admin for a new one.",
                   "ru": "⛔️ Ссылка уже использована или устарела. Попросите у админа новую.",
                   "hy": "⛔️ Հղումն արդեն օգտագործված է կամ ժամկետանց։ Խնդրեք ադմինից նորը։"},
    "joined":     {"en": "👥 {name} is now an admin and will receive requests.",
                   "ru": "👥 {name} теперь админ и будет получать заявки.",
                   "hy": "👥 {name}-ն այժմ ադմին է և կստանա հայտերը։"},
    "left":       {"en": "🚪 You're no longer an admin. Requests won't come to you.",
                   "ru": "🚪 Вы больше не админ. Заявки к вам приходить не будут.",
                   "hy": "🚪 Դուք այլևս ադմին չեք։ Հայտերը ձեզ չեն գա։"},
    "left_last":  {"en": "⚠️ There are no admins now. The next person to send /admin becomes admin.",
                   "ru": "⚠️ Сейчас нет ни одного админа. Следующий, кто отправит /admin, станет админом.",
                   "hy": "⚠️ Այժմ ոչ մի ադմին չկա։ Հաջորդը, ով կուղարկի /admin, կդառնա ադմին։"},
    "trial":      {"en": "⏰ Reminder: the Railway trial for this bot ends on {date}.\n"
                         "Open railway.com → Upgrade, otherwise the bot will stop.",
                   "ru": "⏰ Напоминание: пробный период Railway для бота заканчивается {date}.\n"
                         "Откройте railway.com → Upgrade, иначе бот остановится.",
                   "hy": "⏰ Հիշեցում. բոտի Railway փորձաշրջանն ավարտվում է {date}։\n"
                         "Բացեք railway.com → Upgrade, այլապես բոտը կդադարի աշխատել։"},
}
