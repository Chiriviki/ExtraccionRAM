from __future__ import unicode_literals, division, print_function

# build-in modules
import re
import os


# installed modules
import numpy
from simstring.feature_extractor.character_ngram import CharacterNgramFeatureExtractor

from simstring.database.dict import DictDatabase
from simstring.searcher import Searcher


def make_ngrams(s, n):
    # s = u'{t}{s}{t}'.format(s=safe_unicode(s), t=('$' * (n - 1)))
    n = len(s) if len(s) < n else n
    return (s[i:i + n] for i in range(len(s) - n + 1))


def get_similarity(x, y, n, similarity_name):
    if len(x) == 0 or len(y) == 0:
        # we define similarity between two strings
        # to be 0 if any of the two is empty.
        return 0.

    X, Y = set(make_ngrams(x, n)), set(make_ngrams(y, n))
    intersec = len(X.intersection(Y))

    if similarity_name == 'dice':
        return 2 * intersec / (len(X) + len(Y))
    elif similarity_name == 'jaccard':
        return intersec / (len(X) + len(Y) - intersec)
    elif similarity_name == 'cosine':
        return intersec / numpy.sqrt(len(X) * len(Y))
    elif similarity_name == 'overlap':
        return intersec
    else:
        msg = 'Similarity {} not recognized'.format(similarity_name)
        raise TypeError(msg)




class Simstring:

    def __init__(self, terms_path, similarity_name, threshold):
        if not(os.path.exists(terms_path)):
            err_msg = f'"{terms_path}" does not exists or it is not a directory.'
            raise IOError(err_msg)

        db = DictDatabase(CharacterNgramFeatureExtractor(2))

        exceptions = {'im'}

        with open(terms_path, 'r', encoding='utf8') as f:
                terms = set([line.split('|')[0] for line in f if line.split('|')[0] != ''])
                for term in terms:
                    if term not in exceptions:
                        db.add(term)

        if similarity_name=='dice':
            from simstring.measure.dice import DiceMeasure
            self.searcher = Searcher(db, DiceMeasure())
        elif similarity_name=='jaccard':
            from simstring.measure.jaccard import JaccardMeasure
            self.searcher = Searcher(db, JaccardMeasure())
        elif similarity_name=='cosine':
            from simstring.measure.cosine import CosineMeasure
            self.searcher = Searcher(db, CosineMeasure())
        else:
            raise Exception(f'{similarity_name} no es una similitud válida.')

        self.threshold = threshold

    def get(self, term):
        return self.searcher.search(term, self.threshold)


class TermsDB:

    def __init__(self, terms_path):

        if not(os.path.exists(terms_path)):
            err_msg = f'"{terms_path}" does not exists or it is not a directory.'
            raise IOError(err_msg)

        self.db = {}

        with open(terms_path, 'r', encoding='utf8') as f:
            for line in f:
                term = line.split('|')[0].strip()
                cui = line.split('|')[1].strip()
                semt = [line.split('|')[2].strip()]
                pref = 1 if line.split('|')[3].strip() == "TERM" else 0

                if term in self.db:
                    self.db[term].append((cui, semt, pref))
                else:
                    self.db[term] = [(cui, semt, pref)]

    def get(self, term):
        return self.db[term]

class Intervals(object):
    def __init__(self):
        self.intervals = []

    def _is_overlapping_intervals(self, a, b):
        if b[0] < a[1] and b[1] > a[0]:
            return True
        elif a[0] < b[1] and a[1] > b[0]:
            return True
        else:
            return False

    def __contains__(self, interval):
        return any(
            self._is_overlapping_intervals(interval, other)
            for other in self.intervals
        )

    def append(self, interval):
        self.intervals.append(interval)

