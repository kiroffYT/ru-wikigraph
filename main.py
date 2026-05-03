import os
import sys
import logging
from datetime import datetime
from parser import process_dump
from graph_analysis import analyze_and_sort
from hf_uploader import upload_to_hf

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    hf_token = os.getenv("HF_TOKEN")
    repo_id = "твой-логин/ruwiki-graph-data" # ЗАМЕНИ НА СВОЙ
    
    dump_file = "dump.xml.bz2"
    output_dir = "output"
    date_str = datetime.now().strftime("%d%m%Y")
    
    try:
        logger.info("Старт парсинга (Streaming BZ2)...")
        links_graph = process_dump(dump_file, output_dir, date_str)
        
        logger.info("Старт анализа графа...")
        analyze_and_sort(links_graph, output_dir, date_str)
        
        logger.info("Загрузка на Hugging Face...")
        upload_to_hf(output_dir, repo_id, hf_token)
        
        logger.info("Готово!")
    except Exception as e:
        logger.error(f"Ошибка: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
