"""Henderson shop Telegram bot. Uses only the Python standard library.

Categories and products are read live from https://henderson.am
Run:  python3 bot.py
"""
import html as htmllib
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.request
import uuid

from translations import (CATEGORY_NAMES, GROUP_ICONS, GROUP_NAMES, INFO, LANG_BUTTONS, LANGS, MENU_BUTTONS,
                          ORDER, STORES, UI)

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://henderson.am"
# Photo on the start page: Henderson logo and name
WELCOME_PHOTO = os.path.join(HERE, "welcome.png")
CACHE_SECONDS = 1800  # how long to keep site data before reloading


def load_token():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        with open(os.path.join(HERE, ".env")) as f:
            for line in f:
                if line.startswith("BOT_TOKEN="):
                    token = line.split("=", 1)[1].strip()
    # forgive paste mistakes: spaces, quotes, or "BOT_TOKEN=" pasted into the value
    token = (token or "").strip().strip("'\"").strip()
    if token.startswith("BOT_TOKEN="):
        token = token.split("=", 1)[1].strip().strip("'\"")
    return token


API = f"https://api.telegram.org/bot{load_token()}/"

# certs.pem = macOS trusted certificates, exported with:
#   security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain > certs.pem
CERTS = os.path.join(HERE, "certs.pem")
SSL_CTX = ssl.create_default_context(cafile=CERTS if os.path.exists(CERTS) else None)


# ---------- Telegram ----------

