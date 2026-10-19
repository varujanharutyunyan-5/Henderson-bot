"""Website chat assistant: a chat bubble for henderson.am (widget.js) + its server.

Runs inside the bot (bot.py starts it when PORT is set), sharing catalog, search, admins and texts.
Buttons work without AI. Typed questions go to Claude (needs ANTHROPIC_API_KEY on the server).
Embed on any page:  <script src="https://<this server>/widget.js" defer></script>
Preview on the Mac:  PREVIEW=1 PORT=8081 python3 chat.py  →  http://localhost:8081
"""
import html
import json
import os
import re
import secrets
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from webtext import LEGAL, WT

try:  # installed on the server (requirements.txt); optional for previews
    import anthropic
except ImportError:
    anthropic = None

B = None  # the bot module (set in serve)
LANGS = ("en", "ru", "hy")
PREVIEW = os.environ.get("PREVIEW") == "1"
MODEL = "claude-opus-5-5"
ORIGINS = {o.strip() for o in os.environ.get(
    "CHAT_ORIGINS", "https://henderson.am,https://www.henderson.am").split(",") if o.strip()}
LIMIT_IP_HOUR = 40       # AI messages per visitor address per hour
LIMIT_TURNS = 25         # AI messages per chat
SESSION_HOURS = 3
PAGE = 8                 # product cards per page

client = anthropic.Anthropic() if anthropic and os.environ.get("ANTHROPIC_API_KEY") else None
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️‍⃣]+\\s*")
sessions, hits, lock = {}, {}, threading.Lock()


def plain(text):
    return EMOJI.sub("", re.sub(r"</?(b|i|pre)>", "", text)).strip()


def t(key, lang):
    return WT[key].get(lang) or WT[key]["en"]


# ---------- data helpers (shared by buttons and AI tools) ----------

def card(item):
    """A product as the widget shows it (also what the AI sees, minus the photo)."""
    return {"id": item["url"].rstrip("/").split("/")[-1], "name": item["name"], "color": item["color"],
            "price": item["price"], "approx": B.other_prices(item["amd"]), "url": item["url"],
            "photo": item["photo"]}


def find_item(pid):
    for item in B.index["items"]:
        if item["url"].rstrip("/").endswith("/" + pid):
            return item
    return None


def stores_text(lang):
    return plain(B.ORDER["call_text"][lang])


def info_text(key, lang):
    return plain(B.INFO[key][lang])


def promos_text(lang):
    try:
        promos = B.load_promos()
    except Exception:
        promos = []
    if not promos:
        return info_text("promo", lang)
    lines = []
    for slug, title_ru, until in promos:
        names = B.PROMO_NAMES.get(slug)
        name = title_ru if lang == "ru" or not names else names[0 if lang == "en" else 1]
        lines.append(f"{name} ({B.PROMO['until'][lang]} {until})")
    return "\n".join(lines)


# ---------- buttons (no AI) ----------

def menu_buttons(lang):
    b = B.MENU_BUTTONS
    return [{"label": t("catalog", lang), "action": "sections", "icon": "catalog"},
            {"label": plain(b["sizes"][lang]), "action": "info:sizes", "icon": "sizes"},
            {"label": plain(b["tailor"][lang]), "action": "info:tailor", "icon": "tailor"},
            {"label": plain(b["mtm"][lang]), "action": "info:mtm", "icon": "mtm"},
            {"label": t("stores", lang), "action": "stores", "icon": "stores"},
            {"label": plain(b["delivery"][lang]), "action": "info:delivery", "icon": "delivery"},
            {"label": t("promos", lang), "action": "promos", "icon": "promos"}]


