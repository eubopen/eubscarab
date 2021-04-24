"""HGNC module

Provides tools for interacting progamatically with HGNC database

"""

import httplib2 as http
import json
import pandas as pd
import numpy as np
from urllib.parse import urlparse
from time import sleep


class HGNCquery:
    """A class providing query capabilities against HGNC"""
    def __init__(self):
        pass

    def getHGNCIDbyNCBIGeneID(self, ncbi):
        """Given a list of NCBI Gene IDs, return HGNC IDs or nan if not available"""
        # Setup for sending requests
        headers = {'Accept': 'application/json'}
        uri = 'http://rest.genenames.org'
        method = 'GET'
        body = ''

        # Create dataframe to take results
        df = pd.DataFrame(ncbi)
        df['hgncid'] = 0
        df['hgncid'] = df['hgncid'].astype(int)

        # Loop over each NCBI Gene ID
        for i in ncbi['ncbi_gene_id']:
            # Prep request
            path = '/search/entrez_id/' + str(i)
            target = urlparse(uri + path)
            # Send and receive request
            h = http.Http()
            response, content = h.request(target.geturl(), method, body, headers)
            # Deal with failure
            if response['status'] != '200':
                print('Error detected: ' + response['status'])
                return -1
            # Parse content with the json module
            data = json.loads(content)

            # Extract HGNC ID
            if data['response']['numFound'] == 1:
                hgncid = data['response']['docs'][0]['hgnc_id'].split(':')[1]
                df.loc[df['ncbi_gene_id'] == i, ['hgncid']] = int(hgncid)
            else:
                df.loc[df['ncbi_gene_id'] == i, ['hgncid']] = np.nan
                print(f'NCBI Gene ID {i} MISSING in HGNC!')

            # We must limit requests to 10 a second, so wait 0.1s
            sleep(0.1)

        # Return resulting dataframe
        return df
