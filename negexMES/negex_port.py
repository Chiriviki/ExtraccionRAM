
import jpype
import jpype.imports

# Import default Java packages


class NegexPort:

    def __init__(self, jar_path, routeConfigFiles, route_out, route_in):

        if not jpype.isJVMStarted():
            jpype.startJVM(classpath=[jar_path], convertStrings=False)

        from smn.main import Main
        from java.util import ArrayList
        from java.lang import Integer

        self.smn_Main = Main
        self.java_util_ArrayList = ArrayList
        self.parseInt = Integer.parseInt

        self.route_out = route_out
        self.route_in = route_in

        # TODO checkear validez de archivos

        self.args = ["-isOuputFileGenerated", "FALSE",
                "-routeConfigFiles", routeConfigFiles,
                "-routeOutTextFile", route_out,
                "-routeInTextFile", route_in,
                "-displayon", "FALSE"]

    def _write_to_input_file(self, entries):
        """
        Escribe entradas en archivo de entrada
        :param entries: Entradas en formato (id, entity, text)
        :return:
        """
        data = [f'{id}\t{entity}\t\"{text}\"' for id, entity, text in entries]
        joint_data = "\n".join(data)
        with open(self.route_in, 'w', encoding="ISO_8859_1") as f:  # NEGEX escribe y lee en ISO_8859_1
            f.write(joint_data)


    def _traslate_results(self, results):

        return [(self.parseInt(result.split('\t')[0]),
                 result.split('\t')[3] == "Negated")
                for result in results]

    def get_negated(self, entries):
        """
        Comprueba la negación en un conjunto de entidades
        :param entries: Entradas en formato (id, ent, texto)
        :return:
        """
        self._write_to_input_file(entries)
        negex = self.smn_Main(self.args)
        results = negex.getAnswerList()
        return self._traslate_results(results)
