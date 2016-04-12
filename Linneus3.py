# Linneus3.py
# Implements storage and inference on an ISA hierarchy
# This Python program goes with the book "The Elements of Artificial
# Intelligence".
# This version runs under Python 3.x.

# Steven Tanimoto
# (C) 2012.

# The ISA relation is represented using a dictionary, ISA.
# There is a corresponding inverse dictionary, INCLUDES.
# Each entry in the ISA dictionary is of the form
#  ('turtle' : ['reptile', 'shelled-creature'])

from re import *   # Loads the regular expression module.

ISA = {}
INCLUDES = {}
ARTICLES = {}

def store_isa_fact(category1, category2):
    'Stores one fact of the form A BIRD IS AN ANIMAL'
    # That is, a member of CATEGORY1 is a member of CATEGORY2
    try :
        c1list = ISA[category1]
        c1list.append(category2)
    except KeyError :
        ISA[category1] = [category2]
    try :
        c2list = INCLUDES[category2]
        c2list.append(category1)
    except KeyError :
        INCLUDES[category2] = [category1]
        
def get_isa_list(category1):
    'Retrieves any existing list of things that CATEGORY1 is a'
    try:
        c1list = ISA[category1]
        return c1list
    except:
        return []
    
def get_includes_list(category1):
    'Retrieves any existing list of things that CATEGORY1 includes'
    try:
        c1list = INCLUDES[category1]
        return c1list
    except:
        return []
    
def isa_test1(category1, category2):
    'Returns True if category 2 is (directly) on the list for category 1.'
    c1list = get_isa_list(category1)
    return c1list.__contains__(category2)
    
def isa_test(category1, category2, depth_limit = 10):
    'Returns True if category 1 is a subset of category 2 within depth_limit levels'
    if category1 == category2 : return True
    if isa_test1(category1, category2) : return True
    if depth_limit < 2 : return False
    for intermediate_category in get_isa_list(category1):
        if isa_test(intermediate_category, category2, depth_limit - 1):
            return True
    return False

def store_article(noun, article):
    'Saves the article (in lower-case) associated with a noun.'
    ARTICLES[noun] = article.lower()

def get_article(noun):
    'Returns the article associated with the noun, or if none, the empty string.'
    try:
        article = ARTICLES[noun]
        return article
    except KeyError:
        return ''

def linneus():
    'The main loop; it gets and processes user input, until "bye".'
    print('This is Linneus.  Please tell me "ISA" facts and ask questions.')
    print('For example, you could tell me "An ant is an insect."')
    while True :
        info = input('Enter an ISA fact, or "bye" here: ')
        if info == 'bye': return 'Goodbye now!'
        process(info)

# Some regular expressions used to parse the user sentences:    
# assertion_pattern: "A [category1] is a [category2]."
# query_pattern: "Is a [category1] a [category2]?"
# what_pattern: "What is a [category]?"
# why_pattern: "Why is a [category1] a [category2]?"
assertion_pattern = compile(r"^(a|an|A|An)\s+([-\w]+)\s+is\s+(a|an)\s+([-\w]+)(\.|\!)*$", IGNORECASE)    
query_pattern = compile(r"^is\s+(a|an)\s+([-\w]+)\s+(a|an)\s+([-\w]+)(\?\.)*", IGNORECASE)    
what_pattern = compile(r"^What\s+is\s+(a|an)\s+([-\w]+)(\?\.)*", IGNORECASE)    
why_pattern = compile(r"^Why\s+is\s+(a|an)\s+([-\w]+)\s+(a|an)\s+([-\w]+)(\?\.)*", IGNORECASE)    

skip = ""
def get_terminating_chains(start, endlist, templist):
    if get_isa_list(start):
        global skip
        if start != skip:
            for intermediate_category in get_isa_list(start):
                templist.append(intermediate_category)
                get_terminating_chains(intermediate_category, endlist, templist)
                templist.pop()
    else:
        endlist.append(list(templist))

def indirect_redundancy(category1):
    # Get all terminating chains
    # Check each includes list for shared values with isa chain
    includes_chains = []
    category1_chain = []
    # Get list of includes
    c1list = get_includes_list(category1)
    # For each includes get terminating chains
    for i in c1list:
        global skip
        skip = category1
        get_terminating_chains(i, includes_chains, [i])
    skip = ""
    # For category 1, get terminating chains
    get_terminating_chains(category1, category1_chain, [])

    count = 0
    redundant_chains = []
    # Check each category 1 terminating chain, see if in includes terminating chains
    for i in range(len(category1_chain)):
        for j in category1_chain[i]:
            for k in includes_chains:
                # If it is save it
                if j in k:
                    count += 1
                    redundant_chains.append(list([k[0], j]))
    if count > 0:
        # If single indirect_redundancy
        if count == 1:
            # Complete
            print "Your earlier statement that " + ARTICLES[redundant_chains[0][0]] + " " +\
                  redundant_chains[0][0] + " is " + ARTICLES[redundant_chains[0][1]] + " " +\
                  redundant_chains[0][1] + " is now redundant."
            ISA[redundant_chains[0][0]].remove(redundant_chains[0][1])
            INCLUDES[redundant_chains[0][1]].remove(redundant_chains[0][0])
            print ISA
            print INCLUDES
        # If multi indirect_redundancy (can also detect chained redundnacy)
        else:
            print "The following statements you made earlier are now all redundant:"
            # Get redundant chains except for last one
            for i in redundant_chains[:-1]:
                for j in find_chain(i[0], i[1]):
                    print ARTICLES[j[0]] + " " + j[0] + " is " + ARTICLES[j[1]] + " " +\
                          j[1] + ";"
                    ISA[j[0]].remove(j[1])
                    INCLUDES[j[1]].remove(j[0])
            # Get last redundant chain.
            for i in find_chain(redundant_chains[-1][0], redundant_chains[-1][1])[:-1]:
                    print ARTICLES[i[0]] + " " + i[0] + " is " + ARTICLES[i[1]] + " " +\
                          i[1] + ";"
                    ISA[i[0]].remove(i[1])
                    INCLUDES[i[1]].remove(i[0])
            # Get last link in last redundant chain.
            last = find_chain(redundant_chains[-1][0], redundant_chains[-1][1])[-1]
            print ARTICLES[last[0]] + " " + last[0] + " is " + ARTICLES[last[1]] + " " +\
                  last[1] + "."
            ISA[last[0]].remove(last[1])
            INCLUDES[last[1]].remove(last[0])
            print ISA
            print INCLUDES
    else:
        print "I understand"

