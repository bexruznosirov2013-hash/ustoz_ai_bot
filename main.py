import asyncio
import os
import re
import random
import hashlib
import urllib.request
import zipfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pymupdf as fitz

from docx import Document
from docx.shared import Pt

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


# ============================================================
# USTOZ AI
# ============================================================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "BOT_TOKEN topilmadi!\n"
        "Render Environment Variables ichiga BOT_TOKEN qo'ying."
    )


BOOKS_DIR = Path("books")
BOOKS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


GITHUB_RELEASE = (
    "https://github.com/"
    "bexruznosirov2013-hash/"
    "ustoz_ai_bot/"
    "releases/download/v1.0.0/"
)


GRADE_ZIPS = {
    1: "books_1-sinf.zip",
    2: "books_2-sinf.zip",
    3: "books_3-sinf.zip",
    4: "books_4-sinf.zip",
    5: "books_5-sinf.zip",
    6: "books_6-sinf.zip",
    7: "books_7-sinf.zip",
    8: "books_8-sinf.zip",
    9: "books_9-sinf.zip",
    10: "books_10-sinf.zip",
    11: "books_11-sinf.zip",
}


bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher()


# ============================================================
# RENDER HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8"
        )

        self.end_headers()

        self.wfile.write(
            b"USTOZ AI ISHLAYAPTI"
        )

    def log_message(self, format, *args):
        return


def start_render_server():

    port = int(
        os.getenv(
            "PORT",
            "10000"
        )
    )

    server = HTTPServer(
        (
            "0.0.0.0",
            port
        ),
        HealthHandler
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True
    )

    thread.start()

    print(
        f"[RENDER] Health server "
        f"0.0.0.0:{port} da ishga tushdi",
        flush=True
    )


# ============================================================
# BOOKS YUKLASH
# ============================================================

def download_file(
    url: str,
    destination: Path
):

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "USTOZ-AI-BOT"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=300
    ) as response:

        with open(
            destination,
            "wb"
        ) as file:

            while True:

                chunk = response.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                file.write(
                    chunk
                )


# ============================================================
# ZIP OCHISH
# ============================================================

def extract_zip(
    zip_path: Path,
    destination: Path,
    grade: int
):

    grade_dir = (
        destination /
        f"{grade}-sinf"
    )

    grade_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    with zipfile.ZipFile(
        zip_path,
        "r"
    ) as archive:

        names = archive.namelist()

        prefix = f"{grade}-sinf/"

        has_grade_folder = any(
            name.startswith(prefix)
            for name in names
        )

        if has_grade_folder:

            archive.extractall(
                destination
            )

        else:

            archive.extractall(
                grade_dir
            )


# ============================================================
# BOOKS TAYYORLASH
# ============================================================

async def prepare_books():

    print(
        "=" * 55,
        flush=True
    )

    print(
        "USTOZ AI BOOKS TEKSHIRILMOQDA",
        flush=True
    )

    print(
        "=" * 55,
        flush=True
    )


    for grade, zip_name in GRADE_ZIPS.items():

        grade_dir = (
            BOOKS_DIR /
            f"{grade}-sinf"
        )


        # ----------------------------------------------------
        # AVVAL MAVJUD PDF LARNI TEKSHIRAMIZ
        # ----------------------------------------------------

        pdf_count = 0

        if grade_dir.exists():

            pdf_count = len(
                list(
                    grade_dir.rglob(
                        "*.pdf"
                    )
                )
            )


        if pdf_count > 0:

            print(
                f"[OK] {grade}-sinf: "
                f"{pdf_count} ta PDF mavjud",
                flush=True
            )

            continue


        # ----------------------------------------------------
        # ZIP YUKLASH
        # ----------------------------------------------------

        zip_path = (
            BOOKS_DIR /
            zip_name
        )

        url = (
            GITHUB_RELEASE +
            zip_name
        )


        print(
            f"[DOWNLOAD] {grade}-sinf "
            f"darsliklari yuklanmoqda...",
            flush=True
        )


        try:

            await asyncio.to_thread(
                download_file,
                url,
                zip_path
            )


            print(
                f"[OK] Yuklandi: "
                f"{zip_name}",
                flush=True
            )


            # ------------------------------------------------
            # ZIP NI TO'G'RI PAPKAGA OCHISH
            # ------------------------------------------------

            await asyncio.to_thread(
                extract_zip,
                zip_path,
                BOOKS_DIR,
                grade
            )


            # ------------------------------------------------
            # NATIJANI TEKSHIRISH
            # ------------------------------------------------

            pdf_count = len(
                list(
                    grade_dir.rglob(
                        "*.pdf"
                    )
                )
            )


            if pdf_count > 0:

                print(
                    f"[OK] {grade}-sinf: "
                    f"{pdf_count} ta PDF ochildi",
                    flush=True
                )

            else:

                print(
                    f"[WARNING] {grade}-sinf "
                    f"ichida PDF topilmadi!",
                    flush=True
                )


            # ------------------------------------------------
            # ZIP NI O'CHIRISH
            # ------------------------------------------------

            try:

                zip_path.unlink()

            except Exception:
                pass


        except Exception as error:

            print(
                f"[ERROR] {grade}-sinf: "
                f"{error}",
                flush=True
            )


    print(
        "=" * 55,
        flush=True
    )


    total_pdf = len(
        list(
            BOOKS_DIR.rglob(
                "*.pdf"
            )
        )
    )


    print(
        f"Jami PDF: {total_pdf}",
        flush=True
    )


    print(
        "=" * 55,
        flush=True
    )


