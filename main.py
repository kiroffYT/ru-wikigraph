import os
import sys
import logging
from datetime import datetime
from parser import process_dump
from hf_uploader import upload_to_hf

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    hf_token = os.getenv("HF_TOKEN")
    repo_id = "KirOFFyt/all-russian-wikipedia-data" # ЗАМЕНИ НА СВОЙ
    
    dump_file = "dump.xml.bz2"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Имя файла базы данных с датой
    db_name = f"ruwiki_graph_{datetime.now().strftime('%d%m%Y')}.db"
    db_path = os.path.join(output_dir, db_name)
    
    try:
        logger.info("Начинаем упаковку Википедии в SQLite...")
        process_dump(dump_file, db_path)
        
        logger.info(f"База готова. Размер: {os.path.getsize(db_path) / (1024**2):.2f} MB")
        
        logger.info("Загрузка одного файла на Hugging Face...")
        upload_to_hf(output_dir, repo_id, hf_token)
        
        logger.info("Победа!")
    except Exception as e:
        logger.error(f"Сбой: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
