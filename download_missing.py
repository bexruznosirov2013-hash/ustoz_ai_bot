import requests
from pathlib import Path

BASE = Path("books")

BOOKS = {
    "5-sinf": {
        "ona_tili": "https://old.eduportal.uz/Umumiyfiles/darsliklar/5/ona_tili_5_uzb.pdf",
    },

    "8-sinf": {
        "kimyo": "https://old.eduportal.uz/Umumiyfiles/darsliklar/8/kimyo_8_uzb.pdf",
        "geografiya": "https://old.eduportal.uz/Umumiyfiles/darsliklar/8/ijtimoiy_iqtisodiy_geografiya_8_uzb.pdf",
    },

    "9-sinf": {
        "kimyo": "https://old.eduportal.uz/Umumiyfiles/darsliklar/9/kimyo_9_uzb.pdf",
        "ingliz_tili": "https://old.eduportal.uz/Umumiyfiles/darsliklar/9/ingliz_tili_9_darslik.pdf",
    },

    "11-sinf": {
        "kimyo": "https://old.eduportal.uz/Umumiyfiles/darsliklar/11/kimyo_11_uzb.pdf",
        "geografiya": "https://old.eduportal.uz/Umumiyfiles/darsliklar/11/geografiya_11_uzb.pdf",
    },
}


def download(url, output):
    try:
        print(f"\n⬇️ {output.name}")
        print(url)

        r = requests.get(
            url,
            timeout=60,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        if r.status_code == 200 and len(r.content) > 10000:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(r.content)

            if r.content[:4] == b"%PDF":
                print(f"✅ SAQLANDI: {output}")
                return True
            else:
                output.unlink(missing_ok=True)
                print("❌ Bu PDF emas")
                return False

        print(f"❌ Yuklanmadi: HTTP {r.status_code}")
        return False

    except Exception as e:
        print(f"❌ XATO: {e}")
        return False


def main():
    print("=" * 60)
    print("        USTOZ AI — KITOBLARNI YUKLASH")
    print("=" * 60)

    ok = 0
    fail = 0

    for grade, books in BOOKS.items():
        grade_dir = BASE / grade
        grade_dir.mkdir(parents=True, exist_ok=True)

        for name, url in books.items():
            filename = f"{name}_{grade.split('-')[0]}_uzb.pdf"
            output = grade_dir / filename

            if output.exists() and output.stat().st_size > 10000:
                print(f"⏭️ BOR: {output}")
                continue

            if download(url, output):
                ok += 1
            else:
                fail += 1

    print("\n" + "=" * 60)
    print("YAKUN")
    print("=" * 60)
    print(f"✅ Yuklangan: {ok}")
    print(f"❌ Yuklanmagan: {fail}")
    print("=" * 60)


if __name__ == "__main__":
    main()