def call(method, params=None, timeout=60, upload=None):
    """Call a Telegram method. upload=(field, path) sends a local file."""
    if upload:
        boundary = uuid.uuid4().hex
        body = b""
        for key, value in (params or {}).items():
            value = value if isinstance(value, str) else json.dumps(value)
            body += (f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n'
                     f"{value}\r\n").encode()
        field, path = upload
        with open(path, "rb") as f:
            body += (f'--{boundary}\r\nContent-Disposition: form-data; name="{field}"; '
                     f'filename="{os.path.basename(path)}"\r\n\r\n').encode() + f.read()
        body += f"\r\n--{boundary}--\r\n".encode()
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    else:
        body = json.dumps(params or {}).encode()
        headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(API + method, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
            return json.load(resp).get("result")
    except urllib.error.HTTPError as e:
        error = e.read().decode()
        if "message is not modified" in error:  # tapped to the same product again
            return True
        print(f"Telegram error in {method}: {error}")
        return None


sent = {}  # chat_id -> ids of messages on the current page


def post(chat_id, method, params, upload=None):
    """Send a message and remember it so the next page can delete it."""
    msg = call(method, {"chat_id": chat_id, **params}, upload=upload)
    if msg:
        sent.setdefault(chat_id, []).append(msg["message_id"])
    return msg


def clear_page(chat_id, extra_id=None):
    """Delete every message from the previous page."""
    ids = sent.pop(chat_id, [])
    if extra_id and extra_id not in ids:
        ids.append(extra_id)
    for i in range(0, len(ids), 100):  # Telegram allows 100 per call
        call("deleteMessages", {"chat_id": chat_id, "message_ids": ids[i:i + 100]})


# ---------- henderson.am ----------

_cache = {}  # url -> (time, page)


def fetch_raw(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as resp:
        return resp.read().decode("utf-8", "replace")


def fetch(url):
    hit = _cache.get(url)
    if hit and time.time() - hit[0] < CACHE_SECONDS:
        return hit[1]
    page = fetch_raw(url)
    _cache[url] = (time.time(), page)
    return page


menu = {"time": 0, "nodes": []}  # nodes[i] = {"title", "link", "children": [ids], "parent"}


def load_menu():
    """Read the category tree from the site's own menu."""
    if menu["nodes"] and time.time() - menu["time"] < CACHE_SECONDS:
        return menu["nodes"]
    page = fetch(SITE + "/")
    data = json.loads(re.search(r'id="__NUXT_DATA__"[^>]*>(.*?)</script>', page, re.S).group(1))

    def r(i):
        v = data[i]
        if isinstance(v, list) and v and isinstance(v[0], str) and v[0] in (
                "Reactive", "ShallowReactive", "Ref", "ShallowRef"):
            return r(v[1])
        return v

    def is_node(v):
        return isinstance(v, dict) and {"title", "link", "children"} <= set(v)

    # The top menu is the list of nodes that contains "Одежда" (Clothing)
    top = next(v for v in data if isinstance(v, list) and v and all(isinstance(x, int) for x in v)
               and all(is_node(r(x)) for x in v) and any(r(r(x)["title"]) == "Одежда" for x in v))

    nodes = []

    def add(i, parent):
        n = r(i)
        node_id = len(nodes)
        nodes.append({"title": str(r(n["title"])).strip(), "link": r(n["link"]),
                      "children": [], "parent": parent})
        kids = r(n["children"])
        if isinstance(kids, dict):  # grouped like {"Main": [...]}
            kids = [k for group in kids.values() for k in (r(group) or [])]
        for k in kids or []:
            child = add(k, node_id)
            # skip a child that just repeats its parent (its "All" button covers it)
            if nodes[child]["link"].rstrip("/") == nodes[node_id]["link"].rstrip("/"):
                del nodes[child:]
            else:
                nodes[node_id]["children"].append(child)
        return node_id

    for x in top:
        add(x, None)
    menu.update(time=time.time(), nodes=nodes)
    return nodes


def load_products(link):
    page = fetch(SITE + link)
    products = []
    for card in page.split('class="productCart"')[1:]:
        url = re.search(r'href="(/product/[^"]+)"', card)
        name = re.search(r'itemprop="name" content="([^"]+)"', card)
        price = re.search(r'itemprop="price" content="(\d+)"', card)
        photo = re.search(r'<img src="([^"]+)"', card)
        color = re.search(r'itemprop="color" content="([^"]+)"', card)
        if url and name:
            products.append({
                "name": htmllib.unescape(name.group(1)).strip(),
                "amd": int(price.group(1)) if price else 0,
                "price": f"{int(price.group(1)):,} ֏".replace(",", " ") if price else "",
                "photo": photo.group(1) if photo else "",
                "color": htmllib.unescape(color.group(1)).strip().lower() if color else "",
                "url": SITE + url.group(1),
            })
    return products


# ---------- big groups ----------

# Each group lists site categories by their link. "+link" means "all subcategories of link".
# Site categories not listed anywhere go to "Other" automatically.
GROUPS = [
    ("Suits", ["/catalog/suit-separates", "/catalog/blazers", "/catalog/vests",
                 "/catalog/formal-trousers", "/catalog/ties", "/catalog/bow-ties",
                 "/catalog/cuff-links-tie-clips"]),
    ("Winter clothes", ["/catalog/outerwear", "/catalog/knitwear", "/catalog/thermal-underwear",
                          "/catalog/warm-hats", "/catalog/gloves", "/catalog/scarves"]),
    ("Shirts & polos", ["/catalog/shirts", "/catalog/polos", "/catalog/t-shirts"]),
    ("Trousers & jeans", ["/catalog/muzhskie-bruki", "/catalog/jeans", "/catalog/shorts"]),
    ("Sportswear", ["+/catalog/muzhskaya-sportivnaya-odezhda"]),
    ("Shoes", ["+/catalog/footwear"]),
    ("Bags", ["+/catalog/sumki"]),
    ("Accessories", ["+/catalog/accessories"]),
    ("Home & underwear", ["/catalog/domashnyya-odejda", "/catalog/pijamy",
                            "/catalog/muzhskoe-nizhnee-belyo", "/catalog/socks"]),
]


def load_groups():
    """Turn GROUPS into [(title, [node ids])] using the current site menu."""
    nodes = load_menu()
    by_link = {}
    for i, n in enumerate(nodes):
        by_link.setdefault(n["link"].rstrip("/"), i)

    groups, used = [], set()
    for title, links in GROUPS:
        ids = []
        for link in links:
            i = by_link.get(link.lstrip("+").rstrip("/"))
            if i is None:
                continue
            found = nodes[i]["children"] if link.startswith("+") else [i]
            used.update(nodes[k]["link"].rstrip("/") for k in found + [i])
            ids += [k for k in found if k not in ids]
        if ids:
            groups.append((title, ids))

    # Anything in the main sections that no group covers
    other = [k for i, n in enumerate(nodes) if n["parent"] is None
             for k in n["children"] if nodes[k]["link"].rstrip("/") not in used]
    if other:
        groups.append(("Other", other))
    return groups


def group_of(node_id):
    """Index of the first group that lists this category directly, or None."""
    for gi, (_, ids) in enumerate(load_groups()):
        if node_id in ids:
            return gi
    return None


def back_from(node_id):
    """Where "Back" goes from a category: its group, or its parent category."""
    gi = group_of(node_id)
    if gi is not None:
        return f"g:{gi}"
    parent = load_menu()[node_id]["parent"]
    return "men" if parent is None else f"c:{parent}"


def category_buttons(ids, lang):
    # A category with subcategories opens them; otherwise it shows its clothes
    nodes = load_menu()
    buttons = [{"text": node_name(k, lang),
                "callback_data": f"c:{k}" if nodes[k]["children"] else f"p:{k}:0"} for k in ids]
    return [buttons[i:i + 2] for i in range(0, len(buttons), 2)]


# ---------- languages ----------

# Saved data lives in DATA_DIR (on the server: a permanent volume), otherwise next to bot.py
DATA_DIR = os.environ.get("DATA_DIR", HERE)
LANG_FILE = os.path.join(DATA_DIR, "langs.json")  # chat_id -> "en" / "ru" / "hy"
try:
    with open(LANG_FILE) as f:
        langs = json.load(f)
except (OSError, ValueError):
    langs = {}


def lang_of(chat_id):
    return langs.get(str(chat_id))


def set_lang(chat_id, lang):
    langs[str(chat_id)] = lang
    with open(LANG_FILE, "w") as f:
        json.dump(langs, f)


def t(key, lang):
    return UI[key].get(lang) or UI[key]["en"]


def group_name(title, lang):
    name = title if lang == "en" else GROUP_NAMES.get(title, {}).get(lang, title)
    return f"{GROUP_ICONS[title]} {name}" if title in GROUP_ICONS else name


def node_name(node_id, lang):
    """Category name in the chosen language (the site itself is in Russian)."""
    node = load_menu()[node_id]
    names = CATEGORY_NAMES.get(node["link"].rstrip("/").split("/")[-1])
    if lang == "ru" or not names:
        return node["title"]
    return names[0] if lang == "en" else names[1]


# ---------- prices in USD and RUB ----------

rates = {"time": 0, "USD": None, "RUB": None}


def other_prices(amd):
    """'≈ $455 · ≈ 36 500 ₽' using today's rates, or '' if rates are unavailable."""
    if time.time() - rates["time"] > 12 * 3600:
        try:
            data = json.loads(fetch_raw("https://open.er-api.com/v6/latest/AMD"))
            rates.update(time=time.time(), USD=data["rates"]["USD"], RUB=data["rates"]["RUB"])
        except Exception as e:
            print("Exchange rates unavailable:", e)
            rates["time"] = time.time() - 11 * 3600  # try again in an hour
    if not amd or not rates["USD"]:
        return ""
    usd = round(amd * rates["USD"])
    rub = round(amd * rates["RUB"], -1)
    return f"≈ ${usd:,} · ≈ {rub:,.0f} ₽".replace(",", " ")


# ---------- screens ----------

welcome = {"file_id": None}


def send_logo(chat_id, caption, rows):
    """Send the logo photo with buttons (upload once, then reuse Telegram's copy)."""
    params = {"caption": caption, "parse_mode": "Markdown", "reply_markup": {"inline_keyboard": rows}}
    if welcome["file_id"]:
        msg = post(chat_id, "sendPhoto", {**params, "photo": welcome["file_id"]})
    elif os.path.exists(WELCOME_PHOTO):
        msg = post(chat_id, "sendPhoto", params, upload=("photo", WELCOME_PHOTO))
        if msg:
            welcome["file_id"] = msg["photo"][-1]["file_id"]
    else:
        msg = None
    if not msg:
        params["text"] = params.pop("caption")
        post(chat_id, "sendMessage", params)  # photo failed: text only


def send_languages(chat_id):
    send_logo(chat_id, t("choose_lang", "en"),
              [[{"text": LANG_BUTTONS[code], "callback_data": f"L:{code}"} for code in LANGS]])


def send_menu(chat_id, lang):
    def b(key, data):
        return {"text": MENU_BUTTONS[key][lang], "callback_data": data}
    send_logo(chat_id, t("welcome", lang), [
        [b("catalog", "men")],
        [b("sizes", "i:sizes"), b("tailor", "i:tailor")],
        [b("mtm", "i:mtm"), b("stores", "i:stores")],
        [b("delivery", "i:delivery"), b("promo", "i:promo")],
        [{"text": o("contact_btn", lang), "callback_data": "o"},
         {"text": o("call_store", lang), "callback_data": "call"}],
        [{"text": t("language", lang), "callback_data": "lang"}],
    ])


def send_info(chat_id, key, lang):
    """One of the info pages: sizes, tailoring, made-to-measure, stores, delivery, promotions."""
    post(chat_id, "sendMessage", {
        "text": INFO[key][lang], "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": [[{"text": t("back", lang), "callback_data": "menu"}]]},
    })


def send_men(chat_id, lang):
    buttons = [{"text": group_name(title, lang), "callback_data": f"g:{gi}"}
               for gi, (title, _) in enumerate(load_groups())]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    rows.append([{"text": t("back", lang), "callback_data": "menu"}])
    post(chat_id, "sendMessage", {"text": f"*{MENU_BUTTONS['catalog'][lang]}*", "parse_mode": "Markdown",
                                  "reply_markup": {"inline_keyboard": rows}})


def send_group(chat_id, gi, lang):
    title, ids = load_groups()[gi]
    rows = category_buttons(ids, lang)
    rows.append([{"text": t("back", lang), "callback_data": "men"},
                 {"text": t("menu", lang), "callback_data": "menu"}])
    post(chat_id, "sendMessage", {"text": f"*{group_name(title, lang)}*", "parse_mode": "Markdown",
                                  "reply_markup": {"inline_keyboard": rows}})


def send_category(chat_id, node_id, lang):
    """Show the subcategories of a site category."""
    node = load_menu()[node_id]
    rows = [[{"text": t("all", lang), "callback_data": f"p:{node_id}:0"}]]
    rows += category_buttons(node["children"], lang)
    rows.append([{"text": t("back", lang), "callback_data": back_from(node_id)},
                 {"text": t("menu", lang), "callback_data": "menu"}])
    post(chat_id, "sendMessage", {"text": f"*{node_name(node_id, lang)}*",
                                  "parse_mode": "Markdown", "reply_markup": {"inline_keyboard": rows}})


def send_products(chat_id, node_id, index, lang, card=None):
    """Show one product with < > buttons. card = the product message to update in place."""
    node = load_menu()[node_id]
    items = load_products(node["link"])
    # "Back" from an "All" page goes to the category itself, otherwise to its group or parent
    back = f"c:{node_id}" if node["children"] else back_from(node_id)
    nav = [{"text": t("back", lang), "callback_data": back},
           {"text": t("menu", lang), "callback_data": "menu"}]
    if not items:
        post(chat_id, "sendMessage", {
            "text": f"*{node_name(node_id, lang)}*\n\n{t('no_products', lang)}", "parse_mode": "Markdown",
            "reply_markup": {"inline_keyboard": [nav]}})
        return

    index %= len(items)  # wrap around at both ends
    item = items[index]
    extra = other_prices(item["amd"])
    caption = (f"<b>{htmllib.escape(item['name'])}</b>\n"
               + (f"🎨 {htmllib.escape(item['color'])}\n" if item["color"] else "")
               + "💰 " + item["price"] + (f"  <i>{extra}</i>" if extra else ""))
    buttons = {"inline_keyboard": [
        [{"text": "<", "callback_data": f"p:{node_id}:{index - 1}"},
         {"text": f"{index + 1} / {len(items)} 📋", "callback_data": f"l:{node_id}:{index}"},
         {"text": ">", "callback_data": f"p:{node_id}:{index + 1}"}],
        [{"text": o("order_btn", lang), "callback_data": f"o:{node_id}:{index}"},
         {"text": o("call_btn", lang), "callback_data": "call:p"}],
        nav,
    ]}

    if card and item["photo"] and call("editMessageMedia", {
            "chat_id": chat_id, "message_id": card,
            "media": {"type": "photo", "media": item["photo"], "caption": caption, "parse_mode": "HTML"},
            "reply_markup": buttons}):
        return

    clear_page(chat_id, card)
    params = {"caption": caption, "parse_mode": "HTML", "reply_markup": buttons}
    if item["photo"] and post(chat_id, "sendPhoto", {**params, "photo": item["photo"]}):
        return
    params["text"] = params.pop("caption")
    post(chat_id, "sendMessage", params)


def send_list(chat_id, node_id, current, card, lang):
    """Turn the product card's buttons into a numbered list of all products."""
    items = load_products(load_menu()[node_id]["link"])
    rows = []
    for i, item in enumerate(items):
        name = item["name"] if len(item["name"]) <= 24 else item["name"][:23] + "…"
        if item["color"]:
            name += f" ({item['color']})"
        mark = "👉 " if i == current else ""
        rows.append([{"text": f"{mark}{i + 1}. {name}", "callback_data": f"p:{node_id}:{i}"}])
    rows.append([{"text": t("close", lang), "callback_data": f"p:{node_id}:{current}"}])
    call("editMessageReplyMarkup", {"chat_id": chat_id, "message_id": card,
                                    "reply_markup": {"inline_keyboard": rows}})


# ---------- ordering, reserving and calling ----------

ADMIN_FILE = os.path.join(DATA_DIR, "admin.json")  # the chat that receives requests


def o(key, lang):
    return ORDER[key].get(lang) or ORDER[key]["en"]


def load_admin():
    try:
        with open(ADMIN_FILE) as f:
            return json.load(f).get("chat_id")
    except (OSError, ValueError):
        # On the server the admin chat can also be set with the ADMIN_CHAT_ID variable
        admin = os.environ.get("ADMIN_CHAT_ID", "")
        return int(admin) if admin.lstrip("-").isdigit() else None


def set_admin(chat_id, lang):
    """/admin: the first chat to send it receives all requests."""
    admin = load_admin()
    if admin and admin != chat_id:
        post(chat_id, "sendMessage", {"text": o("admin_taken", lang)})
        return
    with open(ADMIN_FILE, "w") as f:
        json.dump({"chat_id": chat_id}, f)
    print("Admin chat saved")
    post(chat_id, "sendMessage", {"text": o("admin_set", lang)})


orders = {}  # chat_id -> request being filled in: {"step", "item", "type", "store", "note"}


def cancel_row(lang):
    return [{"text": o("cancel", lang), "callback_data": "ox"}]


def send_call(chat_id, lang, back="menu"):
    post(chat_id, "sendMessage", {
        "text": o("call_text", lang), "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": [[{"text": t("back", lang), "callback_data": back}]]}})


