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
        # 口コミを取得する都道府県名
        self.PREF_NAME = 'osaka'
        # 口コミを取得する都道府県名(漢字)
        self.PREF_NAME_KANJI = '大阪府'
        # 口コミを出力するファイルの拡張子
        self.FILE_TYPE = '.html'
        # カウンター
        self.counter = 1

    """
    引数で受け取った都道府県にアクセスし、市区町村の駅単位でURLを取得して返す。
    戻り値 city : 引数で受け取った都道府県の市区町村で、口コミが表示されているURLを返す。
    """

    def getCityUrlList(self):

        # URLにアクセスする。
        res = requests.get(self.BASE_URL + self.PREF_NAME)

        # 市区町村URLのリンクを取得する。
        city_url_links = BeautifulSoup(res.text, 'html.parser').find(attrs={"id": "leadTopPref"}).find_all('a')

        # リンクからURLを取得する。
        city_list = {}
        for link in city_url_links:
            if 'href' in link.attrs:
                city_list['(' + self.PREF_NAME_KANJI + link.text+ ')'] = link.attrs['href']

        return city_list

    """
    市区町村の駅単位で口コミが掲載されているURLを取得して、返す。
    """
    def getStationList(self, city_list):

        review_list = {}
        for city_name in city_list:

            res = requests.get(city_list[city_name])

            # 市区町村の駅URLを取得する。
            div = BeautifulSoup(res.text, 'html.parser').find('div',attrs={'class': 'infoBox infStBx'})

            if div is not None:
                station_url_links = div.find_all('a')

                # 駅単位で口コミが掲載されているURLを取得する。
                if station_url_links is not None:
                    for link in station_url_links:
                        if 'href' in link.attrs:
                            review_list[link.text + city_name] = link.attrs['href'] + 'review'

        return review_list

    """
    引数で受け取ったURLの口コミを取得する。
    """

    def getReview(self, url):

        # URLにアクセスする。
        res = requests.get(url)

        # 口コミが表示されているページのhtmlを取得する。
        soup = BeautifulSoup(res.text, 'html.parser')

        # 口コミを取得して、リストに格納する。

        review_list = []
        review_list = soup.find_all(attrs={"class": "revBox"})
        review_list.extend(soup.find_all(attrs={"class": "revTxt"}))

        # 重複している口コミを削除する。
        unique_review_list = []
        for review in review_list:
            if review.text not in unique_review_list:
                unique_review_list.append(review.text)

        return unique_review_list

    """
    次のリンクがある場合は、再帰的に口コミを取得する。
    """
    def findReviewPage(self, name, url, count):

        if count == 1:
            # 口コミを取得する。(1番目の口コミ)
            review_list = self.getReview(url)

            # 口コミをファイルに書き込む
            self.writeReview(name, review_list)

        count = count + 1

        # URLにアクセスする。
        res = requests.get(url)

        # 口コミが表示されているページのhtmlを取得する。
        soup = BeautifulSoup(res.text, 'html.parser')

        # 次の口コミが記載されているリンクを探す
        div_next = soup.find(attrs={"class": "next"})

        if div_next is not None:
            next_review_link = div_next.find('a').get('href')

            if next_review_link is not None:
                # 次のページで表示されている口コミを取得する。
                next_review_list = self.getReview(next_review_link)

                # 口コミをファイルに書き込む
                self.writeReview(name, next_review_list)

                # また次のページを探す
                self.findReviewPage(name, next_review_link, count)

    """
    口コミをファイルに出力する
    """
    def writeReview(self, city_name, city_review_list):

        # 口コミを保存するフォルダを作成する。
        save_folder_path = './' + self.PREF_NAME

        # フォルダがなければ作成する。
        if not os.path.isdir(save_folder_path):
            os.makedirs(save_folder_path)

        with codecs.open(save_folder_path + '/' + self.PREF_NAME + self.FILE_TYPE, 'a', 'utf-8') as f:

            for review in city_review_list:
                f.writelines('<h1>' + city_name + '</h1>')
                f.writelines('<p>' + review + '</p>')

# 本処理
scrapingReview = ScrapingReview()
city_list = scrapingReview.getCityUrlList()
station_list = scrapingReview.getStationList(city_list)

for station_name in station_list:
    scrapingReview.findReviewPage(station_name, station_list[station_name], 1)
    print(station_name + 'の口コミが書き込み完了しました。')

print('全ての口コミの書き込みが完了しました。')