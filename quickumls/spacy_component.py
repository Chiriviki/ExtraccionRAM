import spacy
from spacy.tokens import Span, Doc
from spacy.language import Language

from .core import QuickUMLS
from . import constants

@Language.factory("quickumls_matcher")
class SpacyQuickUMLS(object):

    def __init__(self, nlp, name, terms_fp, best_match=True, ignore_syntax=False, overlapping_criteria='score', threshold=0.7, window=5,
            similarity_name='jaccard', min_match_length=2):
        """Instantiate SpacyQuickUMLS object

            This creates a quickumls spaCy component which can be used in modular pipelines.
            This module adds entity Spans to the document where the entity label is the UMLS CUI and the Span's "underscore" object is extended to contains "similarity" and "semtypes" for matched concepts.

        Args:
            nlp: Existing spaCy pipeline.  This is needed to update the vocabulary with UMLS CUI values
            terms_fp (str): Path to terms data
            best_match (bool, optional): Whether to return only the top match or all overlapping candidates. Defaults to True.
            ignore_syntax (bool, optional): Wether to use the heuristcs introduced in the paper (Soldaini and Goharian, 2016). TODO: clarify,. Defaults to False
            **kwargs: quickumls keyword arguments (see quickumls in core.py)
        """
        
        self.quickumls = QuickUMLS(terms_fp,
                                   # By default, the quickumls objects creates its own internal spacy pipeline but this is not needed
                                   # when we're using it as a component in a pipeline
                                   spacy_component = True,
                                   overlapping_criteria=overlapping_criteria,
                                   threshold=threshold,
                                   window=window,
                                   similarity_name=similarity_name,
                                   min_match_length=min_match_length)
        
        # save this off so that we can get vocab values of labels later
        self.nlp = nlp
        
        # keep these for matching
        self.best_match = best_match
        self.ignore_syntax = ignore_syntax

        # Excepciones
        self.exceptions = constants.EXCEPTIONS

        # let's extend this with some proprties that we want

        if not Span.has_extension("similarity"):
            Span.set_extension('similarity', default = -1.0)

        if not Span.has_extension("term"):
            Span.set_extension('term', default = -1.0)

        if not Span.has_extension("ent_id"):
            Span.set_extension('ent_id', default = 0)

        if not Doc.has_extension("has_pair"):
            Doc.set_extension("has_pair", default=False)

        # Añade semtypes a Vocab
        for semtype in constants.ACCEPTED_SEMTYPES:
            self.nlp.vocab.strings.add(semtype)

        
    def __call__(self, doc):

        # variables para comprobar si tiene un par de entidades.
        has_drug = False
        has_effect = False

        # pass in the document which has been parsed to this point in the pipeline for ngrams and matches
        matches = self.quickumls._match(doc, best_match=self.best_match, ignore_syntax=self.ignore_syntax)

        ent_id=1
        # Convert quickumls match objects into Spans
        for match in matches:

            # Elimina aquellas coincidencias de las excepciones
            match = self._remove_exceptions(doc, match)
            if len(match)==0: continue

            ngram_match_dict = match[0] # Puede retornar varios semtypes. Añade el primero = mejor putuacion
                    # each match may match multiple ngrams
                    #for ngram_match_dict in match:

            start_char_idx = int(ngram_match_dict['start'])
            end_char_idx = int(ngram_match_dict['end'])

            semtype = ngram_match_dict['semtypes'][0]
            label_id = self.nlp.vocab.strings[semtype]


            # char_span() creates a Span from these character indices
            # UMLS CUI should work well as the label here
            span = doc.char_span(start_char_idx, end_char_idx, label = label_id)
            # add some custom metadata to the spans
            span._.similarity = ngram_match_dict['similarity']
            span._.term = ngram_match_dict['term']
            span._.ent_id = ent_id
            ent_id +=1

            if semtype == "DRUG":
                has_drug = True
            else:
                has_effect = True

            doc.ents = list(doc.ents) + [span]

        doc._.has_pair= has_drug and has_effect

        return doc

    def _remove_exceptions(self, doc, match):
        new_match = []

        for m in match:

            word = m["ngram"]

            if m["term"] in self.exceptions:
                if word == self.exceptions[m["term"]]:
                    continue

            new_match.append(m)

        return new_match


