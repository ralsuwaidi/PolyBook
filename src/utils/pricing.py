from datetime import datetime, timedelta

PRICING = {
    'standard': {
        'input': 0.27,
        'output': 1.10
    },
    'discount': {
        'input': 0.135,
        'output': 0.55
    }
}

def is_off_peak():
    utc_now = datetime.utcnow()
    utc_hour = utc_now.hour + utc_now.minute / 60
    return 16.5 <= utc_hour < 24.5  # 16:30 to 00:30 UTC

def get_pricing_tier():
    return 'discount' if is_off_peak() else 'standard'

def estimate_total_cost(token_count: int):
    tier = get_pricing_tier()
    rate = PRICING[tier]

    total = (token_count / 1_000_000) * (rate["input"] + rate["output"])
    return total, tier

def get_time_until_saver_mode():
    now = datetime.utcnow()
    current_minutes = now.hour * 60 + now.minute
    saver_start_minutes = 16 * 60 + 30  # 16:30 UTC

    if current_minutes >= saver_start_minutes:
        return None  # Already in saver mode
    delta = saver_start_minutes - current_minutes
    return timedelta(minutes=delta)
