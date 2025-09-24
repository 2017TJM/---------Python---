import csv
import random
from datetime import datetime, timedelta
import argparse

REGIONS = ["North", "South", "East", "West"]
PRODUCTS = ["Widget A", "Widget B", "Widget C"]
CHANNELS = ["Online", "Offline"]


def generate_rows(num_rows: int, start_date: str = "2025-01-01"):
	base_date = datetime.strptime(start_date, "%Y-%m-%d")
	for i in range(num_rows):
		date = base_date + timedelta(days=i % 120)
		region = random.choice(REGIONS)
		product = random.choice(PRODUCTS)
		channel = random.choice(CHANNELS)
		amount = round(max(0.0, random.gauss(120, 60)), 2)
		yield {
			"date": date.strftime("%Y-%m-%d"),
			"region": region,
			"product": product,
			"amount": amount,
			"channel": channel,
		}


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--rows", type=int, default=1000)
	parser.add_argument("--out", type=str, default="data/raw/generated_sales.csv")
	args = parser.parse_args()

	with open(args.out, "w", newline="", encoding="utf-8") as f:
		writer = csv.DictWriter(f, fieldnames=["date", "region", "product", "amount", "channel"])
		writer.writeheader()
		for row in generate_rows(args.rows):
			writer.writerow(row)
	print(f"Wrote {args.rows} rows to {args.out}")


if __name__ == "__main__":
	main()
