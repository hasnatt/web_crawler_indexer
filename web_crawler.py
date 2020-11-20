import time

import requests
from bs4 import BeautifulSoup
from constants import (SITE_BASE_URL, SITE_INDEX_URL, MAX_SITE_INDEXES, POSTAL_CODE_REGEX, CONTINENT,
                       INVERTED_INDEX_FILE_NAME, SLEEP_TIME_SECONDS)
from utils import time_print
import json


class WebCrawler:
    session_requests = None
    country_urls = None
    continent_urls = None
    collected_data = None

    def __init__(self):
        self.session_requests = requests.session()
        self.country_urls = []
        self.continent_urls = []
        self.collected_data = {}

    @staticmethod
    def get_words_from_sentence(sentence):
        """
        Breaks the sentence into words
        :param sentence:
        :return: List of words
        """
        sentence = sentence.replace("\n", " ").strip().strip(":")
        return sentence.split(" ")

    def scrape_index_pages(self):
        """
        Collecting all links of countries from index pages
        """
        for index in range(MAX_SITE_INDEXES):
            current_index_page_url = SITE_INDEX_URL.format(index)
            time_print(current_index_page_url)
            result = self.session_requests.get(current_index_page_url)
            if result.ok and result.status_code == 200:
                soup = BeautifulSoup(result.content, "html.parser")
                results_div = soup.find('div', attrs={"id": "results"})
                result_table = results_div.find('table')
                all_result_urls = result_table.find_all('a')
                for result_url in all_result_urls:
                    self.country_urls.append(SITE_BASE_URL.format(result_url['href']))
                self.update_collected_data(current_index_page_url, result_table.text)
            time.sleep(SLEEP_TIME_SECONDS)

    def scrape_country_pages(self):
        """
        Collecting data from country pages and collecting continent URLS
        """
        # Iterating each country URL and collecting data from it
        # country urls are collected already while collecting index pages.
        for index in range(len(self.country_urls)):
            current_country_url = self.country_urls[index]
            time_print(current_country_url)
            result = self.session_requests.get(current_country_url)
            if result.ok and result.status_code == 200:
                soup = BeautifulSoup(result.content, "html.parser")
                result_table = soup.find('table')
                # Collecting all the rows in the table
                all_rows = result_table.find_all('tr')
                for row in all_rows:
                    # Iterating every row and getting all columns that is 2 columns per row in this case.
                    all_columns = row.find_all('td')
                    collect_continent_url = False
                    for column in all_columns:
                        # Iterating each column of each row
                        column_text = str(column.text).strip()
                        # Writing column text in inverted index dictionary
                        self.update_collected_data(current_country_url, column_text)
                        if collect_continent_url:
                            # collecting continent url
                            link = column.find('a')
                            if link:
                                continent_url = SITE_BASE_URL.format(link['href'])
                                if continent_url not in self.continent_urls:
                                    self.continent_urls.append(continent_url)
                        # handling case of not collecting postal code regex value due to invalid characters
                        if column_text == POSTAL_CODE_REGEX:
                            break
                        elif column_text == CONTINENT:
                            collect_continent_url = True
            time.sleep(SLEEP_TIME_SECONDS)

    def scrape_continent_pages(self):
        """
        Collecting data from continent pages
        """
        # Iterating through each continent URL and collecting only names of countries and heading of continent
        for index in range(len(self.continent_urls)):
            current_continent_url = self.continent_urls[index]
            time_print(current_continent_url)
            result = self.session_requests.get(current_continent_url)
            if result.ok and result.status_code == 200:
                soup = BeautifulSoup(result.content, "html.parser")
                continent_heading_text = soup.find('h2').text
                # updating heading text in index dictionary
                self.update_collected_data(current_continent_url, continent_heading_text)
                result_table_text = soup.find('table').text
                # updating table text that includes country names in index dictionary
                self.update_collected_data(current_continent_url, result_table_text)
            time.sleep(SLEEP_TIME_SECONDS)

    def update_collected_data(self, document_url, sentence):
        """
        Updates collected_data dictionary index from sentence
        :param str document_url: Document URL
        :param str sentence: Sentence that will be used to make words
        """
        words = WebCrawler.get_words_from_sentence(sentence)
        for word in words:
            if word:
                # Updating each word in index and putting document url against it and
                # Updating the count of that document url
                word_data_dict = self.collected_data.get(word, {})
                word_document_count = word_data_dict.get(document_url, 0)
                word_data_dict[document_url] = word_document_count + 1
                self.collected_data[word] = word_data_dict

    def create_index_file(self):
        """
        Write collected to file as json
        """
        with open(INVERTED_INDEX_FILE_NAME, "w") as inverted_index_file:
            inverted_index_file.write(json.dumps(self.collected_data))
        self.collected_data = {}
        print(self.collected_data)
