import os

from spacy import Language
from spacy.tokens import Doc, Span

import pickle

@Language.factory("re_adrrf")
class RelationExtraction_ADRRF:

    def __init__(self,nlp, name, encoder_path, model_path, inner_window=14, outer_window=4):

        self.ventana_interior = inner_window
        self.ventana_exterior = outer_window

        # Encoder
        if not os.path.exists(encoder_path):
            raise Exception("No se encontraron los archivos de codificador de contexto en " + encoder_path)

        with open(encoder_path, "rb") as f:
            self.context_encoder = pickle.load(f)

        # Modelo
        if not os.path.exists(model_path):
            raise Exception("No se encontraron los archivos de modelo de clasificación en " + model_path)

        with open(model_path, "rb") as f:
            self.clasif = pickle.load(f)

        # Atributos
        if not Doc.has_extension("relations"):
            Doc.set_extension("relations", default=[])

        if not Doc.has_extension("has_adr"):
            Doc.set_extension("has_adr", default=False)

    def __call__(self, doc):

        entities = { ent._.ent_id:ent for ent in doc.ents}

        # Extrae candidatos
        candidatos = self._extract_candidatos(doc, self.ventana_interior, self.ventana_exterior)

        if candidatos:

            # Guarda los pares de entidades a los que se refiere cada candidato
            pares = [(entities[candidato["ent1"]["id"]],
                       entities[candidato["ent2"]["id"]])
                      for candidato in candidatos]

            # Codifica
            matrix = self.context_encoder.transform(candidatos)

            # Predice
            predictions = self.clasif.predict(matrix)

            # Etiqueta
            relaciones = [ {"ent1":par[0], "ent2":par[1], "type":"ADR"} for par, pred in zip(pares, predictions) if pred==1]
            doc._.relations = relaciones

        return doc


    def _extract_candidatos(self, doc, ventana_interior=14, ventana_exterior=4):
        """
        Extrae las características paa cada par de entidades que cumplen
        con el requisito de estar a cierta distancia. Es posible que no fuera necesario.
        :param doc:
        :param ventana_interior:
        :param ventana_exterior:
        :return:
        """
        def _format_ent(entity, start):
            ent_dict = {}
            ent_dict["id"] = entity._.ent_id
            ent_dict["type"] = entity.label_
            ent_dict["term"] = entity._.term
            ent_dict["start"] = entity.start - start
            ent_dict["end"] = entity.end - start

            return ent_dict

        candidatos = []

        # Obtiene todos las entidades Drug y effect del doc
        drug_ents = [ent for ent in doc.ents if ent.label_ == "DRUG"]
        eff_ents = [ent for ent in doc.ents if ent.label_ == "EFFECT"]

        # Extrae las relaciones candidatas
        for drug in drug_ents:
            for effect in eff_ents:

                primero, segundo = (drug, effect) if drug.start < effect.start else (effect, drug)

                # Comprueba que la distanca entre entidades no supera distancia máxima
                distancia = segundo.start - primero.end
                is_valid = distancia <= ventana_interior

                if is_valid:

                    # Actualiza indices
                    start = max(primero.start - ventana_exterior, 0)
                    end = min(segundo.end + ventana_exterior, len(doc))

                    #Extrae características
                    candidato = {"tokens": [token.text for token in doc[start:end]],
                               "lemmas": [token.lemma_ for token in doc[start:end]],
                               "pos": [token.pos_ for token in doc[start:end]]}

                    candidato["ent1"] = _format_ent(primero, start)
                    candidato["ent2"] = _format_ent(segundo, start)
                    candidatos.append(candidato)

        return candidatos
