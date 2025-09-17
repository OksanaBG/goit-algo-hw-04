"""
Рекурсивно копіює всі файли з вихідної директорії у нову директорію призначення,
розкладаючи їх у підтеки за розширенням файлів.

Використання:
  python sort_copy.py /path/to/src [/path/to/dest]

- Якщо шлях до директорії призначення не передано, буде створено теку "dist"
  на одному рівні з вихідною директорією.
"""

from __future__ import annotations
import argparse
import logging
from pathlib import Path
import shutil
from collections import Counter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Рекурсивне копіювання й сортування файлів за розширенням."
    )
    parser.add_argument("src", type=Path, nargs="?", help="Шлях до вихідної директорії")
    parser.add_argument(
        "dest",
        nargs="?",
        type=Path,
        help='Шлях до директорії призначення (за замовчуванням — тека "dist" поряд із вихідною)',
    )
    args = parser.parse_args()

    # Якщо аргументи не передані — питаємо користувача
    if args.src is None:
        src_input = input("Введіть шлях до вихідної директорії: ").strip()
        args.src = Path(src_input)

    if args.dest is None:
        dest_input = input("Введіть шлях до директорії призначення (Enter = dist): ").strip()
        args.dest = Path(dest_input) if dest_input else None

    return args


def safe_extension(p: Path) -> str:
    """Повертає розширення без крапки в нижньому регістрі; 'no_ext' якщо відсутнє."""
    if not p.is_file():
        return "no_ext"
    ext = p.suffix.lower().lstrip(".")  # останній суфікс (.tar.gz -> gz)
    return ext if ext else "no_ext"


def ensure_unique_path(target: Path) -> Path:
    """Якщо файл вже існує, додає суфікс ' (1)', ' (2)', ... перед розширенням."""
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    i = 1
    while True:
        candidate = target.with_name(f"{stem} ({i}){suffix}")
        if not candidate.exists():
            return candidate
        i += 1


def walk_and_copy(src_dir: Path, dest_root: Path, skip_inside: Path | None = None) -> tuple[int, dict[str, int]]:
    """
    Рекурсивно обходить src_dir та копіює файли в dest_root/<ext>/filename.
    Повертає (кількість_скопійованих_файлів, лічильники_за_розширеннями).
    """
    copied = 0
    per_ext = Counter()

    try:
        entries = list(src_dir.iterdir())
    except (PermissionError, FileNotFoundError, OSError) as e:
        logging.warning("Пропущено %s: %s", src_dir, e)
        return copied, per_ext

    for entry in entries:
        # Пропускаємо директорію призначення, якщо вона знаходиться всередині джерела
        if skip_inside and (skip_inside in entry.parents or entry == skip_inside):
            continue

        if entry.is_dir():
            c, cnt = walk_and_copy(entry, dest_root, skip_inside=skip_inside)
            copied += c
            per_ext.update(cnt)
            continue

        if entry.is_file():
            ext = safe_extension(entry)
            target_dir = dest_root / ext
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                logging.warning("Не вдалося створити теку %s: %s", target_dir, e)
                continue

            target_path = ensure_unique_path(target_dir / entry.name)
            try:
                shutil.copy2(entry, target_path)
                copied += 1
                per_ext[ext] += 1
                logging.info("Скопійовано: %s -> %s", entry, target_path)
            except (PermissionError, FileNotFoundError, OSError) as e:
                logging.warning("Не вдалося скопіювати %s: %s", entry, e)
        else:
            logging.debug("Пропущено не-файл: %s", entry)

    return copied, per_ext


def main() -> None:
    # --- ЛОГУВАННЯ В КОНСОЛЬ + ФАЙЛ ---
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # Обробник для консолі
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Обробник для файлу (режим append!)
    file_handler = logging.FileHandler("copy.log", mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Щоб уникнути дублю при повторному виклику main()
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    # ---------------------------------

    args = parse_args()

    src: Path = args.src.resolve()
    if not src.exists() or not src.is_dir():
        logging.error("Вихідна директорія не існує або це не директорія: %s", src)
        raise SystemExit(1)

    dest = (src.parent / "dist").resolve() if args.dest is None else args.dest.resolve()
    skip_inside = dest if (src == dest or dest in src.parents) else None

    try:
        dest.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        logging.error("Не вдалося створити директорію призначення %s: %s", dest, e)
        raise SystemExit(1)

    logging.info("Джерело:      %s", src)
    logging.info("Призначення:  %s", dest)

    total, per_ext = walk_and_copy(src, dest, skip_inside=skip_inside)

    logging.info("ГОТОВО. Скопійовано файлів: %d", total)
    if total == 0:
        logging.info("Перевірте права доступу та вміст вихідної директорії.")
    else:
        logging.info("Розподіл за розширеннями:")
        for ext, cnt in sorted(per_ext.items(), key=lambda kv: (-kv[1], kv[0])):
            logging.info("  %-10s -> %d", ext, cnt)


if __name__ == "__main__":
    main()