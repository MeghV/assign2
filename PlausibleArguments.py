# PlausibleArguments.py
# Implements storage and inference on an ISA hierarchy. 
# Additionally, both qualified and unqualified statements
# about ISA heirarchies are stored and displayed to the
# user.
# This version runs under Python 3.x.

# Ryan Chui & Megh Vakharia

from re import *   # Loads the regular expression module.

# The ISA relation is represented using a dictionary, ISA.
# There is a corresponding inverse dictionary, INCLUDES.
# Each entry in the ISA dictionary is of the form
#  ('turtle' : ['reptile', 'shelled-creature'])
ISA = {}
INCLUDES = {}
ARTICLES = {}

# Each entry in the QUALIFIERS dictionary is of the form:
# ( 'animal': { 'organism': ['Jones'], 'living-thing': [] } )
# The above corresponds to the statements:
# "Jones says than an animal is an organism"
# "An animal is a living-thing."
QUALIFIERS = {}

# Stores reliability information - a boolean for relability
# as well as the source of this information (whether the info
# is qualified or not.) The structure will look like so:
#  ( 'Smith': { reliable: ['Jones'] } ) == "Jones says that Smith is a reliable source."
#  ( 'Jones': { unreliable: []  ) == "Jones is an unreliable source."
#  ( 'Jones': { unreliable: [], reliable: ["Megh"] ) == "Megh says Jones is a reliable source."
RELIABILITY = {}

def store_reliability_statement(target, reliableLabel, qualifier = None):
    """
    Stores the statement of reliability to the target. If the qualifier's name
    is passed in, it is stored with the reliability statement.
    """
    try:
        targetList = RELIABILITY[target]
        if reliableLabel in targetList:
            if qualifier is not None:
                targetList[reliableLabel].append(qualifier)
        else:
            if qualifier is not None:
                targetList[reliableLabel] = [qualifier]
            else:
                targetList[reliableLabel] = []
    except KeyError:
        if qualifier is not None:
            RELIABILITY[target] = { reliableLabel : [ qualifier ] }
        else: 
            RELIABILITY[target] = { reliableLabel : [ ] }

def store_isa_fact(category1, category2, qualifier = None):
    """
    Stores one fact of the form A BIRD IS AN ANIMAL. If the statement
    has been qualified, the qualifier's name is stored as well.
    """
    try :
        c1list = ISA[category1]
        if category2 not in c1list: c1list.append(category2)
    except KeyError :
        ISA[category1] = [category2]
    try:
        c1qualifiers = QUALIFIERS[category1]
        if category2 in c1qualifiers: 
            if qualifier is not None:
                c1qualifiers[category2].append(qualifier) 
        else:
            if qualifier is not None:
                c1qualifiers[category2] = [qualifier]
            else:
                c1qualifiers[category2] = []
    except KeyError:
        if qualifier is not None:
            QUALIFIERS[category1] = { category2: [ qualifier ]   }
        else: 
            QUALIFIERS[category1] = { category2: [ ] }
    try :
        c2list = INCLUDES[category2]
        if category1 not in c2list: c2list.append(category1)
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

def isa_test_with_trail(category1, category2, depth_limit = 10):
    'Returns the chain of facts that connects category1 to category2.'
    trail = []
    if category1 == category2 : 
        trail += [category1]
        return trail
    if isa_test1(category1, category2) : 
        trail += [category1, category2]
        return trail
    if depth_limit < 2 : return []
    for intermediate_category in get_isa_list(category1):
        trailhead = isa_test_with_trail(intermediate_category, category2, depth_limit - 1)
        if len(trailhead) > 0:
            trail += [category1]
            trail += trailhead
            return trail
    return []


def find_qualifiers(category1, category2):
    'Returns list of qualifiers who have stated category1 is a category2.'
    if category1 in QUALIFIERS and category2 in QUALIFIERS[category1]:
        return QUALIFIERS[category1][category2]
    return []

