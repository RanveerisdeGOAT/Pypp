class List:
    def __init__(self, *args):
        self.list = list(args)

    def append(self, obj):
        self.list.append(obj)

    def pop(self, index=-1):
        return self.list.pop(index)

    def index(self, value):
        return self.list.index(value)

    def get(self, index):
        return self.list[int(index)]

    def __add__(self, other):
        if isinstance(other, List):
            return List(*self.list + other.list)
        elif isinstance(other, list):
            return List(*self.list + other)
        raise TypeError("Can only add List or list to List")

    def __sub__(self, other):
        new_list = self.list.copy()
        if isinstance(other, List):
            other = other.list
        for i in other:
            if i in new_list:
                new_list.remove(i)
        return List(*new_list)

    def __mul__(self, other):
        if isinstance(other, int):
            return List(*(self.list * other))
        raise TypeError("Can only multiply List by an integer")

    def __repr__(self):
        return f"List({', '.join(repr(i) for i in self.list)})"

    def __len__(self):
        return len(self.list)

__include__ = {"stdout": print, "stdin": lambda prompt='': input(prompt), "str": str, "int": int, "float": float, "len": len, 'list': List}