def start_order(chat_id, lang, node_id=None, index=None):
    """Step 1: what kind of request. From a product card, the product is attached."""
    item = None
    if node_id is not None:
        items = load_products(load_menu()[node_id]["link"])
        item = items[index % len(items)] if items else None
    orders[chat_id] = {"step": "type", "item": item}
    kinds = ["t_order", "t_reserve"] if item else ["t_order", "t_reserve", "t_fitting", "t_mtm", "t_other"]
    rows = [[{"text": o(k, lang), "callback_data": f"ot:{k}"}] for k in kinds]
    post(chat_id, "sendMessage", {"text": o("ask_type", lang),
                                  "reply_markup": {"inline_keyboard": rows + [cancel_row(lang)]}})


def ask_store(chat_id, lang, kind):
    """Step 2: which store."""
    orders[chat_id].update(step="store", type=kind)
    rows = [[{"text": f"📍 {name}", "callback_data": f"os:{i}"}] for i, name in enumerate(STORES[lang])]
    post(chat_id, "sendMessage", {"text": o("ask_store", lang),
                                  "reply_markup": {"inline_keyboard": rows + [cancel_row(lang)]}})


def ask_note(chat_id, lang, store):
    """Step 3: size (for a product) or a short message (general request)."""
    order = orders[chat_id]
    order.update(step="note", store=store)
    post(chat_id, "sendMessage", {"text": o("ask_size" if order["item"] else "ask_note", lang),
                                  "reply_markup": {"inline_keyboard": [cancel_row(lang)]}})


