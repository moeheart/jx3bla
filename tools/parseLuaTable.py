file = open("2020-06-04-22-08-41_白某_416.fstt.jx3dat")
s = file.read()

g = open("parsed", "w", encoding="utf-8")

padding = 0
for c in s:
    if c == '{':
        g.write(c)
        padding += 2
        g.write('\n')
        g.write(' '*padding)
    elif c == '}':
        g.write('\n')
        g.write(' '*padding)
        padding -= 2
        g.write(c)
        g.write('\n')
        g.write(' '*padding)
    else:
        g.write(c)
        
g.close()