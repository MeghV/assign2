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

# Each entry in the QUALIFIERS dictionary is of the form
# ( 'animal': { 'organism': ['Jones'], 'living-thing': [] } )
# corresponds to the statements:
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

# Stores aliases of the node cycles
#  ( 'being': ['creature'], 'organism': ['creature']) == "Both 'being' and 'organism' are aliases
#                                                     of 'creature'."
#  ( 'creature': ['being', 'organism'])
ALIASES = {}


def store_reliability_statement(target, reliableLabel, qualifier = None):
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
    'Stores one fact of the form A BIRD IS AN ANIMAL'
    # That is, a member of CATEGORY1 is a member of CATEGORY2
    try :
        c1list = ISA[category1]
        c1list.append(category2)
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
          # Add ISA statement and qualifier list if qualifier is present
        if qualifier is not None:
            QUALIFIERS[category1] = { category2: [ qualifier ]   }
        else: 
            QUALIFIERS[category1] = { category2: [ ] }
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

def isa_test_with_trail(category1, category2, depth_limit = 10):
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

# isa_test_w_trail(dog, organism):
    # isa_test_w_trail(animal, organism):
        # isa_test_w_trail(organism, organism)
        # => [organism]
    # => [animal, organism]
# => [dog, animal, organism]

def qualifier_test(category1, category2, depth_limit = 10):
    trail = isa_test_with_trail(category1, category2)
    if len(trail) > 0:
        resp = "Because "
        # used to list all qualifying sources within the chain,
        # to be used to judge reliability
        qualifying_sources = []
        i = 0
        while i < len(trail) - 1:
            isa_qualifiers = QUALIFIERS[trail[i]][trail[i + 1]]
            # check if someone has qualified the statement
            if len(isa_qualifiers) == 1:
                qualifier = isa_qualifiers[0]
                qualifying_sources.append(qualifier)
                resp += qualifier + " says that "
            elif len(isa_qualifiers) > 1:
                resp += isa_qualifiers[0]
                initial_qualifier = isa_qualifiers[0]
                qualifying_sources.append(initial_qualifier)
                for qualifier in isa_qualifiers[1:]:
                    qualifying_sources.append(qualifier)
                    resp += "and " + qualifier + " "
                resp += "say that "
            
            # comparison
            resp += ARTICLES[trail[i]] + " " + trail[i] + " is " +\
                    ARTICLES[trail[i+1]]+  " " + trail[i+1] 
            if i + 1 == len(trail) - 1:
                resp += ".\n"
            else:
                resp += ",\nand "
            i += 1
        
        # At this point, the ISA chain should be fully explored along
        # within the qualifiers who pointed out relationships, i.e.:
        # Because a dog is definitely an animal,
        # and Jones says that an animal is an organism.
        # Now we check for unreliable sources within the chain:
        for qualifier in set(qualifying_sources):
            if "unreliable" in RELIABILITY[qualifier]:
                # this person has been called "unreliable".
                # now we explore if this statement has been qualified.
                unreliablity_qualifiers = RELIABILITY[qualifier]["unreliable"]
                if len(unreliablity_qualifiers) == 1: 
                    # exactly one person has said this qualifier is unreliable
                    resp += "However, " + unreliablity_qualifiers[0] + " says that " +\
                            qualifier + " is an unreliable source,"
                elif len(unreliablity_qualifiers) > 1:
                    # multiple people have said that this qualifier is unreliable
                    resp += "However, " + unreliablity_qualifiers[0]
                    for unreliablity_somebody in unreliablity_qualifiers[1:]:
                        resp += " and " + unreliablity_somebody
                    resp += " say that " + qualifier + " is an unreliable source,"
                else:
                    # an unqualified statement has been made about this qualifier's
                    # reliability (the USER wrote "[somebody] is unreliable...")
                    resp += "However, " + qualifier + " is an unreliable source,"

                resp += "\nand therefore we cannot be certain about this chain of reasoning."
        return resp
    else:
        return "It is not possible."

def qualify_test1(category1, category2, qualifier = None):
    'Returns True if the qualifier exists for category 1 to category 2.'
    qualifierList = QUALIFIERS[category1]
    if qualifier is not None:
        return category2 in qualifierList and qualifierList[category2].__contains__(qualifier)
    else:
        return category2 in qualifierList

def qualify_test(category1, category2):
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

