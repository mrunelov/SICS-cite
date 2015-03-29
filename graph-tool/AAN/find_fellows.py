import difflib

def parse_names(fullname, has_firstname=True, reverse=False):
    names = fullname.split(" ")
    names[-1] = names[-1].strip() # remove newline
    if reverse: # first name is last, put it first
        r_i = len(names) - 1
        while len(names[r_i]) <= 2: # move past e.g. "C." and such
            r_i -= 1
        names = names[r_i:] + names[:r_i]
        print "After: " + str(names)
    for name in names:
        name = name.replace(",","")
    if has_firstname:
        firstname = names[0]
        lastname = " ".join(names[1:])
    else:
        firstname = ""
        lastname = " ".join(names)
    return [firstname,lastname]

def names_to_str(names):
    return " ".join(names)

def parse_fellows():
    fellows = []
    with open("fellows.txt","r") as f:
        for line in f:
            name = parse_names(line)
            fellows.append(name)
    return fellows


fellows = parse_fellows()
def is_fellow(candidate, has_firstname=True, reverse=False):
    name = parse_names(candidate,has_firstname=has_firstname, reverse=reverse)
    print "Checking fellow: " + str(name)
    for fellow in fellows:
        s = sim(fellow[1],name[-1])
        if s > 0.75:
            print "Found probable match:"
            print names_to_str(fellow) + " MATCHES " + names_to_str(name) 

def sim(a, b):
    #print "COMPARING " + a + " AND " + b
    seq = difflib.SequenceMatcher(a=a.lower(), b=b.lower())
    return seq.ratio()


#candidates = ["Kaplan", "Mercer", "Moore", "Tou Ng", "Palmer"]
#for c in candidates:
    #is_fellow(c,has_firstname=False)
