# -*- coding: UTF-8 -*-
import os
import traceback

import requests
import json
import time
import webbrowser
from bs4 import BeautifulSoup

mainhttp = 'https://www.gequbao.com'
# mp3 保存位置
address = r"D:\tmp\download"
# 歌曲检索关键词，每行一个关键词，可以是歌手，专辑，歌曲名
musicList = r"D:\tmp\download\music.txt"
# 下载失败文件位置
downloadErrorFile = address + r"\error.txt"


def SearchMusic(_name, _retry):
    _getHtml = requests.get(mainhttp + '/s/' + _name).content.decode()
    _soup = BeautifulSoup(_getHtml, 'html.parser')
    _links = {}
    for _soup_a in _soup.find_all('a'):
        _link = _soup_a['href']
        _text = _soup_a.get_text()
        if _text.find('下载') != -1:
            continue
        if _text.find('翻自') != -1 | _text.find('cover') != -1:
            continue
        if _link.find('music') == -1:
            continue

        time.sleep(1)
        _songInfoHtml = requests.get(mainhttp + _link).content.decode()
        _downloadLinkStartSub = _songInfoHtml.index('const url = ')
        _downloadLinkEndSub = _songInfoHtml.index('.replace', _downloadLinkStartSub)
        _downloadLink = _songInfoHtml[
                        _downloadLinkStartSub + "const url = ".__len__() + 1:_downloadLinkEndSub - 1].replace('&amp;',
                                                                                                              '&')

        if _downloadLink.find('music.163') != -1:
            continue

        _mp3Name = _text.replace('\n', '').strip()
        if _mp3Name in _links.keys() and not _retry:
            continue
        else:
            if _mp3Name in _links.keys():
                _mp3Name = _mp3Name + "_" + str(len(_links) + 1)
            _downloadLink = _downloadLink.strip()
            if not _downloadLink.startswith("http"):
                continue
            _links[_mp3Name] = _downloadLink
            print("检索到歌曲 " + _mp3Name + ", 当前共计检索到：" + str(len(_links)) + " 条")
        if _retry and len(_links) >= 3:
            return _links
    return _links


def DownloadMusic(_dir, _musicName, _link):
    print(_musicName + "开始下载......")
    _fileName = _dir + '\\' + _musicName + '.mp3'
    if os.path.exists(_fileName):
        return True
    if not os.path.exists(_dir):
        os.makedirs(_dir)
    try:
        _file = requests.get(_link)
        if _file.text.find("410 Gone") == -1:
            open(_fileName, 'wb').write(_file.content)
            return True
        else:
            return False
    except Exception as e:
        traceback.print_exc()
        return False


def DownloadMusicRetry(_keywords, _musicName):
    print(_musicName + "重试......")
    try:
        _retryLinkMap = SearchMusic(_keywords + " " + _musicName, True)
        for _key in _retryLinkMap:
            time.sleep(10)
            if DownloadMusic(address + '\\' + _keywords, _key, _retryLinkMap[_key]):
                return True
            else:
                print(_key + "重试下载失败")
    except Exception as e:
        traceback.print_exc()
        return False
    return False


fileHandler = open(musicList, "r", encoding='utf-8')
listOfLines = fileHandler.readlines()
fileHandler.close()

for keywords in listOfLines:
    keywords = keywords.strip()
    if len(keywords) <= 1:
        continue
    print("检索 " + keywords + " ......")
    linkMap = SearchMusic(keywords, False)
    for musicName in linkMap:
        time.sleep(10)
        if DownloadMusic(address + '\\' + keywords, musicName, linkMap[musicName]):
            print(musicName + "下载成功")
        else:
            if DownloadMusicRetry(keywords, musicName):
                print(musicName + "重试下载成功")
            else:
                open(downloadErrorFile, 'a').write(keywords + " " + musicName + "\n")
                print(musicName + "无法下载，写入错误文件")
