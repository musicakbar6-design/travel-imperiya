import asyncio
import json
import logging
import os
import re
import sys
from html import escape

from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandObject, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BotCommand, BotCommandScopeChat, CallbackQuery, FSInputFile,
    InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo,
    KeyboardButton, Message, ReplyKeyboardMarkup, WebAppInfo,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("imperiya")

# ============================ SOZLAMALAR ============================
TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_RAW = os.getenv("ADMIN_ID", "").strip()
if not TOKEN and sys.stdin.isatty():
    TOKEN = input("BotFather bergan TOKEN ni kiriting: ").strip()
if not ADMIN_RAW and sys.stdin.isatty():
    ADMIN_RAW = input("Sizning Telegram ID (bilmasangiz Enter bosing): ").strip()
ADMIN_IDS = [int(x) for x in ADMIN_RAW.replace(" ", "").split(",") if x.isdigit()]
PHONE = "+998889990014"
PHONE_VIEW = "+998 88 999 00 14"
PHONE2 = "+998889990015"
PHONE2_VIEW = "+998 88 999 00 15"
MAP_URL = "https://maps.app.goo.gl/1RAuarP3N2u1HtgA9?g_st=it"
MAP_URL = "https://maps.app.goo.gl/1RAuarP3N2u1HtgA9?g_st=it"
MAP_URL = "https://maps.app.goo.gl/1RAuarP3N2u1HtgA9?g_st=it"
MAP_URL = "https://maps.app.goo.gl/1RAuarP3N2u1HtgA9?g_st=it"
MAP_URL = "https://maps.app.goo.gl/1RAuarP3N2u1HtgA9?g_st=it"
MAP_URL = "https://maps.app.goo.gl/1RAuarP3N2u1HtgA9?g_st=it"
DATA_FILE = "data.json"
CACHE = "media_cache"
# ===================================================================

CATS = {
    "hot": "🔥 Issiq turlar",
    "abroad": "🌍 Tashqi turizm",
    "umra": "🕋 Umra",
    "domestic": "🏔 Ichki turizm",
    "promo": "🏷 Aksiya va chegirmalar",
    "about": "💼 Biz haqimizda",
}
LANGS = {"uz": "🇺🇿 O'zbekcha", "ru": "🇷🇺 Русский", "en": "🇬🇧 English", "tr": "🇹🇷 Türkçe", "ar": "🇸🇦 العربية"}

