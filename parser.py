import bz2
import mwxml
import re
import sqlite3
import os

LINK_RE = re.compile(r'\[\[([^:\]\|]+)(?:\|[^\]]+)?\]\]')

def process_dump(dump_path, db_path):
    # Создаем/подключаемся к базе
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Оптимизация SQLite для безумной скорости записи
    cursor.execute("PRAGMA journal_mode = OFF")
    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("CREATE TABLE IF NOT EXISTS links (title TEXT, target TEXT)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON links(title)")

    with bz2.open(dump_path, "rb") as f:
        dump = mwxml.Dump.from_file(f)
        batch = []
        count = 0
        
        for page in dump:
            if page.namespace != 0:
                continue
                
            title = page.title
            for revision in page:
                text = revision.text or ""
                out_links = set(LINK_RE.findall(text))
                
                for link in out_links:
                    batch.append((title, link))
                
                # Сбрасываем данные в базу каждые 10к записей
                if len(batch) >= 10000:
                    cursor.executemany("INSERT INTO links VALUES (?, ?)", batch)
                    conn.commit()
                    batch = []
                    count += 1
                    if count % 10 == 0:
                        print(f"Обработано {count * 1000} страниц...")

        # Записываем остаток
        if batch:
            cursor.executemany("INSERT INTO links VALUES (?, ?)", batch)
            conn.commit()
            
    conn.close()
