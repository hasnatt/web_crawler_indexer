import operator

from constants import (MAX_FIND_QUERY_WORDS, INVERTED_INDEX_FILE_NAME)
import json
import os
from collections import Counter

from utils import command_print


class InvertedIndex:
    inverted_index_dict = None

    def __new__(cls):
        # Controlling object creation only when inverted index json file exists
        # Otherwise there is no point of creating this class object
        if not os.path.isfile(INVERTED_INDEX_FILE_NAME):
            command_print(INVERTED_INDEX_FILE_NAME, "File doesn't exist. Please Use build command first")
        else:
            # Creating object as file exists
            return super(InvertedIndex, cls).__new__(cls)

    def __init__(self):
        # Initializing inverted_index_dict from json file
        with open(INVERTED_INDEX_FILE_NAME, "r") as inverted_index_file:
            self.inverted_index_dict = json.loads(inverted_index_file.read())

    def get_documents(self, search_query, is_find_command):
        """
        Return documents related to words in search query
        :param is_find_command:
        :param search_query:
        :return: 
        """
        result_documents = {}
        # set theoty based key, for the find commande find a set which contains all the words, in the
        # documents.
        final_keys_set = None
        result_document_counter = Counter({})
        query_words = search_query.split(" ")
        # For Print command we have max 1 query words
        max_query_words = 1
        if is_find_command:
            # For Find command we have max 3 query words
            max_query_words = MAX_FIND_QUERY_WORDS
        # Checking the number of query words are greater than limit
        if len(query_words) > max_query_words:
            command_print("Search query can't have more than {} words".format(max_query_words))
        else:
            # Iterating each query word one by one and getting its documents and count dictionary
            for query_word in query_words:
                if query_word:
                    current_word_documents = self.inverted_index_dict.get(query_word, {})
                    result_copy_dict = current_word_documents.copy()
                    # creating set of words that exists in all the documents
                    if not final_keys_set:
                        final_keys_set = set(result_copy_dict.keys())
                    else:
                        final_keys_set = final_keys_set & set(result_copy_dict.keys())
                    # Sum of the dictionaries using counter that adds up count against keys
                    result_document_counter += Counter(result_copy_dict)
            # if we have some result to send back final_key_set will not be empty it will contain
            # every unique document URL
            if final_keys_set:
                summed_counter_dict = dict(result_document_counter)
                # Creating dictionary only that for the words that are common in all words
                result_documents = {key: summed_counter_dict[key] for key in final_keys_set if
                                    key in summed_counter_dict}
                if is_find_command:
                    # Sorting the result dictionary only if it's find command
                    result_documents = dict(sorted(result_documents.items(), key=operator.itemgetter(1), reverse=True))
        return result_documents
