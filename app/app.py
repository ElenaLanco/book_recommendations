from flask import Flask, render_template, request
import pickle
import os
import difflib
import pandas as pd

app = Flask(__name__)


def load_data():
    books = pd.read_csv(os.path.join(app.root_path, "data", "books_cleaned_limited.csv"))
    with open(os.path.join(app.root_path, "data", "res_dict.pickle"), "rb") as output_file:
        res_dict = pickle.load(output_file)
    return books, res_dict


def get_title_info(desired_title, books):
    class SM(difflib.SequenceMatcher):
        def __init__(self, a):
            super().__init__(a=a)

        def __call__(self, b):
            self.set_seq2(b)
            return self.ratio()

    desired_title = desired_title.lower()

    row = books.loc[books["title"].str.lower() == desired_title, :]
    if row.empty:
        close_name = SM(desired_title)
        words_list = [books["title"].drop_duplicates().str.lower().values.tolist()][0]
        best_match = max(words_list, key=close_name)
        row = books.loc[books["title"].str.lower() == best_match, :]

    author = list(row["author"])[0]
    title = list(row["title"])[0]
    author_title = list(row["authortitle"])[0]
    return author, title, author_title


def suggestions_to_dict(suggestions, columns, books, s_author="", n_required=5):
    res_dict = {}
    suggestions = columns.values[suggestions]
    for sug in suggestions:
        row = books.loc[books["authortitle"] == sug, :]
        author = list(row["author"])[0]
        if (s_author!="") & (author==s_author):
            continue
        title = list(row["title"])[0]
        res_dict[sug] = [author, title]
        if len(res_dict.keys()) == n_required:
            return res_dict



@app.route('/_add_numbers')
def add_numbers():
    books, res_dict = load_data()

    s_title = request.args.get("s_title", "The Lord of the Rings", type=str)
    s_author, s_title, s_authortitle = get_title_info(s_title, books)
    searching_title_msg = f"Recommendations for {s_title} from {s_author}:"
    sug_items = res_dict[s_authortitle]

    suggested_books = []
    suggested_authors = []
    for recom_book in sug_items:
        row = books.loc[books["authortitle"] == recom_book, :]
        suggested_books.append(list(row["title"])[0])
        suggested_authors.append(list(row["author"])[0])

    response_data = {"searching_title_msg": searching_title_msg,
                     "book1": suggested_books[0],
                     "book2": suggested_books[1],
                     "book3": suggested_books[2],
                     "book4": suggested_books[3],
                     "book5": suggested_books[4],
                     "author1": suggested_authors[0],
                     "author2": suggested_authors[1],
                     "author3": suggested_authors[2],
                     "author4": suggested_authors[3],
                     "author5": suggested_authors[4],
                     }
    return response_data


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)