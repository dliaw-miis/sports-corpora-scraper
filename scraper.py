#!/usr/bin/python

import getopt
import os
import sys
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from nltk import sent_tokenize, RegexpTokenizer

LANGUAGE = "en"
# TOKENIZER = None


def scrape_file(filename):
    if not os.path.exists(filename):
        print("File does not exist")
        return
    page_list = open(filename, "r").readlines()
    try:
        os.mkdir("pagecache")
    except:
        pass

    if len(page_list) == 0:
        print("No urls found")
        return

    #corpus_file = open(datetime.datetime.now().strftime("%y%m%d%I%M%S") + ".corpus.txt", "w")
    corpus_file = open("corpus.txt", "w")
    # for url in page_list[0:1]:
    for url in page_list:
        print(url)
        # Fetch page data
        output = ""
        stripped_url = url.strip()
        parsed_url = urlparse(stripped_url)
        filename = parsed_url.path.replace("/", "-")
        if not os.path.exists("./pagecache/" + filename):
            try:
                resp = requests.get(stripped_url)
                if resp.status_code != requests.codes.ok:
                    resp.raise_for_status()
                resp.encoding = "utf-8"
                output = resp.text
                page_cache = open("./pagecache/" + filename, "w")
                page_cache.write(output)
                page_cache.close()
                print("downloaded page")
            except Exception as e:
                print(e)
                continue
        else:
            output = open("./pagecache/" + filename, "r").read()
            print("found cached page")

        # Parse page
        article_soup = BeautifulSoup(output, "html.parser")
        if "theplayerstribune" in parsed_url.netloc:
            scrape_players_tribune(article_soup, corpus_file)
        elif "sportingnews" in parsed_url.netloc:
            scrape_sporting_news(article_soup, corpus_file)
        else:
            print("unsupported domain: " + parsed_url)
        print("finished processing: " + url)


def scrape_players_tribune(article_soup, corpus_file):
    content_tags = article_soup.find("article").find_all(["h1", "p"])
    for c in content_tags:
        tag_content = c.text
        if tag_content != None:
            tag_content = tag_content.strip()
            if len(tag_content) > 0:
                sentences = sentence_tokenize(tag_content)
                for sentence in sentences:
                    corpus_file.write(sentence + "\n")


def scrape_sporting_news(article_soup, corpus_file):
    title_tag = article_soup.find("h1", "article-page__title")
    corpus_file.write(title_tag.text + "\n")
    content_tags = article_soup.find(id="article-body").find_all(["h2", "p"])
    for c in content_tags:
        tag_content = c.text
        if tag_content != None:
            tag_content = tag_content.strip()
            if len(tag_content) > 0:
                sentences = sentence_tokenize(tag_content)
                for sentence in sentences:
                    corpus_file.write(sentence + "\n")


def sentence_tokenize(content):
    if LANGUAGE == "en":
        return sent_tokenize(content)
    # elif LANGUAGE == "jp":
    #     return TOKENIZER.tokenize(content)
    else:
        return [content]


def main(argv):
    opts, args = getopt.getopt(argv[1:], "j")

    if len(args) == 0:
        print("No filename provided")
        return

    for opt, arg in opts:
        if opt == "-j":
            global LANGUAGE
            # global TOKENIZER
            LANGUAGE = "jp"
            # TOKENIZER = RegexpTokenizer(u'[^　！？。]*([！？。.\n]|$)')
            break

    scrape_file(args[0])


if __name__ == "__main__":
    main(sys.argv)