def do_action(action, lang):
    """Button press → {"text", "products", "buttons"}."""
    back = [{"label": t("menu", lang), "action": "menu"}]
    if action == "menu":
        return {"text": t("hello", lang), "buttons": menu_buttons(lang)}
    if action == "sections":
        return {"buttons": [{"label": plain(B.group_name(title, lang)), "action": f"group:{gi}"}
                            for gi, (title, _) in enumerate(B.load_groups())] + back}
    if action.startswith("group:"):
        _, ids = B.load_groups()[int(action[6:])]
        return {"buttons": [{"label": B.node_name(k, lang), "action": f"cat:{k}:0"} for k in ids] + back}
    if action.startswith("cat:"):
        _, node, page = action.split(":")
        node, page = int(node), int(page)
        n = B.load_menu()[node]
        kids = [{"label": B.node_name(k, lang), "action": f"cat:{k}:0"} for k in n["children"]] if page == 0 else []
        items = B.load_products(n["link"])
        more = ([{"label": t("more", lang), "action": f"cat:{node}:{page + 1}"}]
                if len(items) > (page + 1) * PAGE else [])
        return {"text": B.node_name(node, lang) if page == 0 else "",
                "products": [card(i) for i in items[page * PAGE:(page + 1) * PAGE]],
                "buttons": more + kids + back}
    if action.startswith("info:") and action[5:] in B.INFO:
        return {"text": info_text(action[5:], lang), "buttons": back}
    if action == "stores":
        return {"text": stores_text(lang), "buttons": back}
    if action == "promos":
        return {"text": promos_text(lang), "buttons": back}
    return {"text": t("error", lang), "buttons": back}


# ---------- AI ----------

SYSTEM = """You are the online shop assistant of the Henderson clothing stores in Yerevan, Armenia, shown \
as a chat window on henderson.am. Visitors come to find clothes, shoes and accessories, check prices and \
sizes, find a store, or reserve an item to try on.

Style:
- Answer in the visitor's language (English, Russian or Armenian). Be warm, direct and brief: usually 1 to 3 \
short sentences, at most about 60 words unless you list items. Plain text only: no markdown, no headings, no \
emojis. For lists use short lines starting with "- ".
- Don't greet again after the first message. Don't repeat the visitor's question.
- If the request is vague, ask at most one question (for example size, colour, budget or occasion), or show \
a few good options right away and offer to narrow down.
- When suggesting products, pick 2 to 4 that fit best and give each one short reason (colour, fit, price). \
Mention the approximate USD price only if the visitor seems to think in dollars or rubles.
- When size matters, offer the size table or measuring tips (shop_info "sizes"); stores can help on site.

Facts:
- Use the tools for every fact about products, prices, stores, services and promotions. Never invent \
products, sizes in stock, discounts or delivery times. If you don't know, say the store can confirm by phone \
(hotline 8248).
- Product names come from the shop's site in Russian; keep them, and explain briefly in the visitor's \
language when helpful. Prices are in Armenian dram.

Special lines at the very end of your reply (each optional, never anywhere else):
SHOW: id1, id2   - product ids from tool results to show as photo cards (up to 6). Use it whenever you \
mention specific products; don't write links or ids in the text.
OPTIONS: reply 1 | reply 2 | reply 3   - up to 3 short next steps the visitor can tap, written as the \
visitor would say them, in their language (for example "Show navy ones | Size table | Reserve in Rio Mall").

Orders and reservations:
- A request is not a purchase: a store calls the visitor to confirm, and payment happens in the store.
- Collect: type (order or reserve to try on, or a service), the product if any, store, size if relevant, the \
visitor's name and phone number. Ask for what is missing in one message.
- Then list the details in short lines and ask the visitor to confirm and agree that their name and phone \
number are sent to Henderson store staff. Call send_request only after a clear yes, then confirm in one \
sentence that the store will call.
- Stay on Henderson shopping. Politely decline unrelated tasks."""

TOOLS = [
    {"name": "search_products", "description": "Search the current catalog by words in any language "
     "(e.g. 'coat', 'черные джинсы', 'գոտի'). Returns up to 12 products.",
     "input_schema": {"type": "object", "properties": {"query": {"type": "string"}},
                      "required": ["query"], "additionalProperties": False}, "strict": True},
    {"name": "list_categories", "description": "The catalog sections and their categories with ids.",
     "input_schema": {"type": "object", "properties": {}, "additionalProperties": False}, "strict": True},
    {"name": "category_products", "description": "Products in one category (id from list_categories).",
     "input_schema": {"type": "object", "properties": {"category_id": {"type": "integer"}},
                      "required": ["category_id"], "additionalProperties": False}, "strict": True},
    {"name": "shop_info", "description": "Store addresses, phones and hours; size table and how to "
     "measure; tailoring/fitting; made-to-measure; delivery, returns and guarantee; current promotions.",
     "input_schema": {"type": "object", "properties": {"topic": {"type": "string", "enum": [
         "stores", "sizes", "tailoring", "made_to_measure", "delivery_returns", "promotions"]}},
                      "required": ["topic"], "additionalProperties": False}, "strict": True},
    {"name": "send_request", "description": "Send an order/reservation/service request to the store staff. "
     "Only after the visitor confirmed the details and agreed to share name and phone.",
     "input_schema": {"type": "object", "properties": {
         "type": {"type": "string", "enum": ["order", "reserve", "fitting", "made_to_measure", "other"]},
         "store": {"type": "string", "enum": ["Rio Mall", "Sayat-Nova Ave 8", "Dalma Garden Mall"]},
         "product_id": {"type": "string", "description": "Product id from tool results, or empty"},
         "size": {"type": "string"}, "message": {"type": "string"},
         "name": {"type": "string"}, "phone": {"type": "string"}},
         "required": ["type", "store", "product_id", "size", "message", "name", "phone"],
         "additionalProperties": False}, "strict": True},
]


