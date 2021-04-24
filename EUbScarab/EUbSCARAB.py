"""EUbScarab module

Provides functionality for interactive with EUbScarab database, as well as useful ingest and aggregation functions

"""

import pandas as pd
import mysql.connector
from mysql.connector import errorcode

import UniProt
import NCBIGene
import HGNC


class EUbSCARABdb:
    """A class providing connectivity to EUbScarab database"""
    def __init__(self):
        try:
            self.mydb = mysql.connector.connect(
                host="demeter.sgc.ox.ac.uk",
                user="bmarsden",
                password="hgcab5h"
            )
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with the user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def __del__(self):
        self.mydb.close()


class Targets:
    """A class to provide support for EUbScarab Target entities"""
    def __init__(self, mydb):
        self.mydb = mydb

    @staticmethod
    def pullRemoteGeneInfobyNCBIGeneID(ncbi):
        """Given a list of NCBI Gene IDs, return salient Gene info from NCBI, UniProt and HGNC"""

        # Get UniProt details for list
        u = UniProt.UniProtQuery(ncbi['ncbi_gene_id'])
        udetails = u.getUniProtIDbyNCBIGeneID()

        # Join
        joined = pd.merge(left=ncbi, right=udetails, left_on='ncbi_gene_id', right_on='From', how='outer') \
            .groupby(['ncbi_gene_id']).first().reset_index()
        joined = joined.rename(columns={"To": "UniProtID"})
        joined = joined.drop("From", 1)

        # Get SwissProt details for list
        udetails = u.getUniProtACCbyNCBIGeneID()

        # Join
        joined = pd.merge(left=joined, right=udetails, left_on='ncbi_gene_id', right_on='From', how='outer') \
            .groupby(['ncbi_gene_id']).first().reset_index()
        joined = joined.rename(columns={"To": "UniProtACC"})
        joined = joined.drop("From", 1)
        joined.head(10)

        joined['Name'] = ""
        joined['Description'] = ""
        joined['Synonyms'] = ""

        # Get NCBI Gene info
        g = NCBIGene.NCBIGeneQuery(ncbi['ncbi_gene_id'])
        results = g.getNCBIGeneInfobyID()

        for record in results['DocumentSummarySet']['DocumentSummary']:
            recordgeneid = int(record.attributes['uid'])
            joined.loc[joined["ncbi_gene_id"] == recordgeneid, ["Name"]] = record['Name']
            joined.loc[joined["ncbi_gene_id"] == recordgeneid, ["Description"]] = record['Description']
            joined.loc[joined["ncbi_gene_id"] == recordgeneid, ["Synonyms"]] = record['OtherAliases']

        # Now do HGNC IDs
        h = HGNC.HGNCquery()
        results = h.getHGNCIDbyNCBIGeneID(ncbi)

        # Join
        joined = pd.merge(left=joined, right=results, left_on='ncbi_gene_id', right_on='ncbi_gene_id',how='outer') \
            .groupby(['ncbi_gene_id']).first().reset_index()
        joined = joined.rename(columns={"hgncid": "HGNCID"})

        # Write resulting dataframe to an Excel file
        joined.to_excel("C:\\Users\\bmarsden\\Desktop\\ncbiUniProt.xls")

        return joined

    def addNewRecordsbyNCBIGeneID(self,ncbigeneids,dryrun):
        """Given a list of NCBI Gene IDs, add missing records in EUbScarab's Target table"""
        # Notify if in dryrun mode
        if dryrun:
            print("Dry-run mode: No changes will be made to database.")
        # Get list of existing records
        query = "select ncbi_gene_id from eubopen.targets"
        df = pd.read_sql(query, con=self.mydb)

        # Work out which are not already in the db
        missing = ncbigeneids[~ncbigeneids.ncbi_gene_id.isin(df.ncbi_gene_id)]
        print(f'Received: {str(len(ncbigeneids.index))}, Missing: {str(len(missing.index))}')
        if len(missing) == 0:
            return 0

        # Get details for the missing targets
        details = self.pullRemoteGeneInfobyNCBIGeneID(missing)

        # Now insert the new records into EUbScarab
        c = self.mydb.cursor()
        for i, r in details.iterrows():
            name = r['Name']
            synonyms = r['Synonyms']
            ncbi = r['ncbi_gene_id']
            hgnc = r['HGNCID']
            uniprotID = r['UniProtID']
            uniprotACC = r['UniProtACC']
            description = r['Description']
            sql = 'insert into eubopen.targets (gene_symbol,synonyms,ncbi_gene_id,hgnc_id,' \
                  'uniprot_id,swissprot_id,site,description) ' \
                  'values (%s,%s,%s,%s,%s,%s,%s,%s)'
            vals = (str(r['Name']), str(r['Synonyms']), str(r['ncbi_gene_id']), str(r['HGNCID']),
                    str(r['UniProtACC']), str(r['UniProtID']), "TBD", str(r['Description']))
            if not dryrun:
                c.execute(sql, vals)
            insert = f'insert into eubopen.targets (gene_symbol,synonyms,ncbi_gene_id,hgnc_id,uniprot_id,' \
                     f'swissprot_id,site,description) ' \
                     f'values ("{name}","{synonyms}",{ncbi},{hgnc},"{uniprotACC}","{uniprotID}","TBD","{description}");'
            print(insert)

        self.mydb.commit()
