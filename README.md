# Henderson Telegram bot

Telegram bot **@Delavdebot** for the Henderson shop ([henderson.am](https://henderson.am)).

## What it does
Clean style with emoji buttons and a short welcome text. English, Русский, Հայերեն.

- `/start` → first time: choose a language; then the logo photo `welcome.png` with the main menu:
  - **🛍 Catalog** → sections (Suits, Winter clothes, Shirts & polos, Trousers & jeans, Sportswear, Shoes, Bags, Accessories, Home & underwear, Other) → the site's categories → products
  - **📏 Sizes & measuring** → how to measure yourself + approximate size table (general guide, not from the site)
  - **✂️ Tailoring & fitting** → services; free within 30 days of purchase; 24 h–7 days
  - **🧵 Made-to-measure** → Su Misura suits and shirts (also women's shirts)
  - **📍 Stores & contacts** → 3 Yerevan stores, hours, phones, hotline
  - **🚚 Delivery & returns** → free delivery to stores, 30-day returns, guarantee
  - **🎁 Promotions** → current offers (static text – update when offers change)
  - **📩 Contact us** → general request (order, reserve, fitting, made-to-measure, other) → store → message → phone
  - **📞 Call the store** → store phones and hotline
  - **🌐 Language**
- Every product has **📩 Order / Reserve** (order or reserve to try on → store → size → phone) and **📞 Call**.
- Requests are sent to the admin chat with the product photo, name, colour, price, size, store, customer name and phone.
  **Setup:** send `/admin` to the bot once from the chat that should receive requests. It's saved in `admin.json`; delete that file to change the admin chat.
- Info page texts are in `INFO` in `translations.py` (facts taken from henderson.am in October 2026). Prices for made-to-measure and paid tailoring weren't on the site, so they say "ask in store".
- Sections are set in `GROUPS` in `bot.py`. Site categories not listed there go to **Other** automatically.
- A category shows one product per message (photo, name, colour, price in ֏ with approximate USD and RUB in italics, using daily rates from open.er-api.com). **<** and **>** flip through them in place.
- The middle button (e.g. **2 / 36 📋**) shows a numbered list of all products; tap one to open it.
- Opening a new page deletes the messages from the previous one. No buttons open the website.
- Product names stay in Russian (the site is only in Russian).

Categories and products are read live from henderson.am (refreshed every 30 minutes), so there is nothing to update by hand.

## Run
```bash
cd "/Users/varuj/CLAUDE /henderson-bot" && python3 bot.py
```
The bot works only while this is running and the Mac is on. Stop it with Ctrl+C.

## Files
- `bot.py`: the bot (plain Python, nothing to install)
- `.env`: the bot token from @BotFather (`BOT_TOKEN=...`). Keep it secret.
- `admin.json`: the chat that receives order/reservation requests (created by `/admin`)
- `translations.py`: texts in English, Russian and Armenian
- `langs.json`: each user's chosen language (created automatically)
- `welcome.png`: the start page photo (1280×1280)
- `certs.pem`: the Mac's trusted certificates, needed because this Python install has none. Re-create it with:
  `security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain > certs.pem`

## Notes
- If henderson.am changes its site design, the category or product reading may stop working and `bot.py` will need updating.
- Each category shows the first 36 products the site lists.
- The project started as a bot for DN8 (instagram.com/dn8team), which has no website, so it was switched to Henderson.