def brief(item):
    c = card(item)
    return {k: c[k] for k in ("id", "name", "color", "price", "approx")}


def run_tool(name, args, s):
    """Execute one tool; returns a compact JSON-able result."""
    if name == "search_products":
        if not B.index["items"]:
            return {"note": "Search is still loading; use list_categories and category_products."}
        items = B.search_products(args["query"])[:12]
    elif name == "list_categories":
        nodes = B.load_menu()
        return [{"section": plain(B.group_name(title, "en")),
                 "categories": [{"id": k, "name": B.node_name(k, "en"), "ru": nodes[k]["title"]} for k in ids]}
                for title, ids in B.load_groups()]
    elif name == "category_products":
        nodes = B.load_menu()
        if not 0 <= args["category_id"] < len(nodes):
            return {"error": "unknown category id"}
        items = B.load_products(nodes[args["category_id"]]["link"])[:20]
    elif name == "shop_info":
        topic = args["topic"]
        if topic == "stores":
            return stores_text("en")
        if topic == "promotions":
            return promos_text("en")
        key = {"sizes": "sizes", "tailoring": "tailor", "made_to_measure": "mtm",
               "delivery_returns": "delivery"}[topic]
        return info_text(key, "en")
    elif name == "send_request":
        return {"sent": send_request(args, s)}
    else:
        return {"error": "unknown tool"}
    for item in items:  # remember what the AI saw, for product cards
        s["seen"][brief(item)["id"]] = item
    return [brief(i) for i in items]


def send_request(a, s):
    kind = {"order": "t_order", "reserve": "t_reserve", "fitting": "t_fitting",
            "made_to_measure": "t_mtm"}.get(a["type"], "t_other")
    store = ["Rio Mall", "Sayat-Nova Ave 8", "Dalma Garden Mall"].index(a["store"])
    item = s["seen"].get(a["product_id"]) or (find_item(a["product_id"]) if a["product_id"] else None)
    if sum(ch.isdigit() for ch in a["phone"]) < 6:
        return False
    sent = False
    for admin in B.load_admins():
        al = B.lang_of(admin) or "en"
        lines = [f"<b>💬 {B.o('new_request', al)}</b> (website chat)", f"{B.o('f_type', al)}: {B.o(kind, al)}"]
        if item:
            lines.append(f"{B.o('f_item', al)}: {html.escape(item['name'])}"
                         + (f" ({html.escape(item['color'])})" if item["color"] else "")
                         + f" – {item['price']}\n{item['url']}")
        if a["size"].strip():
            lines.append(f"{B.o('f_size', al)}: {html.escape(a['size'][:40])}")
        if a["message"].strip():
            lines.append(f"{B.o('f_note', al)}: {html.escape(a['message'][:400])}")
        lines += [f"{B.o('f_store', al)}: {B.STORES[al][store]}",
                  f"{B.o('f_client', al)}: {html.escape(a['name'][:60])}",
                  f"{B.o('f_phone', al)}: {html.escape(a['phone'][:30])}"]
        text = "\n".join(lines)
        if PREVIEW:
            print("Chat request (preview, not sent):\n" + text)
            sent = True
            continue
        ok = bool(item and item["photo"] and B.call("sendPhoto", {
            "chat_id": admin, "photo": item["photo"], "caption": text, "parse_mode": "HTML"}))
        sent = sent or ok or bool(B.call("sendMessage", {"chat_id": admin, "text": text, "parse_mode": "HTML"}))
    print("Chat: request sent" if sent else "Chat: request NOT sent")
    return sent


