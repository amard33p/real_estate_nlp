import logging
from typing import Optional
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)


# Function to reformat date from DD-MM-YYYY to YYYY-MM-DD
def reformat_date(date_str: str) -> Optional[str]:
    try:
        return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")
    except Exception:
        return None


def refresh_cookies(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            should_refresh = False
            jsessionid_cookie_expiry = None
            for cookie in self.session.cookies:
                if cookie.name == "JSESSIONID":
                    jsessionid_cookie_expiry = cookie.expires
                    break
            if "JSESSIONID" not in self.session.cookies:
                logger.info("JSESSIONID cookie not found. Refreshing session.")
                should_refresh = True
            elif jsessionid_cookie_expiry:
                expiry_time = datetime.fromtimestamp(jsessionid_cookie_expiry)
                current_time = datetime.now()
                if expiry_time - current_time <= timedelta(minutes=1):
                    logger.info("JSESSIONID is about to expire. Refreshing session.")
                    should_refresh = True

            if should_refresh:
                self.get_cookies()

        except Exception as e:
            logger.error(f"Error in refresh_cookies decorator: {e}")

        return func(self, *args, **kwargs)

    return wrapper


def clean_status(status):
    if status is not None:
        for prefix in ["REJECTED", "WITHDRAWN", "REVOKED"]:
            if status.startswith(prefix):
                return prefix
        return status
    return "UNKNOWN"
