from antlr4 import *
from gramLexer import gramLexer
from gramListener import gramListener
from gramParser import gramParser
from gramPrint import print_graph, create_image_by_id
import sys

import numpy as np
from numpy import linalg
import random

from mdp import simulation_rand as simulation_rand_mdp


class Etat():

    def __init__(self, nom, id, reward, transitions, predecs, succs) -> None:
        self.id = id
        self.nom = nom
        self.reward = reward
        self.transitions = transitions  # Dictionaire:  transitions[decision] = ligne matrice
        self.predecs = predecs
        self.succs = succs
        self.have_decision = False

    def __repr__(self):
        return f'State: {self.nom} \n Id: {self.id} \n Reward: {self.reward} \n Transitions: {self.transitions} \n Predecs: {self.predecs} \n  Succs: {self.succs} \n Is CM? {not self.have_decision}'
    
    def __str__(self):
        return f'State: {self.nom} \n Id: {self.id} \n Reward: {self.reward} \n Transitions: {self.transitions} \n Predecs: {self.predecs} \n Succs: {self.succs} \n Is CM? {not self.have_decision}'


class gramPrintListener(gramListener):

    def __init__(self, dictt={'transact_type1': [], 'transact_type2': [], 'actions': [], 'etats': []}):
        # self.props = dictt
        pass
    
    def enterStatenoreward(self, ctx):
        # print("States: %s" % str([str(x) for x in ctx.ID()]))
        # self.props['etats'] = ([str(x) for x in ctx.ID()])

        for etat, id in zip([str(x) for x in ctx.ID()], range(len([str(x) for x in ctx.ID()]))):
            etats[etat] = (Etat(nom=etat, id=id, reward = 0,transitions={}, predecs=[], succs=[]))

    def enterStatereward(self, ctx):
        #ids = [str(x) for x in ctx.ID()]
        #dep = ids.pop(0)
        #act = ids.pop(0)
        #weights = [int(str(x)) for x in ctx.INT()]
        #print("Transition from " + dep + " with no action and targets " + str(ids) + " with weights " + str(weights))
        
        for etat, reward, id in zip([str(x) for x in ctx.ID()], [int(str(x)) for x in ctx.INT()], range(len([str(x) for x in ctx.ID()]))):
            etats[etat] = (Etat(nom=etat, id=id, reward=reward,transitions={}, predecs=[], succs=[]))


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

        try:

            etats[dep].transitions[act] = self.make_weights(ids, weights)
            etats[dep].have_decision = True

        except KeyError:
            print('Less states have been declared than those who have been used to define transitions after, making it impossible to proceed. Please correct the .mdp file and retry.')
            sys.exit()



    def enterTransnoact(self, ctx):
        ids = [str(x) for x in ctx.ID()]
        dep = ids.pop(0)
        weights = [int(str(x)) for x in ctx.INT()]
        # print("Transition from " + dep + " with no action and targets " + str(ids) + " with weights " + str(weights))
        # self.props['transact_type2'].append([dep, ids, weights])

        etats[dep].transitions['MC'] = self.make_weights(ids, weights)
        for k in ids:
            etats[dep].succs.append(k)
            if etats[dep].transitions['MC'][etats[k].id] == 1.:
                etats[k].predecs.append(dep)

    def make_weights(self, arrivals, weights):

        array = np.zeros(len(etats))

        for arrival, weight in zip(arrivals, weights):

            try:

                id = etats[arrival].id
                array[id] = int(weight)

            except KeyError:
                print('Less states have been declared than those who have been used to define transitions after, making it impossible to proceed. Please correct the .mdp file and retry.')
                sys.exit()

        return array/array.sum()

def load_mdp(path_to_mdp):
    global chaine  # séquence d'états qui ont été faits
    global etats
    global decisions

    etats = {}
    chaine = []
    decisions = []

    lexer = gramLexer(FileStream(path_to_mdp))
    stream = CommonTokenStream(lexer)
    parser = gramParser(stream)
    tree = parser.program()
    printer = gramPrintListener()
    walker = ParseTreeWalker()
    p = walker.walk(printer, tree)
    check_problems(etats)

    G = print_graph(etats)
    return etats, G

def simulation_choice_decision(etats, G_print, id_image, key):
    departure = chaine[-1]

    print_id = departure.nom

    transitions = departure.transitions[key]

    print_id += key  # add action to the id

    arrival_id = choose_state(transitions)
    filtered_dict = {k: v for k, v in etats.items() if v.id == arrival_id}

    obj = [k for k in filtered_dict.values()]
    departure = obj[0]
    print_id += departure.nom
    create_image_by_id(print_id, G_print, id_image)
    chaine.append(departure)

def simulation_choice_normal(etats, G_print, id_image):
    departure = chaine[-1]
    # print_id = ""

    print_id = departure.nom

    transitions = departure.transitions['MC']

    arrival_id = choose_state(transitions)
    filtered_dict = {k: v for k, v in etats.items() if v.id == arrival_id}

    obj = [k for k in filtered_dict.values()]
    departure = obj[0]
    print_id += departure.nom
    # print(f"print_id = {print_id}")
    create_image_by_id(print_id, G_print, id_image)
    chaine.append(departure)

def simulation_choice(etats, G_print, id_image=None):
    if id_image == 0:
        chaine.append(min(etats.values(), key=lambda obj: obj.id))
        departure = chaine[-1]
        create_image_by_id(departure.nom, G_print, id_image)
        return None
    else:
        departure = chaine[-1]

        if departure.have_decision:
            return 'decision', list(departure.transitions.keys())

        else:
            # simulation_choice_normal(etats, G_print, id_image)
            return 'normal', []


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
        create_image_by_id(print_id, G_print, id_image)
        chaine.append(departure)


def choose_state(weights):
    actions = list(range(len(weights)))
    choice = random.choices(actions, weights=weights, k=1)
    return choice[0]

# Checks for the problems in the ex.mdp file
def check_problems(etats):

    for k in etats:

        if etats[k].have_decision:

            for listt in list(etats[k].transitions.values()):

                if sum(listt) == 0:
                    print(f'The state {k} has no exit states for at least one of its actions, making it impossible to proceed. Please correct the .mdp file and retry.')
                    sys.exit()

            if 'MC'in list(etats[k].transitions.keys()):
                print(f'The state {k} has both deterministic and non-deterministic transitions defined to it, making it impossible to proceed. Please correct the .mdp file and retry.')
                sys.exit()


        else:

            try:

                if sum(list(etats[k].transitions.values())[0]) == 0:
                    print(f'The state {k} (with no actions) has no exit states, making it impossible to proceed. Please correct the .mdp file and retry.')
                    sys.exit()


            except (KeyError, IndexError):
                print('More states have been declared than those who have been used to define transitions after, making it impossible to proceed. Please correct the .mdp file and retry.')
                sys.exit()

    return

def SMC_quantitatif(etats, G, goal_state, turns, epsilon, delta):
    
    # goal_state = str(input('''Please type the state you'd like to test the accessability.'''))
    # turns = int(input('''Please type in how many (at most) transitions you'd like to access such state.'''))    
    # epsilon = float(input('''What's the desired precision (\epsilon)? It has to be a value in the [0,1] interval.'''))
    # delta = float(input('''What's the desired error rate (\delta)? It has to be a value in the [0,1] interval.'''))

    N = int(np.ceil((np.log(2) - np.log(delta))/((2*epsilon)**2)) + 1)
    result1 = f'{N} simulations will be done, assuring the given epsilon and delta.'
    print(result1)
            
    success = 0

    for k in range(N):
        chaine = []
        simulation_rand_mdp(etats, G, chaine, False, turns)
        if goal_state in [k.nom for k in chaine]:
            success += 1

    gamma = success / N

    result2 = f'The given model M respects the property given with probability {gamma}, respecting epsilon ({epsilon}) and delta ({delta})'
    print(result2)

    return result1, result2

def SMC_qualitatif(etats, G, goal_state, turns, epsilon, alpha, beta, theta):

    goal_state = str(input('''Please type the state you'd like to test the accessability.'''))
    turns = int(input('''Please type in how many (at most) transitions you'd like to access such state. Type 0 if that's not important.'''))    
    epsilon = float(input('''What's the desired precision (\epsilon)? It has to be a value in the [0,1] interval.'''))
    alpha = float(input('''What's the desired value for alpha?'''))
    beta = float(input('''What's the desired value for beta?'''))
    theta = float(input('''What's the theta value you'd like to compare to?'''))

    gamma1 = theta - epsilon
    gamma0 = theta + epsilon

    A = (1 - beta)/alpha
    B = beta / (1 - alpha)

    Fm = 0
    Vadd = np.log(gamma1 / gamma0)
    Vrem = np.log((1 - gamma1)/(1 - gamma0))
    Fa = np.log((1 - beta)/alpha)
    Fb = np.log(beta / (1 - alpha)) 

    end = False
    result = ""
    while(not end):

        chaine = []
        simulation_rand(etats, G, chaine, False, turns)
        if goal_state in [k.nom for k in chaine]:
            Fm += Vadd
        else:
            Fm += Vrem

        if Fm >= Fa:
            result = f'Hypothesis H1 accepted: Gamma <= Gamma1 = Gamma - Epsilon ({gamma1})!'
            print(result)
            end = True
            
        if Fm <= Fb:
            result = f'hypothesis H0 accepted: Gamma >= Gamma0 = Gamma + Epsilon ({gamma0})!'
            print(result)
            end = True

    return result

def PCTL_CM(etats):

    goal_state = str(input('''Please type the state you'd like to test the accessability.'''))

    N = int(input('''Would you like to test it for a certain number N of simulations? Type N or 0 if not.'''))

    S1 = []
    S1 = get_predecs(etats, goal_state, S1) + [goal_state]

    S0 = []

    for k in etats:
        S = []
        S = list(set(get_succs(etats, k, S)))
        if goal_state not in S:
            S0.append(k)

    S2 = S1 + S0
    S3 = [k for k in etats if k not in S2]

    print(S0, S1, S3)

    A = []
    b = np.zeros(len(etats))

    for k in etats:
        sum = 0
        if etats[k].nom not in S2:
            A.append(etats[k].transitions['MC'])
            for i, transition in enumerate(etats[k].transitions['MC']):
                if i in [etats[k].id for k in S1]:
                    sum += transition 
                
            b[etats[k].id] = sum


    A = np.delete(A, [etats[s].id for s in S2], 1)
    b = np.delete(b, [etats[s].id for s in S2], 0)

    if N == 0:

        x = np.dot(np.linalg.inv(np.identity(len(A)) - A), b) 
        for k, i in zip(S3, range(len(S3))):
            print(f'The probability for the state {k} is {x[i]}')
    
    else:
        y = np.zeros(len(A))
        for k in range(N):
            print(y)
            y = np.dot(A, y) + b
            print(y)          

        for k, i in zip(S3, range(len(S3))):
            print(f'The probability for the state {k} after at most {N} transitions is {y[i]}')


    return

def get_predecs(etats, state, S0):

    forbidden = [state]
    if etats[state].predecs == []:
        return S0
    
    else:
        for s in etats[state].predecs:
            if s != state and s not in S0:
                S0.append(s)
                get_predecs(etats, s, S0)


    return S0

def get_succs(etats, state, S0):

    forbidden = [state]
    if etats[state].succs == forbidden:
            
        S0.append(state)
            
        return S0
    
    else:
        for s in etats[state].succs:
            if s != state and s not in S0:
                S0.append(s)
                get_succs(etats, s, S0)


    return S0

def PCTL_MDP(etats):

    adv = define_adversaire(etats)
    etatscop = etats.copy()

    for k in adv:
        new_transitions = {'MC':etats[k].transitions[adv[k]]}
        etatscop[k].transitions = new_transitions

    #for k in etatscop.values(): print(k)

    etatscop = inittMDP(etatscop)

    for k in etatscop.values(): print(k)

    PCTL_CM(etatscop)

def inittMDP(etats):

    for dep in etats.values():

        if dep.have_decision:

            for i, k in enumerate(dep.transitions['MC']):
                if k != 0.:
                    etats[dep.nom].succs.append(find_by_id(etats, i))
                if k == 1.:
                    etats[find_by_id(etats, i)].predecs.append(dep.nom)
               
                print(dep.succs, dep.predecs)



    return etats

def find_by_id(etats, id):

    for j in etats.values():
        if j.id == id:
            return j.nom
