from infrastructure.parser import Parser
from infrastructure.repository import Repository


if __name__ == "__main__":
    with open('resources/example.html', 'r') as f_in:
        raw_html = f_in.read()
    repo = Repository()
    news = Parser.parse_news(raw_html)
    added = repo.add_many(news)
    posts = repo.get(offset=30)
    print(posts)