import os


from spacy.language import Language
from spacy.tokens import Span

from .negex_port import NegexPort


@Language.factory("negex_mes")
class NegexComponent:

    def __init__(self, nlp, name, negex_path, window_size=4):

        routeConfigFiles = negex_path + os.sep
        jar_path = os.path.join(negex_path, 'main', 'smn.jar')
        route_in = os.path.join(negex_path, 'in', 'in.txt')
        route_out = os.path.join(negex_path, 'out', 'callKit.result')

        if not os.path.exists(routeConfigFiles):
            raise Exception("No se encontraron los archivos de configuracion de negex en " + negex_path)

        if not os.path.exists(jar_path):
            raise Exception("No se encontraron los archivos de configuracion de negex en " + jar_path)

        if not os.path.exists(route_in):
            raise Exception("No se encontraron los archivos de configuracion de negex en " + route_in)

        if not os.path.exists(route_out):
            raise Exception("No se encontraron los archivos de configuracion de negex en " + route_out)


        self.negex = NegexPort(jar_path, routeConfigFiles, route_out, route_in)

        if not Span.has_extension("negex"):
            Span.set_extension("negex", default=False)

        self.window_size = window_size

    def __call__(self, doc):

        entries, ents_id = self._prepare_input(doc)

        # Ejecuta negex y obtiene respuesta
        response = self.negex.get_negated(entries)

        # Asigna valor de negacion a cada entidad
        for id, negated in response:

            ents_id[id]._.negex = negated

        return doc

    def _prepare_input(self, doc):
        """
        Dado un doc, prepara la entrada
        :param doc:
        :return: tupla en el que el primer elemento se asignan las identidades en fora de dict(id->ent)
        Y el segundo elemento es una lista de (id, ent_text, window_text)
        """
        ents_id = {}
        entries = []
        # Para cada entidad asigna un identificador y guarda la referencia
        for id, ent in enumerate(doc.ents):
            ents_id[id] = ent
            ent_text = ent.text
            text = self._get_window_text(doc, ent.start, ent.end)  # Solo incluye su propia frase
            entries.append((id, ent_text, text))
        return entries, ents_id

    def _get_window_text(self, doc, ent_start, ent_end):
        """
        Obtiene el texto que rodea a la entidad en una ventana
        :param doc:
        :param ent_start:
        :param ent_end:
        :return:
        """
        start = max(ent_start - self.window_size, 0)

        end = min(ent_end + self.window_size, len(doc))

        return doc[start:end].text

