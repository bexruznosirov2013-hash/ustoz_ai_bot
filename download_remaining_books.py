import requests
from pathlib import Path

BOOKS = {
    1: {
        "ona_tili_va_oqish_savodxonligi": [
            "ona_tili_va_o'qish_savodxonligi_1_uzb.pdf",
            "ona_tili_va_o'qish_savodxonligi_1.pdf",
            "ona_tili_va_oqish_savodxonligi_1_uzb.pdf",
        ],
        "tabiiy_fan": [
            "tabiiy_fan_1_uzb.pdf",
            "tabiiy_fan_1.pdf",
        ],
    },

    2: {
        "ona_tili_va_oqish_savodxonligi": [
            "ona_tili_va_o'qish_savodxonligi_2_uzb.pdf",
            "ona_tili_va_o'qish_savodxonligi_2.pdf",
            "ona_tili_va_oqish_savodxonligi_2_uzb.pdf",
        ],
        "tabiiy_fan": [
            "tabiiy_fan_2_uzb.pdf",
            "tabiiy_fan_2.pdf",
        ],
    },

    3: {
        "ona_tili_va_oqish_savodxonligi": [
            "ona_tili_va_o'qish_savodxonligi_3_uzb.pdf",
            "ona_tili_va_o'qish_savodxonligi_3.pdf",
            "ona_tili_va_oqish_savodxonligi_3_uzb.pdf",
        ],
        "tabiiy_fan": [
            "tabiiy_fan_3_uzb.pdf",
            "tabiiy_fan_3.pdf",
        ],
    },

    4: {
        "ona_tili_va_oqish_savodxonligi": [
            "ona_tili_va_o'qish_savodxonligi_4_uzb.pdf",
            "ona_tili_va_o'qish_savodxonligi_4.pdf",
            "ona_tili_va_oqish_savodxonligi_4_uzb.pdf",
        ],
        "tabiiy_fan": [
            "tabiiy_fan_4_uzb.pdf",
            "tabiiy_fan_4.pdf",
        ],
        "tarbiya": [
            "tarbiya_4_uzb.pdf",
            "tarbiya_4.pdf",
        ],
    },

    5: {
        "texnologiya": [
            "texnologiya_5_uzb.pdf",
            "texnologiya_5.pdf",
        ],
        "tarbiya": [
            "tarbiya_5_uzb.pdf",
            "tarbiya_5.pdf",
        ],
    },

    6: {
        "tarbiya": [
            "tarbiya_6_uzb.pdf",
            "tarbiya_6.pdf",
        ],
    },

    7: {
        "tarbiya": [
            "tarbiya_7_uzb.pdf",
            "tarbiya_7.pdf",
        ],
    },

    8: {
        "geografiya": [
            "geografiya_8_uzb.pdf",
            "geografiya_8.pdf",
            "geografiya_8_darslik.pdf",
        ],
        "tarbiya": [
            "tarbiya_8_uzb.pdf",
            "tarbiya_8.pdf",
        ],
    },

    9: {
        "ingliz_tili": [
            "ingliz_tili_9_darslik.pdf",
            "ingliz_tili_9_uzb.pdf",
            "ingliz_tili_9.pdf",
        ],
        "tarbiya": [
            "tarbiya_9_uzb.pdf",
            "tarbiya_9.pdf",
        ],
    },

    11: {
        "kimyo": [
            "kimyo_11_uzb.pdf",
            "kimyo_11.pdf",
        ],
        "geografiya": [
            "geografiya_11_uzb.pdf",
            "geografiya_11.pdf",
        ],
    },
}

BASE = "https://old.eduportal.uz/Umumiyfiles/darsliklar"

session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0"

downloaded = 0
failed = 0

for grade, subjects in BOOKS.items():

    folder = Path("books") / f"{grade}-sinf"
    folder.mkdir(parents=True, exist_ok=True)

    for subject, filenames in subjects.items():

        target = folder / f"{subject}_{grade}_uzb.pdf"

        if target.exists() and target.stat().st_size > 10000:
            print(f"⏭️ BOR: {grade}-sinf -> {subject}")
            continue

        found = False

        for filename in filenames:

            url = f"{BASE}/{grade}/{filename}"

            try:
                print(f"🔎 Tekshirilmoqda: {url}")

                response = session.get(
                    url,
                    timeout=30,
                    allow_redirects=True
                )

                if response.status_code == 200:
                    data = response.content

                    if data[:4] == b"%PDF":

                        target.write_bytes(data)

                        print(f"✅ YUKLANDI: {grade}-sinf -> {subject}")
                        print(f"   {target}")

                        downloaded += 1
                        found = True
                        break

            except Exception as e:
                print(f"⚠️ Xato: {e}")

        if not found:
            print(f"❌ TOPILMADI: {grade}-sinf -> {subject}")
            failed += 1

print()
print("=" * 60)
print("NATIJA")
print("=" * 60)
print(f"✅ Yangi yuklandi: {downloaded}")
print(f"❌ Topilmadi:      {failed}")
print("=" * 60)