class NCBIGeneQuery:
    """A class to query against NCBI"""
    from Bio import Entrez

    def __init__(self,ncbigeneids):
        """Constructor that takes a list of NCBI Gene IDs"""
        # Setup API key and email address
        self.Entrez.api_key = "bff8a45aa66d302f3cb5347f248b275cb608"
        self.Entrez.email = "brian.marsden@sgc.ox.ac.uk"
        self.ncbigeneids = ncbigeneids

    def getNCBIGeneInfobyID(self):
        """Return salient information for the list of NCBI Gene IDs"""
        request = self.Entrez.epost(db="gene", id=",".join(self.ncbigeneids.apply(str)))
        result = self.Entrez.read(request)
        webEnv = result["WebEnv"]
        queryKey = result["QueryKey"]
        data = self.Entrez.esummary(db="gene", webenv=webEnv, query_key=queryKey)
        return self.Entrez.read(data)
