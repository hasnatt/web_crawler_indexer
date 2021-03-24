from web_crawler import WebCrawler
from inverted_index import InvertedIndex
from utils import command_print


class Main:
    crawler = None
    inverted_index = None

    @classmethod
    def build(cls):
        command_print("Build started")
        cls.crawler = WebCrawler()
        # run method for index
        cls.crawler.scrape_index_pages()
        # run method for all country pages
        cls.crawler.scrape_country_pages()
        # run method for all continent pages
        cls.crawler.scrape_continent_pages()
        # create the index from memory
        cls.crawler.create_index_file()
        command_print("Build completed")

    @classmethod
    def load(cls):
        cls.inverted_index = InvertedIndex()
        if cls.inverted_index:
            command_print("Inverted index loaded")

    @classmethod
    def print_or_find(cls, search_query, is_find_command):
        if cls.inverted_index:
            result_dict = cls.inverted_index.get_documents(search_query, is_find_command)
            if not result_dict:
                command_print("No result found against query '{}'".format(search_query))
            for document_url, count in result_dict.items():
                command_print(document_url, count)
        else:
            command_print("Inverted Index is not loaded.")


if __name__ == '__main__':
    command = ""
    main_obj = Main()
    print("Following commands are valid available commands:")
    print("1) build")
    print("2) load")
    print("3) find")
    print("4) print")
    print("5) quit")
    while True:
        command = input("> ")
        if command.strip().lower() == "quit":
            break
        elif command.startswith("build"):
            main_obj.build()
        elif command.startswith("load"):
            main_obj.load()
        # print and find used the same command so we find out if
        # the user entered find or print
        elif command.startswith("find "):
            main_obj.print_or_find(command.split("find ", 1)[1], True)
        elif command.startswith("print "):
            main_obj.print_or_find(command.split("print ", 1)[1], False)
        else:
            command_print("Invalid Command:", command)
        command = ""
