from websharecli.terminal import T


class File:
    def __init__(self, ident=None, name=None, type=None, size=None,
                 negative_votes=None, positive_votes=None, **kwargs):
        self.ident = ident
        self.name = name
        self.type = type
        self._size = None
        self.size = size
        self._negative_votes = None
        self.negative_votes = negative_votes
        self._positive_votes = None
        self.positive_votes = positive_votes

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        try:
            self._size = int(value)
        except TypeError:
            self._size = None

    @property
    def negative_votes(self):
        if self._negative_votes is None:
            return 0
        return self._negative_votes

    @negative_votes.setter
    def negative_votes(self, value):
        try:
            self._negative_votes = int(value)
        except TypeError:
            self._negative_votes = 0

    @property
    def positive_votes(self):
        if self._positive_votes is None:
            return 0
        return self._positive_votes

    @positive_votes.setter
    def positive_votes(self, value):
        try:
            self._positive_votes = int(value)
        except TypeError:
            self._positive_votes = 0

    @property
    def rating(self):
        return self.positive_votes - self.negative_votes

    def __str__(self):
        style = T.yellow
        if self.rating > 0:
            style = T.green
        elif self.rating < 0:
            style = T.red
        return f"{self.size:4d} {self.type:3s} {style}{self.rating:+1d}{T.normal} {T.cyan}{self.ident}{T.normal} {self.name}"

    def matches_query(self, query):
        words = [word.lower() for word in query.split(' ')]
        return all([word in self.name.lower() for word in words])

    def __hash__(self):
        return sum([ord(c) ** n for n, c in enumerate(self.ident)])

    def __eq__(self, other):
        return self.ident == other.ident


def filter_unique(files):
    uniques = []
    for file_ in files:
        if file_ not in uniques:
            uniques.append(file_)
    return uniques


def filter_extensions(files, extensions=None):
    if extensions is None:
        return files
    return [file_ for file_ in files if file_.type in extensions]


def filter_(files, phrase):
    return [file_ for file_ in files if phrase.lower() not in file_.name.lower()]


def filter_exclude(files, exclude=None):
    if exclude is None or not len(exclude):
        return files
    if isinstance(exclude, list):
        for phrase in exclude:
            files = filter_(files, phrase)
    elif isinstance(exclude, str):
        files = filter_(files, exclude)
    else:
        raise NotImplementedError("exclude must be a list or string")
    return files
