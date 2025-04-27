import requests
import traceback


def spyApiRequest(logger):

    for page in range(1, 80):
    # 200 is the OK code for Http requests
        req = requests.get(f"https://steamspy.com/api.php?request=all&page={page}")

        if req.status_code == 500:
            logger.info("Page not found, i.e. finished all available pages.")
            return
        elif req.status_code != 200:
            logger.error(f"Error retreiving page n: {page}")

        try:
            data = req.json()
            return data

        except Exception:
            # Print info about the last 5 call stack traces
            traceback.print_exc(limit=5)
            return {}
