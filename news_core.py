from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote
import xml.etree.ElementTree as ET
import datetime as dt
import email.utils
import html
import re
import time

TOPIC_BANK = [('社会', '防犯カメラ', '防犯カメラ プライバシー'), ('社会', '選択的夫婦別姓', '選択的夫婦別姓'), ('社会', '移民と共生', '外国人労働者 共生'), ('社会', '死刑制度', '死刑制度'), ('社会', 'SNSの実名制', 'SNS 実名制'), ('仕事', '週休3日制', '週休3日'), ('仕事', '生成AIと仕事', '生成AI 仕事'), ('仕事', '副業の自由', '副業 解禁'), ('仕事', 'リモートワーク', 'テレワーク 出社'), ('仕事', '定年延長', '定年延長'), ('教育', '学校の宿題', '宿題 学校'), ('教育', '学校の制服', '学校 制服 自由'), ('教育', '大学無償化', '大学 無償化'), ('教育', 'スマホと子ども', '子ども スマホ 規制'), ('教育', '部活動の地域移行', '部活動 地域移行'), ('暮らし', '食品ロス', '食品ロス'), ('暮らし', 'レジ袋有料化', 'レジ袋 有料化'), ('暮らし', 'キャッシュレス社会', 'キャッシュレス 現金'), ('暮らし', 'ふるさと納税', 'ふるさと納税'), ('暮らし', 'ペットとの暮らし', 'ペット 飼育 責任'), ('健康', '美容整形', '美容整形'), ('健康', '安楽死と尊厳死', '尊厳死 安楽死'), ('健康', '予防医療', '予防医療 健診'), ('健康', 'ワクチン接種', 'ワクチン 接種'), ('健康', '健康食品', '健康食品 効果'), ('環境', '原子力発電', '原発 再稼働'), ('環境', '再生可能エネルギー', '再生可能エネルギー'), ('環境', '電気自動車', '電気自動車 普及'), ('環境', 'プラスチック削減', 'プラスチック 削減'), ('環境', '動物園の役割', '動物園 動物福祉'), ('技術', '生成AIと創作', '生成AI 著作権 創作'), ('技術', '顔認証技術', '顔認証 プライバシー'), ('技術', '自動運転', '自動運転 事故'), ('技術', 'ネットの匿名性', 'インターネット 匿名'), ('技術', 'ロボットと介護', '介護 ロボット'), ('経済', '最低賃金', '最低賃金 引き上げ'), ('経済', '消費税', '消費税 減税'), ('経済', 'ベーシックインカム', 'ベーシックインカム'), ('経済', '観光とオーバーツーリズム', 'オーバーツーリズム'), ('経済', '現金給付と減税', '給付 減税'), ('文化', '推し活と消費', '推し活 消費'), ('文化', '文化財の保存', '文化財 保存'), ('文化', 'スポーツの男女区分', 'スポーツ 男女区分'), ('文化', '電子書籍と紙の本', '電子書籍 紙の本'), ('文化', '映画館の未来', '映画館 配信'), ('地域', '地方移住', '地方移住'), ('地域', '公共交通の維持', '地方 バス 廃止'), ('地域', '空き家問題', '空き家 対策'), ('地域', 'ごみ有料化', 'ごみ 有料化'), ('地域', '学校統廃合', '学校 統廃合')]
_cache = {'at': 0, 'payload': None}

# These are headline-based *angles*, never claims about the author's stance.
ANGLE_RULES = {
    '美容整形': [
        ('安全・健康', ('後遺症', '合併症', 'リスク', '医療事故', 'トラブル', '失敗', '健康被害')),
        ('社会・価値観', ('ルッキズム', '容姿', '偏見', '社会', '差別', '美の基準', '自己肯定')),
        ('体験・選択', ('体験', '経験', '告白', '選択', '自由', '決断', '施術')),
    ],
    '週休3日制': [
        ('働き方・生活', ('生活', '育児', '家族', '余暇', 'ワークライフ', '働き方')),
        ('経営・生産性', ('生産性', '企業', '導入', '経営', '人手不足', '業績')),
        ('給与・制度', ('給与', '給料', '賃金', '収入', '制度', '労働時間')),
    ],
    '生成AIと仕事': [
        ('雇用・不安', ('失業', '雇用', '解雇', '採用', '奪う', '代替', '仕事がない', 'リスク')),
        ('活用・効率', ('活用', '効率', '生産性', '導入', '自動化', '使い方', '任せた')),
        ('人間の役割', ('人間', '創造', 'スキル', '教育', '共存', '役割', '未来')),
    ],
    '食品ロス': [
        ('暮らし・行動', ('家庭', '食卓', '消費者', '買い物', '食べ残し', '家庭で')),
        ('企業・流通', ('企業', 'スーパー', '小売', '流通', '飲食店', '販売')),
        ('制度・環境', ('法律', '制度', '自治体', '環境', '廃棄', '政策')),
    ],
}