def ask_ai(s, text, lang):
    """One visitor message → Claude with tools → {"text", "products"}."""
    s["messages"].append({"role": "user", "content": f"[page language: {lang}]\n{text}"})
    for _ in range(8):  # tool-use loop
        r = client.beta.messages.create(
            model=MODEL, max_tokens=8000, system=SYSTEM, tools=TOOLS, messages=s["messages"],
            output_config={"effort": "low"},          # short shop chats don't need deep thinking
            cache_control={"type": "ephemeral"},       # caches tools + system + earlier turns
            betas=["server-side-fallback-2026-07-01"], fallbacks="default")
        s["messages"].append({"role": "assistant", "content": r.content})  # append-only history
        if r.stop_reason == "tool_use":
            s["messages"].append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": b.id,
                 "content": json.dumps(run_tool(b.name, b.input, s), ensure_ascii=False)}
                for b in r.content if b.type == "tool_use"]})
            continue
        if r.stop_reason != "pause_turn":
            break
    if r.stop_reason == "refusal":
        return {"text": t("error", lang)}
    reply = "".join(b.text for b in r.content if b.type == "text").strip()
    products, buttons = [], []
    m = re.search(r"^\s*OPTIONS:\s*(.+)$", reply, re.M)
    if m:
        reply = (reply[:m.start()] + reply[m.end():]).strip()
        buttons = [{"label": o.strip()[:40], "say": o.strip()[:120]} for o in m.group(1).split("|") if o.strip()][:3]
    m = re.search(r"^\s*SHOW:\s*(.+)$", reply, re.M)
    if m:
        reply = (reply[:m.start()] + reply[m.end():]).strip()
        for pid in [x.strip() for x in m.group(1).split(",")][:6]:
            item = s["seen"].get(pid) or find_item(pid)
            if item:
                products.append(card(item))
    return {"text": reply, "products": products, "buttons": buttons + [{"label": t("menu", lang), "action": "menu"}]}


def chat(body, ip):
    """POST /chat: {"session", "lang", "action"} for buttons or {"session", "lang", "message"} for AI."""
    lang = body.get("lang") if body.get("lang") in LANGS else "en"
    now = time.time()
    with lock:
        for k in [k for k, v in sessions.items() if now - v["time"] > SESSION_HOURS * 3600]:
            del sessions[k]
        sid = body.get("session") if body.get("session") in sessions else secrets.token_urlsafe(16)
        s = sessions.setdefault(sid, {"messages": [], "seen": {}, "time": now, "turns": 0, "busy": False})
        s["time"] = now
    if body.get("action"):
        return {"session": sid, **do_action(str(body["action"])[:40], lang)}
    text = str(body.get("message", "")).strip()[:500]
    if not text:
        return {"session": sid, "text": ""}
    if not client:
        return {"session": sid, "text": t("offline", lang), "buttons": menu_buttons(lang)}
    with lock:
        hits[ip] = [x for x in hits.get(ip, []) if now - x < 3600]
        if len(hits[ip]) >= LIMIT_IP_HOUR or s["busy"]:
            return {"session": sid, "text": t("busy", lang)}
        if s["turns"] >= LIMIT_TURNS:
            return {"session": sid, "text": t("new_chat", lang), "buttons": [{"label": t("restart", lang), "action": "reset"}]}
        hits[ip].append(now)
        s["turns"] += 1
        s["busy"] = True
    try:
        return {"session": sid, **ask_ai(s, text, lang)}
    except Exception as e:
        print("Chat AI error:", type(e).__name__, e)
        with lock:  # drop the broken turn so the history stays valid
            sessions.pop(sid, None)
        return {"session": None, "text": t("error", lang)}
    finally:
        s["busy"] = False


# ---------- widget (one script, Shadow DOM so henderson.am styles don't clash) ----------

ICONS = {  # simple line icons (website rule: SVG icons, never emoji)
    "catalog": '<path d="M10 6a2 2 0 1 1 3 1.7c-.6.4-1 .9-1 1.6V10l-8.5 6.2c-.6.5-.3 1.8.6 1.8h17.8c.9 0 1.2-1.3.6-1.8L12 10"/>',
    "sizes": '<rect x="2" y="8" width="20" height="8" rx="1"/><path d="M6 8v3M10 8v4M14 8v3M18 8v4"/>',
    "tailor": '<circle cx="6" cy="7" r="3"/><circle cx="6" cy="17" r="3"/><path d="M8.6 8.6 20 18M8.6 15.4 20 6"/>',
    "mtm": '<path d="M8 3 12 7 16 3M8 3 4 6v15h16V6l-4-3M12 7v14"/>',
    "stores": '<path d="M12 21s-7-6.2-7-11a7 7 0 1 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "delivery": '<path d="M2 6h12v10H2zM14 10h4l3 3v3h-7"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
    "promos": '<path d="M3 12V3h9l9 9-9 9z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
}