# ============================================================
# FSM
# ============================================================

class TeacherStates(StatesGroup):

    choosing_class = State()

    choosing_subject = State()

    choosing_book = State()

    entering_pages = State()


# ============================================================
# XOTIRA
# ============================================================

USER_DATA = {}

USED_QUESTIONS = {}


# ============================================================
# MATN TOZALASH
# ============================================================

def clean_text(
    text: str
):

    if not text:
        return ""

    text = text.replace(
        "\u00a0",
        " "
    )

    text = text.replace(
        "\r",
        "\n"
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n\s*\n+",
        "\n",
        text
    )

    return text.strip()


def normalize_sentence(
    text: str
):

    text = clean_text(
        text
    )

    text = re.sub(
        r"^\d+$",
        "",
        text
    ).strip()

    return text


# ============================================================
# TELEGRAM HTML XAVFSIZ MATN
# ============================================================

def escape_html(
    text: str
):

    if not text:
        return ""

    text = str(
        text
    )

    text = text.replace(
        "&",
        "&amp;"
    )

    text = text.replace(
        "<",
        "&lt;"
    )

    text = text.replace(
        ">",
        "&gt;"
    )

    return text


# ============================================================
# SINF KLAVIATURASI
# ============================================================

def class_keyboard():

    buttons = []

    for i in range(
        1,
        12
    ):

        buttons.append(
            InlineKeyboardButton(
                text=f"🎓 {i}-sinf",
                callback_data=f"class:{i}"
            )
        )


    rows = []

    for i in range(
        0,
        len(buttons),
        2
    ):

        rows.append(
            buttons[
                i:i + 2
            ]
        )


    return InlineKeyboardMarkup(
        inline_keyboard=rows
    )


# ============================================================
# SUBJECT TOPISH
# ============================================================

def get_subjects(
    grade: int
):

    grade_dir = (
        BOOKS_DIR /
        f"{grade}-sinf"
    )


    if not grade_dir.exists():

        return []


    subjects = []


    for item in sorted(
        grade_dir.iterdir()
    ):

        if item.is_dir():

            pdfs = list(
                item.glob(
                    "*.pdf"
                )
            )

            if pdfs:

                subjects.append(
                    item.name
                )


    for pdf in sorted(
        grade_dir.glob(
            "*.pdf"
        )
    ):

        subjects.append(
            pdf.stem
        )


    return subjects


# ============================================================
# BOOK TOPISH
# ============================================================

def get_books(
    grade: int,
    subject: str
):

    grade_dir = (
        BOOKS_DIR /
        f"{grade}-sinf"
    )


    subject_dir = (
        grade_dir /
        subject
    )


    if (
        subject_dir.exists()
        and subject_dir.is_dir()
    ):

        return sorted(
            subject_dir.glob(
                "*.pdf"
            )
        )


    direct_pdf = (
        grade_dir /
        f"{subject}.pdf"
    )


    if direct_pdf.exists():

        return [
            direct_pdf
        ]


    result = []


    for pdf in grade_dir.glob(
        "*.pdf"
    ):

        if pdf.stem == subject:

            result.append(
                pdf
            )


    return result


