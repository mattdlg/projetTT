from recuperation_inscription import retrieve_players, Joueur
import numpy as np
import sqlite3 as sq
    
class Poule(): 
    def __init__(self, joueurs, numero):
        self.joueurs = joueurs
        self.id = nbToLetter(numero)
        self.score = {}
        for player in joueurs : 
            player.poule = self.id # memorisation de la poule du joueur 
            self.score[player] = 0 # score initiaux des joueurs dans la poule à 0
        self.type = len(self.joueurs)

        self.score_match = {}
        self.classement = {}
        # self.deroulement()

    def __str__(self):
        return f"Poule n°{self.id} - {self.type} joueurs : {self.joueurs}"
    
    def __repr__(self):
        return f"Poule {self.id}"

    def deroulement(self):
        match self.type :
            case 3 :
                self.partie(self.joueurs[0], self.joueurs[2])
                self.partie(self.joueurs[0], self.joueurs[1])
                self.partie(self.joueurs[1], self.joueurs[2])
            case 4 : 
                self.partie(self.joueurs[0], self.joueurs[3])
                self.partie(self.joueurs[1], self.joueurs[2])
                self.partie(self.joueurs[0], self.joueurs[2])
                self.partie(self.joueurs[1], self.joueurs[3])
                self.partie(self.joueurs[0], self.joueurs[1])
                self.partie(self.joueurs[2], self.joueurs[3])
            case _ :
                print("Error : this should not happen")

        self.calcul_vainqueur()
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
            self.score[j1] += 1
        else : 
            print(f"{j2.__repr__()} remporte la partie")
            self.score[j2] += 1

        self.score_match[(j1, j2)] = resultats
        return
            
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
    
    def calcul_vainqueur(self):
        if self.test_equality(self.score):
            index_classement = self.compute_full_points()
            classement = [self.joueurs[index_classement[k]] for k in range(len(index_classement))]
        
        else :
            les_clefs = list(self.score.keys())
            classement = [les_clefs[0]]
            for j in les_clefs[1:] :
                next_score = self.score[j]
                i = 0
                placed = False
                while i < len(classement) and not placed:
                    if next_score > self.score[classement[i]]:
                        classement.insert(i, j)
                        placed = True
                    i += 1

                if not placed:
                    classement.append(j)

        for k in range(len(classement)):
            self.classement[k+1] = classement[k]
        return classement
    
    def test_equality(self, dico):
        for k in range(self.type):
            for j in range(k+1, self.type):
                if dico[self.joueurs[k]] == dico[self.joueurs[j]]:
                    print(f"Il y a égalité entre les joueurs {self.joueurs[k]} et {self.joueurs[j]}")
                    return True
        return False
    
    def compute_full_points(self):
        total_points = [0 for _ in range(self.type)]
        for k in range(self.type):
            for j in range(k+1, self.type):
                match_score = self.score_match[(self.joueurs[k], self.joueurs[j])]
                for i in range(len(match_score)):
                    total_points[k] += match_score[i][0]
                    total_points[j] += match_score[i][1]

        print(f"Total des points : {total_points}")
        classement = np.argsort(total_points)[::-1]
        return classement
    

