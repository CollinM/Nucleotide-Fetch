import argparse
from urllib.request import urlopen
import xml.etree.ElementTree as ET
    
baseURL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
esearch = baseURL + "esearch.fcgi?db=gene&term="
genefetch = baseURL + "efetch.fcgi?db=gene&retmode=xml&id=";
protfetch = baseURL + "efetch.fcgi?db=protein&query_key={}&rettype=fasta&retmode=text"
nucfetch = baseURL + "efetch.fcgi?db=nuccore&id={}&strand={}&seq_start={}&seq_stop={}&rettype=fasta&retmode=text"
strand = {'plus': 1, 'minus': 2}

def parseArgs():
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
        sHandle = urlopen(esearch + query)
        doc = sHandle.read()
        #writeXML(doc, args.accid + '.txt')
        xml = ET.XML(doc)
        result = xml.find('.//Id').text
        print("Resulting ID: {}".format(result))
        return result

    def geneFetch(ID):
        url = genefetch + ID.strip()
        urlHandle = urlopen(url)
        return (urlHandle.read())

    def writeXML(doc, filename):
        """Write a document to disk."""
        filePtr = open(filename+ ".xml", 'w+b')
        filePtr.write(doc)
        filePtr.close()

    searchID = search(accid)
    geneDoc = geneFetch(searchID)
    writeXML(geneDoc, args.accid)
    return ET.XML(geneDoc)

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

def protFetch(ID):
    print("Fetching")
    fHandle = urlopen(efetch.format(ID))
    return ET.XML(fHandle.read())

def nucFetch(refseq, direction, start, end):
    print("Retrieving nucleotide sequence...")
    url = nucfetch.format(refseq, strand[direction], start, end)
    doc = urlopen(url).read()
    return doc

def getNextAccId(accid, direction):
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

def joinSeq(fastaList):
    seq = ""
    for l in fastaList:
        seq += l
    return seq

if __name__ == "__main__":
    args = parseArgs()

    # Retrieve xml for requested ID
    xml = getGeneXML(args.accid)
    gene1Info = parseXML(xml)
    start = gene1Info['to'] if gene1Info['direction'] == 'minus' else gene1Info['from']

    # Retrieve xml for following gene
    nextID = getNextAccId(args.accid, gene1Info['direction'])
    xml = getGeneXML(nextID)
    gene2Info = parseXML(xml)
    end = gene2Info['from'] if gene2Info['direction'] == 'minus' else gene2Info['to']

    # Fetch nucleotides in FASTA
    print("Sequence span and strand:" + str(start) + " - " + str(end) + ', ' + gene1Info['direction'])
    fasta = nucFetch(gene2Info['gi'], gene1Info['direction'], start, end).decode('utf-8')

    # Manipulate FASTA into list
    fasta = fasta.split('\n')
    fastaTail = fasta[1:]
    seq = joinSeq(fastaTail)

    # Write to file
    writeDoc(fasta, gene2Info['refseq'])
    