# ============================================================
# SAHIFA FORMATINI TEKSHIRISH
# ============================================================

def parse_pages(
    value: str
):

    value = value.strip()


    match = re.fullmatch(
        r"(\d+)\s*-\s*(\d+)",
        value
    )


    if match:

        start = int(
            match.group(1)
        )

        end = int(
            match.group(2)
        )


        if start < 1 or end < 1:

            return None


        if start > end:

            return None


        if end - start + 1 > 100:

            return None


        return start, end


    if value.isdigit():

        page = int(
            value
        )


        if page < 1:

            return None


        return page, page


    return None


# ============================================================
# PDF O'QISH
# ============================================================

def read_pdf(
    pdf_path: Path,
    start_page: int,
    end_page: int
):

    try:

        document = fitz.open(
            pdf_path
        )


        total_pages = len(
            document
        )


        if total_pages == 0:

            document.close()

            return (
                "",
                0,
                "PDF bo'sh."
            )


        if start_page > total_pages:

            document.close()

            return (
                "",
                total_pages,
                f"PDF faqat {total_pages} "
                f"sahifadan iborat."
            )


        real_end = min(
            end_page,
            total_pages
        )


        all_text = []


        for page_number in range(
            start_page - 1,
            real_end
        ):

            page = document[
                page_number
            ]


            text = page.get_text(
                "text"
            )


            if text:

                all_text.append(
                    text
                )


        document.close()


        result = clean_text(
            "\n".join(
                all_text
            )
        )


        return (
            result,
            total_pages,
            None
        )


    except Exception as error:

        return (
            "",
            0,
            f"PDF o'qishda xatolik: {error}"
        )


# ============================================================
# GAP BO'LIB AJRATISH
# ============================================================

def split_into_sentences(
    text: str
):

    text = clean_text(
        text
    )


    if not text:

        return []


    parts = re.split(
        r"(?<=[.!?])\s+|\n+",
        text
    )


    sentences = []


    for part in parts:

        part = normalize_sentence(
            part
        )


        if not part:

            continue


        if len(part) < 35:

            continue


        if len(part) > 500:

            part = part[:500]


        sentences.append(
            part
        )


    return sentences


# ============================================================
# SO'ZLAR
# ============================================================

STOP_WORDS = {
    "va",
    "ham",
    "bu",
    "shu",
    "bir",
    "bilan",
    "uchun",
    "ning",
    "ni",
    "ga",
    "da",
    "dan",
    "dir",
    "esa",
    "yoki",
    "ammo",
    "lekin",
    "ular",
    "u",
    "o",
    "men",
    "sen",
    "biz",
    "siz",
    "bo'ladi",
    "bo'lgan",
    "bo'lib",
    "edi",
    "ekan",
    "emas",
    "juda",
    "eng",
    "har",
    "har bir",
    "qanday",
    "qaysi",
    "barcha",
    "ko'p",
    "kam",
}


def extract_words(
    text: str
):

    words = re.findall(
        r"[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳ0-9]+"
        r"(?:['’ʻ`-][A-Za-zА-Яа-яЁёЎўҚқҒғҲҳ0-9]+)*",
        text
    )


    result = []


    for word in words:

        clean = word.strip()


        if len(clean) < 3:

            continue


        if clean.lower() in STOP_WORDS:

            continue


        result.append(
            clean
        )


    return result


# ============================================================
# MUHIM SO'Z TANLASH
# ============================================================

def choose_answer_word(
    sentence: str
):

    words = extract_words(
        sentence
    )


    if not words:

        return None


    candidates = [
        word
        for word in words
        if 4 <= len(word) <= 25
    ]


    if not candidates:

        candidates = words


    candidates.sort(
        key=lambda x: len(x),
        reverse=True
    )


    top = candidates[
        :min(
            5,
            len(candidates)
        )
    ]


    return random.choice(
        top
    )


# ============================================================
# DISTRAKTORLAR
# ============================================================