def headline_angle(topic, title):
    for angle, keywords in ANGLE_RULES.get(topic, []):
        if any(word.casefold() in title.casefold() for word in keywords):
            return angle
    return 'その他の話題'

def choose_diverse_articles(topic, items, limit=3):
    # Prefer distinct headline angles and publishers. Preserve RSS order as tie-breaker.
    chosen, sources, angles, remaining = [], set(), set(), list(items)
    while remaining and len(chosen) < limit:
        candidates = [(i, item) for i, item in enumerate(remaining) if item['source'] not in sources]
        if not candidates:
            break
        i, item = max(candidates, key=lambda pair: (
            int(headline_angle(topic, pair[1]['title']) not in angles), -pair[0]))
        remaining.pop(i)
        angle = headline_angle(topic, item['title'])
        chosen.append({**item, 'angle': angle})
        sources.add(item['source'])
        angles.add(angle)
    return chosen




def fetch_topic(label, query):
    url = 'https://news.google.com/rss/search?q=' + quote(query + ' when:14d') + '&hl=ja&gl=JP&ceid=JP:ja'
    request = Request(url, headers={'User-Agent': 'NeutralNewsPersonalReader/1.6 (+personal RSS reader)'})
    with urlopen(request, timeout=5) as response:
        xml = response.read(1024 * 1024)
    root = ET.fromstring(xml)
    found = []
    seen_urls = set()
    for item in root.findall('./channel/item'):
        title = html.unescape(' '.join((item.findtext('title', '') or '').splitlines()).strip())
        link = (item.findtext('link') or '').strip()
        source_el = item.find('source')
        source = (source_el.text or '').strip() if source_el is not None else ''
        date = (item.findtext('pubDate') or '').strip()
        if not title or not link.startswith('https://') or link in seen_urls:
            continue
        seen_urls.add(link)
        if source and title.endswith(' - ' + source):
            title = title[:-(len(source) + 3)]
        try:
            parsed = email.utils.parsedate_to_datetime(date)
            if parsed < dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=15):
                continue
        except (ValueError, TypeError):
            pass
        found.append({'title': title, 'url': link, 'source': source or '出典未取得', 'date': date})
    return found

def week_start(day=None):
    day = day or dt.date.today()
    return day - dt.timedelta(days=day.weekday())


def weekly_candidates(monday):
    # Stable weekly rotation: four different categories, no AI and no random state.
    # A different four-category combination is selected each Monday.
    import hashlib
    categories = sorted({cat for cat, _, _ in TOPIC_BANK})
    seed = int(hashlib.sha256(monday.isoformat().encode()).hexdigest()[:12], 16)
    ordered = sorted(categories, key=lambda cat: hashlib.sha256(
        (str(seed) + cat).encode()).hexdigest())
    chosen_categories = ordered[:4]
    selected = []
    for category in chosen_categories:
        entries = [(cat, name, query) for cat, name, query in TOPIC_BANK if cat == category]
        # Rotate within category by week; no dependency on Python's randomized hash.
        offset = (monday.toordinal() // 7 + categories.index(category)) % len(entries)
        selected.append(entries[offset])
    # Fallbacks are attempted only when a selected theme has no usable articles.
    remaining = [x for x in TOPIC_BANK if x not in selected]
    remaining.sort(key=lambda x: hashlib.sha256((monday.isoformat() + x[1]).encode()).hexdigest())
    return selected + remaining


def news():
    monday = week_start()
    key = monday.isoformat()
    if (_cache.get('week') == key and _cache['payload'] is not None
            and time.time() - _cache['at'] < 1800):
        return _cache['payload']
    results, errors, used_categories = [], [], set()
    candidates = weekly_candidates(monday)
    # Limit network calls to avoid long waits if feeds are unreachable.
    for category, label, query in candidates[:12]:
        if len(results) >= 4:
            break
        if category in used_categories:
            continue
        try:
            items = fetch_topic(label, query)
            unique = choose_diverse_articles(label, items)
            if unique:
                results.append({'topic': label, 'category': category,
                                'articles': unique, 'count': len(items)})
                used_categories.add(category)
        except Exception as exc:
            errors.append(label + ': 取得できませんでした (' + type(exc).__name__ + ')')
    payload = {'topics': results, 'errors': errors,
               'week_start': key, 'week_end': (monday + dt.timedelta(days=6)).isoformat(),
               'registered_topic_count': len(TOPIC_BANK),
               'updated_at': dt.datetime.now(dt.timezone.utc).isoformat(),
               'notice': '50テーマから週4テーマを自動選出。記事の有無で代替する場合があります。見出しの切り口は推定であり、賛否や著者の背景は判定していません。'}
    if results:
        _cache.update({'at': time.time(), 'payload': payload, 'week': key})
    return payload
