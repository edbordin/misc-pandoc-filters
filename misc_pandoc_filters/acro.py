from panflute import *
import urllib.parse
import sys

#acronyms = set()
definitions = {}

# prints to stderr - useful for debugging
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def acrolinks(elem, doc):
    if type(elem) == Link:
        linkref = elem.url
        acro = elem.content[0].text
        if linkref.startswith('acro:'):
            acrodef = urllib.parse.unquote(linkref[len('acro:'):])
            if acro not in definitions:
                definitions[acro] = acrodef
                return split_spaces(acrodef) + [Space(), Str('('+acro+')')]
            else:
                return split_spaces(acro)

def split_spaces(s):
    res = []
    split = s.split(' ')
    
    for x in split[:-1]:
        res.append(Str(x))
        res.append(Space())
    if len(split) > 0:
        res.append(Str(split[-1]))
    return res

def build_def_list():
    items = []
    for acro in definitions.keys():
        defn = Definition(Para(*split_spaces(definitions[acro])))
        items.append(DefinitionItem(term=[Str(acro)], definitions=[defn]))
    return DefinitionList(*items)

def main():
    doc = load()
    doc = run_filter(acrolinks, doc=doc)
    doc.content =  list(doc.content) + [build_def_list()]
    dump(doc)
    
if __name__ == "__main__":
    main()