# Checks ISA for cycles.
def cycle_check(start, end, cyclelist, templist):
    if get_isa_list(start):
        for intermediate_category in get_isa_list(start):
            if intermediate_category == end:
                cyclelist.append(list(templist))
            else:
                templist.append(intermediate_category)
                cycle_check(intermediate_category, end, cyclelist, templist)
                templist.pop()

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
qualified_pattern = compile(r"^([-\w]+)\s+says\s+that\s+", IGNORECASE)
# Reliability statement: "[somebody] is a/an reliable/unreliable source. "
reliability_pattern = compile(r"^([-\w]+)\s+is\s+(a|an)\s+(reliable|unreliable)\s+(source)(\.|\!)*$", IGNORECASE)
# Why style 1: Why is it possible that [category1] is [category2]?
plausible_why_pattern = compile(r"^Why\s+is\s+it\s+possible\s+that\s+(a|an)\s+([-\w]+)\s+is+\s+(a|an)\s+([-\w]+)(\?\.)*$", IGNORECASE)
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
        if isa_test1(items[1], items[3]) and qualify_test1(items[1], items[3], name):
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
        # Check for cycles
        cyclelist = []
        cycle_check(items[3], items[3], cyclelist, [items[3]])
        # If cycle list contains something.
        if cyclelist:
            # Builds response statement.
            resp = "I infer that "
            for i in cyclelist:
                for j in i[:-1]:
                    resp += j + ", "
                resp += "and " + i[-1] + " are all names for the same thing, and I'll call it " + i[0] + "."
            print resp
            # For each list in cyclelist
            for i in cyclelist:
                # For each element in each list in cyclelist
                # Add all elements to a single value list and remove the old key/value pair
                ALIASES[i[0]] = []
                print i
                for j in i[1:]:
                    ISA[i[0]] += ISA[j]
                    ALIASES[i[0]] += [j]
                    ISA.pop(j)
                    print INCLUDES
                    print ISA
                    # For each key/value pair in ISA
                    # Replace all occurances of the current value with the merged node value
                    for k in ISA:
                        if j in ISA[k] and not k == i[0]:
                            ISA[k].remove(j)
                            ISA[k].append(i[0])
                    # Add all includes to the represntative value.
                    for k in INCLUDES:
                        for l in INCLUDES[k]:
                            if not l == i[0]:
                                INCLUDES[i[0]] += [l]
                    INCLUDES.pop(j,)
                ISA[i[0]].remove(i[0])
        else:
            print("I understand.")
            return

    # Is a [cat1] a [cat2]?
    result_match_object = query_pattern.match(info)
    if result_match_object != None :
        items = result_match_object.groups()
        answer = isa_test(items[1], items[3])
        last_statement = items
        if answer :
            # Now we check if it is qualified:
            qualified = qualify_test(items[1], items[3])
            resp = ""
            if len(qualified) == 1:
                print(qualified[0] + " says that it is.")
            elif len(qualified) > 1:
                resp += qualified[0]
                for name in qualified[1:]:
                    resp += " and " + name
                resp += " say that it is."
                print(resp)
            else:
                print("Yes, it is.")
        else :
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

        # TODO: check if name already matched
        store_reliability_statement(items[0], items[2], name)

        print("Reliability statement! I understand.")
        return

    # Checking for plausible argument
    # "Why is it possible that [category1] is [category2?"
    result_match_object = plausible_why_pattern.match(info)
    if result_match_object != None:
        items = result_match_object.groups()
        print(qualifier_test(items[1], items[3]))
        return
    # Checking for other plausible argument
    # "Why?"
    # Requires that a previous statement has been made
    result_match_object = short_why_pattern.match(info)
    if result_match_object != None:
        if last_statement is not None:
            print(qualifier_test(last_statement[1], last_statement[3]))
            return
        last_statement = None

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

    if x in ALIASES and y in ALIASES[x]:
        return y + " is another name for " + x + ", "
    else:
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
    process("A creature is a being.")
    process("A being is an organism.")
    process("An organism is a creature.")
    # print "> A bug is a creature."
    # process("A bug is a creature.")
    # print "> Is a bug a being?"
    # process("Is a bug a being?")
    # print "> Why is a bug a being?"
    # process("Why is a bug a being?")
    # print "> A living-thing is an organism."
    # process("A living-thing is an organism.")
    # print "> Is a bug an organism?"
    # process("Is a bug an organism?")
    # print "> Why is a bug an organism."
    # process("Why is a bug an organism.")
test()
linneus()

