# backend/app/metrics.py
def debt_equity(total_debt, total_equity):
    try:
        if not total_debt or not total_equity:
            return None
        return total_debt / total_equity
    except:
        return None

def net_margin(profit_after_tax, revenue):
    try:
        if profit_after_tax is None or revenue is None or revenue == 0:
            return None
        return (profit_after_tax / revenue) * 100.0
    except:
        return None
