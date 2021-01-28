
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

def parse_bibtex_file(row_generator,source_nickname,detect_header):
    ret = {}
    current_record=[]
    header = '__no-head'
    def process_record(current_record,ret):
        """
        ret is modified in this function (i.e. 'pass-by-value')
        """
        rec = bibtex_to_dict('\n'.join(current_record))
        try:
            add_nickname_field(rec)
        except KeyError as ke:
            rec['nickname'] = '__missing__'

        rec['source'] = source_nickname
        ret[header].append(rec)

    for row in row_generator:
        new_header = detect_header(row)
        if new_header:
            header = new_header
            if header in ret:
                print(f"Warning: repeating header {header}")
            else:
                ret[header] = []
        if row.strip():
            current_record.append(row)
        elif current_record:
            process_record(current_record,ret)
            current_record = []
    if current_record:
        process_record(current_record,ret)
    return ret

def add_nickname_field(item_data):
    nonwords = {'the','a','on','do','does','in','note.','how'}
    item_data['nickname']="{}{}{}".format(
            item_data['author_list'][0][0], 
            item_data['year'], 
            [
                ''.join(c for c in word if c.isalnum()) 
                for word in item_data['title'].split() 
                if word.lower() not in nonwords
            ][0]
        ).replace(' ','_').lower()
    return item_data

if __name__ == "__main__":
    a = parse_bibtex_file('sample_file.txt')
    1
    

