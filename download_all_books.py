import requests, re
from pathlib import Path

BASE = Path("books")
S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0"

def save(url, path):
    try:
        r = S.get(url, timeout=60)
        if r.status_code == 200 and r.content[:4] == b"%PDF" and len(r.content) > 10000:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(r.content)
            print("✅", path)
            return True
        print("❌", r.status_code, url)
    except Exception as e:
        print("❌", e)
    return False

# 1–3-sinf Ona tili va o‘qish savodxonligi
pages = {
    1: "https://savodxonustoz.uz/101-oqish-kursi/darsliklar?category=ona-tili-va-oqish-savodxonligi&sinf=1",
    2: "https://savodxonustoz.uz/101-oqish-kursi/darsliklar?category=ona-tili-va-oqish-savodxonligi&sinf=2",
    3: "https://savodxonustoz.uz/101-oqish-kursi/darsliklar?category=ona-tili-va-oqish-savodxonligi&sinf=3",
}

for grade, page in pages.items():
    try:
        html = S.get(page, timeout=60).text
        links = re.findall(r'href=["\']([^"\']+\.pdf[^"\']*)["\']', html, re.I)

        seen = set()
        n = 0
        for link in links:
            if link.startswith("/"):
                link = "https://savodxonustoz.uz" + link
            elif link.startswith("http://"):
                link = "https://" + link[7:]

            if link in seen:
                continue
            seen.add(link)

            low = link.lower()
            if "1-qism" in low or "1_qism" in low:
                part = 1
            elif "2-qism" in low or "2_qism" in low:
                part = 2
            else:
                continue

            out = BASE / f"{grade}-sinf" / "ona_tili_va_oqish_savodxonligi" / f"{part}-qism.pdf"
            if save(link, out):
                n += 1

        print(f"📚 {grade}-sinf: {n} ta qism")
    except Exception as e:
        print("❌ Sahifa xatosi:", e)

# Aniq ishlaydigan Eduportal manzillari va ehtimoliy nomlar
candidates = {
    1: [
        ("alifbe", "https://old.eduportal.uz/Umumiyfiles/darsliklar/1/alifbe_1_uzb.pdf"),
    ],
    6: [
        ("geografiya", "https://old.eduportal.uz/Umumiyfiles/darsliklar/6/geografiya_6_uzb.pdf"),
    ],
    8: [
        ("kimyo", "https://old.eduportal.uz/Umumiyfiles/darsliklar/8/kimyo_8_uzb.pdf"),
        ("geografiya", "https://old.eduportal.uz/Umumiyfiles/darsliklar/8/ijtimoiy_iqtisodiy_geografiya_8_uzb.pdf"),
    ],
    9: [
        ("ingliz_tili", "https://old.eduportal.uz/Umumiyfiles/darsliklar/9/ingliz_tili_9_darslik.pdf"),
    ],
    10: [
        ("geografiya", "https://old.eduportal.uz/Umumiyfiles/darsliklar/10/geografiya_10_uzb.pdf"),
    ],
}

for grade, books in candidates.items():
    for name, url in books:
        out = BASE / f"{grade}-sinf" / f"{name}_{grade}_uzb.pdf"
        if out.exists() and out.stat().st_size > 10000:
            print("⏭️ BOR:", out)
        else:
            save(url, out)

# 11-sinfda eski Eduportal nomlari 404 bo‘lgani uchun
# barcha mavjud 11-sinf PDF katalogini tekshirishga urinadi.
# Bu yerda mavjud fayllar saqlanib qoladi.
for name, urls in {
    "kimyo": [
        "https://old.eduportal.uz/Umumiyfiles/darsliklar/11/umumiy_kimyo_11_uzb.pdf",
        "https://old.eduportal.uz/Umumiyfiles/darsliklar/11/organik_kimyo_11_uzb.pdf",
        "https://old.eduportal.uz/Umumiyfiles/darsliklar/11/kimyo_11_uzb.pdf",
    ],
    "geografiya": [
        "https://old.eduportal.uz/Umumiyfiles/darsliklar/11/geografiya_11_uzb.pdf",
        "https://old.eduportal.uz/Umumiyfiles/darsliklar/11/ozbekiston_geografiyasi_11_uzb.pdf",
    ],
}.items():
    out = BASE / "11-sinf" / f"{name}_11_uzb.pdf"
    if out.exists() and out.stat().st_size > 10000:
        print("⏭️ BOR:", out)
        continue
    for url in urls:
        if save(url, out):
            break

print("\n==========================================")
print("📚 KITOBLAR TEKSHIRILDI / YUKLANDI")
print("==========================================")

total = 0
for grade in sorted(BASE.glob("*-sinf"), key=lambda x: int(x.name.split("-")[0])):
    files = list(grade.rglob("*.pdf"))
    print(f"{grade.name}: {len(files)} ta PDF")
    total += len(files)

print("JAMI PDF:", total)
