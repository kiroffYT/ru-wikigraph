import bz2
import mwxml
import re
import hashlib
import os
import json

# Регулярка для поиска ссылок [[Статья]] или [[Статья|Текст]]
LINK_RE = re.compile(r'\[\[([^:\]\|]+)(?:\|[^\]]+)?\]\]')

def get_hex_paths(title):
    """Шестнадцатеричная сегментация на основе MD5 названия."""
    h = hashlib.md5(title.encode('utf-8')).hexdigest()
    return h[0], h[1]

def process_dump(dump_path, output_dir, date_str):
    """Стриминговая обработка сжатого XML дампа."""
    with bz2.open(dump_path, "rb") as f:
        dump = mwxml.Dump.from_file(f)
        links_graph = {}
        
        for page in dump:
            if page.namespace != 0: # Нас интересуют только статьи
                continue
                
            for revision in page:
                text = revision.text or ""
                title = page.title
                
                # Извлекаем ссылки и убираем дубликаты
                out_links = list(set(LINK_RE.findall(text)))
                links_graph[title] = out_links
                
                # Путь для сегментации (X/X/)
                d1, d2 = get_hex_paths(title)
                
                # Очистка названия: только буквы, цифры и пробелы
                safe_title = "".join([c for c in title if c.isalnum() or c==' ']).strip()
                
                # ИСПРАВЛЕНИЕ: Ограничение длины имени файла для Linux (255 байт предел)
                if len(safe_title) > 100:
                    safe_title = safe_title[:100]
                
                path_dir = os.path.join(output_dir, date_str, d1, d2)
                os.makedirs(path_dir, exist_ok=True)
                
                file_path = os.path.join(path_dir, f"{safe_title}.json")
                
                # Сохраняем индивидуальный JSON статьи
                with open(file_path, 'w', encoding='utf-8') as jf:
                    json.dump({"title": title, "links": out_links}, jf, ensure_ascii=False)
                    
    return links_graph
