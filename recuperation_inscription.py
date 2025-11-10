import pandas as pd
import sqlite3 as sq

# Classe Joueur : infos des inscrits
class Joueur():
    def __init__(self, infos):
        self.ID = infos["Licence_AS"]
        self.nom = infos["Nom"]
        self.prenom = infos["Prenom"]
        self.ecole = infos["Ecole"]
        self.classement = infos["Classement"]
        
        self.poule = None
        self.position_finale = None

    def __str__(self):
        return f"Le joueur de licence {self.ID} est {self.nom} {self.prenom}, classé {self.classement} de l'école {self.ecole}."
    
    def __repr__(self):
        return f"{self.ID} - {self.nom} {self.prenom}"

def add_new_player(new_player):
    """Add a new player to the database."""
    new_player_infos = {
        "Licence_AS": new_player[0],
        "Nom": new_player[1],
        "Prenom": new_player[2],
        "Ecole": new_player[3],
        "Classement": new_player[4]
    }
    joueur = Joueur(new_player_infos)

    connection = sq.connect("baseTest2.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Joueurs (
            Licence_AS TEXT PRIMARY KEY,
            Nom TEXT,
            Prenom TEXT,
            Ecole TEXT,
            Classement TEXT
        )
    """)
    cursor.execute("""
        INSERT INTO Joueurs (Licence_AS, Nom, Prenom, Ecole, Classement)
        VALUES (?, ?, ?, ?, ?)
    """, (joueur.ID, joueur.nom, joueur.prenom, joueur.ecole, joueur.classement))
    connection.commit()
    connection.close()

def add_csv_players(file):
    """Add multiple players from a CSV file to the database."""
    # Read the CSV file into a DataFrame
    # file.read().decode("utf-8")
    connection = sq.connect("baseTest2.db")
    # open the datasets
    data_inscripts = pd.read_csv(file,header=0)
    # to sqlite3
    data_inscripts.to_sql("Joueurs", connection, if_exists='replace',index=False)
    connection.close()

def retrieve_players(ranked=True):
    """Retrieve all players from the database."""
    connection = sq.connect("baseTest2.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master WHERE type='table' AND name='Joueurs';
    """)
    if cursor.fetchone() is None:
        return None  # Table does not exist
    # récupération des joueurs classés ou non classés
    if ranked:
        df = pd.read_sql_query("SELECT * FROM Joueurs WHERE Classement != 'NC';", connection)
        df["Classement"] = df["Classement"].astype(int) 
        # sorting part classement décroissant
        df.sort_values("Classement", axis=0, ascending=False, inplace=True, kind='quicksort', na_position='last', ignore_index=False, key=None)

    else :
        df = pd.read_sql_query("SELECT * FROM Joueurs WHERE Classement = 'NC';", connection)

    list_players = [Joueur(df.iloc[k, :]) for k in range(len(df["Licence_AS"]))]
    connection.close()
    return list_players

def delete_one_player(licence_AS):
    connection = sq.connect("baseTest2.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Joueurs WHERE Licence_AS = ?;", (licence_AS,))
    connection.commit()
    connection.close()    


if __name__ == "__main__":
    # make a connection
    connection = sq.connect("baseTest.db")

    # open the datasets
    data_inscripts = pd.read_csv("Inscription_test.csv",header=0)

    # to sqlite3
    data_inscripts.to_sql("Joueurs", connection, if_exists='replace',index=False)
    print(data_inscripts)
    connection.close()




