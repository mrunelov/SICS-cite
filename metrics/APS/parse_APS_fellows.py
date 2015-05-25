
def find_between(s, first, last):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

with open("APS-Fellow-Archive.html","r") as f,\
        open("APS-fellows.txt", "w+") as out:
    for line in f:
        if "<strong>" in line:
            name = find_between(line,"<strong>","</strong>")
            out.write(name + "\n")