WIDGET_JS = r"""(function(){
if (window.__hendersonChat) return; window.__hendersonChat = 1;
var API = %(api)s, T = %(texts)s, ICONS = %(icons)s, LOGO = %(logo)s;
var lang = (document.documentElement.lang || navigator.language || 'en').slice(0,2).toLowerCase();
if (!T[lang]) lang = 'en';
var sid = null; try { sid = localStorage.getItem('hchat'); } catch (e) {}
function svg(p, cls){ return '<svg class="' + (cls || 'i') + '" viewBox="' + (cls === 'logo' ? '0 0 40 41' : '0 0 24 24') + '" aria-hidden="true">' + p + '</svg>'; }
var host = document.createElement('div'); host.style.cssText = 'position:fixed;right:20px;bottom:20px;z-index:2147483000';
document.body.appendChild(host);
var root = host.attachShadow({mode: 'open'});
root.innerHTML = '<style>%(css)s</style>' +
 '<button class="fab">' + svg('<path d="M4 5h16v11H9l-5 4z"/>') + '<span></span></button>' +
 '<section class="panel" role="dialog" hidden><header>' + svg(LOGO, 'logo') +
 '<div class="ttl"><strong></strong><small></small></div>' +
 '<select aria-label="Language"><option value="en">EN</option><option value="ru">RU</option><option value="hy">HY</option></select>' +
 '<button class="x">' + svg('<path d="M6 6l12 12M18 6 6 18"/>') + '</button></header>' +
 '<div class="log" aria-live="polite"></div><div class="btns"></div>' +
 '<form><input maxlength="500" autocomplete="off"><button class="go">' + svg('<path d="M4 12h15M13 6l6 6-6 6"/>') + '</button></form>' +
 '<footer><a target="_blank" rel="noopener"></a></footer></section>';
var $ = function(s){ return root.querySelector(s); };
var panel = $('.panel'), log = $('.log'), btns = $('.btns'), input = $('input'), sel = $('select');
sel.value = lang;
function texts(){ var L = T[lang]; $('.fab span').textContent = L.open; $('.fab').setAttribute('aria-label', L.open);
  $('.ttl strong').textContent = L.title; $('.ttl small').textContent = 'henderson.am'; panel.setAttribute('aria-label', L.title);
  input.placeholder = L.placeholder; $('.go').setAttribute('aria-label', L.send); $('.x').setAttribute('aria-label', L.close);
  $('footer a').textContent = L.privacy; $('footer a').href = API.replace(/\/chat$/, '/privacy?lang=' + lang); }
texts();
function scroll(){ log.scrollTop = log.scrollHeight; }
function add(cls, text){ if (!text) return; var d = document.createElement('div'); d.className = 'msg ' + cls;
  d.textContent = text; log.appendChild(d); scroll(); return d; }
function cards(list){ if (!list || !list.length) return; var row = document.createElement('div'); row.className = 'cards';
  list.forEach(function(p){ var c = document.createElement('article'); c.className = 'card';
    c.innerHTML = '<a class="img" target="_blank" rel="noopener"><img loading="lazy" alt=""></a><div class="b"><div class="n"></div>' +
      '<div class="c"></div><div class="p"></div><div class="a"></div><div class="row"><a class="v" target="_blank" rel="noopener"></a><button class="r"></button></div></div>';
    c.querySelector('img').src = p.photo; c.querySelector('img').alt = p.name; c.querySelector('.img').href = p.url;
    c.querySelector('.n').textContent = p.name; c.querySelector('.c').textContent = p.color || '';
    c.querySelector('.p').textContent = p.price; c.querySelector('.a').textContent = p.approx || '';
    var v = c.querySelector('.v'); v.href = p.url; v.textContent = T[lang].view;
    var r = c.querySelector('.r'); r.textContent = T[lang].reserve;
    r.onclick = function(){ say(T[lang].reserve_msg.replace('{item}', p.name + (p.color ? ' (' + p.color + ')' : '') + ', ' + p.price + ' [' + p.id + ']')); };
    row.appendChild(c); });
  log.appendChild(row); scroll(); }
function buttons(list){ btns.innerHTML = ''; list = list || [];
  btns.className = 'btns' + (list.some(function(b){ return b.icon; }) ? ' tiles' : '');
  list.forEach(function(b){ var x = document.createElement('button');
    x.innerHTML = (b.icon ? svg(ICONS[b.icon]) : '') + '<span></span>'; x.querySelector('span').textContent = b.label;
    if (b.say) x.className = 'say';
    x.onclick = function(){ if (b.action === 'reset') { sid = null; log.innerHTML = ''; send({action: 'menu'}); }
      else if (b.say) { say(b.say); } else { add('me', b.label); send({action: b.action}); } };
    btns.appendChild(x); }); }
function send(body){ body.session = sid; body.lang = lang; var w = add('bot wait', T[lang].typing);
  input.disabled = true; btns.innerHTML = '';
  fetch(API, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)})
  .then(function(r){ return r.json(); }).then(function(d){ w.remove(); sid = d.session;
    try { sid ? localStorage.setItem('hchat', sid) : localStorage.removeItem('hchat'); } catch (e) {}
    add('bot', d.text); cards(d.products); buttons(d.buttons); })
  .catch(function(){ w.remove(); add('bot', T[lang].error); buttons([{label: T[lang].menu, action: 'menu'}]); })
  .then(function(){ input.disabled = false; input.focus(); }); }
function say(text){ add('me', text); send({message: text}); }
$('.fab').onclick = function(){ panel.hidden = false; $('.fab').hidden = true; if (!log.children.length) send({action: 'menu'}); input.focus(); };
$('.x').onclick = function(){ panel.hidden = true; $('.fab').hidden = false; $('.fab').focus(); };
root.addEventListener('keydown', function(e){ if (e.key === 'Escape' && !panel.hidden) $('.x').onclick(); });
sel.onchange = function(){ lang = sel.value; texts(); log.innerHTML = ''; send({action: 'menu'}); };
$('form').onsubmit = function(e){ e.preventDefault(); var v = input.value.trim(); if (!v) return; input.value = ''; say(v); };
})();"""