def make_distractors(
    correct_answer: str,
    source_text: str
):

    words = extract_words(
        source_text
    )


    unique = []


    correct_lower = (
        correct_answer.lower()
    )


    for word in words:

        if word.lower() == correct_lower:

            continue


        if word.lower() in {
            x.lower()
            for x in unique
        }:

            continue


        if (
            len(word) < 3
            or len(word) > 30
        ):

            continue


        unique.append(
            word
        )


    similar = [
        word
        for word in unique
        if abs(
            len(word)
            - len(correct_answer)
        ) <= 6
    ]


    if len(similar) >= 3:

        unique = similar


    random.shuffle(
        unique
    )


    distractors = []


    for word in unique:

        if word.lower() == correct_lower:

            continue


        if word.lower() in {
            x.lower()
            for x in distractors
        }:

            continue


        distractors.append(
            word
        )


        if len(distractors) == 3:

            break


    return distractors


# ============================================================
# SAVOL HASH
# ============================================================

def question_hash(
    question: str,
    answer: str
):

    raw = (
        question.strip().lower()
        + "|"
        + answer.strip().lower()
    )


    return hashlib.sha256(
        raw.encode(
            "utf-8"
        )
    ).hexdigest()


# ============================================================
# 20 TA TEST GENERATOR
# ============================================================

def generate_questions(
    source_text: str,
    count: int = 20,
    user_id: int = 0
):

    sentences = split_into_sentences(
        source_text
    )


    if len(sentences) < 5:

        return []


    used = USED_QUESTIONS.setdefault(
        user_id,
        set()
    )


    random.shuffle(
        sentences
    )


    questions = []


    for sentence in sentences:

        if len(questions) >= count:

            break


        answer = choose_answer_word(
            sentence
        )


        if not answer:

            continue


        distractors = make_distractors(
            answer,
            source_text
        )


        if len(distractors) < 3:

            continue


        pattern = re.escape(
            answer
        )


        question_text = re.sub(
            pattern,
            "_____",
            sentence,
            count=1
        )


        if question_text == sentence:

            continue


        q_hash = question_hash(
            question_text,
            answer
        )


        if q_hash in used:

            continue


        options = [
            answer,
            distractors[0],
            distractors[1],
            distractors[2],
        ]


        random.shuffle(
            options
        )


        correct_letter = "ABCD"[
            options.index(
                answer
            )
        ]


        question = {

            "question":
                question_text,

            "options": {

                "A":
                    options[0],

                "B":
                    options[1],

                "C":
                    options[2],

                "D":
                    options[3],
            },

            "answer":
                correct_letter,

            "answer_text":
                answer,
        }


        questions.append(
            question
        )


        used.add(
            q_hash
        )


    return questions


# ============================================================
# TESTNI MATNGA AYLANTIRISH
# ============================================================

def question_to_text(
    index: int,
    question: dict
):

    question_text = escape_html(
        question["question"]
    )


    result = []


    result.append(
        f"<b>{index}. "
        f"{question_text}</b>"
    )


    for letter in [
        "A",
        "B",
        "C",
        "D"
    ]:

        option = escape_html(
            question["options"][
                letter
            ]
        )


        result.append(
            f"{letter}) {option}"
        )


    answer = escape_html(
        question["answer_text"]
    )


    result.append(
        f"✅ <b>To'g'ri javob: "
        f"{question['answer']}) "
        f"{answer}</b>"
    )


    return "\n".join(
        result
    )


# ============================================================
# UZUN XABARNI BO'LISH
# ============================================================

async def send_questions(
    message: Message,
    questions: list
):

    for start in range(
        0,
        len(questions),
        5
    ):

        chunk = questions[
            start:start + 5
        ]


        text = []


        for local_index, question in enumerate(
            chunk,
            start=start + 1
        ):

            text.append(
                question_to_text(
                    local_index,
                    question
                )
            )


        await message.answer(
            "\n\n".join(
                text
            )
        )


# ============================================================
# TEST TUGMALARI
# ============================================================

def test_menu_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="🔄 Yana 20 ta",
                    callback_data="again"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📄 Word fayl",
                    callback_data="word"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📚 Boshqa fan",
                    callback_data="subjects"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🎓 Boshqa sinf",
                    callback_data="classes"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🏠 Asosiy menyu",
                    callback_data="home"
                )
            ],
        ]
    )


# ============================================================
# WORD YARATISH
# ============================================================

