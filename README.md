Nucleotide-Fetch
================

Utility to fetch the nucleotide sequence of two consecutive genes from
Entrez

This was specifically hacked together to allow the user to input one
Entrez Accession ID and get back the nucleotide sequence of the
specified gene, the next downstream gene (depending on which strand
the specified gene is on), and the interstitial region.

While this behavior is certainly a niche, the underlying functions are
a decent reference for how to use the Entrez E-Utilities API's with
Python.  I specifically did not use the Requests library here because
I wanted maximum portability to bare Python installations.  I'm sure
the code could be much cleaner with Requests.

Written (and tested) in Python 3.3.x

Good reference on the Entrez E-utilities API:
http://www.ncbi.nlm.nih.gov/books/NBK25499/

## Usage

    python3 seqFetch.py YP_XXXXXXXXX.X

This will write 3 files in the working directory:
* The full Entrez gene record for the requested accession ID
* The full Entrez gene record for the next gene
* The fasta file of the sequence

## Known Issues

As of this writing, Entrez Gene is displaying an odd behavior where
the nucleotide indices bounding the sequence are off by one in the
positive direction.  This results in the output sequence having an
extra base, i.e. len(seq) % 3 != 0 that isn't actually part of the
sequence.

The XPath queries used are _very_ generic and could easily break if
the returned XML is in a different order.  During testing the API
always returned in the same order (as it should), but it could change
in the future.

