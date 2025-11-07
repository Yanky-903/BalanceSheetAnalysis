import re
import pdfplumber
import pandas as pd

def extract_tables_and_text(pdf_path):
    """
    Returns (tables, full_text) where tables is a list of pandas DataFrames.
    """
    tables = []
    text_all = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_all += page.extract_text() or ""
            try:
                page_tables = page.extract_tables()
            except Exception:
                page_tables = []
            for t in page_tables:
                try:
                    df = pd.DataFrame(t[1:], columns=t[0])
                except Exception:
                    try:
                        df = pd.DataFrame(t)
                    except Exception:
                        continue
                tables.append(df)
    return tables, text_all

def find_amount_in_df(df, kws):
    """
    Scan dataframe df for any cell containing one of the keywords in kws.
    When found, look to the right in the same row for the first numeric-looking cell and return it.
    """
    try:
        cols = list(df.columns)
    except Exception:
        return None

    for col_idx, col in enumerate(cols):
        try:
            series = df[col]
        except Exception:
            continue

        if hasattr(series, "items"):
            iterator = series.items()
        else:
            iterator = enumerate(series)

        for i, val in iterator:
            if val is None:
                continue
            sval = str(val).lower()
            for kw in kws:
                if kw in sval:
                    try:
                        row = df.iloc[i]
                    except Exception:
                        row = None
                    if row is None:
                        continue
                    for c in cols[col_idx+1:]:
                        cand = str(row.get(c, "")).replace(",", "")
                        m = re.search(r"([0-9]+(?:[\\.,][0-9]+)*)", cand)
                        if m:
                            num_s = m.group(1).replace(",", "")
                            try:
                                return float(num_s)
                            except Exception:
                                try:
                                    return float(num_s.replace(",","."))
                                except Exception:
                                    continue
    return None

def extract_key_numbers(tables, text):
    """
    Try to extract main numeric KPIs from the list of pandas DataFrames (tables)
    and fallback to searching the raw text when necessary.
    """
    numbers = {}
    kws_map = {
        "revenue": ["revenue", "sales", "total income", "net sales"],
        "total_assets": ["total assets", "assets"],
        "total_liabilities": ["total liabilities", "liabilities"],
        "profit_after_tax": ["profit after tax", "net profit", "profit for the period"],
        "ebitda": ["ebitda", "earnings before interest, tax, depreciation and amortisation"]
    }

    for k, kws in kws_map.items():
        val = None
        for df in tables:
            try:
                found = find_amount_in_df(df, kws)
            except Exception:
                found = None
            if found:
                val = found
                break

        if val is None and text:
            t = text.lower()
            for kw in kws:
                idx = t.find(kw)
                if idx != -1:
                    snippet = t[idx: idx + 200]
                    m = re.search(r"([0-9]+(?:[\\.,][0-9]+)*)", snippet)
                    if m:
                        s = m.group(1).replace(",", "")
                        try:
                            val = float(s)
                        except Exception:
                            try:
                                val = float(s.replace(",","."))
                            except Exception:
                                val = None
                        break
        if val is not None:
            numbers[k] = val

    return numbers