WIDGET_CSS = (
    ":host{all:initial;font:15px/1.45 -apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,'Noto Sans Armenian',sans-serif;color:#1c1c1e}"
    "*{box-sizing:border-box}button,input,select{font:inherit;color:inherit}button{cursor:pointer}"
    ".i{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;flex:none}"
    ".fab{display:flex;gap:10px;align-items:center;background:#15284B;color:#fff;border:0;border-radius:8px;padding:13px 18px;"
    "box-shadow:0 6px 20px rgba(21,40,75,.28);font-weight:500}.fab:hover{background:#0e1c36}"
    ".panel{width:min(390px,calc(100vw - 24px));height:min(640px,calc(100vh - 40px));background:#f6f4ef;border-radius:10px;"
    "display:flex;flex-direction:column;box-shadow:0 12px 40px rgba(0,0,0,.22);overflow:hidden}"
    ".panel[hidden],.fab[hidden]{display:none}"
    "header{display:flex;gap:10px;align-items:center;background:#15284B;color:#fff;padding:12px 12px 12px 14px}"
    ".logo{width:28px;height:29px;fill:#fff;flex:none}.ttl{flex:1;min-width:0;display:flex;flex-direction:column}"
    ".ttl strong{font-weight:600;font-size:15px}.ttl small{font-size:12px;opacity:.7}"
    "header select{background:rgba(255,255,255,.12);color:#fff;border:0;border-radius:6px;padding:4px 6px;font-size:13px}header select option{color:#000}"
    ".x{background:none;border:0;color:#fff;padding:4px;border-radius:6px;display:flex}.x:hover{background:rgba(255,255,255,.12)}"
    ".log{flex:1;overflow:auto;padding:16px 14px 8px;display:flex;flex-direction:column;gap:10px}.log>*{flex-shrink:0}"
    ".msg{max-width:86%;padding:9px 12px;white-space:pre-wrap;word-wrap:break-word;font-size:14.5px}"
    ".bot{background:#fff;border:1px solid #e6e2da;border-radius:12px 12px 12px 3px;align-self:flex-start}"
    ".me{background:#15284B;color:#fff;border-radius:12px 12px 3px 12px;align-self:flex-end}"
    ".wait{color:#7a7e85;font-style:italic}"
    ".cards{display:flex;gap:10px;overflow-x:auto;padding:2px 2px 6px;scroll-snap-type:x mandatory}"
    ".card{flex:0 0 168px;background:#fff;border:1px solid #e6e2da;border-radius:10px;overflow:hidden;scroll-snap-align:start;display:flex;flex-direction:column}"
    ".card .img{display:block;background:#efece6}.card img{width:100%;aspect-ratio:3/4;object-fit:cover;display:block}"
    ".card .b{padding:9px 10px 10px;display:flex;flex-direction:column;flex:1;font-size:13px}"
    ".card .n{font-weight:600;line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}"
    ".card .c{color:#7a7e85;font-size:12px;margin-top:2px}.card .p{color:#15284B;font-weight:700;font-size:15px;margin-top:6px}"
    ".card .a{color:#7a7e85;font-size:11.5px}.card .row{display:flex;gap:6px;margin-top:auto;padding-top:8px}"
    ".card .v,.card .r{flex:1;text-align:center;font-size:12px;border-radius:6px;padding:7px 4px;text-decoration:none}"
    ".card .v{border:1px solid #cfcac1;color:#15284B}.card .r{border:0;background:#15284B;color:#fff}"
    ".card .v:hover{border-color:#15284B}.card .r:hover{background:#0e1c36}"
    ".btns{display:flex;flex-wrap:wrap;gap:6px;padding:4px 14px 10px;max-height:170px;overflow:auto}"
    ".btns button{display:flex;gap:6px;align-items:center;background:#fff;border:1px solid #d9d4ca;border-radius:6px;padding:7px 11px;color:#15284B;font-size:13px}"
    ".btns button:hover{border-color:#15284B}.btns button.say{background:#eef1f7;border-color:#d5dceb}"
    ".btns.tiles{display:grid;grid-template-columns:1fr 1fr;max-height:none}.btns.tiles button{padding:10px;text-align:left}"
    "form{display:flex;gap:8px;padding:10px 12px;border-top:1px solid #e6e2da;background:#fff}"
    "form input{flex:1;min-width:0;border:1px solid #d9d4ca;border-radius:8px;padding:10px 12px;background:#faf9f6}"
    "form input:focus{outline:none;border-color:#15284B;background:#fff}"
    ".go{background:#15284B;color:#fff;border:0;border-radius:8px;width:42px;display:flex;align-items:center;justify-content:center}"
    "footer{padding:0 12px 8px;background:#fff;font-size:11px;text-align:right}footer a{color:#7a7e85}"
    ":focus-visible{outline:2px solid #3d5a99;outline-offset:2px}"
    "@media (max-width:480px){:host{}.panel{height:calc(100vh - 32px)}}"
)

