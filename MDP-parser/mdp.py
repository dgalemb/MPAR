from antlr4 import *
from gramLexer import gramLexer
from gramListener import gramListener
from gramParser import gramParser
from gramPrint import print_graph, print_graph2
import sys

class Etat():

    def __init__(self, nom, id, transitions = {}) -> None:
        self.id = id
        self.nom = nom
        self.transitions = transitions

class gramPrintListener(gramListener):

    def __init__(self, dictt = {'transact_type1': [], 'transact_type2': [], 'actions' : [], 'etats': []}):
        self.props = dictt
        pass

    def enterDefstates(self, ctx):
        print("States: %s" % str([str(x) for x in ctx.ID()]))
        self.props['etats'] = ([str(x) for x in ctx.ID()])

        for etat, id in zip([str(x) for x in ctx.ID()], range(len([str(x) for x in ctx.ID()]))):
            chaine.append(Etat(nom = etat, id = id))

    def enterDefactions(self, ctx):
        print("Actions: %s" % str([str(x) for x in ctx.ID()]))
        self.props['actions'] = [str(x) for x in ctx.ID()]

    def enterTransact(self, ctx):
        ids = [str(x) for x in ctx.ID()]
        dep = ids.pop(0)
        act = ids.pop(0)
        weights = [int(str(x)) for x in ctx.INT()]
        print("Transition from " + dep + " with action "+ act + " and targets " + str(ids) + " with weights " + str(weights))
        self.props['transact_type1'].append([dep, act, ids, weights])


    def enterTransnoact(self, ctx):
        ids = [str(x) for x in ctx.ID()]
        dep = ids.pop(0)
        weights = [int(str(x)) for x in ctx.INT()]
        print("Transition from " + dep + " with no action and targets " + str(ids) + " with weights " + str(weights))
        self.props['transact_type2'].append([dep, ids, weights])



def main():

    global chaine

    chaine = []

    lexer = gramLexer(FileStream("ex.mdp"))
    stream = CommonTokenStream(lexer)
    parser = gramParser(stream)
    tree = parser.program()
    printer = gramPrintListener()
    walker = ParseTreeWalker()
    p = walker.walk(printer, tree)

    print(printer.props)
    print([k.nom for k in chaine])

    # print_graph()
    print_graph2()


def change_state(etat):

    pass

    #return id_etat

if __name__ == '__main__':
    main()
