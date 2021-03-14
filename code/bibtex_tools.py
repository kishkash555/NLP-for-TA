import json
import networkx as nx
from os import path
import PyPDF2 as pdf
import pickle

example_bibtex =\
"""
article{48,
  author = {Zhu, K and Zang, R and Tsung, F},
  title = {Pushing quality along the supply chain},
  journal = {Manag. Sci},
  year = {2007},
  pages = {421--436},
  volume = {53},
  number = {3}
}
"""
from collections import Counter

def nx_to_sigm_json(gr):
    return str(json.dumps(nx.readwrite.json_graph.node_link_data(gr))).replace('links','edges')

def spring_layout(gr):
        locs = nx.drawing.layout.spring_layout(gr)
        nx.set_node_attributes(gr, {k: {'x': round(v[0],3) , 'y': round(v[1],3), 'size': 3, 'label': k, } for k, v in locs.items()})

class ref_dict(dict):
    """
    this is a dictionary with each entry representing an article
    each value is a list of dictionary representing references
    the nickname field of each article is its unique identified
    this class helps make the code for creating and manipulating this entity
    more readable and concentrated
    """
  
    def write_json(self,file):
        json.dump(self,file)
    
    def from_json(self, json_string='', json_file=''):
        if json_string:
            self.update(json.loads(json_string))
        elif json_file:
            with open(json_file,'rt') as a:
                self.update(json.load(a))
        else:
            raise ValueError("need either an input_string or a filename")
    
    def replace_nicknames(self,replace_spec):
        """
        extract the nickname field of each entry in each value and 
        replace with corrected nickname.
        The replace spec is based on manual review for small error
        especially when title and journal are the same but year is different
        """
        all_dicts = sum(self.values(),[])
        replace_counter = Counter()
        # replace occurrences in values
        for cit in all_dicts:
            if cit.get('nickname') in replace_spec:
                nn_to_replace = cit['nickname']
                replace_counter[nn_to_replace] += 1
                cit['nickname'] = replace_spec[nn_to_replace]
        # replace occurrences in keys
        for k in self.keys():
            if k in replace_spec:
                replace_counter[k] +=1
                self[replace_spec[k]] = self[k]
                del self[k]
        return replace_counter

    def to_graph(self):
        """
        Create a directed graph for the main articles (those appearing as keys)
        """
        gr = nx.DiGraph()
        edge_id=0
        for source_node, references in self.items():
            gr.add_node(source_node)
            for reference in references:
                if reference['nickname'] in self:
                    gr.add_edge(reference['nickname'], source_node, id=edge_id, type='arrow')
                    edge_id +=1


        return gr

    def to_bib_coupling_graph(self):
        ref_nick_sets = { k: set([ref['nickname'] for ref in v if ref['nickname']!='__missing__']) for k, v in self.items()}
        nodes = list(self.keys())
        gr = nx.Graph()
        gr.add_nodes_from(nodes)
        edge_id=1000
        for i,first_node in enumerate(nodes):
            for second_node in nodes[i+1:]:
                common_refs = len(ref_nick_sets[first_node].intersection(ref_nick_sets[second_node]))
                if common_refs:
                    gr.add_edge(first_node, second_node, id=edge_id, weight=common_refs)
                    edge_id += 1
        return gr

    def save(self,fname):
        with open(fname,'wb') as a:
            pickle.dump(self, a)

    @staticmethod
    def load(fname):
        with open(fname,'rb') as a:
            obj = pickle.load(a)
            if type(obj)==dict:
                obj = ref_dict(obj) 
        return obj
        