LOGO_PATHS = ('<polygon points="27.2,27.5 23.1,27.5 23.1,21.9 16.9,21.9 16.9,27.5 12.8,27.5 12.8,13.1 16.9,13.1 '
              '16.9,18.3 23.1,18.3 23.1,13.1 27.2,13.1"/><path d="M38,22.1l1.8-1.8L38,18.5l-1.5-1.5c1.2-1.6,1.9-3.6,'
              '1.9-5.7c0-5.2-4.2-9.4-9.4-9.4c-2.1,0-4.1,0.7-5.7,1.9l-1.5-1.5L20,0.5l-1.8,1.8l-1.5,1.5c-1.6-1.2-3.6-1.9'
              '-5.7-1.9c-5.2,0-9.4,4.2-9.4,9.4c0,2.1,0.7,4.1,1.9,5.7L2,18.5l-1.8,1.8L2,22.1l1.5,1.5c-1.2,1.6-1.9,3.6'
              '-1.9,5.7c0,5.2,4.2,9.4,9.4,9.4c2.1,0,4.1-0.7,5.7-1.9l1.5,1.5l1.8,1.8l1.8-1.8l1.5-1.5c1.6,1.2,3.6,1.9,'
              '5.7,1.9c5.2,0,9.4-4.2,9.4-9.4c0-2.1-0.7-4.1-1.9-5.7L38,22.1z M35.9,29.3c0,3.8-3.1,6.9-6.9,6.9c-2,0-3.7'
              '-0.8-5-2.1l-0.8-0.8L20,36.6l-3.2-3.2L16,34.1c-1.3,1.3-3,2.2-5,2.2c-3.8,0-6.9-3.1-6.9-6.9c0-1.9,0.8-3.7,'
              '2.1-4.9L7,23.6l-3.2-3.2L7,17.1l-0.8-0.8c-1.3-1.3-2.1-3-2.1-5c0-3.8,3.1-6.9,6.9-6.9c2,0,3.7,0.8,5,2.1'
              'l0.8,0.8L20,4.1l3.2,3.2l0.8-0.8c1.3-1.3,3-2.1,5-2.1c3.8,0,6.9,3.1,6.9,6.9c0,2-0.8,3.7-2.1,5L33,17.1'
              'l3.2,3.2L33,23.6l0.8,0.8C35.1,25.6,35.9,27.4,35.9,29.3L35.9,29.3z"/>')


