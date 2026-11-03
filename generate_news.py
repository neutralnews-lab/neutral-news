"""Build a static weekly feed for GitHub Pages. No keys or paid APIs."""
import json
from pathlib import Path
from news_core import news


def main():
    data = news()
    if not data['topics']:
        raise RuntimeError('記事を取得できませんでした。既存のニュースを上書きしません。')
    output = Path(__file__).parent / 'docs' / 'news.json'
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Updated', output, 'topics:', len(data['topics']))


if __name__ == '__main__':
    main()