def create_word_file(
    user_id: int,
    questions: list,
    grade: int,
    subject: str,
    book_name: str,
    page_range: str
):

    document = Document()


    title = document.add_heading(
        "USTOZ AI — TEST",
        level=0
    )


    title.alignment = 1


    p = document.add_paragraph()


    p.add_run(
        f"Sinf: {grade}-sinf\n"
        f"Fan: {subject}\n"
        f"Darslik: {book_name}\n"
        f"Sahifa: {page_range}\n"
        f"Testlar soni: {len(questions)}"
    )


    document.add_paragraph("")


    for index, question in enumerate(
        questions,
        start=1
    ):

        p = document.add_paragraph()


        run = p.add_run(
            f"{index}. "
            f"{question['question']}"
        )


        run.bold = True


        for letter in [
            "A",
            "B",
            "C",
            "D"
        ]:

            document.add_paragraph(
                f"{letter}) "
                f"{question['options'][letter]}"
            )


        answer = document.add_paragraph()


        answer_run = answer.add_run(
            f"To'g'ri javob: "
            f"{question['answer']}) "
            f"{question['answer_text']}"
        )


        answer_run.bold = True


        document.add_paragraph("")


    document.add_heading(
        "Javoblar kaliti",
        level=1
    )


    answer_text = []


    for index, question in enumerate(
        questions,
        start=1
    ):

        answer_text.append(
            f"{index}. "
            f"{question['answer']}"
        )


    document.add_paragraph(
        " | ".join(
            answer_text
        )
    )


    styles = document.styles


    styles["Normal"].font.name = "Arial"

    styles["Normal"].font.size = Pt(11)


    filename = (
        f"ustoz_ai_{user_id}.docx"
    )


    filepath = Path(
        filename
    )


    document.save(
        filepath
    )


    return filepath


# ============================================================
# START
# ============================================================

@dp.message(
    Command("start")
)
async def start_command(
    message: Message,
    state: FSMContext
):

    await state.clear()


    await message.answer(
        "🎓 <b>USTOZ AI</b>\n\n"
        "O'qituvchilar uchun aqlli test generator.\n\n"
        "Men darslikning siz ko'rsatgan "
        "sahifalarini o'qib, shu mavzudan "
        "test tayyorlayman.\n\n"
        "📚 Avval sinfni tanlang:",
        reply_markup=class_keyboard()
    )


    await state.set_state(
        TeacherStates.choosing_class
    )


# ============================================================
# RESTART
# ============================================================

@dp.message(
    Command("restart")
)
async def restart_command(
    message: Message,
    state: FSMContext
):

    await state.clear()


    await message.answer(
        "🔄 <b>Jarayon qayta boshlandi!</b>\n\n"
        "🎓 Sinfni tanlang:",
        reply_markup=class_keyboard()
    )


    await state.set_state(
        TeacherStates.choosing_class
    )


# ============================================================
# HELP
# ============================================================

@dp.message(
    Command("help")
)
async def help_command(
    message: Message
):

    await message.answer(
        "📖 <b>USTOZ AI yordam</b>\n\n"
        "1️⃣ /start — botni boshlash\n"
        "2️⃣ Sinfni tanlash\n"
        "3️⃣ Fanni tanlash\n"
        "4️⃣ Darslikni tanlash\n"
        "5️⃣ Sahifa oralig'ini yozish\n"
        "   Masalan: <code>10-20</code>\n"
        "6️⃣ Bot 20 ta test tayyorlaydi\n"
        "7️⃣ Testni Word formatida olish mumkin\n\n"
        "🔄 /restart — jarayonni boshidan boshlash\n"
        "❓ /help — yordam"
    )


# ============================================================
# JOIN
# ============================================================

@dp.message(
    Command("join")
)
async def join_command(
    message: Message
):

    await message.answer(
        "🤖 <b>USTOZ AI</b>\n\n"
        "Bu bot o'qituvchilarga darslik asosida "
        "test tayyorlashda yordam beradi.\n\n"
        "📚 Darslik → Sahifa → Test → Word"
    )


# ============================================================
# CLASS TANLASH
# ============================================================

