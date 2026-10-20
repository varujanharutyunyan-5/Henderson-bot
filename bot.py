"""Henderson shop Telegram bot. Uses only the Python standard library.

Categories and products are read live from https://henderson.am
Run:  python3 bot.py
"""
import html as htmllib
import json
import os
import re
import ssl
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid

from translations import (ADMIN, CATEGORY_NAMES, GROUP_ICONS, GROUP_NAMES, INFO, LANG_BUTTONS, LANGS,
                          MENU_BUTTONS, ORDER, PROMO, PROMO_NAMES, SEARCH, SEARCH_WORDS, STORES, UI)

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

def call(method, params=None, timeout=60, upload=None, raise_network=False):
    """Call a Telegram method. upload=(field, path) sends a local file. Returns None on any failure."""
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
    except (urllib.error.URLError, OSError, ValueError) as e:  # timeout, connection reset, bad reply
        if raise_network:
            raise
        print(f"Telegram connection problem in {method}: {e}")
        return None


def save_json(path, data):
    """Write a data file safely: a crash mid-write can't leave a half-written file."""
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f)
    os.replace(tmp, path)


sent = {}  # chat_id -> ids of messages on the current page
BOT = {"username": ""}  # filled in at start


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

_cache = {}  # key -> {"time", "value", "failed"}: parsed site data, not whole pages (they are ~1.5 MB each)