class ref_dict_tools:
    @staticmethod
    def bibtex_to_dict(citation):
        ret = {}
        for row in citation.split('\n'):
            if '=' in row:
                field, value = row.split('=',1)
                ret[field.strip()] = value.strip(' {},\n')
        if 'author' in ret:
            author_list = ret['author'].split(' and ')
            
            ret['author_list'] = [
                tuple(name_part.strip() for name_part in author.split(',')) for author in author_list
                ]
        return ret

    @staticmethod
    def parse_bibtex_file(row_generator,source_nickname,detect_header):
        ret = {}
        current_record=[]
        header = '__no-head'
        def process_record(current_record,ret):
            """
            ret is modified in this function (i.e. 'pass-by-value')
            """
            rec = ref_dict_tools.bibtex_to_dict('\n'.join(current_record))
            try:
                ref_dict_tools.add_nickname_field(rec)
            except KeyError as ke:
                rec['nickname'] = '__missing__'

            rec['source'] = source_nickname
            ret[header].append(rec)

        for row in row_generator:
            new_header = detect_header(row)
            if new_header:
                header = new_header
                if header in ret:
                    header = get_nonexistent_key(header,ret)
                
                ret[header] = []
            if row.strip():
                current_record.append(row)
            elif current_record:
                process_record(current_record,ret)
                current_record = []
        if current_record:
            process_record(current_record,ret)
        return ret


    @staticmethod
    def add_nickname_field(item_data):
        nonwords = {'the','a','on','do','does','in','note.','how','an','implementing','to'}
        item_data['nickname']="{}{}{}".format(
                item_data['author_list'][0][0], 
                item_data['year'], 
                [
                    ''.join(c for c in word if c.isalnum()) 
                    for word in item_data.get('title' if 'title' in item_data else 'booktitle','notitle').split() 
                    if word.lower() not in nonwords
                ][0]
            ).replace(' ','_').lower()
        return item_data

def file_list_to_nicknames(file_list):
    """
    input: a list of filenames contain full text articles.
    The file name is presumed to be based on first author and year 
    eg. 'Cao et al 2020.pdf'
    This function uses the information in the file name
    as well as the title, taken from the file's metadata
    to construct the article's nickname
    """
    md = [get_pdf_metadata(f) for f in file_list]

    prefixes={'de', 'van', 'mc'}

    fnames = [path.basename(a) for a in file_list] 
    auths = [a.lower().split(' ') for a in fnames]
    auths = [a[0] if a[0] not in prefixes else a[0]+a[1] for a in auths]
    years = [a.split('.')[0].split(' ')[-1].rstrip('abcd') for a in fnames]
    titles = [d.get('/Title','NoTitle') if hasattr(d,'get') else 'Unknown' for d in md ] #,d.get('/doi','NoTitle'))

    entries = [ {
        'title': t,
        'year': y,
        'author_list': [(a,'')]
        }
        for t,y,a in zip(titles, years, auths)
    ]
    return { fn.split('.')[0]: ref_dict_tools.add_nickname_field(e) for fn, e in zip(fnames,entries)}

def get_pdf_metadata(fname):
    with open(fname,'rb') as f:
        inp_file = pdf.PdfFileReader(f)
        d=inp_file.getDocumentInfo()
    return d

def get_nonexistent_key(candidate, d):
    """
    Get the path to a filename which does not exist by incrementing path.

    Examples
    --------
    >>> get_nonexistant_path('/etc/issue')
    '/etc/issue-1'
    >>> get_nonexistant_path('whatever/1337bla.py')
    'whatever/1337bla.py'
    """
    if not candidate in d:
        return candidate
    i = 1
    new_name = candidate.rsplit("-",1)[0] 
    new_name = "{}-{}".format(new_name, i)
    while new_name in d:
        i += 1
        new_name = "{}-{}".format(candidate, i)
    print("Changed {} to {}".format(candidate, new_name))
    return new_name


if __name__ == "__main__":
    files = ['../articles_from_tatiana/fulltext-pdf-batch2/Cao et al 2020.pdf',
            '../articles_from_tatiana/fulltext-pdf-batch2/Chen et al 2020.pdf']
    file_list_to_nicknames(files)
 #   get_pdf_metadata(files[0])
    """
    a = ref_dict_tools.parse_bibtex_file('sample_file.txt')
    1
    """

