import os
import json
import markdown
from bs4 import BeautifulSoup
import re
import yaml

def extract_text_from_markdown(markdown_content):
    """
    Преобразует Markdown в HTML, затем удаляет HTML-теги,
    а также удаляет Frontmatter, блоки кода, макросы MkDocs и служебные комментарии,
    оставляя максимально чистый текст для обучения ИИ.
    При этом сохраняет Markdown таблицы в читаемом формате.
    """
    
    # 1. Удаление Frontmatter с использованием YAML парсера
    lines = markdown_content.splitlines()
    content_without_frontmatter = markdown_content
    
    # Проверяем, начинается ли файл с frontmatter (---)
    if lines and lines[0].strip() == '---':
        # Ищем закрывающие ---
        end_frontmatter = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_frontmatter = i
                break
        
        if end_frontmatter > 0:
            # Удаляем frontmatter
            content_without_frontmatter = '\n'.join(lines[end_frontmatter + 1:])
    
    # Дополнительно удаляем любые оставшиеся строки, похожие на frontmatter
    lines = content_without_frontmatter.splitlines()
    cleaned_lines = []
    
    for line in lines:
        stripped_line = line.strip()
        # Пропускаем строки с метаданными или Notion URL
        if (stripped_line.startswith('https://www.notion.so/n8n/Frontmatter-') or
            re.match(r'^(title|description|contentType|tags|hide|aliases|priority|redirect_from):\s*.*', stripped_line)):
            continue
        cleaned_lines.append(line)
    
    cleaned_markdown_content = '\n'.join(cleaned_lines)

    # 2. Удаление блоков кода (```)
    cleaned_markdown_content = re.sub(r'```.*?```', '', cleaned_markdown_content, flags=re.DOTALL)

    # 3. Удаление inline кода в обратных кавычках, но сохраняем содержимое
    cleaned_markdown_content = re.sub(r'`([^`]+)`', r'\1', cleaned_markdown_content)

    # 4. Удаление макросов MkDocs
    cleaned_markdown_content = re.sub(r'\[\[.*?\]\]', '', cleaned_markdown_content)

    # 5. Удаление служебных блоков MkDocs Material
    cleaned_markdown_content = re.sub(r'///.*?///', '', cleaned_markdown_content, flags=re.DOTALL)

    # 6. Удаление HTML комментариев
    cleaned_markdown_content = re.sub(r'<!--.*?-->', '', cleaned_markdown_content, flags=re.DOTALL)
    
    # 7. Удаление маркеров Snippets
    cleaned_markdown_content = re.sub(r'--8<--\s*".*?"', '', cleaned_markdown_content)

    # 8. Удаление всех URL ссылок (включая Notion и обычные HTTP/HTTPS)
    cleaned_markdown_content = re.sub(r'https?://[^\s\)]+', '', cleaned_markdown_content)
    
    # 9. Удаление Markdown ссылок [текст](url), но сохраняем текст
    cleaned_markdown_content = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', cleaned_markdown_content)
    
    # 10. Удаление reference-style ссылок [текст][ref]
    cleaned_markdown_content = re.sub(r'\[([^\]]*)\]\[[^\]]*\]', r'\1', cleaned_markdown_content)
    
    # 11. Удаление определений ссылок [ref]: url
    cleaned_markdown_content = re.sub(r'^\[.*?\]:\s*.*$', '', cleaned_markdown_content, flags=re.MULTILINE)

    # 12. Сохранение и форматирование таблиц
    # Находим все таблицы и обрабатываем их отдельно
    table_pattern = r'(\|.*\|.*?\n(?:\|[\s\-\|:]*\|.*?\n)?(?:\|.*\|.*?\n)*)'
    tables = re.findall(table_pattern, cleaned_markdown_content, flags=re.MULTILINE | re.DOTALL)
    
    # Временно заменяем таблицы на плейсхолдеры
    table_placeholders = {}
    processed_tables = []
    for i, table in enumerate(tables):
        placeholder = f"__TABLE_PLACEHOLDER_{i}__"
        formatted_table = format_markdown_table(table)
        table_placeholders[placeholder] = formatted_table
        processed_tables.append(table)
        cleaned_markdown_content = cleaned_markdown_content.replace(table, placeholder, 1)

    # 13. Преобразование оставшегося Markdown в HTML и извлечение текста
    html = markdown.markdown(cleaned_markdown_content, extensions=['tables'])
    soup = BeautifulSoup(html, 'html.parser')

    # Удаляем скрипты и стили
    for script_or_style in soup(['script', 'style']):
        script_or_style.extract()
    
    text = soup.get_text()
    
    # 14. Восстанавливаем таблицы в читаемом формате
    for placeholder, table in table_placeholders.items():
        # Форматируем таблицу для лучшей читаемости
        formatted_table = format_markdown_table(table)
        text = text.replace(placeholder, formatted_table)

    # 15. Финальная очистка
    # Удаляем избыточные пустые строки и пробелы
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    # Объединяем строки с одной пустой строкой между абзацами
    final_text = '\n'.join(lines)
    
    # Удаляем множественные переводы строк
    final_text = re.sub(r'\n{3,}', '\n\n', final_text)
    
    return final_text.strip()


