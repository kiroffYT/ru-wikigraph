import bz2
import mwxml
import re
import sqlite3
import os

# Регулярка для извлечения чистых внутренних ссылок
LINK_RE = re.compile(r'\[\[([^:\]\|]+)(?:\|[^\]]+)?\]\]')

def process_dump(dump_path, db_path):
    # Создаем/подключаемся к базе
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Настройки для экстремальной скорости записи
    cursor.execute("PRAGMA journal_mode = OFF")
    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA cache_size = -2000000") # Используем до 2ГБ кэша в RAM
    cursor.execute("PRAGMA temp_store = MEMORY")
    
    # Создаем таблицу БЕЗ индекса (индекс создадим в конце)
    cursor.execute("DROP TABLE IF EXISTS links")
    cursor.execute("CREATE TABLE links (title TEXT, target TEXT)")

    with bz2.open(dump_path, "rb") as f:
        dump = mwxml.Dump.from_file(f)
        batch = []
        page_counter = 0 # Счётчик реально обработанных страниц
        total_counter = 0 # Общий счётчик страниц в дампе
        
        for page in dump:
            total_counter += 1
            
            # Пропускаем всё, что не является основной статьёй
            if page.namespace != 0:
                if total_counter % 100000 == 0:
                    print(f"Пропущено {total_counter} служебных страниц...")
                continue
                
            title = page.title
            for revision in page:
                text = revision.text or ""
                # Извлекаем уникальные ссылки из текста статьи
                out_links = set(LINK_RE.findall(text))
                
                for link in out_links:
                    batch.append((title, link))
                
                # Сбрасываем батч в базу
                if len(batch) >= 50000: # Увеличил размер батча для скорости
                    cursor.executemany("INSERT INTO links VALUES (?, ?)", batch)
                    conn.commit()
                    batch = []
                    page_counter += 1
                    print(f"Обработано {total_counter} объектов дампа | Статей в базе: {page_counter * 50000}")

        # Записываем остатки данных
        if batch:
            cursor.executemany("INSERT INTO links VALUES (?, ?)", batch)
            conn.commit()
            
    # --- ФИНАЛЬНАЯ ИНДЕКСАЦИЯ (Самый важный этап для сайта) ---
    print("Создание индекса... На 9ГБ это займёт время, не прерывай процесс!")
    cursor.execute("CREATE INDEX idx_title ON links(title)")
    conn.commit()
    
    print("Сжатие и оптимизация базы (VACUUM)...")
    cursor.execute("VACUUM")
    conn.commit()
    
    conn.close()
    print("Всё готово. База готова к деплою на Hugging Face!")
