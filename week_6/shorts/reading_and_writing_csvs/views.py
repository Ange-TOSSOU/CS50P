import numpy as np
from PIL import Image
import csv


def main():
    with open("views.csv", encoding="utf-8") as views, open(
        "analysis.csv", "w", newline="", encoding="utf-8"
    ) as analysis:
        reader = csv.DictReader(views)
        writer = csv.DictWriter(analysis, fieldnames=reader.fieldnames + ["brightness"])
        writer.writeheader()

        for row in reader:
            brightness = calculate_brightness(f"{row['id']}.jpeg")
            row["brightness"] = round(brightness, 2)
            writer.writerow(row)


def calculate_brightness(filename):
    with Image.open(filename) as image:
        brightness = np.mean(np.array(image.convert("L"))) / 255
    return brightness


main()