T = {
    "uz": {
        "welcome": "✈️ Imperiya Travel botiga xush kelibsiz!\nQuyidagi menyudan tanlang:",
        "hot": "🔥 Issiq turlar", "abroad": "🌍 Tashqi turizm", "umra": "🕋 Umra",
        "domestic": "🏔 Ichki turizm", "promo": "🏷 Aksiya va chegirmalar", "about": "💼 Biz haqimizda",
        "site": "🌐 Sayt", "contact": "📞 Operator bilan aloqa", "lang": "🌐 Tilni o'zgartirish",
        "empty": "📞 Narxlar va batafsil ma'lumot uchun operatorga murojaat qiling:\n+998 88 999 00 14\n+998 88 999 00 15", "book": "📞 Bron qilish",
        "contact_text": "📞 Biz bilan bog'laning:", "site_open": "🌐 Saytni ochish",
        "nosite": "Sayt hozircha ulanmagan.", "map": "📍 Xaritada ko'rish", "map": "📍 Xaritada ko'rish", "map": "📍 Xaritada ko'rish", "map": "📍 Xaritada ko'rish", "map": "📍 Xaritada ko'rish", "map": "📍 Xaritada ko'rish",
    },
    "ru": {
        "welcome": "✈️ Добро пожаловать в бот Imperiya Travel!\nВыберите в меню:",
        "hot": "🔥 Горящие туры", "abroad": "🌍 Зарубежные туры", "umra": "🕋 Умра",
        "domestic": "🏔 Внутренний туризм", "promo": "🏷 Акции и скидки", "about": "💼 О нас",
        "site": "🌐 Сайт", "contact": "📞 Связь с оператором", "lang": "🌐 Сменить язык",
        "empty": "📞 За ценами и подробностями обращайтесь к оператору:\n+998 88 999 00 14\n+998 88 999 00 15", "book": "📞 Забронировать",
        "contact_text": "📞 Свяжитесь с нами:", "site_open": "🌐 Открыть сайт",
        "nosite": "Сайт пока не подключен.", "map": "📍 Открыть на карте", "map": "📍 Открыть на карте", "map": "📍 Открыть на карте", "map": "📍 Открыть на карте", "map": "📍 Открыть на карте", "map": "📍 Открыть на карте",
    },
    "en": {
        "welcome": "✈️ Welcome to Imperiya Travel bot!\nChoose from the menu:",
        "hot": "🔥 Hot tours", "abroad": "🌍 International tours", "umra": "🕋 Umrah",
        "domestic": "🏔 Domestic tours", "promo": "🏷 Deals & discounts", "about": "💼 About us",
        "site": "🌐 Website", "contact": "📞 Contact operator", "lang": "🌐 Change language",
        "empty": "📞 For prices and details, contact our operator:\n+998 88 999 00 14\n+998 88 999 00 15", "book": "📞 Book now",
        "contact_text": "📞 Contact us:", "site_open": "🌐 Open website",
        "nosite": "Website is not connected yet.", "map": "📍 Open map", "map": "📍 Open map", "map": "📍 Open map", "map": "📍 Open map", "map": "📍 Open map", "map": "📍 Open map",
    },
    "tr": {
        "welcome": "✈️ Imperiya Travel botuna hoş geldiniz!\nMenüden seçin:",
        "hot": "🔥 Sıcak turlar", "abroad": "🌍 Yurt dışı turlar", "umra": "🕋 Umre",
        "domestic": "🏔 Yurt içi turlar", "promo": "🏷 Kampanyalar", "about": "💼 Hakkımızda",
        "site": "🌐 Web sitesi", "contact": "📞 Operatörle iletişim", "lang": "🌐 Dil değiştir",
        "empty": "📞 Fiyat ve ayrıntılar için operatörle iletişime geçin:\n+998 88 999 00 14\n+998 88 999 00 15", "book": "📞 Rezervasyon",
        "contact_text": "📞 Bizimle iletişime geçin:", "site_open": "🌐 Siteyi aç",
        "nosite": "Web sitesi henüz bağlı değil.", "map": "📍 Haritada aç", "map": "📍 Haritada aç", "map": "📍 Haritada aç", "map": "📍 Haritada aç", "map": "📍 Haritada aç", "map": "📍 Haritada aç",
    },
    "ar": {
        "welcome": "✈️ مرحباً بكم في بوت Imperiya Travel!\nاختر من القائمة:",
        "hot": "🔥 العروض الساخنة", "abroad": "🌍 السياحة الخارجية", "umra": "🕋 العمرة",
        "domestic": "🏔 السياحة الداخلية", "promo": "🏷 العروض والخصومات", "about": "💼 من نحن",
        "site": "🌐 الموقع", "contact": "📞 التواصل مع المشغل", "lang": "🌐 تغيير اللغة",
        "empty": "📞 للأسعار والتفاصيل تواصل مع المشغل:\n+998 88 999 00 14\n+998 88 999 00 15", "book": "📞 احجز الآن",
        "contact_text": "📞 تواصل معنا:", "site_open": "🌐 افتح الموقع",
        "nosite": "الموقع غير متصل بعد.", "map": "📍 افتح الخريطة", "map": "📍 افتح الخريطة", "map": "📍 افتح الخريطة", "map": "📍 افتح الخريطة", "map": "📍 افتح الخريطة", "map": "📍 افتح الخريطة",
    },
}
CHOOSE_LANG = "🌐 Tilni tanlang / Выберите язык / Choose language / Dil seçin / اختر اللغة"
KEYS = list(CATS) + ["site", "contact", "lang"]
BTN = {T[l][k]: k for l in T for k in KEYS}

