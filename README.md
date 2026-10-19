# Henderson Telegram bot

Telegram bot **@Delavdebot** for the Henderson shop ([henderson.am](https://henderson.am)).

## What it does
Clean style with emoji buttons and a short welcome text. English, Русский, Հայերեն.

- `/start` → first time: choose a language; then the logo photo `welcome.png` with the main menu:
  - **🔍 Search** → type a word in English, Russian or Armenian (coat, пальто, վերարկու, black jeans). Typing any text in the chat also searches.
  - **🛍 Catalog** → sections (Suits, Winter clothes, Shirts & polos, Trousers & jeans, Sportswear, Shoes, Bags, Accessories, Home & underwear, 🎁 Gifts, 👜 Unisex, Other) → the site's categories → products
  - **📏 Sizes & measuring** → how to measure yourself + approximate size table (general guide, not from the site)
  - **✂️ Tailoring & fitting** → services; free within 30 days of purchase; 24 h–7 days
  - **🧵 Made-to-measure** → Su Misura suits and shirts (also women's shirts)
  - **📍 Stores & contacts** → 3 Yerevan stores, hours, phones, hotline
  - **🚚 Delivery & returns** → free delivery to stores, 30-day returns, guarantee
  - **🏷 Promotions** → read live from henderson.am/offers/ (ended offers are hidden; known offers are translated in `PROMO_NAMES`)
  - **📩 Contact us** → general request (order, reserve, fitting, made-to-measure, other) → store → message → phone
  - **📞 Call the store** → store phones and hotline
  - **🌐 Language**
- Every product has **📩 Order / Reserve** (order or reserve to try on → store → size → phone) and **📞 Call**.
- Requests are sent to the admin chat with the product photo, name, colour, price, size, store, customer name and phone.
  **Admins:** the first person to send `/admin` becomes admin. An admin sends `/admin` to open the admin panel:
  **➕ Invite admin** makes a one-time link (24 h) for a new admin; **🚪 Stop being admin** leaves. Several admins all get every request.
  To hand over: invite the new person, then tap 🚪 Stop being admin.
- **Trial reminder:** admins get a message 5 days and 1 day before `TRIAL_END` (Railway variable, default 2026-11-13).
- **Search list:** built in the background from every catalog page (about 15–20 minutes, gently), refreshed every 12 hours, saved as `search-index.json` so it's ready after a restart.
- Info page texts are in `INFO` in `translations.py` (facts taken from henderson.am in October 2026). Prices for made-to-measure and paid tailoring weren't on the site, so they say "ask in store".
- Sections are set in `GROUPS` in `bot.py`. Site categories not listed there go to **Other** automatically.
- A category shows one product per message (photo, name, colour, price in ֏ with approximate USD and RUB in italics, using daily rates from open.er-api.com). **<** and **>** flip through them in place.
- The middle button (e.g. **2 / 36 📋**) shows a numbered list of all products; tap one to open it.
- Opening a new page deletes the messages from the previous one. No buttons open the website.
- Product names stay in Russian (the site is only in Russian).

Categories and products are read live from henderson.am (refreshed every 30 minutes), so there is nothing to update by hand.

## Website chat assistant (chat.py)
A chat bubble for henderson.am. Henderson's web team adds one line to the site:
`<script src="https://<railway domain>/widget.js" defer></script>`
- Buttons (no AI cost): catalog sections → categories → product cards (photo, price, View, Order or reserve), sizes, tailoring, made-to-measure, stores, delivery, promotions. EN / RU / HY.
- Typed questions: Claude Opus 5.5 (effort low, prompt caching, automatic fallback if a request is declined) with tools: search, categories, category products, shop info, send request. Answers end with product cards and up to 3 suggested replies.
- Requests go to the same Telegram admins as the bot (marked "website chat"), only after the visitor confirms and agrees to share name and phone.
- Limits: 40 AI messages per visitor address per hour, 25 per chat, 500 characters per message.
- Needs the Railway variable `ANTHROPIC_API_KEY` (without it, buttons work and typed questions get a friendly "use the buttons" reply). Allowed sites: `CHAT_ORIGINS` (default henderson.am).
- Privacy page: `/privacy` (fill in [COMPANY] and [EMAIL] in webtext.py first). Preview: `PREVIEW=1 PORT=8081 python3 chat.py`.

## Run
The bot runs on **Railway** (project `henderson-bot`, service `bot`), so it works when the Mac is off.
- Code comes from the private GitHub repo `varujanharutyunyan-5/Henderson-bot` (branch `main`); every `git push` redeploys it.
- Railway variables: `BOT_TOKEN` (Telegram token from @BotFather), `ADMIN_CHAT_ID` (chat that receives requests), `DATA_DIR=/data`.
- Saved data (`langs.json`, `admin.json`) lives on the Railway volume `bot-data` mounted at `/data`.
- Railway trial: 30 days or $5, then a paid plan is needed to keep it running.

**Don't run `python3 bot.py` on the Mac while Railway is running** – two copies conflict and messages get lost.
To test locally, stop the Railway service first.

## Files
- `bot.py`: the bot (plain Python, nothing to install)
- `.env`: the bot token from @BotFather (`BOT_TOKEN=...`). Keep it secret.
- `admin.json`: the chat that receives order/reservation requests (created by `/admin`)
- `chat.py`, `webtext.py`: website chat assistant and its texts
- `translations.py`: texts in English, Russian and Armenian
- `langs.json`: each user's chosen language (created automatically)
- `welcome.png`: the start page photo (1280×1280)
- `certs.pem`: the Mac's trusted certificates, needed because this Python install has none. Re-create it with:
  `security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain > certs.pem`

## Notes
- If henderson.am changes its site design, the category or product reading may stop working and `bot.py` will need updating.
- Each category shows the first 36 products the site lists.
- The project started as a bot for DN8 (instagram.com/dn8team), which has no website, so it was switched to Henderson.
