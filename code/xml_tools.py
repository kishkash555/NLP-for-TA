from lxml import etree

def get_keywords(fname):
    try:
        tree = etree.parse(fname)
        kws = [a for a in tree.getiterator() if a.tag.endswith('keywords')]
        if kws:
            for kws in kws[0].itertext():
                if not kws.strip() or len(kws)<2:
                    continue
                p =0
                for i,char in enumerate(kws[3:],3):
                    if char ==";" or char.isupper() and kws[i-1]==" " and kws[p:i].lower().strip().split(' ')[-1] not in {'and', 'multi'}:
                        yield kws[p:i].strip().lower()
                        p = i 
                yield kws[p:].lower()
    except:
        pass
        
def get_abstract_contents(fname):
    try:
        tree = etree.parse(fname)
    except etree.XMLSyntaxError:
        return ''
    abstr = [a for a in tree.getiterator() if a.tag.endswith('abstract')]
    if abstr:
        text = ''.join([a.strip() for a in abstr[0].itertext()])
        return text
    return ''