## Recherche du nombre de poule à créer :
def decomposition(n):
    if (n%4 == 0) : 
        return (0, n // 4)
    elif (n%3 == 0) :
        return (n // 3, 0)
    
    div4 = (n // 4) 
    reste = n%4
    while reste != 0:
        if reste < 3 : 
            div4 -=1
            reste += 4 

        div3 = reste // 3
        reste = reste % 3
        if reste != 0 : 
            div4 -=1
            reste = n - div4*4
        else : 
            return div3, div4
        
# print(decomposition(14))

## Placement des joueurs dans les poules
def repartition(joueurs):
    nb_poule_3j, nb_poule_4j = decomposition(len(joueurs))
    nb_total = nb_poule_3j + nb_poule_4j
    list_repartition = [[] for _ in range(nb_total)]

    # Placement des 4 meilleurs joueurs dans les 4 poules dans l'ordre :
    for i in range(nb_total):
        list_repartition[i].append(joueurs[i])

    joueur_restant = len(joueurs) - nb_total
    while joueur_restant >= nb_total :
        list_pos = list(np.arange(0, nb_total, 1))
        while len(list_pos) != 0 :
            next_pos = np.random.randint(0, len(list_pos))
            list_repartition[list_pos[next_pos]].append(joueurs[-joueur_restant])
            list_pos.remove(list_pos[next_pos])
            joueur_restant -= 1

    for k in range(0, joueur_restant):
        list_repartition[k].append(joueurs[-(k+1)])
        
    return list_repartition

def creation_poule(repartition_joueurs):
    list_poule = [Poule(repartition_joueurs[k], k+1) for k in range(len(repartition_joueurs))]
    
    # Add the poule to the database
    connection = sq.connect("baseTest2.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Poules (Poule TEXT, Joueur TEXT, Position_Initiale INTEGER)")
    cursor.execute("DELETE FROM Poules")  # Clear previous data
    for poule in list_poule:
        k = 1
        for joueur in poule.joueurs:
            cursor.execute("INSERT INTO Poules (Poule, Joueur, Position_Initiale) VALUES (?, ?, ?)", (poule.id, joueur.ID, k))
            k += 1
    connection.commit()
    connection.close()
   
    return list_poule

def retrieve_poule_data(poule_id):
    connection = sq.connect("baseTest2.db")
    cursor = connection.cursor()
    cursor.execute("SELECT Joueur FROM Poules WHERE Poule = ?", (poule_id,))
    joueurs_ids = cursor.fetchall()

    list_joueurs = []
    for id in joueurs_ids:
        id = id[0]
        cursor.execute("SELECT * FROM Joueurs WHERE Licence_AS = ?", (id,))
        joueur_info = cursor.fetchone()
        if joueur_info:
            joueur = Joueur({
                "Licence_AS": joueur_info[0],
                "Nom": joueur_info[1],
                "Prenom": joueur_info[2],
                "Ecole": joueur_info[3],
                "Classement": joueur_info[4]
            })
            list_joueurs.append(joueur)
    connection.close()
    return list_joueurs


def deroulement_matchs(list_joueurs):
        match len(list_joueurs) :
            case 3 :
                parties = {"1": (list_joueurs[0], list_joueurs[2]),
                           "2": (list_joueurs[0], list_joueurs[1]),
                           "3": (list_joueurs[1], list_joueurs[2])}
            case 4 : 
                parties = {"1": (list_joueurs[0], list_joueurs[3]),
                           "2": (list_joueurs[1], list_joueurs[2]),
                           "3": (list_joueurs[0], list_joueurs[2]),
                           "4": (list_joueurs[1], list_joueurs[3]),
                           "5": (list_joueurs[0], list_joueurs[1]),
                           "6": (list_joueurs[2], list_joueurs[3])}
            case _ :
                print("Error : this should not happen")
                return None

        return parties


def save_match_to_db(match_data):
    connection = sq.connect("baseTest2.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Matches (
            Poule TEXT,
            Joueur1 TEXT,
            Joueur2 TEXT,
            SetJ1 INTEGER,
            SetJ2 INTEGER,
            SetScores TEXT
        )
    """)
    cursor.execute("DELETE FROM Matches WHERE Poule = ? AND Joueur1 = ? AND Joueur2 = ?", (match_data["poule_id"], match_data["joueur1"].ID, match_data["joueur2"].ID))
    cursor.execute("""
        INSERT INTO Matches (Poule, Joueur1, Joueur2, SetJ1, SetJ2, SetScores)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        match_data["poule_id"],
        match_data["joueur1"].ID,
        match_data["joueur2"].ID,
        match_data["setj1"],
        match_data["setj2"],
        str(match_data["set_scores"])
    ))
    connection.commit()
    connection.close()

def retrieve_matchs_from_db(poule_id):
    connection = sq.connect("baseTest2.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Matches WHERE Poule = ?", (poule_id,))
    matchs = cursor.fetchall()
    matchs = [ {
        "poule_id": match[0],
        "joueur1": retrieve_player_from_id(match[1]),
        "joueur2": retrieve_player_from_id(match[2]),
        "setj1": match[3],
        "setj2": match[4],
        "set_scores": eval(match[5]),
        "winner": None
    } for match in matchs]
    matchs = {(j1, j2): match for match in matchs for j1, j2 in [(match["joueur1"].ID, match["joueur2"].ID)]}

    for match in matchs.values() :
        match["winner"] = compute_match_winner(match)
    connection.close()
    return matchs

def compute_match_winner(match_data):
    if match_data["setj1"] == 3:
        winner_position = retrieve_player_position_in_poule(match_data["joueur1"].ID, match_data["poule_id"])
    elif  match_data["setj2"] == 3:
        winner_position = retrieve_player_position_in_poule(match_data["joueur2"].ID, match_data["poule_id"])
    else:
        winner_position = None
        print("Error: No winner determined, as none of the players reached 3 sets won.")
    return int(winner_position) if winner_position else None

def retrieve_player_position_in_poule(player_id, poule_id):
    connection = sq.connect("baseTest2.db")
    cursor = connection.cursor()
    cursor.execute("SELECT Position_Initiale FROM Poules WHERE Poule = ? AND Joueur = ?", (poule_id, player_id))
    position = cursor.fetchone()
    connection.close()

    if position:
        return position[0]
    else:
        return None

def retrieve_player_from_id(player_id):
    connection = sq.connect("baseTest2.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Joueurs WHERE Licence_AS = ?", (player_id,))
    joueur_info = cursor.fetchone()
    connection.close()

    if joueur_info:
        joueur = Joueur({
            "Licence_AS": joueur_info[0],
            "Nom": joueur_info[1],
            "Prenom": joueur_info[2],
            "Ecole": joueur_info[3],
            "Classement": joueur_info[4]
        })
        return joueur
    else:
        return None

def calcul_vainqueur(poule_id):
    all_matchs = retrieve_matchs_from_db(poule_id)
    players = {}
    scores = {}
    full_scores = {}
    for match in all_matchs.values():
        j1, j2 = match["joueur1"].ID, match["joueur2"].ID
        j1_pos = retrieve_player_position_in_poule(j1, poule_id)
        j2_pos = retrieve_player_position_in_poule(j2, poule_id)
        if j1 not in players.keys() :
            players[j1] = j1_pos
            scores[j1] = 0
            full_scores[j1] = 0 
        if j2 not in players.keys() :
            players[j2] = j2_pos
            scores[j2] = 0
            full_scores[j2] = 0

        full_scores[j1] += sum(val[0] for val in match["set_scores"])
        full_scores[j2] += sum(val[1] for val in match["set_scores"])

        if match["winner"] == j1_pos:
            scores[j1] += 1
        else : 
            scores[j2] += 1

    if test_equality(scores):
        index_classement = np.argsort(list(full_scores.values()))[::-1]
        classement = [list(full_scores.keys())[index_classement[k]] for k in range(len(index_classement))]
    
    else :
        index_classement = np.argsort(list(scores.values()))[::-1]
        classement = [list(scores.keys())[index_classement[k]] for k in range(len(index_classement))]

    final_position = []
    for k in range(len(classement)):
        final_position.append((k+1, classement[k]))
    print(final_position)

    # save results to database
    connection = sq.connect("baseTest2.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Classement (Poule TEXT, Position INTEGER, Joueur TEXT)")
    cursor.execute("DELETE FROM Classement WHERE Poule = ?", (poule_id,))
    for position, joueur in final_position:
        cursor.execute("INSERT INTO Classement (Poule, Position, Joueur) VALUES (?, ?, ?)", (poule_id, position, joueur))
    connection.commit()
    connection.close()

    return final_position
    
def test_equality(dico):
    joueurs = list(dico.keys())
    for k in range(len(joueurs)):
        for j in range(k+1, len(joueurs)):
            if dico[joueurs[k]] == dico[joueurs[j]]:
                print(f"Il y a égalité entre les joueurs {joueurs[k]} et {joueurs[j]}")
                return True
    return False


def lancer_les_poules(list_poule):
    dico_classement = {}
    for poule in list_poule :
        poule.deroulement()
        print(poule.classement)
        dico_classement[poule.numero] = poule.classement
    
    return dico_classement

def nbToLetter(num):
    return chr(num + 64)

if __name__ == "__main__" :  
    retrieve_matchs_from_db("A")
    """classement = lancer_les_poules(creation_poule(repartition(retrieve_players(ranked=True))))

    connection = sq.connect("baseTest.db")
    cursor = connection.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS Classement (Poule INTEGER, First INTEGER, Second INTEGER, Third INTEGER, Fourth INTEGER)")
    cursor.execute("DELETE FROM Classement")  # Clear previous data
    for num, poule in classement.items():
        cursor.execute("INSERT INTO Classement (Poule, First, Second, Third, Fourth) VALUES (?, ?, ?, ?, ?)",
                    (num, poule[1].ID, poule[2].ID, poule[3].ID, None if len(poule) < 4 else poule[4].ID))
        
    connection.commit()
    connection.close()"""