@dp.callback_query(
    TeacherStates.choosing_class,
    F.data.startswith("class:")
)
async def class_selected(
    callback: CallbackQuery,
    state: FSMContext
):

    grade = int(
        callback.data.split(":")[1]
    )


    subjects = get_subjects(
        grade
    )


    await state.update_data(
        grade=grade,
        subjects=subjects
    )


    if not subjects:

        await callback.message.edit_text(
            f"🎓 <b>{grade}-sinf</b>\n\n"
            "📚 Bu sinf uchun darslik topilmadi.\n\n"
            "Iltimos, birozdan keyin qayta urinib ko'ring.\n\n"
            "🔄 /restart"
        )


        await callback.answer()

        return


    buttons = []


    for index, subject in enumerate(
        subjects
    ):

        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"📚 {subject}",
                    callback_data=f"subject:{index}"
                )
            ]
        )


    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Sinflar",
                callback_data="classes"
            )
        ]
    )


    await callback.message.edit_text(
        f"🎓 <b>{grade}-sinf</b>\n\n"
        "📚 Fanni tanlang:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
    )


    await state.set_state(
        TeacherStates.choosing_subject
    )


    await callback.answer()


# ============================================================
# SUBJECT TANLASH
# ============================================================

@dp.callback_query(
    TeacherStates.choosing_subject,
    F.data.startswith("subject:")
)
async def subject_selected(
    callback: CallbackQuery,
    state: FSMContext
):

    data = await state.get_data()


    subjects = data.get(
        "subjects",
        []
    )


    grade = data.get(
        "grade"
    )


    try:

        index = int(
            callback.data.split(":")[1]
        )


        subject = subjects[
            index
        ]


    except (
        ValueError,
        IndexError
    ):

        await callback.answer(
            "Fan topilmadi.",
            show_alert=True
        )

        return


    books = get_books(
        grade,
        subject
    )


    await state.update_data(
        subject=subject,
        books=[
            str(x)
            for x in books
        ]
    )


    if not books:

        await callback.message.edit_text(
            f"📚 <b>{subject}</b>\n\n"
            "Bu fan uchun darslik PDF topilmadi.\n\n"
            "Iltimos, /restart qiling."
        )


        await callback.answer()

        return


    buttons = []


    for i, book in enumerate(
        books
    ):

        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"📖 {book.stem}",
                    callback_data=f"book:{i}"
                )
            ]
        )


    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Fanlar",
                callback_data="subjects"
            )
        ]
    )


    await callback.message.edit_text(
        f"🎓 {grade}-sinf\n"
        f"📚 <b>{subject}</b>\n\n"
        "📖 Darslikni tanlang:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
    )


    await state.set_state(
        TeacherStates.choosing_book
    )


    await callback.answer()


# ============================================================
# BOOK TANLASH
# ============================================================

@dp.callback_query(
    TeacherStates.choosing_book,
    F.data.startswith("book:")
)
async def book_selected(
    callback: CallbackQuery,
    state: FSMContext
):

    data = await state.get_data()


    books = data.get(
        "books",
        []
    )


    subject = data.get(
        "subject"
    )


    grade = data.get(
        "grade"
    )


    try:

        index = int(
            callback.data.split(":")[1]
        )


        book_path = Path(
            books[index]
        )


    except (
        ValueError,
        IndexError
    ):

        await callback.answer(
            "Darslik topilmadi.",
            show_alert=True
        )

        return


    await state.update_data(
        book=str(book_path),
        book_name=book_path.stem
    )


    await callback.message.edit_text(
        f"🎓 <b>{grade}-sinf</b>\n"
        f"📚 <b>{subject}</b>\n"
        f"📖 <b>{book_path.stem}</b>\n\n"
        "📄 Qaysi sahifalardan test kerak?\n\n"
        "Masalan:\n"
        "<code>10-20</code>\n\n"
        "Yoki bitta sahifa:\n"
        "<code>15</code>"
    )


    await state.set_state(
        TeacherStates.entering_pages
    )


    await callback.answer()


# ============================================================
# PAGE INPUT
# ============================================================

