class Que:
    def __init__(self):
        self.qlist = []

    def isEmpty(self):
        return self.qlist == []

    def qput(self, data):
        self.qlist.insert(0,data)

    def qget(self):
        return self.qlist.pop()

    def size(self):
        return len(self.qlist)