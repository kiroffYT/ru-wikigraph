import mwxml
import re
import hashlib
import os
import json
from datetime import datetime

# Регулярка для поиска ссылок вида [[Название статьи]] или [[Название статьи|Текст]]
LINK_RE = re.compile(r'\[\[([^:\]\|]+)(?:\|[^\]]+)?\]\]')

def get_hex_paths(title):
    """Шестнадцатеричная сегментация: берем первые 2 символа MD5 хэша."""
    h = hashlib.md5(title.encode('utf-8')).hexdigest()
    return h[0], h[1]

def process_dump(dump_path, output_dir, date_str):
    """Стриминговое чтение дампа без загрузки его целиком в RAM."""
    dump = mwxml.Dump.from_file(open(dump_path, "rb"))
    
    links_graph = {}
    
    for page in dump:
        # Исключаем служебные страницы (пространство имен 0 - это статьи)
        if page.namespace != 0:
            continue
            
        for revision in page:
            text = revision.text or ""
            title = page.title
            
            # Извлекаем ссылки
            out_links = LINK_RE.findall(text)
            out_links = list(set([link.strip() for link in out_links])) # Убираем дубли
            
            links_graph[title] = out_links
            
            # Формируем структуру X/X/article.json
            d1, d2 = get_hex_paths(title)
            safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            path_dir = os.path.join(output_dir, date_str, d1, d2)
            os.makedirs(path_dir, exist_ok=True)
            
            file_path = os.path.join(path_dir, f"{safe_title}.json")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({"title": title, "links": out_links}, f, ensure_ascii=False)
                
    return links_graph