def format_markdown_table(table_text):
    """
    Форматирует Markdown таблицу в более читаемый текстовый формат
    """
    lines = [line.strip() for line in table_text.strip().split('\n') if line.strip()]
    if len(lines) < 1:
        return ""
    
    # Убираем разделительную строку с |---|---|
    header_line = lines[0] if lines else ""
    data_lines = []
    
    for line in lines[1:]:
        # Пропускаем разделительные строки таблицы
        if not re.match(r'^\|[\s\-\|:]+\|$', line) and line.strip():
            data_lines.append(line)
    
    # Если нет заголовков или данных, просто возвращаем очищенный текст
    if not header_line.startswith('|'):
        return table_text.replace('|', ' ').strip()
    
    # Извлекаем заголовки
    headers = [cell.strip() for cell in header_line.split('|')[1:-1] if cell.strip()]
    
    # Форматируем таблицу
    formatted_lines = []
    
    # Добавляем строки данных
    for line in data_lines:
        if line.startswith('|') and line.endswith('|'):
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells and any(cell for cell in cells):  # Проверяем, что строка не пустая
                row_text = []
                for i, cell in enumerate(cells):
                    if cell:
                        if i < len(headers) and headers[i]:
                            row_text.append(f"{headers[i]}: {cell}")
                        else:
                            row_text.append(cell)
                if row_text:
                    formatted_lines.append(" | ".join(row_text))
    
    # Если таблица пустая, возвращаем простой текст
    if not formatted_lines:
        return table_text.replace('|', ' ').strip()
    
    return '\n'.join(formatted_lines)


def process_documentation(docs_base_path, output_json_path):
    """
    Проходит по всем Markdown-файлам в указанной директории,
    извлекает очищенный текст и сохраняет его в JSON.
    """
    documentation_data = []
    
    print(f"Начинаю обработку документов из: {docs_base_path}")
    processed_count = 0
    
    for root, _, files in os.walk(docs_base_path):
        for file_name in files:
            if file_name.endswith('.md'):
                file_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(file_path, docs_base_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        markdown_content = f.read()
                    
                    clean_text = extract_text_from_markdown(markdown_content)
                    
                    if clean_text and len(clean_text.strip()) > 50:  # Минимальная длина для сохранения
                        documentation_data.append({
                            "file_path": relative_path,
                            "content": clean_text
                        })
                        processed_count += 1
                        print(f"[OK] Обработан файл: {relative_path} ({len(clean_text)} символов)")
                    else:
                        print(f"[SKIP] Пропущен файл (слишком мало содержимого): {relative_path}")
                        
                except Exception as e:
                    print(f"[ERR] Ошибка при обработке файла {file_path}: {e}")
    
    if documentation_data:
        try:
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(documentation_data, f, ensure_ascii=False, indent=2)
            print(f"\n[SUCCESS] Все очищенные данные успешно сохранены в: {output_json_path}")
            print(f"[STATS] Статистика:")
            print(f"   - Всего документов обработано: {processed_count}")
            print(f"   - Общий размер JSON файла: {os.path.getsize(output_json_path) / 1024 / 1024:.2f} MB")
        except Exception as e:
            print(f"[ERR] Ошибка при сохранении JSON-файла {output_json_path}: {e}")
    else:
        print("\n[WARN] Нет данных для сохранения. Проверьте путь к документации и содержание файлов.")


if __name__ == "__main__":
    docs_directory = r'C:\Users\CENTR\n8n-docs\docs' 
    output_file = r'C:\Users\CENTR\n8n-docs\site\n8n_documentation_cleaned_improved.json'
    
    if not os.path.isdir(docs_directory):
        print(f"[ERR] Ошибка: Директория '{docs_directory}' не найдена. Пожалуйста, проверьте путь.")
    else:
        process_documentation(docs_directory, output_file)