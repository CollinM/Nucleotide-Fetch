import argparse
import sys
from urllib.request import urlopen
import xml.etree.ElementTree as ET
    
baseURL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
entrezSearch = baseURL + "esearch.fcgi?db=gene&term="
genefetch = baseURL + "efetch.fcgi?db=gene&retmode=xml&id=";
nucfetch = baseURL + "efetch.fcgi?db=nuccore&id={}&strand={}&seq_start={}&seq_stop={}&rettype=fasta&retmode=text"
strand = {'plus': 1, 'minus': 2}

def parseArgs():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser("Convert GI refs to protein sequence")
    parser.add_argument("accid", type=str, help="accession ID")
    return parser.parse_args()

def getGeneXML(accid):
    """
    Search Entrez Gene using the accession id (parameter).  Fetch the
    full Entrez Gene record and write it to disk as <accid>.xml.
    Return the Python XML object for the record.
    """
    def search(query):
        print("Searching \"{}\"".format(query))
        sHandle = urlopen(entrezSearch + query)
        doc = sHandle.read()
        #writeXML(doc, args.accid + '.txt')
        xml = ET.XML(doc)
        result = xml.find('.//Id').text
        print("Resulting ID: {}".format(result))
        return result

    def fetchGene(ID):
        url = genefetch + ID.strip()
        urlHandle = urlopen(url)
        return (urlHandle.read())

    def writeXML(doc, filename):
        """Write a document to disk."""
        filePtr = open(filename+ ".xml", 'w+b')
        filePtr.write(doc)
        filePtr.close()

    try:
        searchID = search(accid)
        geneDoc = fetchGene(searchID)
        writeXML(geneDoc, accid)
        return ET.XML(geneDoc)
    except AttributeError:
        print("Search for {} returned 0 results!".format(accid))
        print("EXITING EARLY!")
        sys.exit(0)

def parseXML(xml):
    result = {}
    result['gi'] = xml.find('.//Gene-source_src-int').text
    result['direction'] = xml.find('.//Na-strand').get('value')
    result['from'] = str(int(xml.find('.//Seq-interval_from').text))
    result['to'] = str(int(xml.find('.//Seq-interval_to').text) + 1)
    result['refseq'] = xml.find('.//Gene-commentary_accession').text
    result['refseq'] += '.' + xml.find('.//Gene-commentary_version').text
    return result

def writeDoc(strList, filename):
    """Write a document to disk."""
    print("Writing {} to disk...".format(filename))
    with open(filename + ".txt", 'w') as filePtr:
        for s in strList:
            print(s, file=filePtr)

def fetchNuc(refseq, direction, start, end):
    """

    """
    print("Retrieving nucleotide sequence...")
    url = nucfetch.format(refseq, strand[direction], start, end)
    doc = urlopen(url).read()
    return doc

def getNextAccId(accid, direction):
    """
    Get the accession ID for the next gene on the correct strand.
    """
    for i in range(len(accid)):
        try:
            if accid[i] == '0':
                continue
            prefix = accid[:i]
            num = float(accid[i:])
            break
        except:
            continue
    if direction == 'plus':
        num += 1
    else:
        num -= 1
    return prefix + str(num)

if __name__ == "__main__":
    args = parseArgs()

    # Retrieve xml for requested ID
    xml = getGeneXML(args.accid)
    gene1Info = parseXML(xml)
    start = gene1Info['to'] if gene1Info['direction'] == 'minus' else gene1Info['from']

    # Retrieve xml for next gene
    nextID = getNextAccId(args.accid, gene1Info['direction'])
    xml = getGeneXML(nextID)
    gene2Info = parseXML(xml)
    end = gene2Info['from'] if gene2Info['direction'] == 'minus' else gene2Info['to']

    # Fetch nucleotides in FASTA
    print("Sequence span and strand:" + str(start) + " - " + str(end) + ', ' + gene1Info['direction'])
    fasta = fetchNuc(gene2Info['gi'], gene1Info['direction'], start, end).decode('utf-8')

    # Manipulate FASTA into list
    fasta = fasta.split('\n')

    # Translate nucleotides to amino acids
    # fastaTail = fasta[1:]
    # seq = ""
    # for l in fastaTail:
    #     seq += l

    # Write to file
    writeDoc(fasta, gene2Info['refseq'])
    
