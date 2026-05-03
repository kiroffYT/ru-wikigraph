import os
import sys
import logging
from datetime import datetime
from parser import process_dump
from graph_analysis import analyze_and_sort
from hf_uploader import upload_to_hf

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # 1. Настройки из переменных окружения
    hf_token = os.getenv("HF_TOKEN")
    repo_id = "твой_юзернейм/ruwiki-data" # Замени на свой репозиторий
    
    dump_file = "dump.xml.bz2"
    output_dir = "output_data"
    date_str = datetime.now().strftime("%d%m%Y")
    
    if not os.path.exists(dump_file):
        logger.error(f"Файл дампа {dump_file} не найден. Прерывание.")
        sys.exit(1)

    if not hf_token:
        logger.error("Переменная окружения HF_TOKEN не установлена.")
        sys.exit(1)

    try:
        # 2. Парсинг дампа
        logger.info(f"Начинаем обработку дампа для даты: {date_str}")
        links_graph = process_dump(dump_file, output_dir, date_str)
        logger.info(f"Парсинг завершен. Обработано статей: {len(links_graph)}")

        # 3. Анализ графа и метрики
        logger.info("Запуск анализа графа (PageRank, входящие ссылки)...")
        analyze_and_sort(links_graph, output_dir, date_str)
        logger.info("Анализ успешно завершен.")

        # 4. Загрузка данных на Hugging Face
        # Мы загружаем всю папку текущей даты
        upload_folder = os.path.join(output_dir, date_str)
        logger.info(f"Загрузка данных из {upload_folder} на Hugging Face...")
        
        # Передаем путь к конкретной папке даты, чтобы на HF структура была /DDMMYYYY/...
        upload_to_hf(output_dir, repo_id, hf_token)
        
        logger.info("Пайплайн успешно выполнен!")

    except Exception as e:
        logger.exception(f"Произошла критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