@dp.message(
    TeacherStates.entering_pages
)
async def pages_entered(
    message: Message,
    state: FSMContext
):

    value = (
        message.text or ""
    ).strip()


    parsed = parse_pages(
        value
    )


    if not parsed:

        await message.answer(
            "❌ Sahifa formati noto'g'ri.\n\n"
            "Masalan:\n"
            "<code>10-20</code>\n"
            "yoki\n"
            "<code>15</code>\n\n"
            "Maksimal oralig': 100 sahifa."
        )

        return


    start_page, end_page = parsed


    data = await state.get_data()


    book = Path(
        data.get(
            "book",
            ""
        )
    )


    grade = data.get(
        "grade"
    )


    subject = data.get(
        "subject"
    )


    book_name = data.get(
        "book_name"
    )


    if not book.exists():

        await message.answer(
            "❌ Darslik PDF topilmadi.\n"
            "Iltimos, /restart qiling."
        )

        return


    await message.answer(
        "📖 Darslik o'qilmoqda...\n"
        f"📄 Sahifalar: {start_page}-{end_page}\n\n"
        "⏳ Biroz kuting..."
    )


    source_text, total_pages, error = read_pdf(
        book,
        start_page,
        end_page
    )


    if error:

        await message.answer(
            f"❌ {escape_html(error)}"
        )

        return


    if not source_text.strip():

        await message.answer(
            "❌ Tanlangan sahifalardan matn topilmadi.\n\n"
            "Bu PDF skanerlangan rasm bo'lishi mumkin. "
            "Bunday PDF uchun OCR kerak bo'ladi.\n\n"
            "Boshqa matnli PDF bilan sinab ko'ring."
        )

        return


    if end_page > total_pages:

        await message.answer(
            f"ℹ️ Darslikda {total_pages} ta sahifa bor.\n"
            f"Siz so'ragan {end_page}-sahifa mavjud emas.\n"
            f"Shuning uchun {start_page}-{total_pages} "
            "oralig'i ishlatildi."
        )


    await message.answer(
        "🧠 <b>20 ta test tayyorlanmoqda...</b>\n\n"
        "📚 Testlar faqat tanlangan sahifalardagi "
        "matndan tuziladi."
    )


    user_id = message.from_user.id


    questions = generate_questions(
        source_text=source_text,
        count=20,
        user_id=user_id
    )


    if len(questions) < 20:

        await message.answer(
            f"⚠️ Bu sahifalardan faqat "
            f"<b>{len(questions)}</b> ta yangi test "
            "tuzish mumkin bo'ldi.\n\n"
            "20 ta test kerak bo'lsa, sahifa oralig'ini "
            "kengaytiring yoki boshqa sahifalarni tanlang."
        )


    if not questions:

        await message.answer(
            "❌ Test yaratish uchun yetarli matn topilmadi.\n\n"
            "Ko'proq sahifa tanlang."
        )

        return


    USER_DATA[user_id] = {

        "source_text":
            source_text,

        "questions":
            questions,

        "grade":
            grade,

        "subject":
            subject,

        "book":
            str(book),

        "book_name":
            book_name,

        "page_range":
            (
                f"{start_page}-"
                f"{min(end_page, total_pages)}"
            ),
    }


    await state.update_data(

        source_text=
            source_text,

        questions=
            questions,

        grade=
            grade,

        subject=
            subject,

        book=
            str(book),

        book_name=
            book_name,

        page_range=
            (
                f"{start_page}-"
                f"{min(end_page, total_pages)}"
            )
    )


    await send_questions(
        message,
        questions
    )


    await message.answer(
        "🎉 <b>Testlar tayyor!</b>\n\n"
        "Quyidagi tugmalardan foydalanishingiz mumkin:",
        reply_markup=test_menu_keyboard()
    )


# ============================================================
# YANA 20 TA
# ============================================================

@dp.callback_query(
    F.data == "again"
)
async def again_questions(
    callback: CallbackQuery,
    state: FSMContext
):

    user_id = callback.from_user.id


    data = USER_DATA.get(
        user_id
    )


    if not data:

        data = await state.get_data()


    source_text = data.get(
        "source_text"
    )


    if not source_text:

        await callback.message.answer(
            "❌ Eski test ma'lumotlari topilmadi.\n"
            "Iltimos, /restart qiling."
        )


        await callback.answer()

        return


    await callback.message.answer(
        "🔄 <b>Yangi 20 ta test tayyorlanmoqda...</b>"
    )


    questions = generate_questions(
        source_text=source_text,
        count=20,
        user_id=user_id
    )


    if not questions:

        await callback.message.answer(
            "⚠️ Bu sahifalardan boshqa yangi savollar "
            "tuzish qiyin bo'ldi.\n\n"
            "📄 Boshqa sahifalarni tanlang."
        )


        await callback.answer()

        return


    data["questions"] = questions


    USER_DATA[user_id] = data


    await state.update_data(
        questions=questions
    )


    await send_questions(
        callback.message,
        questions
    )


    await callback.message.answer(
        "✅ Yangi testlar tayyor!",
        reply_markup=test_menu_keyboard()
    )


    await callback.answer()