# ============================ MA'LUMOT ============================
DATA = {"users": {}, "seq": 0, "items": {k: {} for k in CATS}}
LOCK = asyncio.Lock()


def load():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                DATA.update(json.load(f))
        except Exception as e:
            log.error("load error: %s", e)
    for k in CATS:
        v = DATA["items"].setdefault(k, {})
        if isinstance(v, list):
            DATA["items"][k] = {"uz": v}


def save():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(DATA, f, ensure_ascii=False)


async def backup(bot: Bot):
    """data.json ni admin chatiga yuborib pin qiladi (Render qayta ishga tushsa tiklanadi)."""
    if not ADMIN_IDS:
        return
    admin = ADMIN_IDS[0]
    try:
        old = (await bot.get_chat(admin)).pinned_message
        msg = await bot.send_document(
            admin, FSInputFile(DATA_FILE, filename="data.json"),
            caption="💾 Zaxira nusxa (o'chirmang)", disable_notification=True)
        await bot.pin_chat_message(admin, msg.message_id, disable_notification=True)
        if old and old.document and old.document.file_name == "data.json":
            try:
                await bot.delete_message(admin, old.message_id)
            except Exception:
                pass
    except Exception as e:
        log.error("backup error: %s", e)


async def restore(bot: Bot):
    if os.path.exists(DATA_FILE) or not ADMIN_IDS:
        return
    try:
        pm = (await bot.get_chat(ADMIN_IDS[0])).pinned_message
        if pm and pm.document and pm.document.file_name == "data.json":
            await bot.download(pm.document, destination=DATA_FILE)
            log.info("Zaxiradan tiklandi")
    except Exception as e:
        log.error("restore error: %s", e)


async def persist(bot: Bot):
    save()
    await backup(bot)


async def autobackup(bot: Bot):
    last = len(DATA["users"])
    while True:
        await asyncio.sleep(6 * 3600)
        if len(DATA["users"]) != last:
            last = len(DATA["users"])
            await persist(bot)


def get_lang(uid: int) -> str:
    return DATA["users"].get(str(uid), "uz")


def site_url(lang: str = "uz"):
    base = (os.getenv("SITE_URL") or os.getenv("RENDER_EXTERNAL_URL") or "").rstrip("/")
    return f"{base}/?lang={lang}" if base else None


# ============================ KLAVIATURALAR ============================
def kb(rows):
    return InlineKeyboardMarkup(inline_keyboard=rows)


def btn(text, data):
    return InlineKeyboardButton(text=text, callback_data=data)


def lang_kb():
    return kb([[btn(v, f"lang:{k}")] for k, v in LANGS.items()])


def menu_kb(lang: str):
    t = T[lang]
    rows = [["hot"], ["abroad", "umra"], ["domestic", "promo"], ["about", "site"], ["contact", "lang"]]
    url = site_url(lang)

    def b(k):
        if k == "site" and url:
            return KeyboardButton(text=t[k], web_app=WebAppInfo(url=url))
        return KeyboardButton(text=t[k])

    return ReplyKeyboardMarkup(keyboard=[[b(k) for k in r] for r in rows], resize_keyboard=True)


def book_kb(lang: str):
    return kb([[btn(T[lang]["book"], "book")]])


async def send_contact(bot: Bot, chat_id: int, lang: str):
    await bot.send_message(
        chat_id, f"{T[lang]['contact_text']}\n\n📞 {PHONE_VIEW}\n📞 {PHONE2_VIEW}",
        reply_markup=kb([[InlineKeyboardButton(text=T[lang]["map"], url=MAP_URL)]]))
    await bot.send_contact(chat_id, phone_number=PHONE, first_name="Imperiya Travel")
    await bot.send_contact(chat_id, phone_number=PHONE2, first_name="Imperiya Travel 2")


async def send_item(bot: Bot, chat_id: int, it: dict, lang: str):
    k = book_kb(lang)
    text = it.get("text") or ""
    media = it.get("media", [])[:10]
    if not media:
        return await bot.send_message(chat_id, text or "—", reply_markup=k)
    if len(media) == 1:
        m = media[0]
        send = bot.send_video if m["t"] == "video" else bot.send_photo
        kw = {m["t"]: m["f"]}
        if len(text) <= 1024:
            return await send(chat_id, caption=text or None, reply_markup=k, **kw)
        await send(chat_id, **kw)
        return await bot.send_message(chat_id, text, reply_markup=k)
    group = []
    for i, m in enumerate(media):
        cls = InputMediaVideo if m["t"] == "video" else InputMediaPhoto
        group.append(cls(media=m["f"], caption=text if (i == 0 and len(text) <= 1024) else None))
    await bot.send_media_group(chat_id, group)
    if len(text) > 1024:
        await bot.send_message(chat_id, text, reply_markup=k)
    else:
        await bot.send_message(chat_id, "👇", reply_markup=k)


async def show_cat(bot: Bot, chat_id: int, key: str, lang: str):
    items = DATA["items"].get(key, {}).get(lang, [])
    if not items:
        return await bot.send_message(chat_id, T[lang]["empty"], reply_markup=book_kb(lang))
    for it in items[-15:]:
        try:
            await send_item(bot, chat_id, it, lang)
        except Exception as e:
            log.error("send_item error: %s", e)


# ============================ ADMIN ============================
admin_router = Router()
admin_router.message.filter(F.from_user.id.in_(ADMIN_IDS))
admin_router.callback_query.filter(F.from_user.id.in_(ADMIN_IDS))


class Add(StatesGroup):
    media = State()
    text = State()


class Bc(StatesGroup):
    msg = State()


PANEL = "⚙️ Admin panel:"


def admin_kb():
    return kb([[btn("➕ Qo'shish", "adm:add")], [btn("🗑 O'chirish", "adm:del")],
               [btn("📊 Statistika", "adm:stat"), btn("📢 Xabar yuborish", "adm:bc")]])


def cat_kb(prefix):
    return kb([[btn(n, f"{prefix}:{k}")] for k, n in CATS.items()] + [[btn("⬅️ Orqaga", "adm:back")]])


def lang_pick_kb(prefix, cat, back, counts=False):
    rows = []
    for k, v in LANGS.items():
        label = f"{v} ({len(DATA['items'][cat].get(k, []))})" if counts else v
        rows.append([btn(label, f"{prefix}:{cat}:{k}")])
    rows.append([btn("⬅️ Orqaga", back)])
    return kb(rows)


@admin_router.message(Command("cancel"), StateFilter("*"))
async def cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("❌ Bekor qilindi. /settings")


@admin_router.message(Command("settings", "setting", "seting"), StateFilter("*"))
async def settings(m: Message, state: FSMContext):
    await state.clear()
    await m.answer(PANEL, reply_markup=admin_kb())


@admin_router.callback_query(F.data == "adm:back")
async def adm_back(c: CallbackQuery):
    await c.message.edit_text(PANEL, reply_markup=admin_kb())
    await c.answer()


@admin_router.callback_query(F.data == "adm:add")
async def adm_add(c: CallbackQuery):
    await c.message.edit_text("➕ Qaysi bo'limga qo'shamiz?", reply_markup=cat_kb("adm:ac"))
    await c.answer()


@admin_router.callback_query(F.data.startswith("adm:ac:"))
async def adm_ac(c: CallbackQuery):
    cat = c.data.split(":")[2]
    await c.message.edit_text(f"{CATS[cat]}\nQaysi til uchun?", reply_markup=lang_pick_kb("adm:al", cat, "adm:add"))
    await c.answer()


@admin_router.callback_query(F.data.startswith("adm:al:"))
async def adm_al(c: CallbackQuery, state: FSMContext):
    _, _, cat, lang = c.data.split(":")
    await state.clear()
    await state.set_state(Add.media)
    await state.update_data(cat=cat, lang=lang, media=[], text="")
    await c.message.answer(
        f"{CATS[cat]} → {LANGS[lang]}\n\n"
        "🎬 Video / 🖼 rasmlarni yuboring (bir nechta, maksimum 10). Tavsifni birinchi rasm tagiga yozsangiz ham bo'ladi.\n"
        "Tugagach: /done\nFaqat matn bo'lsa: /done\nBekor qilish: /cancel")
    await c.answer()


@admin_router.message(Add.media, Command("done"))
async def add_done(m: Message, state: FSMContext):
    d = await state.get_data()
    if d.get("text"):
        return await finish(m, state)
    await state.set_state(Add.text)
    await m.answer("📝 Tavsifni yuboring (yoki /skip — tavsifsiz):")


@admin_router.message(Add.media, F.video | F.photo)
async def add_media(m: Message, state: FSMContext):
    async with LOCK:
        d = await state.get_data()
        media = d.get("media", [])
        if len(media) >= 10:
            return await m.answer("Maksimum 10 ta. /done yozing.")
        media.append({"t": "video", "f": m.video.file_id} if m.video else {"t": "photo", "f": m.photo[-1].file_id})
        upd = {"media": media, "grp": m.media_group_id}
        if m.caption and not d.get("text"):
            upd["text"] = m.caption
        say = (not m.media_group_id) or d.get("grp") != m.media_group_id
        await state.update_data(**upd)
    if say:
        await m.answer(f"✅ {len(media)} ta qabul qilindi. Yana yuboring yoki /done")


@admin_router.message(Add.media)
async def add_media_bad(m: Message):
    await m.answer("Video yoki rasm yuboring. Tugatish: /done, bekor: /cancel")


@admin_router.message(Add.text, Command("skip"))
async def add_skip(m: Message, state: FSMContext):
    await finish(m, state, "")


@admin_router.message(Add.text, F.text)
async def add_text(m: Message, state: FSMContext):
    await finish(m, state, m.text)


async def finish(m: Message, state: FSMContext, text=None):
    d = await state.get_data()
    text = d.get("text", "") if text is None else text
    media = d.get("media", [])
    await state.clear()
    if not media and not text:
        return await m.answer("Hech narsa qo'shilmadi. /settings")
    DATA["seq"] += 1
    DATA["items"][d["cat"]].setdefault(d["lang"], []).append({"id": DATA["seq"], "media": media, "text": text})
    await persist(m.bot)
    await m.answer(f"✅ Qo'shildi: {CATS[d['cat']]} → {LANGS[d['lang']]}\n/settings")


@admin_router.callback_query(F.data == "adm:del")
async def adm_del(c: CallbackQuery):
    await c.message.edit_text("🗑 Qaysi bo'limdan o'chiramiz?", reply_markup=cat_kb("adm:dc"))
    await c.answer()


@admin_router.callback_query(F.data.startswith("adm:dc:"))
async def adm_dc(c: CallbackQuery):
    cat = c.data.split(":")[2]
    await c.message.edit_text(f"{CATS[cat]}\nQaysi til?", reply_markup=lang_pick_kb("adm:dl", cat, "adm:del", True))
    await c.answer()


async def render_list(message: Message, cat: str, lang: str):
    items = DATA["items"][cat].get(lang, [])
    rows = []
    for it in items:
        label = (it.get("text") or "media")[:28].replace("\n", " ")
        rows.append([btn(f"🗑 {it['id']}: {label}", f"adm:rm:{cat}:{lang}:{it['id']}")])
    rows.append([btn("⬅️ Orqaga", f"adm:dc:{cat}")])
    await message.edit_text(
        f"{CATS[cat]} → {LANGS[lang]}\n" + ("O'chiriladigan elementni tanlang:" if items else "Bo'sh"),
        reply_markup=kb(rows))


@admin_router.callback_query(F.data.startswith("adm:dl:"))
async def adm_dl(c: CallbackQuery):
    _, _, cat, lang = c.data.split(":")
    await render_list(c.message, cat, lang)
    await c.answer()


@admin_router.callback_query(F.data.startswith("adm:rm:"))
async def adm_rm(c: CallbackQuery):
    _, _, cat, lang, iid = c.data.split(":")
    DATA["items"][cat][lang] = [i for i in DATA["items"][cat].get(lang, []) if str(i["id"]) != iid]
    await persist(c.bot)
    await render_list(c.message, cat, lang)
    await c.answer("O'chirildi ✅")


@admin_router.callback_query(F.data == "adm:stat")
async def adm_stat(c: CallbackQuery):
    lines = [f"👥 Foydalanuvchilar: {len(DATA['users'])}"]
    for k, n in CATS.items():
        lines.append(f"{n}: " + ", ".join(f"{l}={len(DATA['items'][k].get(l, []))}" for l in LANGS))
    await c.message.answer("\n".join(lines))
    await c.answer()


@admin_router.callback_query(F.data == "adm:bc")
async def adm_bc(c: CallbackQuery, state: FSMContext):
    await state.set_state(Bc.msg)
    await c.message.answer("📢 Hamma foydalanuvchiga yuboriladigan xabarni (matn/rasm/video) yuboring.\nBekor: /cancel")
    await c.answer()


@admin_router.message(Bc.msg)
async def bc_send(m: Message, state: FSMContext):
    await state.clear()
    ok = 0
    for uid in list(DATA["users"]):
        try:
            await m.bot.copy_message(int(uid), m.chat.id, m.message_id)
            ok += 1
        except Exception:
            pass
        await asyncio.sleep(0.05)
    await m.answer(f"✅ Yuborildi: {ok}/{len(DATA['users'])}")


# ============================ FOYDALANUVCHI ============================
user_router = Router()


async def route(m: Message, key: str):
    lang = get_lang(m.from_user.id)
    if key == "lang":
        return await m.answer(CHOOSE_LANG, reply_markup=lang_kb())
    if key == "contact":
        return await send_contact(m.bot, m.chat.id, lang)
    if key == "site":
        url = site_url(lang)
        if not url:
            return await m.answer(T[lang]["nosite"])
        return await m.answer(T[lang]["site"], reply_markup=kb([
            [InlineKeyboardButton(text=T[lang]["site_open"], web_app=WebAppInfo(url=url))],
            [InlineKeyboardButton(text="🔗 Browser", url=url)]]))
    await show_cat(m.bot, m.chat.id, key, lang)


@user_router.message(Command("settings", "setting", "seting", "done", "skip", "cancel"))
async def not_admin(m: Message):
    await m.answer(
        "⛔ Siz admin emassiz.\n"
        f"Sizning ID: {m.from_user.id}\n"
        f"Botdagi ADMIN_ID: {ADMIN_IDS or 'YOZILMAGAN'}\n\n"
        "ADMIN_ID sizning ID'ingiz bilan bir xil bo'lishi kerak.")


@user_router.message(Command("id"))
async def my_id(m: Message):
    await m.answer(f"Sizning ID: {m.from_user.id}")


@user_router.message(CommandStart())
@user_router.message(Command("menu"))
async def start(m: Message, state: FSMContext):
    await state.clear()
    lang = get_lang(m.from_user.id)
    await m.answer(T[lang]["welcome"], reply_markup=menu_kb(lang))
    await m.answer(CHOOSE_LANG, reply_markup=lang_kb())


@user_router.message(Command("hot", "abroad", "umra", "domestic", "promo", "about", "site", "contact", "language"))
async def cmd(m: Message, command: CommandObject):
    key = "lang" if command.command == "language" else command.command
    await route(m, key)


@user_router.callback_query(F.data.startswith("lang:"))
async def set_lang(c: CallbackQuery):
    lang = c.data.split(":")[1]
    if lang not in T:
        return await c.answer()
    DATA["users"][str(c.from_user.id)] = lang
    save()
    try:
        await c.message.delete()
    except Exception:
        pass
    await c.bot.send_message(c.from_user.id, T[lang]["welcome"], reply_markup=menu_kb(lang))
    await c.answer()


@user_router.callback_query(F.data == "book")
async def book(c: CallbackQuery):
    await send_contact(c.bot, c.from_user.id, get_lang(c.from_user.id))
    await c.answer()


@user_router.message(F.text.in_(set(BTN)))
async def menu(m: Message):
    await route(m, BTN[m.text])


@user_router.message()
async def fallback(m: Message):
    lang = get_lang(m.from_user.id)
    await m.answer(T[lang]["welcome"], reply_markup=menu_kb(lang))


# ============================ SAYT ============================
CSS = """
:root{--bg:#f6f7fb;--fg:#14213d;--card:#fff;--ac:#0a7cff;--mut:#5b6478}
@media(prefers-color-scheme:dark){:root{--bg:#0e1320;--fg:#eef1f8;--card:#182036;--mut:#9aa6bf}}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--fg)}
header{background:linear-gradient(135deg,#0a7cff,#00c2a8);color:#fff;padding:34px 16px;text-align:center}
header h1{margin:0 0 6px;font-size:clamp(28px,6vw,44px)}
header p{margin:0;opacity:.9}
.lang{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:16px}
.lang a{color:#fff;text-decoration:none;padding:6px 12px;border-radius:20px;background:rgba(255,255,255,.2);font-size:14px}
.lang a.on{background:#fff;color:#0a7cff;font-weight:600}
.cats{position:sticky;top:0;z-index:5;display:flex;gap:8px;overflow-x:auto;padding:10px 12px;background:var(--bg)}
.cats a{white-space:nowrap;text-decoration:none;color:var(--fg);background:var(--card);padding:8px 14px;border-radius:20px;font-size:14px;box-shadow:0 1px 6px rgba(0,0,0,.08)}
main{max-width:1100px;margin:auto;padding:0 14px 90px}
h2{margin:28px 0 12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:16px}
.card{background:var(--card);border-radius:16px;padding:12px;box-shadow:0 2px 12px rgba(0,0,0,.08)}
.med{display:grid;gap:6px}
.med img,.med video{width:100%;border-radius:12px;background:#000}
.card p{color:var(--mut);line-height:1.55}
.btn{display:block;text-align:center;background:var(--ac);color:#fff;text-decoration:none;padding:11px;border-radius:12px;font-weight:600}
.fabs{position:fixed;right:14px;bottom:14px;display:flex;flex-direction:column;gap:8px}
.fab{background:#12b76a;color:#fff;padding:12px 18px;border-radius:30px;text-decoration:none;font-weight:700;text-align:center;box-shadow:0 6px 20px rgba(0,0,0,.3)}
.empty{text-align:center;color:var(--mut);padding:60px 0}
"""


def page(lang: str) -> str:
    t = T[lang]
    langs = "".join(f'<a href="/?lang={k}" class="{"on" if k == lang else ""}">{v}</a>' for k, v in LANGS.items())
    nav, secs = "", ""
    for cat in CATS:
        items = DATA["items"][cat].get(lang, [])
        nav += f'<a href="#{cat}">{t[cat]}</a>'
        cards = ""
        if not items:
            cards = f'<article class="card"><p>{escape(t["empty"]).replace(chr(10), "<br>")}</p><a class="btn" href="tel:{PHONE}">{t["book"]}</a></article>'
        for it in reversed(items):
            med = ""
            for m in it.get("media", []):
                if m["t"] == "video":
                    med += f'<video src="/m/{m["f"]}" controls preload="metadata" playsinline></video>'
                else:
                    med += f'<img src="/m/{m["f"]}" loading="lazy" alt="">'
            txt = escape(it.get("text") or "").replace("\n", "<br>")
            cards += f'<article class="card"><div class="med">{med}</div><p>{txt}</p><a class="btn" href="tel:{PHONE}">{t["book"]}</a></article>'
        secs += f'<section id="{cat}"><h2>{t[cat]}</h2><div class="grid">{cards}</div></section>'
    if not secs:
        secs = f'<div class="empty">{t["empty"]}</div>'
    d = "rtl" if lang == "ar" else "ltr"
    return (
        f'<!doctype html><html lang="{lang}" dir="{d}"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>Imperiya Travel</title><style>{CSS}</style></head><body>'
        f'<header><h1>✈️ Imperiya Travel</h1><p>{PHONE_VIEW} · {PHONE2_VIEW}</p><p><a style="color:#fff" href="{MAP_URL}" target="_blank">{t["map"]}</a></p><p><a style="color:#fff" href="{MAP_URL}" target="_blank">{t["map"]}</a></p><p><a style="color:#fff" href="{MAP_URL}" target="_blank">{t["map"]}</a></p><p><a style="color:#fff" href="{MAP_URL}" target="_blank">{t["map"]}</a></p><p><a style="color:#fff" href="{MAP_URL}" target="_blank">{t["map"]}</a></p><p><a style="color:#fff" href="{MAP_URL}" target="_blank">{t["map"]}</a></p><div class="lang">{langs}</div></header>'
        f'<div class="cats">{nav}</div><main>{secs}</main>'
        f'<div class="fabs"><a class="fab" href="tel:{PHONE}">📞 {PHONE_VIEW}</a><a class="fab" href="tel:{PHONE2}">📞 {PHONE2_VIEW}</a></div></body></html>'
    )