def widget_js(base):
    texts = {lang: {k: v.get(lang) or v["en"] for k, v in WT.items()} for lang in LANGS}
    return WIDGET_JS % {"api": json.dumps(base + "/chat"), "texts": json.dumps(texts, ensure_ascii=False),
                        "icons": json.dumps(ICONS), "logo": json.dumps(LOGO_PATHS),
                        "css": WIDGET_CSS.replace("'", "\\'")}


def privacy_page(lang):
    parts = "".join(f"<h2>{html.escape(h)}</h2><p>{html.escape(p)}</p>" for h, p in LEGAL["privacy"][lang])
    return (f'<!doctype html><html lang="{lang}"><meta charset="utf-8"><meta name="viewport" '
            f'content="width=device-width,initial-scale=1"><title>Privacy | Henderson assistant</title>'
            f'<style>body{{font:16px/1.6 -apple-system,Arial,sans-serif;max-width:720px;margin:32px auto;'
            f'padding:0 16px;color:#1c1c1e}}h1,h2{{color:#15284B}}</style><h1>Privacy</h1>{parts}</html>')


DEMO = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Chat widget preview</title><body style="font:16px/1.5 -apple-system,Arial,sans-serif;max-width:720px;margin:40px auto;padding:0 16px">
<h1>Chat widget preview</h1><p>This page only shows the chat bubble in the corner. On henderson.am it appears the same way
after adding one line to the site:</p><pre style="background:#f4f2ee;padding:12px;white-space:pre-wrap">&lt;script src="%s/widget.js" defer&gt;&lt;/script&gt;</pre>
<script src="/widget.js?v=%s" defer></script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # no visitor addresses or texts in the log
        pass

    def base(self):
        proto = self.headers.get("X-Forwarded-Proto", "http")
        return f"{proto}://{self.headers.get('Host', 'localhost')}"

    def send(self, status, body, ctype="text/html; charset=utf-8", cache="no-store"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(status)
        origin = self.headers.get("Origin", "")
        if origin in ORIGINS or origin == self.base() or origin.startswith("http://localhost"):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", cache)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send(204, b"")

    def do_GET(self):
        url = urllib.parse.urlsplit(self.path)
        lang = (urllib.parse.parse_qs(url.query).get("lang", ["en"])[0])
        lang = lang if lang in LANGS else "en"
        if url.path == "/widget.js":
            return self.send(200, widget_js(self.base()), "text/javascript; charset=utf-8", "public, max-age=600")
        if url.path == "/privacy":
            return self.send(200, privacy_page(lang))
        if url.path == "/":
            return self.send(200, DEMO % (self.base(), int(time.time())))
        self.send(404, "Not found", "text/plain")

    def do_POST(self):
        if urllib.parse.urlsplit(self.path).path != "/chat":
            return self.send(404, "Not found", "text/plain")
        try:
            length = min(int(self.headers.get("Content-Length") or 0), 4000)
            body = json.loads(self.rfile.read(length) or b"{}")
            ip = self.headers.get("X-Forwarded-For", self.client_address[0]).split(",")[0].strip()
            result = chat(body if isinstance(body, dict) else {}, ip)
        except Exception as e:
            print("Chat error:", type(e).__name__, e)
            result = {"session": None, "text": t("error", "en")}
        self.send(200, json.dumps(result, ensure_ascii=False), "application/json; charset=utf-8")


def serve(bot_module, port):
    global B
    B = bot_module
    print(f"Chat widget is running on port {port} (AI {'on' if client else 'off: no ANTHROPIC_API_KEY'})")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":  # preview: widget only, no Telegram polling
    import bot
    threading.Thread(target=bot.index_loop, daemon=True).start()
    serve(bot, int(os.environ.get("PORT", "8081")))
