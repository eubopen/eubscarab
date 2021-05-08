#!/usr/bin/env python

import pandas as pd

import EUbSCARAB

# Example work flow for reading in list of NCBI Gene IDs, checking if they exist in EUbScarab, inserting if not,
# and writing out details of all genes in an Excel file.

# Read in file and tidy up
ncbi = pd.read_excel('ncbi.xlsx', engine='openpyxl')
ncbi.columns=['ncbi_gene_id']

# Connect to EUbScarab
eub = EUbSCARAB.EUbSCARABdb()
t= EUbSCARAB.Targets(eub.mydb)

# Add new Target records for the missing set of NCBI gene IDs read in
# Note that the second parameter, if set to True, causes a dry-run to occur
t.addNewRecordsbyNCBIGeneID(ncbi, False)

# Get info and write out Excel file summarising info for the Genes specified
t.pullRemoteGeneInfobyNCBIGeneID(ncbi)
quit()

