import json
import os


from spacy import Language
from spacy.tokens import Doc, Span



@Language.factory("re_adrdb")
class RelationExtraction_ADRDB():

    def __init__(self, nlp, name, relations_fp):

        if not os.path.exists(relations_fp):
            raise Exception("No se encontraron los archivos de BBDD ADR en " + relations_fp)

        with open(relations_fp, 'r', encoding='utf8') as f:
            self.relations = json.load(f)

        if not Doc.has_extension("relations"):
            Doc.set_extension("relations", default=[])

        if not Doc.has_extension("has_adr"):
            Doc.set_extension("has_adr", default=False)

    def __call__(self, doc):

        # Extrae relaciones
        rels = self.extract_relations(doc)

        doc._.relations=rels

        return doc

    def extract_relations(self, doc):
        rels = []

        drug_ents = [ent for ent in doc.ents if ent.label_ == "DRUG"]
        eff_ents = [ent for ent in doc.ents if ent.label_ == "EFFECT"]

        # Extrae las relaciones
        for drug in drug_ents:
            for effect in eff_ents:

                primero, segundo = (drug, effect) if drug.start < effect.start else (effect, drug)

                # Comprueba que la distanca entre entidades no supera distancia máxima
                distancia = segundo.start - primero.end

                # Extrae las relaciones entre las dos etidades
                rel = self._are_related(drug._.term, effect._.term)
                if rel=="adverse effect":
                    doc._.has_adr = True

                # Coloca primero la que aparece primero
                ent1 = drug if drug.start < effect.start else effect
                ent2 = effect if ent1 == drug else drug

                # Crea y añade la relacion
                rels.append({"ent1": ent1, "ent2": ent2, "type": rel, "dist":distancia})

        return rels

    def _are_related(self, drug_term, eff_term):
        """
        :param drug_term:
        :param eff_term:
        :return:
        """
        if drug_term in self.relations:
            if eff_term in self.relations[drug_term]:
                return self.relations[drug_term][eff_term]
        return "unrelated"


