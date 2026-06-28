with open("categories.txt","r", encoding="utf-8") as f:
    list = [line.rstrip('\n') for line in f.readlines()]