import bz2
import mwxml
import re
import sqlite3
import os

# Регулярка для извлечения чистых внутренних ссылок
LINK_RE = re.compile(r'\[\[([^:\]\|]+)(?:\|[^\]]+)?\]\]')

def clean_wiki_text(text):
    """
    Очистка текста от элементов, которые не должны считаться 
    основным контентом при поиске первой ссылки.
    """
    # 1. Удаляем инфобоксы и шаблоны {{...}}
    # Используем жадный поиск для простых шаблонов
    text = re.sub(r'\{\{[^\{}]+\}\}', '', text)
    
    # 2. Удаляем таблицы {|...|}
    text = re.sub(r'\{\|.*?\|\}', '', text, flags=re.DOTALL)
    
    # 3. Удаляем файлы и категории, так как они не ведут на другие статьи
    # (Хотя регулярка LINK_RE их частично фильтрует, лучше убрать из текста совсем)
    text = re.sub(r'\[\[(Файл|Категория|File|Category):.*?\]\]', '', text, flags=re.IGNORECASE)
    
    return text

def process_dump(dump_path, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Настройки для экстремальной скорости записи
    cursor.execute("PRAGMA journal_mode = OFF")
    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA cache_size = -2000000") 
    cursor.execute("PRAGMA temp_store = MEMORY")
    
    cursor.execute("DROP TABLE IF EXISTS links")
    cursor.execute("CREATE TABLE links (title TEXT, target TEXT)")

    with bz2.open(dump_path, "rb") as f:
        dump = mwxml.Dump.from_file(f)
        batch = []
        page_counter = 0 
        total_counter = 0 
        
        for page in dump:
            total_counter += 1
            
            if page.namespace != 0:
                if total_counter % 10000 == 0:
                    print(f"Пропущено {total_counter} служебных страниц...")
                continue
                
            title = page.title
            for revision in page:
                raw_text = revision.text or ""
                
                # ШАГ 1: Очищаем текст от мусора ПЕРЕД извлечением ссылок
                clean_text = clean_wiki_text(raw_text)
                
                # ШАГ 2: Извлекаем ВСЕ ссылки, сохраняя их ПОРЯДОК (без set!)
                # Теперь rowid в базе будет соответствовать порядку в тексте
                out_links = LINK_RE.findall(clean_text)
                
                for link in out_links:
                    batch.append((title, link))
                
                if len(batch) >= 10000: # Можно увеличить батч для скорости
                    cursor.executemany("INSERT INTO links VALUES (?, ?)", batch)
                    conn.commit()
                    batch = []
                    page_counter += 1
                    print(f"Обработано {total_counter} объектов | Записей в батчах: {page_counter}")

        if batch:
            cursor.executemany("INSERT INTO links VALUES (?, ?)", batch)
            conn.commit()
            
    # --- ФИНАЛЬНАЯ ИНДЕКСАЦИЯ ---
    print("Создание индекса... Это критично для работы app.py!")
    cursor.execute("CREATE INDEX idx_title ON links(title)")
    conn.commit()
    
    print("Оптимизация базы...")
    cursor.execute("VACUUM")
    conn.commit()
    
    conn.close()
    print("Всё готово. Теперь режим 'Первонаха' будет работать корректно!")
