"""Константы и параметры запуска системы «Три цены»."""

from dataclasses import dataclass
from datetime import datetime

import pandas as pd

# === Config ===
YEARS = 5
TXT_FOLDER = 'txt'
LOGS_FOLDER = 'logs'
REPORTS_FOLDER = 'reports'

ASSETS_CONFIG = {
    'IMOEX': {'name': 'Индекс Московской биржи',    'currency': 'RUB'},
    'SBER':  {'name': 'Акции Сбербанка',            'currency': 'RUB'},
    'GOLD':  {'name': 'Фонд GOLD ETF',                  'currency': 'RUB'},
    'AMNY':  {'name': 'Фонд Атон в юанях ETF',          'currency': 'RUB'},
    'MOEX':  {'name': 'Акции Московской биржи',     'currency': 'RUB'},
    'MTSS':  {'name': 'Акции МТС',                  'currency': 'RUB'},
    'LKOH':  {'name': 'Акции Лукойл',               'currency': 'RUB'},
    'NLMK':  {'name': 'Акции Новолипецкий МК',      'currency': 'RUB'},
    'OZON':  {'name': 'Акции Озон',                 'currency': 'RUB'},
    'PLZL':  {'name': 'Акции Полюс',                'currency': 'RUB'},
    'T':     {'name': 'Акции Т-Технологии',         'currency': 'RUB'},
    'Si':    {'name': 'Фьючерсы Доллар США / Рубль', 'currency': 'RUB'},
    'NG':    {'name': 'Фьючерсы на газ',             'currency': 'USD'},
    'BR':    {'name': 'Фьючерсы на нефть Brent',     'currency': 'USD'},
    'GD':    {'name': 'Фьючерсы на золото',          'currency': 'USD'},
    'SV':    {'name': 'Фьючерсы на серебро',         'currency': 'USD'},
    'PT':    {'name': 'Фьючерсы на платину',         'currency': 'USD'},
    'Ri':    {'name': 'Фьючерсы Ri',                 'currency': 'RUB'},
    'SR':    {'name': 'Фьючерсы Сбербанка',           'currency': 'RUB'},
}


@dataclass(frozen=True)
class RunParams:
    """Параметры конкретного запуска: даты и имена файлов."""

    years: int
    today_str: str
    pdf_filename: str
    log_filename: str
    start_date: pd.Timestamp


def build_run_params() -> RunParams:
    """Считает даты и имена файлов для текущего запуска.

    Дата начала — 1 января текущего года минус YEARS лет.
    """
    now = datetime.today()
    start_year = now.year - YEARS
    return RunParams(
        years=YEARS,
        today_str=now.strftime('%d.%m.%Y'),
        pdf_filename=f'{now.strftime("%Y-%m-%d")}-3price-{YEARS}.pdf',
        log_filename=f'{now.strftime("%Y-%m")}-3price.log',
        start_date=pd.to_datetime(f'{start_year}-01-01'),
    )
