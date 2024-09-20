import csv
import nltk
from pprint import pprint

nltk.download("stopwords")
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter


def preprocess_text(text):
    """Tokenize and remove stopwords from the text."""
    stop_words = set(stopwords.words("english"))
    tokens = word_tokenize(text.lower())
    return [word for word in tokens if word.isalnum() and word not in stop_words]


def count_keywords(csv_file, column_index):
    keyword_counter = Counter()

    with open(csv_file, "r", newline="") as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header row if present

        for row in csv_reader:
            if len(row) > column_index:
                # Split the cell content into words and count them
                words = row[column_index]
                words = preprocess_text(words)
                keyword_counter.update(words)

    return keyword_counter


def main():
    csv_file = "data/candidates.csv"
    column_index = 4

    result = count_keywords(csv_file, column_index)

    pprint(result.most_common(100))

    with open("data/keywords.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Keyword", "Count"])
        for keyword, count in result.most_common(200):
            writer.writerow([keyword, count])


if __name__ == "__main__":
    main()
