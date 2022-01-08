import os
import json
import requests


def main():
    with open("coverage.json", "rt+") as fp:
        db = json.load(fp)
        totals = db.get("totals", {})
        coverage = int(totals.get("percent_covered_display", "0"), 10)
    if coverage < 90:
        color = "red"
    elif coverage < 95:
        color = "yellow"
    else:
        color = "green"
    title = "code coverage".replace(" ", "%20")
    value = f"{coverage:d} %".replace("%", "%25").replace(" ", "%20")
    badge_url = f"https://badgen.net/badge/{title}/{value}/{color}"
    badge_data = requests.get(badge_url).content
    output_path = f"{os.getenv('OUTPATH', '.')}/cov_badge.svg"
    with open(output_path, "wb+") as fp:
        fp.write(badge_data)


if __name__ == "__main__":
    main()
