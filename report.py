"""Генерация PDF-отчёта «Три цены»: титульная страница с таблицей и графики."""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.table import Table

from analysis import compute_levels

LEVEL_COLOR = '#ff7f0e'
BASE_COLORS = ['#1f77b4', '#2ca02c', '#d62728', '#9467bd', '#8c564b',
               '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#ff7f0e']


def plural_years(n: int) -> str:
    """Склонение слова «год»: 1 год / 2–4 года / 5–20 лет (с учётом 11–14)."""
    if n % 10 == 1 and n % 100 != 11:
        return "год"
    if n % 10 in [2, 3, 4] and n % 100 not in [12, 13, 14]:
        return "года"
    return "лет"


def assign_chart_colors(data_dict: dict, assets_config: dict) -> dict[str, str]:
    """Цвета линий распределяем в порядке исходного словаря конфигурации."""
    ordered_tickers = [ticker for ticker in assets_config if ticker in data_dict]
    return {ticker: BASE_COLORS[i % len(BASE_COLORS)] for i, ticker in enumerate(ordered_tickers)}


def _render_title_page(pdf: PdfPages, data_dict: dict, assets_config: dict,
                       price_level_map: dict, price_color_map: dict, params) -> None:
    """Первая страница: заголовок и таблица тикеров."""
    fig = plt.figure(figsize=(14, 8))
    ax = fig.add_subplot(111)
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Заголовок
    ax.text(0.5, 0.97, f'{params.today_str}. Три ценовых диапазона',
            fontsize=20, fontweight='bold', ha='center', transform=ax.transAxes)
    ax.text(0.5, 0.91,
            f'Анализ за {params.years} {plural_years(params.years)} (с {params.start_date.strftime("%d.%m.%Y")})',
            fontsize=14, ha='center', transform=ax.transAxes)

    # === Данные таблицы ===
    table_data = [['Тикер', 'Наименование', 'Текущая цена', 'Диапазон цены']]

    # Строим таблицу строго по порядку из ASSETS_CONFIG
    for ticker, cfg in assets_config.items():
        if ticker in data_dict and not data_dict[ticker].empty:
            last_price = data_dict[ticker]['close'].iloc[-1]
            price_str = f'{last_price:.2f}'
            level = price_level_map[ticker]
            table_data.append([ticker, cfg['name'], price_str, level])

    # Параметры таблицы
    col_widths = [0.12, 0.23, 0.16, 0.19]
    row_height = 0.045
    n_rows = len(table_data)
    table_height = n_rows * row_height
    table_bottom = 0.88 - table_height

    table = Table(ax, bbox=[0.15, table_bottom, 0.7, table_height])

    for i, row in enumerate(table_data):
        for j, cell in enumerate(row):
            facecolor = '#e0e0e0' if i == 0 else '#ffffff'
            fontweight = 'bold' if i == 0 else 'normal'

            cell_loc = 'center'
            text_to_display = cell

            if j == 0:
                cell_loc = 'center'
                text_to_display = cell
            elif j == 1:
                cell_loc = 'left'
                text_to_display = f" {cell}"
            elif j == 2:
                cell_loc = 'right'
                text_to_display = f"{cell}  "

            cell_obj = table.add_cell(i, j, width=col_widths[j], height=row_height,
                                      text=text_to_display, loc=cell_loc, facecolor=facecolor)
            cell_obj.get_text().set_fontweight(fontweight)
            cell_obj.get_text().set_fontsize(10)

            # === Цвет текста в столбце "Диапазон цены" (j=3) ===
            if i > 0 and j == 3:
                ticker_key = row[0]
                if ticker_key in price_color_map:
                    cell_obj.get_text().set_color(price_color_map[ticker_key])

    ax.add_table(table)

    # Контроль полей — без обрезки
    plt.subplots_adjust(left=0.1, right=0.9, top=0.85, bottom=0.2)
    pdf.savefig(fig, dpi=150, metadata={'Creator': 'Python'})
    plt.close(fig)


def _render_ticker_chart(pdf: PdfPages, ticker: str, df: pd.DataFrame, cfg: dict, color: str, params) -> None:
    """Страница с графиком одного тикера и пунктирными уровнями «трёх цен»."""
    # График строится строго по уже отфильтрованным данным
    min_p, level_1_3, level_2_3, max_p = (round(v, 2) for v in compute_levels(df))
    key_levels = sorted({min_p, level_1_3, level_2_3, max_p})
    key_levels_str = [f'{lvl:.2f}' for lvl in key_levels]

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(df['begin'], df['close'], color=color, linewidth=1.0)

    for level in key_levels:
        ax.axhline(y=level, color=LEVEL_COLOR, linestyle='--', linewidth=1.2)

    y_ticks = sorted(set(list(ax.get_yticks()) + key_levels))
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f'{y:.2f}' for y in y_ticks])

    for label in ax.yaxis.get_ticklabels():
        if label.get_text() in key_levels_str:
            label.set_color(LEVEL_COLOR)

    asset_name = cfg['name']
    currency = cfg['currency']

    ax.set_title(f'{asset_name} ({ticker}) — за {params.years} {plural_years(params.years)}',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel(f'Цена ({currency})', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=0)
    ax.set_xlabel('')
    plt.tight_layout()
    pdf.savefig(fig, dpi=150)
    plt.close(fig)


def generate_pdf(pdf_path: str, data_dict: dict, assets_config: dict,
                 price_level_map: dict, price_color_map: dict, params) -> None:
    """Собирает PDF: титульная страница, затем графики по порядку ASSETS_CONFIG."""
    close_colors = assign_chart_colors(data_dict, assets_config)

    with PdfPages(pdf_path) as pdf:
        # --- Первая страница: титульный лист ---
        _render_title_page(pdf, data_dict, assets_config, price_level_map, price_color_map, params)

        # --- Графики: вывод строго по порядку из ASSETS_CONFIG ---
        for ticker in assets_config:
            if ticker not in data_dict:
                continue
            _render_ticker_chart(pdf, ticker, data_dict[ticker], assets_config[ticker],
                                 close_colors[ticker], params)
