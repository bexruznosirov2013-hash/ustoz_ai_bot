from pathlib import Path

BOOKS = {
    1: [
        "ona_tili_va_oqish_savodxonligi",
        "tabiiy_fan",
    ],
    2: [
        "ona_tili_va_oqish_savodxonligi",
        "tabiiy_fan",
    ],
    3: [
        "ona_tili_va_oqish_savodxonligi",
        "tabiiy_fan",
    ],
    4: [
        "ona_tili_va_oqish_savodxonligi",
        "tabiiy_fan",
        "tarbiya",
    ],
    5: [
        "texnologiya",
        "tarbiya",
    ],
    6: [
        "tarbiya",
    ],
    7: [
        "tarbiya",
    ],
    8: [
        "geografiya",
        "ingliz_tili",
        "tarbiya",
    ],
    9: [
        "ingliz_tili",
        "tarbiya",
    ],
    11: [
        "algebra_va_analiz_asoslari",
        "geometriya",
        "kimyo",
        "geografiya",
    ],
}

ROOT = Path("books")

missing = []
found = []

for grade, subjects in BOOKS.items():
    folder = ROOT / f"{grade}-sinf"

    for subject in subjects:
        files = list(folder.glob(f"*{grade}_uzb.pdf"))

        exists = False

        for file in files:
            name = file.stem.lower()

            if subject == "ona_tili_va_oqish_savodxonligi":
                if "ona_tili" in name and ("oqish" in name or "o'qish" in name):
                    exists = True

            elif subject == "tabiiy_fan":
                if "tabiiy" in name:
                    exists = True

            elif subject == "algebra_va_analiz_asoslari":
                if "algebra" in name:
                    exists = True

            elif subject == "geometriya":
                if "geometriya" in name:
                    exists = True

            elif subject in name:
                exists = True

        if exists:
            found.append(f"{grade}-sinf -> {subject}")
        else:
            missing.append(f"{grade}-sinf -> {subject}")

print()
print("=" * 60)
print("TOPILGANLAR")
print("=" * 60)

for x in found:
    print("✅", x)

print()
print("=" * 60)
print("HALI YETISHMAYOTGANLAR")
print("=" * 60)

for x in missing:
    print("❌", x)

Path("still_missing_books.txt").write_text(
    "\n".join(missing),
    encoding="utf-8"
)

print()
print("=" * 60)
print(f"✅ Bor: {len(found)}")
print(f"❌ Yetishmaydi: {len(missing)}")
print("=" * 60)
print()
print("📄 still_missing_books.txt yangilandi.")