def ask_phone(chat_id, lang, note):
    """Step 4: phone number (button shares the Telegram contact)."""
    orders[chat_id].update(step="phone", note="" if note.strip() == "-" else note.strip())
    post(chat_id, "sendMessage", {"text": o("ask_phone", lang), "reply_markup": {
        "keyboard": [[{"text": o("share_phone", lang), "request_contact": True}],
                     [{"text": o("cancel", lang)}]],
        "resize_keyboard": True, "one_time_keyboard": True}})


def finish_order(chat_id, lang, phone, user):
    """Send the request to the admin chat and thank the customer."""
    order = orders.pop(chat_id)
    admin = load_admin()
    sent = False
    if admin:
        al = lang_of(admin) or "en"
        item = order["item"]
        name = " ".join(filter(None, [user.get("first_name"), user.get("last_name")]))
        if user.get("username"):
            name += f" (@{user['username']})"
        lines = [f"<b>{o('new_request', al)}</b>",
                 f"{o('f_type', al)}: {o(order['type'], al)}"]
        if item:
            lines.append(f"{o('f_item', al)}: {htmllib.escape(item['name'])}"
                         + (f" ({htmllib.escape(item['color'])})" if item["color"] else "")
                         + f" – {item['price']}\n{item['url']}")
        if order["note"]:
            label = o("f_size", al) if item else o("f_note", al)
            lines.append(f"{label}: {htmllib.escape(order['note'])}")
        lines += [f"{o('f_store', al)}: {STORES[al][order['store']]}",
                  f"{o('f_client', al)}: {htmllib.escape(name)}",
                  f"{o('f_phone', al)}: {htmllib.escape(phone)}"]
        text = "\n".join(lines)
        if item and item["photo"]:
            sent = bool(call("sendPhoto", {"chat_id": admin, "photo": item["photo"],
                                           "caption": text, "parse_mode": "HTML"}))
        if not sent:
            sent = bool(call("sendMessage", {"chat_id": admin, "text": text, "parse_mode": "HTML"}))
        print("Order: request sent to admin" if sent else "Order: sending to admin FAILED")
    else:
        print("No admin chat yet: send /admin to the bot to receive requests")

    # Confirmation also removes the phone keyboard
    post(chat_id, "sendMessage", {"text": o("sent", lang) if sent else o("not_sent", lang),
                                  "reply_markup": {"remove_keyboard": True}})
    if not sent:
        send_call(chat_id, lang)
    send_menu(chat_id, lang)