def process(info) :
    'Handles the user sentence, matching and responding.'
    result_match_object = assertion_pattern.match(info)
    if result_match_object != None :
        items = result_match_object.groups()
        store_article(items[1], items[0])
        store_article(items[3], items[2])

        # Direct Redundancy Detection
         # Existing Relation Check
        if isa_test1(items[1], items[3]):
            print("You told me that earlier.")
            return

        # Reflexivity Property: a = a
        if(items[3] == items[1]):
            print("You don't have to tell me that.")
            return

        # Transitivity: a = b & b = c : a = c
        inc_list = get_includes_list(items[3])
        isa_list = get_isa_list(items[1])
        for includes in inc_list:
            if includes in isa_list:
                print("You don't have to tell me that.")
                return
        
        # Statement can create non-redundant relation
        store_isa_fact(items[1], items[3])
        indirect_redundancy(items[1])
        return
    result_match_object = query_pattern.match(info)
    if result_match_object != None :
        items = result_match_object.groups()
        answer = isa_test(items[1], items[3])
        if answer :
            print("Yes, it is.")
        else :
            print("No, as far as I have been informed, it is not.")
        return
    result_match_object = what_pattern.match(info)
    if result_match_object != None :
        items = result_match_object.groups()
        supersets = get_isa_list(items[1])
        if supersets != [] :
            first = supersets[0]
            a1 = get_article(items[1]).capitalize()
            a2 = get_article(first)
            print(a1 + " " + items[1] + " is " + a2 + " " + first + ".")
            return
        else :
            subsets = get_includes_list(items[1])
            if subsets != [] :
                first = subsets[0]
                a1 = get_article(items[1]).capitalize()
                a2 = get_article(first)
                print(a1 + " " + items[1] + " is something more general than " + a2 + " " + first + ".")
                return
            else :
                print("I don't know.")
        return
    result_match_object = why_pattern.match(info)
    if result_match_object != None :
        items = result_match_object.groups()
        if not isa_test(items[1], items[3]) :
            print("But that's not true, as far as I know!")
        else:
            answer_why(items[1], items[3])
        return
    print("I do not understand.  You entered: ")
    print(info)

def answer_why(x, y):
    'Handles the answering of a Why question.'
    if x == y:
        print("Because they are identical.")
        return
    if isa_test1(x, y):
        print("Because you told me that.")
        return
    print("Because " + report_chain(x, y))
    return

from functools import reduce
def report_chain(x, y):
    'Returns a phrase that describes a chain of facts.'
    chain = find_chain(x, y)
    all_but_last = chain[0:-1]
    last_link = chain[-1]
    main_phrase = reduce(lambda x, y: x + y, map(report_link, all_but_last))
    last_phrase = "and " + report_link(last_link)
    new_last_phrase = last_phrase[0:-2] + '.'
    return main_phrase + new_last_phrase

def report_link(link):
    'Returns a phrase that describes one fact.'
    x = link[0]
    y = link[1]
    a1 = get_article(x)
    a2 = get_article(y)
    return a1 + " " + x + " is " + a2 + " " + y + ", "
    
def find_chain(x, z):
    'Returns a list of lists, which each sublist representing a link.'
    if isa_test1(x, z):
        return [[x, z]]
    else:
        for y in get_isa_list(x):
            if isa_test(y, z):
                temp = find_chain(y, z)
                temp.insert(0, [x,y])
                return temp

def test() :
    # process("A hawk is a bird.")
    # process("A hawk is a raptor.")
    # process("A raptor is a bird.")

    process("A hawk is an animal.")
    process("A hawk is a raptor.")
    process("A bird is an animal.")
    process("A raptor is a bird.")

    # process("A chinook is an organism.")
    # process("A sockeye is a salmon.")
    # process("A fish is an animal.")
    # process("A sockeye is an organism.")
    # process("A chinook is an animal.")
    # process("A chinook is a salmon.")
    # process("A sockeye is an animal.")
    # process("A fish is an organism.")
    # process("A salmon is a fish.")

test()
linneus()

