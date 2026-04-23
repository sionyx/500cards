import argparse
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def wrap_text(text, max_width, canvas_obj):
    """Простой перенос текста по словам."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if canvas_obj.stringWidth(test_line, "ArialUnicodeMS", 11) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines if lines else [""]

def create_flashcard_pdf(phrases, output_filename="flashcards.pdf"):
    """Генерирует PDF с карточками (3×6 на странице)."""
    # Регистрация шрифта, поддерживающего кириллицу
    font_path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
    try:
        pdfmetrics.registerFont(TTFont('ArialUnicodeMS', font_path))
    except:
        print("⚠️  Не удалось загрузить шрифт Arial Unicode MS, используем стандартный шрифт")
        font_name = "Helvetica"
    else:
        font_name = "ArialUnicodeMS"
    
    width, height = A4
    c = canvas.Canvas(output_filename, pagesize=A4)

    # Настройки макета
    margin_x = 10 * mm
    margin_y = 10 * mm
    cols, rows = 3, 6
    cards_per_page = cols * rows

    card_width = (width - 2 * margin_x) / cols
    card_height = (height - 2 * margin_y) / rows

    for i, phrase in enumerate(phrases):
        # Переход на новую страницу каждые 18 карточек
        if i > 0 and i % cards_per_page == 0:
            c.showPage()

        idx_on_page = i % cards_per_page
        col = idx_on_page % cols
        row = idx_on_page // cols

        x = margin_x + col * card_width
        y = height - margin_y - (row + 1) * card_height

        # Рамка карточки
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.setLineWidth(1)
        c.rect(x + 1, y + 1, card_width - 2, card_height - 2, fill=0, stroke=1)

        # Текст фразы
        c.setFont(font_name, 11)
        c.setFillColorRGB(0, 0, 0)
        text_x = x + card_width / 2
        max_width = card_width - 10
        lines = wrap_text(phrase, max_width, c)
        line_height = 14
        total_text_height = len(lines) * line_height
        start_y = (y + card_height / 2) + (total_text_height / 2) - line_height / 2

        for j, line in enumerate(lines):
            c.drawCentredString(text_x, start_y - j * line_height, line)

    c.save()
    print(f"✅ PDF успешно создан: {output_filename}")

def main():
    parser = argparse.ArgumentParser(description="Генератор PDF с карточками фраз (3×6 на странице)")
    parser.add_argument("-i", "--input", required=True, help="Путь к файлу с фразами (по одной на строку)")
    parser.add_argument("-o", "--output", default="flashcards.pdf", help="Путь к выходному PDF (по умолчанию flashcards.pdf)")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"❌ Ошибка: файл '{args.input}' не найден.")
        return

    with open(args.input, "r", encoding="utf-8") as f:
        phrases = []
        for line in f:
            line = line.strip()
            # Пропускаем пустые строки и строки, начинающиеся с "#"
            if not line or line.startswith("#"):
                continue
            # Удаляем числа в скобках в конце строки
            if line.endswith(")"):
                # Ищем последнее вхождение " (" и удаляем всё после него
                last_paren = line.rfind(" (")
                if last_paren != -1:
                    line = line[:last_paren]
            phrases.append(line)

    if not phrases:
        print("❌ Ошибка: файл пуст или не содержит фраз.")
        return

    # Если фраз меньше 100, дополняем заглушками (можно удалить этот блок, если всегда ровно 100)
    while len(phrases) < 100:
        phrases.append(f"[Фраза {len(phrases) + 1}]")

    create_flashcard_pdf(phrases, args.output)

if __name__ == "__main__":
    main()