def fetch_raw(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as resp:  # the site can be slow
        return resp.read().decode("utf-8", "replace")


def cached(key, build):
    """build() once per CACHE_SECONDS. If the site fails or changes, keep the older result
    and don't try again for 5 minutes (each try can take up to 60 s)."""
    hit, now = _cache.get(key), time.time()
    if hit and (now - hit["time"] < CACHE_SECONDS or now - hit["failed"] < 300):
        return hit["value"]
    try:
        value = build()
    except Exception as e:
        if not hit:
            raise
        print(f"Site problem ({key}), using the saved copy:", type(e).__name__, e)
        hit["failed"] = now
        return hit["value"]
    _cache[key] = {"time": now, "value": value, "failed": 0}
    return value


def load_menu():
    """The category tree from the site's own menu: nodes[i] = {"title", "link", "children": [ids], "parent"}."""
    return cached("menu", read_menu)["nodes"]


def catalog_links():
    """Every catalog link on the home page (some, like belts, aren't in the menu)."""
    return cached("menu", read_menu)["links"]


def read_menu():
    page = fetch_raw(SITE + "/")
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
    return {"nodes": nodes, "links": {l.rstrip("/") for l in re.findall(r'href="(/catalog/[^"?#]+)"', page)}}


def load_products(link):
    """The products on a category page. (The site shows the first 36; the rest come from its protected API.)"""
    return cached("products:" + link, lambda: read_products(link))


def read_products(link):
    page = fetch_raw(SITE + link)
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
    ("Suits & formal wear", ["/catalog/suit-separates", "/catalog/blazers", "/catalog/vests",
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
    ("Gifts", ["/catalog/gift-cards-am", "/catalog/gift-box", "/catalog/ties", "/catalog/fragrance",
               "/catalog/muzhskie-koshelki-portmone-i-zazhimy", "/catalog/cuff-links-tie-clips",
               "/catalog/muzhskie-kluchnicy-vizitnicy-oblozhki"]),
    ("Unisex", ["/catalog/umbrellas", "/catalog/glasses", "/catalog/scarves", "/catalog/gloves",
                "/catalog/rjukzaki", "/catalog/roadbags", "/catalog/suitcase"]),
]


_groups = {"nodes": None, "groups": []}


def load_groups():
    """Turn GROUPS into [(title, [node ids])] using the current site menu (rebuilt when the menu is)."""
    nodes = load_menu()
    if _groups["nodes"] is nodes:
        return _groups["groups"]
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
    _groups.update(nodes=nodes, groups=groups)
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
except OSError:
    langs = {}
except ValueError:  # damaged file: keep a copy instead of overwriting everyone's choice
    print("langs.json is damaged; saved a copy as langs.json.bad")
    os.replace(LANG_FILE, LANG_FILE + ".bad")
    langs = {}


def lang_of(chat_id):
    return langs.get(str(chat_id))


def set_lang(chat_id, lang):
    langs[str(chat_id)] = lang
    save_json(LANG_FILE, langs)


def t(key, lang):
    return UI[key].get(lang) or UI[key]["en"]


def group_label(title, lang):
    """Section name without its icon (the website uses its own icons)."""
    return title if lang == "en" else GROUP_NAMES.get(title, {}).get(lang, title)


def group_name(title, lang):
    name = group_label(title, lang)
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


# ---------- search ----------

INDEX_HOURS = 12      # rebuild the search list this often
INDEX_PAUSE = 1.5     # seconds between category pages, to go easy on the site
index = {"items": [], "time": 0}


def index_items():
    return index["items"]
searches = {}  # chat_id -> {"q": text, "items": [...]} – the last search results
INDEX_FILE = os.path.join(os.environ.get("DATA_DIR", HERE), "search-index.json")


def build_index():
    """Read every category page once and collect all products (runs in the background)."""
    # every catalog page: the menu plus all catalog links on the home page (e.g. belts aren't in the menu)
    tops = {n["link"].rstrip("/") for n in load_menu() if n["parent"] is None}
    links = {n["link"].rstrip("/") for n in load_menu()}
    links |= catalog_links()
    found, failed = {}, 0
    for link in sorted(links - tops):
        slug = link.split("/")[-1]
        try:
            for item in load_products(link):
                entry = found.setdefault(item["url"], {**item, "cats": set()})
                entry["cats"].add(slug)
        except Exception as e:
            print("Search list: skipped a page:", e)
            failed += 1
        time.sleep(INDEX_PAUSE)
    if failed > len(links) // 4 or len(found) < len(index["items"]) // 2:  # the site was having problems
        raise RuntimeError(f"only {len(found)} products, {failed} pages failed; keeping the old list")
    index.update(items=list(found.values()), time=time.time())
    print(f"Search list ready: {len(index['items'])} products")
    try:  # keep a copy so the search works right after a restart
        save_json(INDEX_FILE, {"time": index["time"],
                               "items": [{**p, "cats": sorted(p["cats"])} for p in index["items"]]})
    except OSError as e:
        print("Could not save the search list:", e)


def index_loop():
    try:  # start from the saved copy, then refresh it when it's old
        with open(INDEX_FILE) as f:
            saved = json.load(f)
        index.update(items=[{**p, "cats": set(p["cats"])} for p in saved["items"]], time=saved["time"])
        print(f"Search list loaded: {len(index['items'])} products")
        time.sleep(max(0, saved["time"] + INDEX_HOURS * 3600 - time.time()))
    except (OSError, ValueError, KeyError):
        pass
    while True:
        try:
            build_index()
            time.sleep(INDEX_HOURS * 3600)
        except Exception as e:
            print("Search list failed, retrying in 5 minutes:", e)
            time.sleep(300)


RU_ENDINGS = {"", "ый", "ий", "ой", "ая", "яя", "ое", "ее", "ые", "ие", "ых", "их", "ую", "юю", "ого", "его",
              "ому", "ему", "ым", "им", "ыми", "ими", "а", "у", "ы", "и", "е", "ом", "ам", "ах", "ов", "ей"}
STOP_WORDS = {"для", "в", "во", "на", "с", "со", "и", "или", "по", "из", "от", "до", "к", "у", "мне", "есть",
              "хочу", "нужен", "нужна", "нужно", "нужны", "какие", "какой", "a", "an", "the", "for", "with",
              "and", "or", "in", "of", "to", "i", "me", "need", "want", "some", "any", "do", "you", "have"}
COLOR_CODES = {"blk": "black", "brw": "brown", "nav": "navy", "wht": "white", "gry": "grey", "bge": "beige"}


def colors_of(code):
    """Site colour code → plain colours: "dnavy" → navy, "navy1" → navy, "blk/brw" → black, brown."""
    out = set()
    for part in code.split("/"):
        part = COLOR_CODES.get(part.rstrip("0123456789"), part.rstrip("0123456789"))
        out |= {part, part[1:]} if part[:1] in ("d", "l") and len(part) > 4 else {part}
        out.add(COLOR_CODES.get(part[1:], ""))
    return out


def stem_match(w, word):
    """A Russian word form of a stem: "черные", "черную" → "черн"; but not "сертификат" → "сер"."""
    return w.startswith(word) and w[len(word):] in RU_ENDINGS


def name_match(w, name):
    """A whole word of a category name, or its plural ("shirt" → "shirts", but not "t-shirts" or "suitcases")."""
    return w == name or any(x == w or (x.startswith(w) and len(x) - len(w) <= 2) for x in name.split())


def search_products(q):
    """Products matching every word of q (Russian, English or Armenian): name, colour or category."""
    q = " ".join(q.lower().replace("ё", "е").split())
    if any(w not in STOP_WORDS for w in q.split()):  # "свитер для зимы" → "свитер зимы"
        q = " ".join(w for w in q.split() if w not in STOP_WORDS)
    all_cats = [(n["link"].rstrip("/").split("/")[-1],
                 [n["title"].lower()] + [x.lower() for x in
                                         CATEGORY_NAMES.get(n["link"].rstrip("/").split("/")[-1], ())])
                for n in load_menu()]

    def word_matcher(w):
        terms = {w}
        if not w.isascii() and len(w) >= 5:  # Russian case endings: "рубашку" → "рубашк" (in "рубашка")
            terms.add(w[:-2] if w[-2:] in RU_ENDINGS else w[:-1])
        for word, stems in SEARCH_WORDS.items():
            if (w == word or w.rstrip("s") == word.rstrip("s")  # "card" is not "cardigan"
                    or (len(w) >= 4 and word.startswith(w) and len(word) - len(w) <= 2)
                    or (not word.isascii() and len(word) >= 3 and stem_match(w, word))):
                terms.update(stems)
        cats = {slug for slug, names in all_cats if any(len(w) >= 3 and name_match(w, x) for x in names)}
        return lambda p: (any(term in p["name"].lower().replace("ё", "е") for term in terms)
                          or bool(colors_of(p["color"]) & terms) or bool(p["cats"] & cats))

    # two-word phrases first ("bow tie", "gift card"), then single words
    words = q.split()
    for phrase in [w for w in SEARCH_WORDS if " " in w and w in q]:
        q = q.replace(phrase, phrase.replace(" ", "_"))
    words = [w.replace("_", " ") for w in q.split()]
    matchers = [word_matcher(w) for w in words]
    found = [p for p in index["items"] if all(m(p) for m in matchers)]
    if not found and len(matchers) > 1:  # a sentence: keep only the words that find something
        matchers = [m for m in matchers if any(m(p) for p in index["items"])]
        found = [p for p in index["items"] if all(m(p) for m in matchers)] if matchers else []
    return found[:60]


def ask_search(chat_id, lang):
    post(chat_id, "sendMessage", {
        "text": SEARCH["prompt"][lang],
        "reply_markup": {"inline_keyboard": [[{"text": t("back", lang), "callback_data": "menu"}]]}})


def run_search(chat_id, lang, q):
    clear_page(chat_id)
    retry = [[{"text": SEARCH["again"][lang], "callback_data": "find"},
              {"text": MENU_BUTTONS["catalog"][lang], "callback_data": "men"}],
             [{"text": t("menu", lang), "callback_data": "menu"}]]
    if not index["items"]:
        post(chat_id, "sendMessage", {"text": SEARCH["wait"][lang], "reply_markup": {"inline_keyboard": retry}})
        return
    items = search_products(q)
    print(f"Search: {len(items)} results")
    if not items:
        post(chat_id, "sendMessage", {"text": SEARCH["none"][lang].format(q=q[:40]),
                                      "reply_markup": {"inline_keyboard": retry}})
        return
    searches[chat_id] = {"q": q[:40], "items": items}
    send_products(chat_id, "s", 0, lang)


# ---------- live promotions ----------

def load_promos():
    """Current offers from henderson.am/offers/: [(slug, Russian title, valid-until date)]."""
    today = tuple(time.gmtime(time.time() + 4 * 3600)[:3])  # the date in Yerevan (UTC+4)
    return [p for p in cached("promos", read_promos) if tuple(map(int, reversed(p[2].split(".")))) >= today]


def read_promos():
    page = fetch_raw(SITE + "/offers/")
    promos, seen = [], set()
    for link, inner in re.findall(r'<a[^>]+href="/offers/([^"/]+)/?"[^>]*>(.*?)</a>', page, re.S):
        text = " ".join(htmllib.unescape(re.sub(r"<[^>]+>", " ", inner)).split())
        m = re.match(r"Действительна до (\d\d\.\d\d\.\d{4})\s+(.*?)\s*(Подробнее)?$", text)
        if not m or link in seen:
            continue
        seen.add(link)
        promos.append((link, m.group(2), m.group(1)))
    return promos


def current_promos(lang):
    """[(name in lang, valid-until date)]: [] when no offer is running, None when the page can't be loaded."""
    try:
        promos = load_promos()
    except Exception as e:
        print("Promotions page unavailable:", e)
        return None
    out = []
    for slug, title_ru, until in promos:
        names = PROMO_NAMES.get(slug)
        out.append((title_ru if lang == "ru" or not names else names[0 if lang == "en" else 1], until))
    return out


def send_promos(chat_id, lang):
    promos = current_promos(lang)
    if promos is None:  # site unreachable: say so and point to the store
        send_info(chat_id, "promo", lang)
        return
    if not promos:
        post(chat_id, "sendMessage", {
            "text": f"<b>{PROMO['title'][lang]}</b>\n\n{PROMO['none'][lang]}", "parse_mode": "HTML",
            "reply_markup": {"inline_keyboard": [[{"text": t("back", lang), "callback_data": "menu"}]]}})
        return
    lines = [f"<b>{PROMO['title'][lang]}</b>", ""]
    for name, until in promos:
        lines += [f"🏷 {htmllib.escape(name)}", f"📅 {PROMO['until'][lang]} {until}", ""]
    lines.append(PROMO["note"][lang])
    post(chat_id, "sendMessage", {
        "text": "\n".join(lines), "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": [[{"text": t("back", lang), "callback_data": "menu"}]]}})


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
        [b("catalog", "men"), b("search", "find")],
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


def items_of(chat_id, key):
    """Products behind a product card: a category (key = node id) or the last search (key = "s")."""
    if key == "s":
        return searches.get(chat_id, {}).get("items", [])
    return load_products(load_menu()[int(key)]["link"])


def send_products(chat_id, key, index, lang, card=None):
    """Show one product with < > buttons. card = the product message to update in place."""
    items = items_of(chat_id, key)
    if key == "s":
        title = f"🔍 {htmllib.escape(searches.get(chat_id, {}).get('q', ''))}"
        back = "find"
    else:
        node_id = int(key)
        title = htmllib.escape(node_name(node_id, lang))
        # "Back" from an "All" page goes to the category itself, otherwise to its group or parent
        back = f"c:{node_id}" if load_menu()[node_id]["children"] else back_from(node_id)
    nav = [{"text": t("back", lang), "callback_data": back},
           {"text": t("menu", lang), "callback_data": "menu"}]
    if not items:
        clear_page(chat_id, card)
        post(chat_id, "sendMessage", {
            "text": f"<b>{title}</b>\n\n{t('no_products', lang)}", "parse_mode": "HTML",
            "reply_markup": {"inline_keyboard": [nav]}})
        return

    index %= len(items)  # wrap around at both ends
    item = items[index]
    extra = other_prices(item["amd"])
    caption = (f"<b>{htmllib.escape(item['name'])}</b>\n"
               + (f"🎨 {htmllib.escape(item['color'])}\n" if item["color"] else "")
               + "💰 " + item["price"] + (f"  <i>{extra}</i>" if extra else ""))
    buttons = {"inline_keyboard": [
        [{"text": "<", "callback_data": f"p:{key}:{index - 1}"},
         {"text": f"{index + 1} / {len(items)} 📋", "callback_data": f"l:{key}:{index}"},
         {"text": ">", "callback_data": f"p:{key}:{index + 1}"}],
        [{"text": o("order_btn", lang), "callback_data": f"o:{key}:{index}:{product_id(item)}"[:64]},
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


def send_list(chat_id, key, current, card, lang):
    """Turn the product card's buttons into a numbered list of all products."""
    items = items_of(chat_id, key)
    rows = []
    for i, item in enumerate(items):
        name = item["name"] if len(item["name"]) <= 24 else item["name"][:23] + "…"
        if item["color"]:
            name += f" ({item['color']})"
        mark = "👉 " if i == current else ""
        rows.append([{"text": f"{mark}{i + 1}. {name}", "callback_data": f"p:{key}:{i}"}])
    rows.append([{"text": t("close", lang), "callback_data": f"p:{key}:{current}"}])
    call("editMessageReplyMarkup", {"chat_id": chat_id, "message_id": card,
                                    "reply_markup": {"inline_keyboard": rows}})


# ---------- ordering, reserving and calling ----------

ADMIN_FILE = os.path.join(DATA_DIR, "admin.json")  # the chat that receives requests


def o(key, lang):
    return ORDER[key].get(lang) or ORDER[key]["en"]


def load_admin_data():
    """{"admins": [{"id", "name"}], "invite": {"code", "expires"}}"""
    try:
        with open(ADMIN_FILE) as f:
            data = json.load(f)
    except OSError:
        data = {}
    except ValueError:  # damaged file: don't let a stranger become the first admin
        print("admin.json is damaged: fix or delete it on the server. Nobody can become admin until then.")
        return {"admins": [], "damaged": True}
    if "chat_id" in data:  # older format: one admin
        data = {"admins": [{"id": data["chat_id"], "name": ""}]}
    if "admins" not in data:
        # On the server the first admin can also come from the ADMIN_CHAT_ID variable
        env = os.environ.get("ADMIN_CHAT_ID", "")
        data["admins"] = [{"id": int(env), "name": ""}] if env.lstrip("-").isdigit() else []
    return data


def save_admin_data(data):
    if not data.get("damaged"):
        save_json(ADMIN_FILE, data)


def load_admins():
    return [a["id"] for a in load_admin_data()["admins"]]


def user_name(user):
    name = " ".join(filter(None, [user.get("first_name"), user.get("last_name")])) or "?"
    return name + (f" (@{user['username']})" if user.get("username") else "")


def add_admin(chat_id, user, lang):
    data = load_admin_data()
    if chat_id not in [a["id"] for a in data["admins"]]:
        data["admins"].append({"id": chat_id, "name": user_name(user)})
    data.pop("invite", None)
    save_admin_data(data)
    print("Admin added")
    post(chat_id, "sendMessage", {"text": o("admin_set", lang)})
    for a in data["admins"]:  # tell the other admins
        if a["id"] != chat_id:
            al = lang_of(a["id"]) or "en"
            call("sendMessage", {"chat_id": a["id"], "text": ADMIN["joined"][al].format(name=user_name(user))})


def admin_command(chat_id, user, lang):
    """/admin: first person becomes admin; an admin gets the admin panel."""
    data = load_admin_data()
    ids = [a["id"] for a in data["admins"]]
    if not ids and not data.get("damaged"):
        add_admin(chat_id, user, lang)
    elif chat_id in ids:
        send_admin_panel(chat_id, lang)
    else:
        post(chat_id, "sendMessage", {"text": o("admin_taken", lang)})


def send_admin_panel(chat_id, lang):
    admins = load_admin_data()["admins"]
    names = "\n".join(f"• {htmllib.escape(a['name'] or str(a['id']))}" + (" 👈" if a["id"] == chat_id else "")
                      for a in admins)
    post(chat_id, "sendMessage", {
        "text": f"{ADMIN['panel'][lang]}\n{names}", "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": [
            [{"text": ADMIN["invite_btn"][lang], "callback_data": "ai"}],
            [{"text": ADMIN["leave_btn"][lang], "callback_data": "al"}],
            [{"text": t("close", lang), "callback_data": "x"}]]}})


def make_invite(chat_id, lang):
    if chat_id not in load_admins():
        return
    data = load_admin_data()
    code = uuid.uuid4().hex[:12]
    data["invite"] = {"code": code, "expires": time.time() + 24 * 3600}
    save_admin_data(data)
    link = f"https://t.me/{BOT['username']}?start=adm_{code}"
    post(chat_id, "sendMessage", {"text": ADMIN["invite"][lang].format(link=link)})


def use_invite(chat_id, user, lang, code):
    invite = load_admin_data().get("invite") or {}
    if invite.get("code") == code and invite.get("expires", 0) > time.time():
        add_admin(chat_id, user, lang)
    else:
        post(chat_id, "sendMessage", {"text": ADMIN["bad_invite"][lang]})


def leave_admins(chat_id, lang):
    data = load_admin_data()
    data["admins"] = [a for a in data["admins"] if a["id"] != chat_id]
    save_admin_data(data)
    print("Admin left")
    post(chat_id, "sendMessage", {"text": ADMIN["left"][lang] + ("" if data["admins"] else "\n\n" + ADMIN["left_last"][lang])})


# ---------- reminder before the Railway trial ends ----------

TRIAL_END = os.environ.get("TRIAL_END", "2026-11-13")  # YYYY-MM-DD; empty = no reminders
REMIND_DAYS = (5, 1)  # remind this many days before
REMINDER_FILE = os.path.join(DATA_DIR, "reminders.json")
last_check = {"time": 0}


def check_reminders():
    if not TRIAL_END or time.time() - last_check["time"] < 3600:
        return
    last_check["time"] = time.time()
    try:
        end = time.mktime(time.strptime(TRIAL_END, "%Y-%m-%d"))
    except ValueError:
        print("TRIAL_END is not a date like 2026-11-13; no reminders")
        return
    try:
        with open(REMINDER_FILE) as f:
            done = json.load(f)
    except (OSError, ValueError):
        done = []
    days_left = (end - time.time()) / 86400
    for days in REMIND_DAYS:
        if str(days) not in done and 0 < days_left <= days:
            date = time.strftime("%d.%m.%Y", time.localtime(end))
            got = [call("sendMessage", {"chat_id": admin,
                                        "text": ADMIN["trial"][lang_of(admin) or "en"].format(date=date)})
                   for admin in load_admins()]
            if any(got):  # try again next hour if nobody received it
                done.append(str(days))
                save_json(REMINDER_FILE, done)
                print(f"Trial reminder sent ({days} days before)")


# chat_id -> request being filled in: {"step", "item", "type", "store", "note"}; saved so a restart keeps it
ORDER_FILE = os.path.join(DATA_DIR, "orders.json")
try:
    with open(ORDER_FILE) as f:
        orders = {int(k): v for k, v in json.load(f).items()}
except (OSError, ValueError):
    orders = {}


def save_orders():
    try:
        save_json(ORDER_FILE, orders)
    except OSError as e:
        print("Could not save orders:", e)


def drop_order(chat_id, lang=None):
    """Forget an unfinished request; at the phone step also remove the phone keyboard."""
    order = orders.pop(chat_id, None)
    if order:
        save_orders()
        if lang and order["step"] == "phone":
            post(chat_id, "sendMessage", {"text": o("cancel", lang), "reply_markup": {"remove_keyboard": True}})
    return order


def cancel_row(lang):
    return [{"text": o("cancel", lang), "callback_data": "ox"}]


def send_call(chat_id, lang, back="menu"):
    post(chat_id, "sendMessage", {
        "text": o("call_text", lang), "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": [[{"text": t("back", lang), "callback_data": back}]]}})


def product_id(item):
    return item["url"].rstrip("/").rsplit("/", 1)[-1]


def start_order(chat_id, lang, key=None, index=None, pid=None):
    """Step 1: what kind of request. From a product card, the product is attached."""
    item = None
    if key is not None:
        items = items_of(chat_id, key)
        item = items[index % len(items)] if items else None
        if pid and (not item or product_id(item) != pid):  # the list changed or was lost in a restart
            item = next((i for i in items + index_items() if product_id(i) == pid), None)
    orders[chat_id] = {"step": "type", "item": item}
    save_orders()
    kinds = ["t_order", "t_reserve"] if item else ["t_order", "t_reserve", "t_fitting", "t_mtm", "t_other"]
    rows = [[{"text": o(k, lang), "callback_data": f"ot:{k}"}] for k in kinds]
    post(chat_id, "sendMessage", {"text": o("ask_type", lang),
                                  "reply_markup": {"inline_keyboard": rows + [cancel_row(lang)]}})


def ask_store(chat_id, lang, kind):
    """Step 2: which store."""
    orders[chat_id].update(step="store", type=kind)
    save_orders()
    rows = [[{"text": f"📍 {name}", "callback_data": f"os:{i}"}] for i, name in enumerate(STORES[lang])]
    post(chat_id, "sendMessage", {"text": o("ask_store", lang),
                                  "reply_markup": {"inline_keyboard": rows + [cancel_row(lang)]}})


def ask_note(chat_id, lang, store):
    """Step 3: size (for a product) or a short message (general request)."""
    order = orders[chat_id]
    order.update(step="note", store=store)
    save_orders()
    post(chat_id, "sendMessage", {"text": o("ask_size" if order["item"] else "ask_note", lang),
                                  "reply_markup": {"inline_keyboard": [cancel_row(lang)]}})


def ask_phone(chat_id, lang, note):
    """Step 4: phone number (button shares the Telegram contact)."""
    orders[chat_id].update(step="phone", note="" if note.strip() == "-" else note.strip()[:300])
    save_orders()
    post(chat_id, "sendMessage", {"text": o("ask_phone", lang), "reply_markup": {
        "keyboard": [[{"text": o("share_phone", lang), "request_contact": True}],
                     [{"text": o("cancel", lang)}]],
        "resize_keyboard": True, "one_time_keyboard": True}})


DRY_RUN = False  # chat preview on the Mac: print requests instead of sending them


def valid_phone(phone):
    return sum(ch.isdigit() for ch in phone) >= 6


def notify_admins(kind, item, store, fields, name, phone, source=""):
    """Send a request to every admin in their language. fields = [(label key, text)]. True if any got it."""
    sent = False
    for admin in load_admins():
        al = lang_of(admin) or "en"
        lines = [f"<b>{o('new_request', al)}</b>{source}", f"{o('f_type', al)}: {o(kind, al)}"]
        if item:
            lines.append(f"{o('f_item', al)}: {htmllib.escape(item['name'])}"
                         + (f" ({htmllib.escape(item['color'])})" if item["color"] else "")
                         + f" – {item['price']}\n{item['url']}")
        lines += [f"{o(key, al)}: {htmllib.escape(value)}" for key, value in fields]
        lines += [f"{o('f_store', al)}: {STORES[al][store]}",
                  f"{o('f_client', al)}: {htmllib.escape(name)}",
                  f"{o('f_phone', al)}: {htmllib.escape(phone)}"]
        text = "\n".join(lines)
        if DRY_RUN:
            print("Request (preview, not sent):\n" + text)
            sent = True
            continue
        ok = bool(item and item["photo"] and len(text) <= 1024 and call("sendPhoto", {
            "chat_id": admin, "photo": item["photo"], "caption": text, "parse_mode": "HTML"}))
        ok = ok or bool(call("sendMessage", {"chat_id": admin, "text": text, "parse_mode": "HTML"}))
        print("Order: request sent to an admin" if ok else "Order: sending to an admin FAILED")
        sent = sent or ok
    if not load_admins():
        print("No admin yet: send /admin to the bot to receive requests")
    return sent


def finish_order(chat_id, lang, phone, user):
    """Send the request to the admin chat and thank the customer."""
    order = orders.pop(chat_id)
    save_orders()
    item = order["item"]
    note = [("f_size" if item else "f_note", order["note"])] if order.get("note") else []
    try:
        sent = notify_admins(order["type"], item, order["store"], note, user_name(user), phone)
    except Exception as e:  # the customer must still hear back and get the phone numbers
        print("Order: sending FAILED:", type(e).__name__, e)
        sent = False

    # Confirmation also removes the phone keyboard
    post(chat_id, "sendMessage", {"text": o("sent", lang) if sent else o("not_sent", lang),
                                  "reply_markup": {"remove_keyboard": True}})
    if not sent:
        send_call(chat_id, lang)
    send_menu(chat_id, lang)


def cancel_order(chat_id, lang):
    if orders.pop(chat_id, None):
        save_orders()
        post(chat_id, "sendMessage", {"text": o("cancel", lang), "reply_markup": {"remove_keyboard": True}})


def handle_order_message(chat_id, lang, msg):
    """Typed answers during an order. Returns True if the message was used."""
    order = orders.get(chat_id)
    if not order:
        return False
    text = msg.get("text") or msg.get("caption") or ""
    if text == o("cancel", lang):
        cancel_order(chat_id, lang)
        send_menu(chat_id, lang)
    elif text.startswith("/"):  # /start or another command: leave the request
        drop_order(chat_id, lang)
        return False
    elif order["step"] == "note":
        if not text:  # a sticker or voice message: ask again in words
            post(chat_id, "sendMessage", {"text": o("ask_size" if order["item"] else "ask_note", lang),
                                          "reply_markup": {"inline_keyboard": [cancel_row(lang)]}})
            return True
        print("Order: size/message received")
        ask_phone(chat_id, lang, text)
    elif order["step"] == "phone":
        phone = (msg.get("contact") or {}).get("phone_number") or text
        if valid_phone(phone):
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
        text = msg.get("text", "")
        if text.startswith("/admin"):
            admin_command(chat_id, msg.get("from", {}), lang or "en")
            return
        if text.startswith("/start adm_"):
            use_invite(chat_id, msg.get("from", {}), lang or "en", text.split("adm_", 1)[1].strip())
            return
        try:
            if lang and handle_order_message(chat_id, lang, msg):
                return
            drop_order(chat_id, lang)
            text = msg.get("text", "").strip()
            if lang and text and not text.startswith("/"):
                run_search(chat_id, lang, text)
                return
            clear_page(chat_id)
            send_menu(chat_id, lang) if lang else send_languages(chat_id)
        except Exception as e:  # e.g. henderson.am is down: answer instead of going silent
            print("Error:", type(e).__name__, e)
            post(chat_id, "sendMessage", {
                "text": t("error", lang or "en"),
                "reply_markup": {"inline_keyboard": [[{"text": t("menu", lang or "en"), "callback_data": "menu"}]]}})
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
                drop_order(chat_id, lang)  # start over if one was in progress
                if data == "o":
                    clear_page(chat_id, message_id)
                    start_order(chat_id, lang)
                else:
                    _, key, index, *pid = data.split(":")
                    start_order(chat_id, lang, key, int(index), pid[0] if pid else None)
                return
            if data.startswith(("ot:", "os:")):
                call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})
                order = orders.get(chat_id)
                step = "type" if data.startswith("ot:") else "store"
                if order and order["step"] == step:
                    ask_store(chat_id, lang, data[3:]) if step == "type" else ask_note(chat_id, lang, int(data[3:]))
                elif not order:  # a button from a finished or forgotten request
                    clear_page(chat_id)
                    send_menu(chat_id, lang)
                return  # an old question of the current request: just removed
            if data == "ox":
                call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})
                order = drop_order(chat_id, lang)
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
            if data in ("ai", "al"):  # admin panel buttons
                call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})
                if chat_id in load_admins():
                    make_invite(chat_id, lang) if data == "ai" else leave_admins(chat_id, lang)
                return
            # Middle button: show the list of products on the same message
            if data.startswith("l:"):
                _, key, index = data.split(":")
                send_list(chat_id, key, int(index), message_id, lang)
                return
            # < and > on a product card update that same message
            if data.startswith("p:") and "photo" in q["message"]:
                _, key, index = data.split(":")
                send_products(chat_id, key, int(index), lang, card=message_id)
                return
            # New page: remove everything from the last one, and leave any unfinished request
            drop_order(chat_id, lang)
            clear_page(chat_id, message_id)
            if data == "menu":
                send_menu(chat_id, lang)
            elif data == "lang":
                send_languages(chat_id)
            elif data == "call":
                send_call(chat_id, lang)
            elif data == "i:promo":
                send_promos(chat_id, lang)
            elif data.startswith("i:") and data[2:] in INFO:
                send_info(chat_id, data[2:], lang)
            elif data == "find":
                ask_search(chat_id, lang)
            elif data == "men":
                send_men(chat_id, lang)
            elif data.startswith("g:"):
                send_group(chat_id, int(data[2:]), lang)
            elif data.startswith("c:"):
                send_category(chat_id, int(data[2:]), lang)
            elif data.startswith("p:"):
                _, key, index = data.split(":")
                send_products(chat_id, key, int(index), lang)
        except Exception as e:
            print("Error:", e)
            post(chat_id, "sendMessage", {
                "text": t("error", lang),
                "reply_markup": {"inline_keyboard": [[{"text": t("menu", lang), "callback_data": "menu"}]]}})


def main():
    while True:  # keep trying if the internet is down at startup
        try:
            me = call("getMe", raise_network=True)
            break
        except urllib.error.URLError as e:
            print("No connection to Telegram, retrying:", e)
            time.sleep(5)
    if not me:
        print("Could not connect. Check BOT_TOKEN in .env")
        return
    BOT["username"] = me["username"]
    print(f"Bot @{me['username']} is running. Press Ctrl+C to stop.")
    threading.Thread(target=index_loop, daemon=True).start()  # search list, built in the background
    if os.environ.get("PORT"):  # on the server: also run the website chat assistant
        import chat
        threading.Thread(target=chat.serve, args=(sys.modules[__name__], int(os.environ["PORT"])),
                         daemon=True).start()
    offset = 0
    while True:
        try:
            check_reminders()
            updates = call("getUpdates", {"offset": offset, "timeout": 30}, timeout=40)
            if updates is None:  # Telegram or network error: don't hammer it
                time.sleep(3)
                continue
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