def cancel_order(chat_id, lang):
    if orders.pop(chat_id, None):
        post(chat_id, "sendMessage", {"text": o("cancel", lang), "reply_markup": {"remove_keyboard": True}})


def handle_order_message(chat_id, lang, msg):
    """Typed answers during an order. Returns True if the message was used."""
    order = orders.get(chat_id)
    if not order:
        return False
    text = msg.get("text", "")
    if text == o("cancel", lang):
        cancel_order(chat_id, lang)
        send_menu(chat_id, lang)
    elif order["step"] == "note" and text:
        print("Order: size/message received")
        ask_phone(chat_id, lang, text)
    elif order["step"] == "phone":
        phone = (msg.get("contact") or {}).get("phone_number") or text
        if sum(ch.isdigit() for ch in phone) >= 6:
            print("Order: phone received")
            finish_order(chat_id, lang, phone, msg.get("from", {}))
        else:
            print("Order: not a phone number, asking again")
            post(chat_id, "sendMessage", {"text": o("bad_phone", lang)})
    else:
        return False
    return True


def handle(update):
    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        lang = lang_of(chat_id)
        if msg.get("text", "").startswith("/admin"):
            set_admin(chat_id, lang or "en")
            return
        if lang and handle_order_message(chat_id, lang, msg):
            return
        orders.pop(chat_id, None)
        clear_page(chat_id)
        send_menu(chat_id, lang) if lang else send_languages(chat_id)
    elif "callback_query" in update:
        q = update["callback_query"]
        call("answerCallbackQuery", {"callback_query_id": q["id"]})
        data = q.get("data", "")
        chat_id = q["message"]["chat"]["id"]
        message_id = q["message"]["message_id"]
        if data == "noop":
            return
        if data.startswith("L:") and data[2:] in LANGS:
            set_lang(chat_id, data[2:])
            data = "menu"
        lang = lang_of(chat_id)
        if not lang:  # no language chosen yet
            clear_page(chat_id, message_id)
            send_languages(chat_id)
            return
        try:
            # Ordering steps: keep the product card, add the questions below it
            if data == "o" or data.startswith("o:"):
                orders.pop(chat_id, None)  # start over if one was in progress
                if data == "o":
                    clear_page(chat_id, message_id)
                    start_order(chat_id, lang)
                else:
                    _, node_id, index = data.split(":")
                    start_order(chat_id, lang, int(node_id), int(index))
                return
            if data.startswith(("ot:", "os:")) and chat_id in orders:
                call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})
                if data.startswith("ot:"):
                    ask_store(chat_id, lang, data[3:])
                else:
                    ask_note(chat_id, lang, int(data[3:]))
                return
            if data == "ox":
                call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})
                order = orders.pop(chat_id, None)
                if not (order and order["item"]):  # general request: nothing left on screen
                    clear_page(chat_id)
                    send_menu(chat_id, lang)
                return
            if data == "call:p":  # from a product card: show phones under it
                post(chat_id, "sendMessage", {
                    "text": o("call_text", lang), "parse_mode": "HTML",
                    "reply_markup": {"inline_keyboard": [[{"text": t("close", lang), "callback_data": "x"}]]}})
                return
            if data == "x":
                call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})
                return
            # Middle button: show the list of products on the same message
            if data.startswith("l:"):
                _, node_id, index = data.split(":")
                send_list(chat_id, int(node_id), int(index), message_id, lang)
                return
            # < and > on a product card update that same message
            if data.startswith("p:") and "photo" in q["message"]:
                _, node_id, index = data.split(":")
                send_products(chat_id, int(node_id), int(index), lang, card=message_id)
                return
            # New page: remove everything from the last one
            clear_page(chat_id, message_id)
            if data == "menu":
                send_menu(chat_id, lang)
            elif data == "lang":
                send_languages(chat_id)
            elif data == "call":
                send_call(chat_id, lang)
            elif data.startswith("i:") and data[2:] in INFO:
                send_info(chat_id, data[2:], lang)
            elif data == "men":
                send_men(chat_id, lang)
            elif data.startswith("g:"):
                send_group(chat_id, int(data[2:]), lang)
            elif data.startswith("c:"):
                send_category(chat_id, int(data[2:]), lang)
            elif data.startswith("p:"):
                _, node_id, index = data.split(":")
                send_products(chat_id, int(node_id), int(index), lang)
        except Exception as e:
            print("Error:", e)
            post(chat_id, "sendMessage", {
                "text": t("error", lang),
                "reply_markup": {"inline_keyboard": [[{"text": t("menu", lang), "callback_data": "menu"}]]}})


def main():
    while True:  # keep trying if the internet is down at startup
        try:
            me = call("getMe")
            break
        except urllib.error.URLError as e:
            print("No connection to Telegram, retrying:", e)
            time.sleep(5)
    if not me:
        print("Could not connect. Check BOT_TOKEN in .env")
        return
    print(f"Bot @{me['username']} is running. Press Ctrl+C to stop.")
    offset = 0
    while True:
        try:
            updates = call("getUpdates", {"offset": offset, "timeout": 30}, timeout=40) or []
            for update in updates:
                offset = update["update_id"] + 1
                # short log line (commands and buttons only, no personal data)
                text = update.get("message", {}).get("text", "")
                data = update.get("callback_query", {}).get("data", "")
                print(time.strftime("%H:%M:%S"), "command:" if text.startswith("/") else "button:" if data else "message",
                      text if text.startswith("/") else data)
                try:
                    handle(update)
                except Exception as e:
                    print("Error:", e)
        except KeyboardInterrupt:
            print("Stopped.")
            break
        except Exception as e:
            print("Connection problem, retrying:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()
