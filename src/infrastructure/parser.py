from datetime import datetime

from bs4 import BeautifulSoup

class Parser:
    @staticmethod
    def parse_news(raw_html) -> []:
        parsed_html = BeautifulSoup(raw_html, features="html.parser")
        news_list = parsed_html.body.find_all('a', attrs={'class': 'storylink'})
        results = []
        for news in news_list:
            news_elem = {
                "title": news.text,
                "url": news.attrs['href'],
                "created": datetime.utcnow().isoformat()  
            }
            results.append(news_elem)
        return results

if __name__ == "__main__":
    with open('resources/example.html', 'r') as f_in:
        raw_html = f_in.read()
    news_list = Parser.parse_news(raw_html=raw_html)
    print(news_list)