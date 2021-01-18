# coding: UTF-8

import requests
from bs4 import BeautifulSoup
import lxml.html
import twitter
import feedparser
import json
import difflib
import os
#config.pyに環境変数を設定している場合は読み込み
#import config

# ツイートに含めるハッシュタグを定義
hash_tag = "#都市大 #プレスリリース #新聞会 @tcuprs"
# 東京都市大学RSSリンク
RSS_URL = 'https://www.tcu.ac.jp/news/all/feed/'
# 類似度を決めるための指標 0.65ってのは感覚で決めた仮置きだけど多分これくらいで判定できると思う.
check_difflib_rate = float(0.65)

"""
東京都市大学の最新記事のタイトルとURLをリストに格納しreturnする
@param null

@return List tweet_contents
"""

def tcuprsNewArticleCrawler():
    
    tweet_contents = []
    # 東京都市大学の記事をRSSから取得
    feed = feedparser.parse(RSS_URL, response_headers={"content-type": "text/xml; charset=utf-8"})
    
    for entry in feed.entries:
        # タイトル取得
        tweet_contents.append(entry.title)
        # リンクの取得
        tweet_contents.append(entry.links[0].href)
        # 最新記事のみ取得するため一回目のループで終了する
        break
    return tweet_contents

"""
TwitterAPIを起動させtcuprsNewArticleCrawlerから返却された値が最新のものであれば内容をツイートする

@param null
@return null

"""

def usingTwitterAPI():
    
    content = ""
    recent_tweet_contents = ""
    
    # os.environから環境変数を読み込み
    # 別途サーバー側でos.environ(環境変数)を設定する必要あり
    CONSUMER_KEY = os.environ["YOUR_CONSUMER_KEY"]
    CONSUMER_SECRETY = os.environ["YOUR_CONSUMER_SECRET"]
    TOKEN = os.environ["YOUR_TOKEN"]
    TOKEN_SECRET = os.environ["YOUR_TOKEN_SECRET"]
    
    # authに環境変数を代入
    auth = twitter.OAuth(consumer_key=CONSUMER_KEY,
                        consumer_secret=CONSUMER_SECRETY,
                        token=TOKEN,
                        token_secret=TOKEN_SECRET)

    # 認証情報を付与
    t = twitter.Twitter(auth=auth)

    # RSSから取得した情報を取得
    tweet_contents = tcuprsNewArticleCrawler()

    # 自身のタイムラインからツイート内容を取得
    timelines = t.statuses.home_timeline()

    # 最新のタイムラインのツイートを取得
    for timeline in timelines:
        recent_tweet_contents = timeline['text']
        break

    # ツイート内容の作成
    content += tweet_contents[0] + "\n"
    content += tweet_contents[1] + "\n"
    content += hash_tag
    print(content)

    # 最新のツイートとの類似度をチェック
    #TODO 文字列比較で完全一致がうまくいかないから一旦類似度で対応.恐らくTwitterAPIから拾ってきている文言の形式とRSSから拾ってる文言の形式が若干違うんだと思う.
    s = difflib.SequenceMatcher(None, recent_tweet_contents, content).ratio()
    
    # 類似度のログを出力
    print("+++++++++++++++++++++++++++")
    print(s)
    print("++++++++++++++++++++++++++++")

    # ツイートの類似度が 65%以下だったらツイートする
    if s < check_difflib_rate:
        # ツイートする
        t.statuses.update(status=content)
        # ツイート内容のログ出力
        print(content)
    else:
        print("最新の記事はありません")

def main():
    usingTwitterAPI()

if __name__ == '__main__':
    main()
    
