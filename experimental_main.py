import os
import requests
from utils.get_char import _Getch
from elasticsearch import Elasticsearch


class ExperimentalMain(object):

    def __init__(self):
        pass

    @staticmethod
    def get_results_by_prefix(es, prefix):
        res = es.search(index="sw", body={"query": {"prefix": {"name": prefix}}})
        results_list = ExperimentalMain.results_to_string_list(res)
        return results_list

    @staticmethod
    def autocomplete():

        print("Connecting to Elastic Search...")

        # Connect to the ES Cluster
        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

        getch = _Getch()
        import os
        ngram = ''
        finished = False
        results = []
        fuzzy = False

        the_byte = ''
        while not finished:
            os.system('cls')
            #print("Type a person/company name (type @ to switch search-mode / type ! to exit):")
            print("Type a Star Wars character name (fuzzy = %s)" % fuzzy)
            print("(type @ to switch search-mode / type ! to exit)")
            # print("the_byte = %s" % the_byte)
            print(">>> %s" % ngram)
            print("\r\n")
            for r in results:
                print(r)
            the_byte = getch()
            k = the_byte.decode("utf-8")

            # Should we terminate?
            if k == '!':
                finished = True
                continue

            # Should switch search mode
            if k == '@':
                fuzzy = not fuzzy
                continue

            # Should we erase last character?
            if the_byte == b'\x08':
                the_byte = 'DELETE'
                ngram = ngram[:-1]
            else:
                ngram += k

            # If 2 characters and more, start the search and show results:
            if not fuzzy and len(ngram) >= 2:
                #results = [x+1 for x in range(0, len(ngram))]
                results = ExperimentalMain.get_results_by_prefix(es, ngram.lower())

            if fuzzy and len(ngram) >= 4:
                results = ExperimentalMain.get_results_by_fuzzy(es, ngram.lower())
        pass


    @staticmethod
    def get_results_by_fuzzy(es, search_term):
        q = {"query": {
                "match": {
                    "name": {
                        "query": search_term,
                        "fuzziness": 1
                        #"prefix_length": 1
                    }
                }
            }}
        res = es.search(index="sw", body=q)
        results_list = ExperimentalMain.results_to_string_list(res)
        return results_list

    @staticmethod
    def test_elastic_search():

        # Check that ES node is responding
        res = requests.get('http://localhost:9200')
        print(res.content)

        # Connect to the ES Cluster
        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

        results = ExperimentalMain.get_results_by_prefix(es, 'ja')

        name = r'lÜke'
        results = ExperimentalMain.get_results_by_fuzzy(es, name)

        # let's iterate over swapi people documents and index them
        import json
        r = requests.get('http://localhost:9200')
        i = 0
        while i < 87 and r.status_code == 200:
            i += 1
            if i == 17:
                continue
            r = requests.get('http://swapi.co/api/people/' + str(i))
            txt = r.text  # equals to: r.content.decode("utf-8")
            es.index(index='sw', doc_type='people', id=i, body=json.loads(txt))
        print(i)

        # Lets try to get something out of ES
        res = es.get(index='sw', doc_type='people', id=5)

        res = es.search(index="sw", body={"query": {"prefix": {"name": "lu"}}})

        res = es.search(index="sw", body={"query": {"match": {"name": {"query": "jaba", "fuzziness": 2, "prefix_length": 1}}}})

        pass


if __name__ == '__main__':

    # Insert another comment

    # Elastic Search Tests...
    #ExperimentalMain.autocomplete()
    ExperimentalMain.test_elastic_search()