def report_chain_with_qualifiers(category1, category2):
    """
    Reports the connections between category1 and category2 with related qualifier
    information, such as qualifiers and their reliability.
    """
    # Gets chain between category1 and category2
    trail = isa_test_with_trail(category1, category2)
    if len(trail) > 0: # A chain exists!
        resp = "Because " # Begin the response string
        qualifying_sources = [] # Stores all of the qualifiers related to the statement
        i = 0
        while i < len(trail) - 1:
            isa_qualifiers = QUALIFIERS[trail[i]][trail[i + 1]]
            # Check if someone has qualified the statement and if so,
            # list their names.
            if len(isa_qualifiers) >= 1:
                qualifier = isa_qualifiers[0]
                qualifying_sources.append(qualifier)
                resp += isa_qualifiers[0] + " "
                for qualifier in isa_qualifiers[1:]:
                    qualifying_sources.append(qualifier)
                    resp += "and " + qualifier + " "
                if len(isa_qualifiers) == 1:
                    resp += "says that "
                else:
                    resp += "say that"
            
            # List the categories that are being matched.
            resp += ARTICLES[trail[i]] + " " + trail[i] + " is " +\
                    ARTICLES[trail[i+1]]+  " " + trail[i+1] 
            if i + 1 == len(trail) - 1:
                resp += "."
            else:
                resp += ",\nand "
            i += 1
        
        # At this point, the ISA chain should be fully explored.
        # Now we check for unreliable sources within the chain:
        for qualifier in set(qualifying_sources):
            if qualifier in RELIABILITY:
                if "unreliable" in RELIABILITY[qualifier]:
                    resp += "\n"
                    # This person has been called "unreliable".
                    # Now we explore if this statement has been qualified.
                    unreliablity_qualifiers = RELIABILITY[qualifier]["unreliable"]
                    resp += "However, "
                    if len(unreliablity_qualifiers) >= 1:
                        resp += unreliablity_qualifiers[0] + " "
                        for unreliablity_somebody in unreliablity_qualifiers[1:]:
                            resp += "and " + unreliablity_somebody + " "
                        if len(unreliablity_qualifiers) == 1:
                            resp += "says that "
                        else:
                            resp += "say that "
                    resp += qualifier + " is an unreliable source,"
                    resp += "\nand therefore we cannot be certain about this chain of reasoning."
        return resp
    else: # Chain does not exist
        return "It is not possible."

def qualifier_for_chain(category1, category2, qualifier = None):
    'Returns True if the qualifier exists for category 1 to category 2.'
    qualifierList = QUALIFIERS[category1]
    if qualifier is not None:
        return category2 in qualifierList and qualifierList[category2].__contains__(qualifier)
    else:
        return category2 in qualifierList

def qualify_test(category1, category2):
    'Returns the list of qualifiers that have stated category1 is a category2.'
    if category1 in QUALIFIERS and category2 in QUALIFIERS[category1]:
        qualifier_list = QUALIFIERS[category1][category2]
        return qualifier_list
    return []

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

# Part III. Qualified Statements & Plausible Arguments Regex
# Qualified statement: "[somebody] says that [assertion_pattern]"
qualified_pattern = compile(r"^([-\w]+)\s+says\s+that?\s+?", IGNORECASE)
# Reliability statement: "[somebody] is a/an reliable/unreliable source. "
reliability_pattern = compile(r"^([-\w]+)\s+is\s+(a|an)\s+(reliable|unreliable)\s+(source)(\.|\!)*$", IGNORECASE)
# Reliability question: "Why is [somebody] a/an reliable/unreliable source?"
reliability_why_pattern = compile(r"^(Why)?[\s+]?is\s+([-\w]+)\s+(a|an)\s+(reliable|unreliable)\s+(source)(\?)*$", IGNORECASE)
# Why style 1a: Why is it possible that [category1] is [category2]?
plausible_why_pattern = compile(r"^Why\s+is\s+it\s+possible\s+that\s+(a|an)\s+([-\w]+)\s+is+\s+(a|an)\s+([-\w]+)(\?|\.)*$", IGNORECASE)
# Why style 2: Why?
short_why_pattern = compile(r"^Why(\?)*$", IGNORECASE)

last_statement = None

