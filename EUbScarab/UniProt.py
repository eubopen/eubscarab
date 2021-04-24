import pandas as pd
import urllib.parse
import urllib.request
from io import StringIO


class UniProtQuery:
    def __init__(self, query):
        self.url = 'https://www.uniprot.org/uploadlists/'
        self.params = {
            'from': 'P_ENTREZGENEID',
            'to': 'ACC',
            'format': 'tab',
            'query': query.apply(str).str.cat(sep=' ')
        }

    def __getUniProt(self):
        data = urllib.parse.urlencode(self.params)
        data = data.encode('utf-8')
        req = urllib.request.Request(self.url, data)
        with urllib.request.urlopen(req) as f:
            response = f.read()
        return pd.read_csv(StringIO(response.decode('utf-8')), sep='\t')

    def getUniProtIDbyNCBIGeneID(self):
        self.params['to'] = 'ID'
        return self.__getUniProt()

    def getUniProtACCbyNCBIGeneID(self):
        self.params['to'] = 'ACC'
        return self.__getUniProt()
