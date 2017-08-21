# coding: utf-8

import requests
from bs4 import BeautifulSoup
import os
import codecs

"""
スマイティから口コミ情報を抽出するプログラム。
"""

class ScrapingReview:

    def __init__(self):
        # スマイティのURL
        self.BASE_URL = 'http://sumaity.com/town/'
        # レビューを取得する都道府県名
        self.PREF_NAME = 'osaka'
        # レビューを出力するファイルの拡張子
        self.FILE_TYPE = '.html'

    """
    引数で受け取った都道府県にアクセスし、市区町村のURLを取得して返す。

    引数 pref_url：都道府県ページのURL
    戻り値 city : 引数で受け取った都道府県の市区町村で、レビューが表示されているURLを返す。
    """

    def getCityUrlList(self):

        # URLにアクセスする。
        res = requests.get(self.BASE_URL + self.PREF_NAME)

        # 市区町村URLのリンクを取得する。
        city_url_links = BeautifulSoup(res.text, 'html.parser').find(attrs={"id": "searchPref"}).find_all('a')

        city = {}

        for link in city_url_links:
            if 'href' in link.attrs:
                city[link.text] = link.attrs['href'] + 'review/'

        return city

    """
    引数で受け取った市区町村単位でレビューを取得する。
    """

    def getCityReview(self, city_name, city_url):

        # URLにアクセスする。
        res = requests.get(city_url)

        # レビューが表示されているページのhtmlを取得する。
        soup = BeautifulSoup(res.text, 'html.parser')

        # レビューを取得して、リストに格納する。

        city_review_list = soup.find_all(attrs={"class": "revBox"})
        city_review_list.extend(soup.find_all(attrs={"class": "revTxt"}))

        return city_review_list

    """
    次のリンクがある場合は、再帰的にレビューを取得する。
    """
    def findReviewPage(self, city_name, city_url, count):

        if count == 1:
            # レビューを取得する。(1番目のレビュー)
            city_review_list = self.getCityReview(city_name, city_url)

            # レビューをファイルに書き込む
            self.writeReview(city_name, city_review_list)

        count = count + 1

        # URLにアクセスする。
        res = requests.get(city_url)

        # レビューが表示されているページのhtmlを取得する。
        soup = BeautifulSoup(res.text, 'html.parser')

        # 次のレビューが記載されているリンクを探す
        div_next = soup.find(attrs={"class": "next"})

        if div_next is not None:
            next_review_link = div_next.find('a').get('href')

            if next_review_link is not None:
                # 次のページで表示されているレビューを取得する。
                city_review_list = self.getCityReview(city_name, next_review_link)

                # レビューをファイルに書き込む
                self.writeReview(city_name, city_review_list)

                # また次のページを探す
                self.findReviewPage(city_name, next_review_link, count)

    """
    レビューを出力する
    """

    def writeReview(self, city_name, city_review_list):

        # レビューを保存するフォルダを作成する。
        save_folder_path = './' + self.PREF_NAME

        # フォルダがなければ作成する。
        if not os.path.isdir(save_folder_path):
            os.makedirs(save_folder_path)

        with codecs.open(save_folder_path + '/' + self.PREF_NAME + self.FILE_TYPE, 'a', 'utf-8') as f:
            for review in city_review_list:
                f.writelines('<h1>' + city_name + '</h1>')
                f.writelines('<p>' + review.text + '</p>')

# 本処理
scrapingReview = ScrapingReview()
city_list = scrapingReview.getCityUrlList()

for city_name in city_list:
    scrapingReview.findReviewPage(city_name, city_list[city_name], 1)
    print(city_name + 'のレビューが書き込み完了しました。')
