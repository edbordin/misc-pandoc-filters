'''
Pandoc filter enabling markdown entensions for docx output

Copyright (C) Edward Bordin 2016
'''

from pandocfilters import *
import json
import sys
import re

secBrkXml = '<w:p><w:pPr><w:sectPr>\
<w:pgSz w:w="11906" w:h="16838"/>\
<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/>\
<w:cols w:space="708"/>\
<w:docGrid w:linePitch="360"/>\
</w:sectPr></w:pPr></w:p>'
secBrkXml2 = '<w:sectPr><w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/></w:sectPr>'

pageBrkXml='<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>'

def readJSON():
    try: 
        input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    except AttributeError:
        # Python 2 does not have sys.stdin.buffer.
        # REF: http://stackoverflow.com/questions/2467928/python-unicodeencodeerror-when-reading-from-stdin
        input_stream = codecs.getreader("utf-8")(sys.stdin)
        
    doc = json.loads(input_stream.read())
    return doc
    
def readFormat():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        return ""

def writeJSON(doc):
    print(json.dumps(doc))
    #json.dump(doc, sys.stdout)

#Paper sizes (w,h) in mm
paper_sizes = {
               'A0' : (841,1189),
               'A1' : (594,841),
               'A2' : (420,594),
               'A3' : (297,420),
               'A4' : (210,297),
               'A5' : (148,210),
               'A6' : (105,148)
               # TODO add more sizes, maybe put this in a separate file
              }

def main():
    jsondoc = readJSON()
    format = readFormat()
    meta = jsondoc['meta']
    doc = jsondoc['blocks']
    
    cur_size = 'A4'
    cur_orientation = 'portrait'
    
    # if format != 'docx' and False:
        # alt = doc
    # else:
    alt = []
    for block in doc:
        if block_matches(block,('RawBlock', 'latex', r'\newpage')):
            alt.append(RawBlock('openxml',pageBrkXml))
        elif block_matches(block,('RawBlock', 'latex')):
            texcmd = block['c'][1]
            if texcmd.startswith(r'\pagelayout'):
                eprint(texcmd)
                try:
                    texcmd = re.split(r'\{|\}', texcmd)
                    new_size = texcmd[1]
                    new_orientation = texcmd[3]
                    alt.append(RawBlock('openxml',gen_sectPr(cur_size,cur_orientation)))
                    if new_size not in paper_sizes:
                        raise ValueError('Paper size %s not known' % new_size)
                    cur_size = new_size
                    cur_orientation = new_orientation
                except Exception as e:
                    eprint('Error:',e)
                    alt.append(block)
        else:
            alt.append(block)
    alt.append(RawBlock('openxml',gen_sectPr(cur_size,cur_orientation, wrap_in_para=False)))
    eprint('=======')
    
    jsondoc['blocks'] = alt
    writeJSON(jsondoc)

# recursively checks if the block contains all of the items in the tuple
# Tuple is in the format (Type, Val1, Val2)
def block_matches(block, pattern):
    if block['t'] != pattern[0]:
        return False

    for i in range(1,len(pattern)):
        if isinstance(pattern[i], str):
            if block['c'][i-1] != pattern[i]:
                return False
        elif not block_matches(block['c'][i-1], pattern[i]):
            return False
    return True

# prints to stderr - useful for debugging
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# word defines page dimensions as multiples of 1/20 pt at 72 dpi
def mm_to_1_20_pt(mm):
    return int(round(mm / 25.4 * 72 * 20,0))

# generates the <sectPr> xml with page size and orientation - goes at the *end* of the section for some stupid reason
def gen_sectPr(size, orientation, wrap_in_para=True):
    w = mm_to_1_20_pt(paper_sizes[size][0])
    h = mm_to_1_20_pt(paper_sizes[size][1])
    
    # another stupid quirk - in landscape the width and height have to be swapped
    if orientation == 'landscape':
        w,h = h,w
    res = '<w:sectPr><w:pgSz w:w="%d" w:h="%d" w:orient="%s"/></w:sectPr>' % (w,h,orientation)
    if wrap_in_para:
        res = '<w:p><w:pPr>' + res + '</w:p></w:pPr>'
    eprint(res)
    return res

    
if __name__ == "__main__":
    main()