def process(info) :
    'Handles the user sentence, matching and responding.'
    global last_statement
    name = None
    # Check if statement is qualified
    qualifier_match_object = qualified_pattern.match(info)
    if qualifier_match_object != None:
        items = qualified_pattern.split(info)
        name = items[1]
        statement = items[2]
        info = statement
    result_match_object = assertion_pattern.match(info)
    if result_match_object != None :
        items = result_match_object.groups()
        store_article(items[1], items[0])
        store_article(items[3], items[2])
        last_statement = items

        # Direct Redundancy Detection
        # Existing Relation Check
        if isa_test1(items[1], items[3]) and qualifier_for_chain(items[1], items[3], name):
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
        store_isa_fact(items[1], items[3], name)
        print("I understand.")
        return
    # Is a [category1] a [category2]?
    result_match_object = query_pattern.match(info)
    if result_match_object != None :
        items = result_match_object.groups()
        last_statement = items
        # check if they're a direct match
        if isa_test1(items[1], items[3]):
            # now we check if someone has qualified the 
            # directly linked statement
            isa_qualifiers = find_qualifiers(items[1], items[3])
            if len(isa_qualifiers) >= 1:
                resp = ""
                qualifier = isa_qualifiers[0]
                resp += qualifier + " "
                for qualifier in isa_qualifiers[1:]:
                    resp += "and " + qualifier + " "
                if len(isa_qualifiers) > 1:
                    resp += "say that it is."
                else:
                    resp += "says that it is."
                print(resp)
            else:
                print("Yes, it is.")
        # categories are not directly linked, so we check for
        # an indirect link through ISA chains
        elif isa_test(items[1], items[3]):
            print("It's quite possible that " + ARTICLES[items[1]] + " " +\
                    items[1] + " is " + ARTICLES[items[3]] + " " + items[3] + ".")
        else:
            print("I have no reason to believe so.")
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
            last_statement = items
        return
    
    # Checking for reliability statements:
    # "[somebody] is a/an reliable/unreliable source."
    result_match_object = reliability_pattern.match(info)
    if result_match_object != None:
        items = result_match_object.groups()
        store_reliability_statement(items[0], items[2], name)

        print("I understand.")
        return

    # Checking for reliabiltiy question:
    # "Why is [somebody] a/an reliable/unreliable source?"
    # "Is [somebody] a/an reliable/unreliable source?"
    result_match_object = reliability_why_pattern.match(info)
    if result_match_object != None:
        items = result_match_object.groups()
        why_q = (items[0] != None and items[0].lower() == 'why')
        name = items[1]
        reliability_term = items[3]
        article = items[2]
        if reliability_term == "reliable":
            opposite_reliability = "unreliable"
        elif reliability_term == "unreliable":
            opposite_reliability = "unreliable"
        if name in RELIABILITY:
            resp = ""
            reliability_information = RELIABILITY[name]
            if reliability_term in reliability_information:
                if not why_q:
                    resp += "Yes, "
                else:
                    resp += "Because "
                reliability_qualifiers = reliability_information[reliability_term]
                if len(reliability_qualifiers) >= 1:
                    resp += reliability_qualifiers[0] + " "
                    for person in reliability_qualifiers[1:]:
                        resp += "and " + person + " "
                else:
                    resp += "you "
                resp += "told me that."
                print(resp)
                return
            resp += "I don't know if " + name + " is " + article + " " + reliability_term + " source"

            if opposite_reliability in reliability_information:
                opposite_reliability_qualifiers = reliability_information[opposite_reliability]
                resp += ",\nbut "
                if len(opposite_reliability_qualifiers) >= 1:
                    resp += opposite_reliability_qualifiers[0] + " "
                    for person in opposite_reliability_qualifiers[1:]:
                        resp += "and " + person + " "
                else:
                    resp += "you "
                resp += "told me that " + name + " is " + article + " " + opposite_reliability + " source"
            resp += "."
            print(resp)
            return
        print("I have no information about the reliability of " + name + ".")
        return

    # Checking for plausible argument:
    # "Why is it possible that [category1] is [category2?"
    result_match_object = plausible_why_pattern.match(info)
    if result_match_object != None:
        items = result_match_object.groups()
        print(report_chain_with_qualifiers(items[1], items[3]))
        return
    # Checking for other plausible argument:
    # "Why?"
    # Requires that a previous statement has been made
    result_match_object = short_why_pattern.match(info)
    if result_match_object != None:
        if last_statement is not None:
            print(report_chain_with_qualifiers(last_statement[1], last_statement[3]))
            return
        last_statement = None
    print("I do not understand.  You entered: ")
    print(info)

def answer_why(x, y):
    'Handles the answering of a Why question.'
    if x == y:
        print("Because they are identical.")
        return
    if isa_test1(x, y):
        # Check who qualified the statement
        isa_qualifiers = find_qualifiers(x,y)
        resp = "Because "
        if len(isa_qualifiers) >= 1:
            resp += isa_qualifiers[0] + " "
            for qualifier in isa_qualifiers[1:]:
                resp += "and " + qualifier + " "
        else:
            resp += "you "
        resp += "told me that."
        print(resp)
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

def report_link(link, reportEnd = ", "):
    'Returns a phrase that describes one fact.'
    x = link[0]
    y = link[1]
    a1 = get_article(x)
    a2 = get_article(y)
    return a1 + " " + x + " is " + a2 + " " + y + reportEnd

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
    return
    # process("Jones says that an animal is an organism.")
    # process("Jones says that Smith is a reliable source.")
    # process("A dog is an animal.")
    # process("Jones is an unreliable source.")
test()
linneus()

