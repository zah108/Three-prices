"""Точка входа системы «Три цены».

Запуск: python main.py  (из папки проекта).
"""

import logging
import os
import sys
from datetime import datetime

import analysis
import config
import data_loader
import log_setup
import report


def main() -> int:
    params = config.build_run_params()
    log_path = log_setup.setup_logging(config.LOGS_FOLDER, params.log_filename)
    log_setup.write_banner(log_path)

    # === Чтение локальных данных ===
    data_dict = data_loader.load_data(config.TXT_FOLDER, config.ASSETS_CONFIG, params.start_date)

    # === Определение уровня цены и цвета ===
    price_level_map, price_color_map = analysis.build_price_maps(data_dict)

    if not data_dict:
        # Фикс: раньше при пустых данных скрипт падал с NameError на final_line
        logging.error("Нет данных для сохранения в PDF. Проверьте структуру файлов в папке txt")
        return 1

    # Фикс: раньше без папки reports/ PdfPages падал с FileNotFoundError
    os.makedirs(config.REPORTS_FOLDER, exist_ok=True)
    pdf_path = os.path.join(config.REPORTS_FOLDER, params.pdf_filename)
    report.generate_pdf(pdf_path, data_dict, config.ASSETS_CONFIG, price_level_map, price_color_map, params)

    logging.info(f"Проанализировано: {len(data_dict)} тикеров")
    final_line = (f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                  f"✅ Готово: {params.pdf_filename} — сохранён в папке {config.REPORTS_FOLDER}")
    print(final_line)
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(final_line + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
