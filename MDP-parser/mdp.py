from antlr4 import *
from gramLexer import gramLexer
from gramListener import gramListener
from gramParser import gramParser
from gramPrint import print_graph, create_image_by_id
import sys

import numpy as np
import random


class Etat():

    def __init__(self, nom, id, transitions) -> None:
        self.id = id
        self.nom = nom
        self.transitions = transitions  # Dictionaire:  transitions[decision] = ligne matrice
        self.have_decision = False

class gramPrintListener(gramListener):

    def __init__(self, dictt={'transact_type1': [], 'transact_type2': [], 'actions': [], 'etats': []}):
        #self.props = dictt
        pass

    def enterDefstates(self, ctx):
        # print("States: %s" % str([str(x) for x in ctx.ID()]))
        # self.props['etats'] = ([str(x) for x in ctx.ID()])

        for etat, id in zip([str(x) for x in ctx.ID()], range(len([str(x) for x in ctx.ID()]))):
            etats[etat] = (Etat(nom=etat, id=id, transitions={}))

    def enterDefactions(self, ctx):
        # print("Actions: %s" % str([str(x) for x in ctx.ID()]))
        # self.props['actions'] = [str(x) for x in ctx.ID()]
        pass

    def enterTransact(self, ctx):
        ids = [str(x) for x in ctx.ID()]
        dep = ids.pop(0)
        act = ids.pop(0)
        weights = [int(str(x)) for x in ctx.INT()]
        # print("Transition from " + dep + " with action "+ act + " and targets " + str(ids) + " with weights " + str(weights))
        # self.props['transact_type1'].append([dep, act, ids, weights])

        etats[dep].transitions[act] = self.make_weights(ids, weights)
        etats[dep].have_decision = True

    def enterTransnoact(self, ctx):
        ids = [str(x) for x in ctx.ID()]
        dep = ids.pop(0)
        weights = [int(str(x)) for x in ctx.INT()]
        # print("Transition from " + dep + " with no action and targets " + str(ids) + " with weights " + str(weights))
        # self.props['transact_type2'].append([dep, ids, weights])

        etats[dep].transitions['MC'] = self.make_weights(ids, weights)

    def make_weights(self, arrivals, weights):

        array = np.zeros(len(etats))

        for arrival, weight in zip(arrivals, weights):

            id = etats[arrival].id
            array[id] = int(weight)

        return array/array.sum()


def main():

    global chaine  # s??quence d'??tats qui ont ??t?? faits
    global etats
    global decisions

    etats = {}
    chaine = []
    decisions = []

    lexer = gramLexer(FileStream("simu-mdp.mdp"))
    stream = CommonTokenStream(lexer)
    parser = gramParser(stream)
    tree = parser.program()
    printer = gramPrintListener()
    walker = ParseTreeWalker()
    p = walker.walk(printer, tree)

    G = print_graph(etats)

    print('Would you like to simulate it by choosing each action, simulating randomly or defining a positional opponent? Type 1 or 2 or 3 respectively.')
    choice = int(input('Your choice (1 or 2 or 3):'))

    print('For how many transitions would you like to simulate?')
    n = int(input('Your choice (default is 10):'))

    if choice == 1:
        simulation_choice(etats, G, n)
    elif choice == 2:
        simulation_rand(etats, G, n)
    else:
        adv = define_adversaire(etats)
        simulation_adv(etats, adv, G, n)

    print([k.nom for k in chaine])  # print all selected states


def simulation_choice(etats,G_print, n=10):

    chaine.append(min(etats.values(), key=lambda obj: obj.id))
    departure = chaine[-1]

    print_id = ""
    id_image = 0

    create_image_by_id(departure.nom, G_print, id_image)

    for k in range(n):
        id_image += 2
        print(f'The current state is {departure.nom}')
        print_id = departure.nom

        if departure.have_decision:

            print(f'You have the action(s) {list(departure.transitions.keys())} as choices')
            key = str(input('Enter your choice:'))
            transitions = departure.transitions[key]

            print_id += key  # add action to the id

            arrival_id = choose_state(transitions)
            filtered_dict = {k: v for k, v in etats.items() if v.id == arrival_id}

        else:

            transitions = departure.transitions['MC']

            arrival_id = choose_state(transitions)
            filtered_dict = {k: v for k, v in etats.items() if v.id == arrival_id}

        obj = [k for k in filtered_dict.values()]
        departure = obj[0]
        print_id += departure.nom
        print(f"print_id = {print_id}")
        create_image_by_id(print_id, G_print, id_image)
        chaine.append(departure)


def simulation_rand(etats, G_print, n=10):

    chaine.append(min(etats.values(), key=lambda obj: obj.id))
    departure = chaine[-1]  # S0 object state
    print_id = ""
    id_image = 0

    create_image_by_id(departure.nom, G_print, id_image)

    for k in range(n):
        id_image += 2
        print(f'The current state is {departure.nom}')
        print_id = departure.nom

        if departure.have_decision:

            random_key = random.choice(list(departure.transitions.keys()))
            random_transitions = departure.transitions[random_key]
            print(f'The action {random_key} has been chosen')

            print_id += random_key

            arrival_id = choose_state(random_transitions)
            filtered_dict = {k: v for k, v in etats.items() if v.id == arrival_id}

        else:

            transitions = departure.transitions['MC']

            arrival_id = choose_state(transitions)
            filtered_dict = {k: v for k, v in etats.items() if v.id == arrival_id}

        obj = [k for k in filtered_dict.values()]
        departure = obj[0]
        print_id += departure.nom
        # print(f"print_id = {print_id}")
        create_image_by_id(print_id, G_print, id_image)
        chaine.append(departure)


def simulation_adv(etats, adv, G_print, n=10):
    chaine.append(min(etats.values(), key=lambda obj: obj.id))
    departure = chaine[-1]
    print_id = ""
    id_image = 0

    create_image_by_id(departure.nom, G_print, id_image)

    for k in range(n):
        id_image += 2
        print(f'The current state is {departure.nom}')
        print_id = departure.nom

        if departure.have_decision:

            key = adv[departure.nom]
            transitions = departure.transitions[key]
            print(f'The action {key} has been chosen by the opponent')

            print_id += key

            arrival_id = choose_state(transitions)
            filtered_dict = {k: v for k, v in etats.items() if v.id == arrival_id}

        else:

            transitions = departure.transitions['MC']

            arrival_id = choose_state(transitions)
            filtered_dict = {k: v for k, v in etats.items() if v.id == arrival_id}

        obj = [k for k in filtered_dict.values()]
        departure = obj[0]
        print_id += departure.nom
        print(f"print_id = {print_id}")
        create_image_by_id(print_id, G_print, id_image)
        chaine.append(departure)


def choose_state(weights):
    actions = list(range(len(weights)))
    choice = random.choices(actions, weights=weights, k=1)
    return choice[0]


def define_adversaire(etats):

    adv = {}

    etat_choices = [k for k in etats.values() if k.have_decision]
    for etat in etat_choices:
        print(f'For the state {etat.nom} the choices are: {list(etat.transitions.keys())} with the respective probabilities {list(etat.transitions.values())}')
        adv[etat.nom] = str(input('Your choice for your adversiare is: '))

    print(f"Etats choisis = {etat_choices}")

    return adv


def identifier_ensembles(etats):

    accessibles = {}

    for k in etats:
        pass

if __name__ == '__main__':
    main()
