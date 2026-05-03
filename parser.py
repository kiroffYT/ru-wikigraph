import bz2
import mwxml
import re
import hashlib
import os
import json

LINK_RE = re.compile(r'\[\[([^:\]\|]+)(?:\|[^\]]+)?\]\]')

def get_hex_paths(title):
    h = hashlib.md5(title.encode('utf-8')).hexdigest()
    return h[0], h[1]

def process_dump(dump_path, output_dir, date_str):
    # Открываем bz2 файл в бинарном режиме чтения
    with bz2.open(dump_path, "rb") as f:
        dump = mwxml.Dump.from_file(f)
        links_graph = {}
        
        for page in dump:
            if page.namespace != 0: # Только статьи
                continue
                
            for revision in page:
                text = revision.text or ""
                title = page.title
                
                # Извлекаем уникальные ссылки
                out_links = list(set(LINK_RE.findall(text)))
                links_graph[title] = out_links
                
                # Сегментация X/X/article.json
                d1, d2 = get_hex_paths(title)
                # Очистка названия для имени файла
                safe_title = "".join([c for c in title if c.isalnum() or c==' ']).strip()
                
                path_dir = os.path.join(output_dir, date_str, d1, d2)
                os.makedirs(path_dir, exist_ok=True)
                
                file_path = os.path.join(path_dir, f"{safe_title}.json")
                with open(file_path, 'w', encoding='utf-8') as jf:
                    json.dump({"title": title, "links": out_links}, jf, ensure_ascii=False)
                    
    return links_graph
