#!/usr/bin/python3
# 
# Simple filter that forces the author to define acronyms on first usage.
# A link element is used to define the acronym the first time:
# `[acro:TLA](Three Letter Acronym)`
# 
# For all subsequent uses of the acronym, use:
# `[acro:TLA]()`
# 
# The filter will warn if multiple definitions are given and will throw an error if the acronym is never defined.
# Optionally insert `$acronyms_list` into the document to generate a Definition List of acronyms used in the document


from panflute import *
import urllib.parse
import sys
import warnings

#acronyms = set()
__definitions = {}
ACRO_TAG='acro:'

# prints to stderr - useful for debugging
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def prepare(doc):
    doc.backmatter = {}

def acrolinks(elem, doc):
    if type(elem) == Link and type(elem.content[0]) == Str:
        linkref = elem.url
        acro = elem.content[0].text
        if acro.startswith(ACRO_TAG):
            stripped_acro = acro[len(ACRO_TAG):]
            acrodef = urllib.parse.unquote(linkref)
            if stripped_acro not in doc.backmatter:
                if len(acrodef) == 0:
                    raise ValueError(f'Definition not given for first use of acronym: {stripped_acro}\nExample syntax: [acro:TLA](Three Letter Acronym)\n')
                doc.backmatter[stripped_acro] = acrodef
                return split_spaces(acrodef) + [Space(), Str('('+stripped_acro+')')]
            else:
                if len(acrodef) > 0:
                    warnings.warn(f'Definition given for acronym that was already defined: {stripped_acro}\nExample syntax after first use: [acro:TLA]()\n')
                return split_spaces(stripped_acro)

def split_spaces(s):
    res = []
    split = s.split(' ')
    
    for x in split[:-1]:
        res.append(Str(x))
        res.append(Space())
    if len(split) > 0:
        res.append(Str(split[-1]))
    return res

def finalize(doc):
    items = []
    for acro in sorted(doc.backmatter.keys()):
        defn = Definition(Para(*split_spaces(doc.backmatter[acro])))
        items.append(DefinitionItem(term=[Str(acro)], definitions=[defn]))
    doc = doc.replace_keyword('$acronyms_list', DefinitionList(*items))

def main():
    doc = load()
    doc = run_filter(acrolinks, prepare, finalize, doc=doc)
    # doc.content =  list(doc.content) + [build_def_list()]
    dump(doc)
    
if __name__ == "__main__":
    main()
