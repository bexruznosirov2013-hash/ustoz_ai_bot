import requests
from pathlib import Path
from urllib.parse import quote
import re
import time

BOOKS_DIR = Path("books")
MISSING_FILE = Path("missing_books.txt")

BASE_URLS = [
    "https://old.eduportal.uz/Umumiyfiles/darsliklar/{grade}/{filename}",
    "https://old.eduportal.uz/Umumiyfiles/darsliklar/{grade}/{filename}",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/155.0 Safari/537.36"
}

# missing_books.txt ichidagi fan nomlarini haqiqiy fayl nomlariga moslash
ALIASES = {
    "ona_tili_va_oqish_savodxonligi": [
        "ona_tili_va_o'qish_savodxonligi",
        "ona_tili_va_oqish_savodxonligi",
        "ona_tili_va_o'qish_savodxonligi",
        "ona_tili_va_oqish_savodxonligi"
    ],

    "tabiiy_fan": [
        "tabiiy_fan",
        "tabiiy_fanlar",
        "tabiiy_fan_"
    ],

    "adabiyot": [
        "adabiyot"
    ],

    "texnologiya": [
        "texnologiya"
    ],

    "tarbiya": [
        "tarbiya"
    ],

    "jismoniy_tarbiya": [
        "jismoniy_tarbiya"
    ],

    "geografiya": [
        "geografiya"
    ],

    "ingliz_tili": [
        "ingliz_tili",
        "english"
    ],

    "kimyo": [
        "kimyo",
        "organik_kimyo",
        "anorganik_kimyo"
    ],

    "chqbt": [
        "chqbt",
        "chaqiruvga_qadar_boshlangich_tayyorgarlik",
        "chaqiruvga_qadar_boshlang'ich_tayyorgarlik",
        "chaqiruvga_qadar_boshlangich_tayyorlov"
    ],

    "algebra_va_analiz_asoslari": [
        "algebra_va_analiz_asoslari",
        "algebra_analiz_asoslari"
    ],

    "geometriya": [
        "geometriya"
    ]
}


def clean_name(text):
    text = text.lower()
    text = text.replace("'", "")
    text = text.replace("ʻ", "")
    text = text.replace("’", "")
    text = text.replace("‘", "")
    text = text.replace("`", "")
    text = re.sub(r"[^a-z0-9_]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def possible_filenames(subject, grade):
    names = ALIASES.get(subject, [subject])

    result = []

    for name in names:
        name = clean_name(name)

        # asosiy variant
        result.append(f"{name}_{grade}_uzb.pdf")

        # ba'zi kitoblarda 1qism / 2qism bo'lishi mumkin
        result.append(f"{name}_1qism_{grade}_uzb.pdf")
        result.append(f"{name}_2qism_{grade}_uzb.pdf")
        result.append(f"{name}_1_qism_{grade}_uzb.pdf")
        result.append(f"{name}_2_qism_{grade}_uzb.pdf")

    # takrorlarni olib tashlash
    return list(dict.fromkeys(result))


def download_file(url, output):
    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=25,
            allow_redirects=True
        )

        if r.status_code == 200:
            content = r.content

            # haqiqiy PDF ekanini tekshirish
            if content[:4] == b"%PDF":
                output.write_bytes(content)
                return True

    except Exception:
        pass

    return False


def try_download(grade, subject):
    folder = BOOKS_DIR / f"{grade}-sinf"
    folder.mkdir(parents=True, exist_ok=True)

    filenames = possible_filenames(subject, grade)

    for filename in filenames:

        # Bir nechta nomlash variantini sinab ko'ramiz
        variants = [
            filename,
            filename.replace("_uzb", "_lotin"),
            filename.replace("_uzb", ""),
        ]

        for variant in variants:

            url = (
                f"https://old.eduportal.uz/"
                f"Umumiyfiles/darsliklar/{grade}/{variant}"
            )

            output = folder / variant

            print(f"   🔎 {variant}")

            if download_file(url, output):
                print(f"   ✅ TOPILDI: {output}")
                return output

    return None


def read_missing():
    if not MISSING_FILE.exists():
        print("❌ missing_books.txt topilmadi!")
        return []

    result = []

    text = MISSING_FILE.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if "→" not in line:
            continue

        left, right = line.split("→", 1)

        grade_match = re.search(r"(\d+)", left)

        if not grade_match:
            continue

        grade = int(grade_match.group(1))
        subject = right.strip()

        result.append((grade, subject))

    return result


def main():

    print("=" * 60)
    print("       USTOZ AI — YETISHMAYOTGAN KITOBLAR")
    print("=" * 60)

    missing = read_missing()

    if not missing:
        print("❌ Yetishmayotgan kitoblar topilmadi.")
        return

    print(f"\n📚 Qidiriladigan kitoblar: {len(missing)}")
    print()

    found = []
    not_found = []

    for index, (grade, subject) in enumerate(missing, 1):

        print("=" * 60)
        print(f"[{index}/{len(missing)}] {grade}-sinf → {subject}")

        # Jismoniy tarbiya uchun PDF mavjud bo'lmasa
        # uni xato deb hisoblamaymiz
        if subject == "jismoniy_tarbiya":
            result = try_download(grade, subject)

            if result:
                found.append((grade, subject, result))
            else:
                print("   ⚠️ Uzbek PDF topilmadi — o'tkazib yuborildi.")
            continue

        result = try_download(grade, subject)

        if result:
            found.append((grade, subject, result))
        else:
            print("   ❌ TOPILMADI")
            not_found.append((grade, subject))

        time.sleep(0.5)

    print()
    print("=" * 60)
    print("                 NATIJA")
    print("=" * 60)

    print(f"✅ Yangi yuklangan: {len(found)}")
    print(f"❌ Topilmagan:      {len(not_found)}")
    print()

    if found:
        print("YUKLANGANLAR:")
        for grade, subject, path in found:
            print(f"  ✅ {grade}-sinf → {subject}")
            print(f"     {path}")

    print()

    if not_found:
        print("HALI TOPILMAGANLAR:")
        for grade, subject in not_found:
            print(f"  ❌ {grade}-sinf → {subject}")

        Path("still_missing_books.txt").write_text(
            "\n".join(
                f"{grade}-sinf → {subject}"
                for grade, subject in not_found
            ),
            encoding="utf-8"
        )

        print()
        print("📄 Ro'yxat saqlandi:")
        print("   still_missing_books.txt")

    print()
    print("=" * 60)
    print("TUGADI")
    print("=" * 60)


if __name__ == "__main__":
    main()
  