async def index(request: web.Request):
    lang = request.query.get("lang", "uz")
    return web.Response(text=page(lang if lang in T else "uz"), content_type="text/html")


async def media(request: web.Request):
    fid = request.match_info["fid"]
    if not re.fullmatch(r"[A-Za-z0-9_-]{10,300}", fid):
        raise web.HTTPNotFound()
    bot: Bot = request.app["bot"]
    try:
        f = await bot.get_file(fid)
        path = os.path.join(CACHE, fid + os.path.splitext(f.file_path or "")[1])
        if not os.path.exists(path):
            await bot.download_file(f.file_path, destination=path)
    except Exception as e:
        log.warning("media error: %s", e)
        raise web.HTTPNotFound()
    return web.FileResponse(path, headers={"Cache-Control": "public, max-age=86400"})


# ============================ ISHGA TUSHIRISH ============================
async def set_commands(bot: Bot):
    cmds = [
        BotCommand(command="start", description="🚀 Boshlash"),
        BotCommand(command="menu", description="📋 Menyu"),
        BotCommand(command="hot", description="🔥 Issiq turlar"),
        BotCommand(command="abroad", description="🌍 Tashqi turizm"),
        BotCommand(command="umra", description="🕋 Umra"),
        BotCommand(command="domestic", description="🏔 Ichki turizm"),
        BotCommand(command="promo", description="🏷 Aksiya va chegirmalar"),
        BotCommand(command="about", description="💼 Biz haqimizda"),
        BotCommand(command="site", description="🌐 Sayt"),
        BotCommand(command="contact", description="📞 Operator bilan aloqa"),
        BotCommand(command="language", description="🌐 Tilni o'zgartirish"),
    ]
    try:
        await bot.set_my_commands(cmds)
        extra = cmds + [BotCommand(command="settings", description="⚙️ Admin panel"),
                        BotCommand(command="cancel", description="❌ Bekor qilish")]
        for a in ADMIN_IDS:
            await bot.set_my_commands(extra, scope=BotCommandScopeChat(chat_id=a))
    except Exception as e:
        log.error("set_commands error: %s", e)


async def main():
    if not TOKEN:
        raise SystemExit("BOT_TOKEN topilmadi! CMD: set BOT_TOKEN=... yoki Render Environment ga yozing.")
    os.makedirs(CACHE, exist_ok=True)
    bot = Bot(TOKEN)
    try:
        me = await bot.get_me()
        log.info("Bot topildi: @%s", me.username)
    except Exception:
        await bot.session.close()
        raise SystemExit("\n❌ TOKEN NOTO'G'RI! BotFather -> /mybots -> botingiz -> API Token dan haqiqiy tokenni nusxalang.\n")
    await restore(bot)
    load()
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(admin_router)
    dp.include_router(user_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)

    app = web.Application()
    app["bot"] = bot
    app.router.add_get("/", index)
    app.router.add_get("/m/{fid}", media)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", "10000"))).start()

    asyncio.create_task(autobackup(bot))
    log.info("Bot ishga tushdi. ADMIN_ID = %s", ADMIN_IDS)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())