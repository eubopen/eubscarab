#!/usr/bin/env python

import pandas as pd

import EUbSCARAB

# Read in file and tidy up
ncbi = pd.read_excel('C:\\Users\\bmarsden\\Desktop\\ncbi.xlsx', engine='openpyxl')
ncbi.columns=['ncbi_gene_id']

# Connect to EUbScarab
eub = EUbSCARAB.EUbSCARABdb()
t= EUbSCARAB.Targets(eub.mydb)

# Add new Target records for the missing set of NCBI gene IDs read in
t.addNewRecordsbyNCBIGeneID(ncbi, False)

# Get info and write out Excel file summarising info for the Genes specified
t.pullRemoteGeneInfobyNCBIGeneID(ncbi)
quit()

