from .medtagger.Med_Tagger import Med_Tagger
from spacy.tokenizer import Tokenizer
from spacy.tokens import Doc


class SPACCC_tokenizer(Tokenizer):

    def __init__(self, nlp_vocab):
        super().__init__(nlp_vocab)
        self.tagger = Med_Tagger()

    def __call__(self, text):

        words = []
        lemmas = []
        pos = []
        spaces = []

        if not len(text.strip()) == 0:
            spaccc_tags = self.tagger.get_results(text)

            # No devuelve resultados
            if len(spaccc_tags) == 0: raise Exception("El contenedor de Freeling no devolvió resultados")

            else:
                # La ultima etiqueta es siempre vacía
                tags = self._split_sent_tags(spaccc_tags)
                words += tags[0]
                lemmas += tags[1]
                pos += tags[2]

            spaces = self._get_spaces(text, words)
        doc = Doc(self.vocab, words=words, spaces=spaces, lemmas=lemmas, pos=pos)
        return doc

    def _split_sent_tags(self, sent_tags):
        """
        Divide la la salida de Med-Tagger en array de words, lemma y pos
        :param sent_tags:
        :return: tupla de arrays de words, lemma y pos
        """
        #tags = list(zip(*sent_tags))
        # TODO SPACCC mete un \n al final de cada frase se podría aprovechar para coger frases.
        #  Por ahora se limpia
        sent_tags = [tag for tag in sent_tags if tag != tuple('\n')]

        words = [tag[0] for tag in sent_tags]
        lemmas = [tag[1] for tag in sent_tags]
        pos = [self._pos_tags_map(tag[2]) for tag in sent_tags]
        return words, lemmas, pos


    def _get_spaces(self, text, tags):
        """
        Obtiene los espacios originales del texto.
        Solo probado para espacios simples!
        :param text: Texto original
        :param tags: Tokens del texto
        :return: array boolean, en la posicion i es verdadero sin entre el token i y el i+1 hay un espacio
        """
        start = 0
        end = len(text)
        spaces = []
        for tag in tags[:-1]:
            # Pasa la palabra detectada
            text.find(tag, start, end)
            start += len(tag)

            # Comprueba si el siguiente caracter es un espacio
            if text[start] == ' ':
                start += 1
                spaces.append(True)
            else:
                spaces.append(False)

        spaces.append(False)
        return spaces

    def _pos_tags_map(self, label):
        """
        mapea las eqitquetas de freeling en etiquetas de spacy
        :param label:
        :return:
        """
        if len(label)>0:

            if label[0] == 'P':
                pos = 'PRON'
            elif label[0] == 'N':
                if label[1] == 'P':
                    pos = "PROPN"
                else:
                    pos = "NOUN"
            elif label[0] == 'D':
                pos = 'DET'
            elif label[0] == 'A':
                pos = 'ADJ'
            elif label[0] == 'C':
                pos = 'CONJ'
            elif label[0] == 'R':
                pos = 'ADV'
            elif label[0] == 'S':
                pos = "ADP"
            elif label[0] == 'V':
                if label[1] == 'M':
                    pos = "VERB"
                else:
                    pos = "AUX"
            elif label[0] == 'Z':
                pos = 'NUM'
            elif label[0] == 'I':
                pos = "INTJ"
            elif label[0] == 'F':
                if label[1] == 'p' or label[1] == 'd' or label[1] == 'c':
                    pos = "PUNCT"
                else:
                    pos = "SYM"
            else:
                pos = "X"
        else:
            pos = 'X'
        # DATE de freeling se queda sin mapear
        return pos