# ============================================================
# WORD
# ============================================================

@dp.callback_query(
    F.data == "word"
)
async def word_callback(
    callback: CallbackQuery,
    state: FSMContext
):

    user_id = callback.from_user.id


    data = USER_DATA.get(
        user_id
    )


    if not data:

        data = await state.get_data()


    questions = data.get(
        "questions"
    )


    if not questions:

        await callback.answer(
            "Testlar topilmadi.",
            show_alert=True
        )

        return


    await callback.message.answer(
        "📄 <b>Word fayl tayyorlanmoqda...</b>"
    )


    try:

        filepath = create_word_file(
            user_id=user_id,
            questions=questions,
            grade=data.get(
                "grade"
            ),
            subject=data.get(
                "subject"
            ),
            book_name=data.get(
                "book_name"
            ),
            page_range=data.get(
                "page_range"
            )
        )


        document = FSInputFile(
            filepath
        )


        await callback.message.answer_document(
            document=document,
            caption=(
                "📄 <b>USTOZ AI TEST</b>\n\n"
                "Word fayl tayyor.\n"
                "Uni yuklab olib, o'zgartirishingiz "
                "yoki chop etishingiz mumkin."
            )
        )


        try:

            filepath.unlink()

        except Exception:
            pass


    except Exception as error:

        await callback.message.answer(
            "❌ Word yaratishda xatolik:\n"
            f"<code>{escape_html(error)}</code>"
        )


    await callback.answer()


# ============================================================
# FANLAR
# ============================================================

@dp.callback_query(
    F.data == "subjects"
)
async def back_to_subjects(
    callback: CallbackQuery,
    state: FSMContext
):

    data = await state.get_data()


    grade = data.get(
        "grade"
    )


    if not grade:

        await callback.answer()

        return


    subjects = get_subjects(
        grade
    )


    await state.update_data(
        subjects=subjects
    )


    if not subjects:

        await callback.message.edit_text(
            f"🎓 {grade}-sinf\n\n"
            "📚 Darsliklar topilmadi."
        )


        await callback.answer()

        return


    buttons = []


    for index, subject in enumerate(
        subjects
    ):

        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"📚 {subject}",
                    callback_data=f"subject:{index}"
                )
            ]
        )


    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Sinflar",
                callback_data="classes"
            )
        ]
    )


    await callback.message.edit_text(
        f"🎓 <b>{grade}-sinf</b>\n\n"
        "📚 Fanni tanlang:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
    )


    await state.set_state(
        TeacherStates.choosing_subject
    )


    await callback.answer()


# ============================================================
# SINFLAR
# ============================================================

@dp.callback_query(
    F.data == "classes"
)
async def back_to_classes(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.clear()


    await callback.message.edit_text(
        "🎓 <b>Sinfni tanlang:</b>",
        reply_markup=class_keyboard()
    )


    await state.set_state(
        TeacherStates.choosing_class
    )


    await callback.answer()


# ============================================================
# HOME
# ============================================================

@dp.callback_query(
    F.data == "home"
)
async def home_callback(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.clear()


    await callback.message.edit_text(
        "🏠 <b>USTOZ AI</b>\n\n"
        "O'qituvchi uchun test generator.\n\n"
        "🎓 Sinfni tanlang:",
        reply_markup=class_keyboard()
    )


    await state.set_state(
        TeacherStates.choosing_class
    )


    await callback.answer()


# ============================================================
# UNKNOWN MESSAGE
# ============================================================

@dp.message()
async def unknown_message(
    message: Message
):

    await message.answer(
        "🤖 Men sizni tushunmadim.\n\n"
        "Boshlash uchun /start ni bosing.\n"
        "Yordam: /help\n"
        "Qayta boshlash: /restart"
    )


# ============================================================
# MAIN
# ============================================================

async def main():

    start_render_server()


    print(
        "=" * 55,
        flush=True
    )


    print(
        "USTOZ AI ISHGA TAYYORLANMOQDA",
        flush=True
    )


    print(
        "=" * 55,
        flush=True
    )


    await prepare_books()


    print(
        "=" * 55,
        flush=True
    )


    print(
        "USTOZ AI ISHGA TUSHDI",
        flush=True
    )


    print(
        "=" * 55,
        flush=True
    )


    await dp.start_polling(
        bot
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )
