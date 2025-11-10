import numpy as np
import sqlite3 as sq
import random
from recuperation_inscription import Joueur


class Node():
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.winner = None

    def __str__(self):
        if self.winner is not None:
            return f"{self.winner.__repr__()}"
            # return f"{self.left.__repr__()} vs {self.right.__repr__()}"
        elif type(self.left) == Node and type(self.right) == Node:
            return f"Left subpart : {self.left.__repr__()} \nRight subpart : {self.right.__repr__()}"
    
    def __repr__(self):
        if type(self.left) == Joueur and type(self.right) == Joueur:
            return f"{self.left.__repr__()} vs {self.right.__repr__()}"
        elif type(self.left) == Node and type(self.right) == Node:
            return f"{self.left.__repr__()} < | > {self.right.__repr__()}"

class Tableau():
    def __init__(self, poules):
        self.poules = poules
        self.nb_poules = len(poules)
        self.depth = self.depth_tableau(self.nb_poules * 4)

        self.create_tableau()
        self.pos_tableau = self.generer_tableau(poules)
        self.player_positioning(self.root, self.pos_tableau)

        self.score_match = {}
        self.classement = {}



    def depth_tableau(self, n):
        """
        Fonction qui renvoie la profondeur du tableau pour n joueurs
        """
        if n <=2 :
            return 0
        else:
            return 1 + self.depth_tableau(n//2)
        
    def generer_positions_fixes(self, nb_poules):
        """
        Génère les positions fixes pour les 1ers et 2èmes de poule en garantissant :
        - Les 1ers sont bien répartis.
        - Les 2èmes ne rencontrent pas leur 1er de poule au 1er tour.
        """
        N = nb_poules * 4  # Taille du tableau

        # Positions prédéfinies pour les 1ers (ex: [0, 15, 8, 7] pour 4 poules)
        if nb_poules == 4:
            pos_premiers = [0, 15, 8, 7]  # Haut/Bas de tableau opposés
        else:
            # Fallback pour d'autres tailles (à adapter si besoin)
            pos_premiers = sorted([0, N - 1, N // 2, (N // 2) - 1][:nb_poules], reverse=True)

        # Placement des 2èmes : dans l'autre moitié ET pas en face de leur 1er
        pos_deuxiemes = []
        for i in range(nb_poules):
            premier_pos = pos_premiers[i]
            moitie_premier = 0 if premier_pos < N // 2 else 1
            moitie_cible = 1 - moitie_premier  # On choisit l'autre moitié

            positions_interdites = {p ^ 1 for p in pos_premiers}
            # Positions disponibles dans l'autre moitié
            positions_disponibles = [
                p for p in range(N)
                if (p < N // 2) == (moitie_cible == 0)  # Bonne moitié
                and p not in pos_premiers
                and p not in pos_deuxiemes
                and p not in positions_interdites  # Évite un match direct contre un 1er
            ]

            if not positions_disponibles:
                # Fallback : on prend n'importe quelle position libre (rare)
                positions_disponibles = [
                    p for p in range(N)
                    if p not in pos_premiers
                    and p not in pos_deuxiemes
                    and p not in positions_interdites
                ]

            if not positions_disponibles:
                positions_disponibles = [
                    p for p in range(N)
                    if p not in pos_premiers
                    and p not in pos_deuxiemes
                    and p != premier_pos ^ 1  # Évite le match direct contre SON premier
                ]

            chosen_pos = random.choice(positions_disponibles)
            pos_deuxiemes.append(chosen_pos)

        return pos_premiers, pos_deuxiemes

    def generer_tableau(self, poules, seed=None):
        if seed is not None:
            random.seed(seed)

        nb_poules = len(poules)
        N = nb_poules * 4

        # Extraction des joueurs par position
        premiers = [p[0] for p in poules]
        deuxiemes = [p[1] for p in poules]
        troisiemes = [p[2] for p in poules if len(p) > 2]
        quatriemes = [p[3] for p in poules if len(p) > 3]
        joueurs_restants = troisiemes + quatriemes
        random.shuffle(joueurs_restants)

        # Positions fixes
        pos_premiers, pos_deuxiemes = self.generer_positions_fixes(nb_poules)
        print(f"1ers : {dict(zip(pos_premiers, premiers))}")
        print(f"2èmes : {dict(zip(pos_deuxiemes, deuxiemes))}")

        # Initialisation du tableau
        tableau = [None] * N
        for pos, joueur in zip(pos_premiers, premiers):
            tableau[pos] = joueur
        for pos, joueur in zip(pos_deuxiemes, deuxiemes):
            tableau[pos] = joueur

        # Remplissage des autres joueurs
        positions_libres = [i for i in range(N) if tableau[i] is None]
        for pos in positions_libres:
            adversaire_pos = pos ^ 1
            adversaire = tableau[adversaire_pos]

            # Éviter les joueurs de la même poule que l'adversaire
            if adversaire:
                poule_adversaire = next(p for p in poules if adversaire in p)
                candidats = [j for j in joueurs_restants if j not in poule_adversaire]
            else:
                candidats = joueurs_restants.copy()

            # Priorité : éviter de mettre 2 joueurs d'une même poule dans la même moitié
            moitie_pos = 0 if pos < N // 2 else 1
            meilleurs_candidats = []
            for j in candidats:
                j_poule = next(p for p in poules if j in p)
                conflit = any(
                    tableau[p] in j_poule and ((p < N // 2) == moitie_pos)
                    for p in range(N)
                )
                if not conflit:
                    meilleurs_candidats.append(j)

            # Choix final
            choix = meilleurs_candidats if meilleurs_candidats else candidats
            if choix:
                joueur = random.choice(choix)
                tableau[pos] = joueur
                joueurs_restants.remove(joueur)

        return tableau

    def create_tableau(self):
        """
        Fonction qui crée le tableau de match
        """
        self.root = Node(None, None)
        self.create_node(self.root, self.depth)
        return
    
    def create_node(self, node, depth):
        """
        Fonction qui crée un noeud du tableau de match
        """
        if depth == 0:
            node.left = None
            node.right = None
        else:
            node.left = Node(None, None)
            node.right = Node(None, None)
            self.create_node(node.left, depth-1)
            self.create_node(node.right, depth-1)
        return
    
    def player_positioning(self, root, tableau):
        """
        Fonction qui positionne les joueurs dans le tableau
        """
        # If this is a leaf (created with left/right == None), assign Joueur objects
        # directly to the left and right so subsequent code treats them as players.
        if root.left is None and root.right is None:
            # pop players in order and attach them as leaf values
            try:
                left_player = tableau.pop(0)
            except IndexError:
                left_player = Joueur({"Licence_AS": None, "Nom": None, "Prenom": None, "Ecole": None, "Classement": None})
            try:
                right_player = tableau.pop(0)
            except IndexError:
                right_player = Joueur({"Licence_AS": None, "Nom": None, "Prenom": None, "Ecole": None, "Classement": None})

            root.left = left_player
            root.right = right_player
            return
        
        if root.left is not None:
            self.player_positioning(root.left, tableau)
        if root.right is not None:
            self.player_positioning(root.right, tableau)
        return

    def __str__(self):
        """
        Fonction qui renvoie le tableau de match sous forme de chaîne de caractères
        """
        return str(self.root)
    
    def run_matches(self, root):
        """
        Fonction qui lance les matchs du tableau
        """
        if root.left is None and root.right is None:
            root.winner = None 
            return
        if root.left is None and root.right is not None:
            if type(root.right) is Joueur:
                root.winner = root.right
            else:
                self.run_matches(root.right)
                root.winner = root.right.winner
        if root.right is None and root.left is not None:
            if type(root.left) is Joueur:
                root.winner = root.left
            else:
                self.run_matches(root.left)
                root.winner = root.left.winner

        if type(root.left) is Joueur and type(root.right) is Joueur:
            if root.left.ID == None :
                root.winner = root.right
            elif root.right.ID == None :
                root.winner = root.left
            else :
                # Simuler le match entre root.left et root.right
                root.winner = self.partie(root.left, root.right)

        if type(root.left) is Node and type(root.right) is Node:
            self.run_matches(root.left)
            self.run_matches(root.right)
            root.winner = self.partie(root.left.winner, root.right.winner)
        if type(root.left) is Joueur and type(root.right) is Node:
            self.run_matches(root.right)
            if root.left.ID == None :
                root.winner = root.right.winner
            else :
                root.winner = self.match(root.left, root.right.winner)
        if type(root.left) is Node and type(root.right) is Joueur:
            self.run_matches(root.left)
            if root.right.ID == None :
                root.winner = root.left.winner
            else :
                root.winner = self.match(root.left.winner, root.right)
        
        return
    
    def partie(self, j1, j2):
        print(f"Début de la partie entre les joueurs {j1.__repr__()} et {j2.__repr__()} !")
        resultats = []
        setj1, setj2 = 0, 0
        while len(resultats) < 5 and (setj1 != 3 and setj2 != 3):
            next_score = self.manche(len(resultats)+1)
            resultats.append(next_score)
            if next_score[0] > next_score[1] : 
                setj1 += 1
            elif next_score[0] < next_score[1] : 
                setj2 += 1
            else : 
                print("This should not happen")
        
        if setj1 == 3 :
            print(f"{j1.__repr__()} remporte la partie")
            winner = j1
        else : 
            print(f"{j2.__repr__()} remporte la partie")
            winner = j2

        self.score_match[(j1, j2)] = resultats
        return winner
            
    def manche(self, n):
        print(f"Scores de la manche n°{n}")
        
        while True :
            good_score = False

            score_j1 = input("Rentrer le score du premier joueur (0-11) :")
            score_j2 = input("Rentrer le score du second joueur (0-11) :")

            if score_j1.isdigit() and score_j2.isdigit():
                score_j1 = int(score_j1)
                score_j2 = int(score_j2)

                if (score_j1 >= 0 and score_j2 >= 0) :
                    if (score_j1 >= 10 and score_j2 >= 10) and (abs(score_j1 - score_j2) == 2) :
                        good_score = True
                    elif (score_j1 == 11 and score_j2 <= 9) or (score_j2 == 11 and score_j1 <= 9):
                        good_score = True

            if good_score :
                break
            else : 
                print("Erreur, valeur inconnu ou résultat impossible")

        return (score_j1, score_j2)
    
    def get_winner(self):
        """
        Fonction qui renvoie le vainqueur du tableau
        """
        return self.root.winner
    
    def get_dico_tableau(self, root, dico, level):
        """
        Fonction qui renvoie le dictionnaire du tableau
        """
        # Only operate on Node instances. If root is not a Node, nothing to do.
        if not isinstance(root, Node):
            return dico

        # If both children are Joueur instances (leaf pairing), add them directly
        if isinstance(root.left, Joueur) and isinstance(root.right, Joueur):
            dico[level] = dico.get(level, []) + [(root.left, root.right, root.winner)]
            return dico

        # Recurse only into children that are Node objects
        if isinstance(root.left, Node):
            self.get_dico_tableau(root.left, dico, level+1)
        if isinstance(root.right, Node):
            self.get_dico_tableau(root.right, dico, level+1)

        # After processing deeper levels, record this node's matchup using
        # either the child Node.winner or the child Joueur directly.
        left_val = root.left.winner if isinstance(root.left, Node) else root.left
        right_val = root.right.winner if isinstance(root.right, Node) else root.right
        dico[level] = dico.get(level, []) + [(left_val, right_val, root.winner)]
        return dico

    def _collect_leaves(self, root, lst):
        """Recursively collect Joueur instances from the tree in left-to-right order."""
        # If root is not a Node, nothing to collect
        if not isinstance(root, Node):
            return

        # If the two children are players, append them in order
        if isinstance(root.left, Joueur) and isinstance(root.right, Joueur):
            lst.append(root.left)
            lst.append(root.right)
            return

        # Otherwise, recurse left then right, handling cases where a child is a Joueur
        if isinstance(root.left, Node):
            self._collect_leaves(root.left, lst)
        elif isinstance(root.left, Joueur):
            lst.append(root.left)

        if isinstance(root.right, Node):
            self._collect_leaves(root.right, lst)
        elif isinstance(root.right, Joueur):
            lst.append(root.right)

    def get_positions_map(self):
        """Return an ordered dict-like mapping {pos: joueur} of leaf players left-to-right.

        This is suitable to pass directly to the SVG template which expects either a
        mapping or a list of (pos, joueur) pairs.
        """
        leaves = []
        self._collect_leaves(self.root, leaves)
        return {i: leaves[i] for i in range(len(leaves))}

def size_tableau(n):
    """
    Fonction qui renvoie la taille du tableau pour n joueurs
    """
    if n == 1:
        return 1
    elif n == 2:
        return 2
    else:
        return 2 * size_tableau(n//2)
    

def create_final_tableau():
    """
    Fonction qui crée le tableau final
    """
    connection = sq.connect("baseTest2.db")
    cursor = connection.cursor()
    poule_results = cursor.execute("SELECT * FROM Classement;").fetchall()
    dico_poules = {}
    for results in poule_results:
        poule, position, joueur = results[0], results[1], results[2]
        if poule not in dico_poules:
            dico_poules[poule] = {}
        if joueur is not None:
            joueur = cursor.execute("SELECT * FROM Joueurs WHERE Licence_AS = ?;", (joueur,)).fetchone()
            info_joueur = {
                "Licence_AS": joueur[0],
                "Nom": joueur[1],
                "Prenom": joueur[2],
                "Ecole": joueur[3],
                "Classement": joueur[4]
            }
            joueur = Joueur(info_joueur)
        else:
            joueur = Joueur({"Licence_AS": None, "Nom": None, "Prenom": None, "Ecole": None, "Classement": None})

        dico_poules[poule][position] = joueur
    
    connection.close()

    list_poules = [[dico_poules[poule][pos] for pos in sorted(dico_poules[poule].keys())] for poule in sorted(dico_poules.keys())]
    tableau = Tableau(list_poules)
    print("\nTableau final :")
    print(tableau)

    dico_tableau = tableau.get_positions_map()
    size_tableau = tableau.depth_tableau(len(list_poules)*4)
    return dico_tableau, size_tableau


        


if __name__ == "__main__":
    connection = sq.connect("baseTest.db")
    cursor = connection.cursor()
    poule_results = cursor.execute("SELECT First, Second, Third, Fourth FROM Classement;").fetchall()

    poule_results = [list(poule) for poule in poule_results]

    for poule in poule_results:
        for i in range(len(poule)):
            if poule[i] is not None:
                joueur = cursor.execute("SELECT * FROM Joueurs WHERE Licence_AS = ?;", (poule[i],)).fetchone()
                info_joueur = {
                    "Licence_AS": joueur[0],
                    "Nom": joueur[1],
                    "Prenom": joueur[2],
                    "Ecole": joueur[3],
                    "Classement": joueur[4]
                }
                joueur = Joueur(info_joueur)
                poule[i] = joueur
            else:
                joueur = Joueur({"Licence_AS": None, "Nom": None, "Prenom": None, "Ecole": None, "Classement": None})
                poule[i] = joueur

    connection.close()

    # print(poule_results)

    # print("\nTableau final :")
    # tableau = generer_tableau(poule_results, seed=40)
    # for i, joueur in enumerate(tableau):
    #     print(f"Position {i}: {joueur.__repr__()}")

    tableau = Tableau(poule_results)
    print("\nTableau final :")
    print(tableau)

    tableau.run_matches(tableau.root)
    print("\nRésultats des matchs :")
    for match, result in tableau.score_match.items():
        print(f"{match[0].__repr__()} vs {match[1].__repr__()} : {result}")
    print(f"\nVainqueur du tableau : {tableau.get_winner().__repr__()}")











