from flask import Flask, request, url_for, render_template, make_response, jsonify

from recuperation_inscription import add_new_player, retrieve_players, delete_one_player, add_csv_players
from phase_de_poule import (creation_poule, 
                            repartition, 
                            retrieve_poule_data, 
                            deroulement_matchs, 
                            save_match_to_db, 
                            retrieve_player_from_id, 
                            retrieve_matchs_from_db,
                            calcul_vainqueur)
from phase_de_tableau import (create_final_tableau)

import datetime 
from io import BytesIO

app = Flask(__name__)

app.jinja_env.filters['zip'] = zip

@app.route("/", methods = ["GET"])
def menu():
    html_str = render_template('menu.html')
    return html_str

@app.route("/about", methods = ["GET"])
def about():
    html_str = render_template('about.html')
    return html_str

@app.route("/contact", methods = ["GET"])
def contact():
    html_str = render_template('contact.html')
    return html_str

@app.route("/tournament", methods = ["GET"])
def tournament():
    html_str = render_template('tournament.html')
    return html_str

@app.route("/inscription", methods = ["GET"])
def inscription():
    html_str = render_template('inscription.html')
    return html_str

@app.route("/inscription", methods = ["POST"])
def inscription_post():
    # Récupérer les données du formulaire
    new_player = list(request.form.values())
    # ajout du joueur dans la base de données
    add_new_player(new_player)

    return render_template('players.html', ranked_players=retrieve_players(ranked=True), non_ranked_players=retrieve_players(ranked=False))

@app.route("/players", methods = ["GET"])
def players():
    # This would typically fetch player data from a database
    """players_data = [
        {"Licence_AS": "MQ1E393721", "Nom": "Gueucier", "Prenom": "Alice", "Ecole": "INSA", "Classement": 10},
        {"Licence_AS": "MQ1E345678", "Nom": "Deleglise", "Prenom": "Matthieu", "Ecole": "INSA", "Classement": 19},
        {"Licence_AS": "MQ1E230762", "Nom": "Rodriguez", "Prenom": "Nina", "Ecole": "INSA", "Classement": 8},
        {"Licence_AS": "MQ1E224243", "Nom": "Jadin", "Prenom": "Guilhem", "Ecole": "INSA", "Classement": 6},
        {"Licence_AS": "MQ1E727834", "Nom": "Cuzin", "Prenom": "Justin", "Ecole": "INSA", "Classement": 13},
        {"Licence_AS": "MQ1E234943", "Nom": "Prevot", "Prenom": "Clement", "Ecole": "INSA", "Classement": 20}
    ]"""
    r_players_data = retrieve_players(ranked=True)
    nr_players_data = retrieve_players(ranked=False)

    html_str = render_template('players.html', ranked_players=r_players_data, non_ranked_players=nr_players_data)
    return html_str

@app.route("/delete_player/<player_id>", methods = ["GET"])
def delete_player(player_id):
    # This would typically delete all players from a database
    delete_one_player(player_id)
    return render_template('players.html', ranked_players=retrieve_players(ranked=True), non_ranked_players=retrieve_players(ranked=False))

@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    # Check if the post request has the file part
    print(request.files)
    if 'csv_file' not in request.files:
        return render_template('upload_csv.html', error="No file part")
    file = request.files['csv_file']
    if file.filename == '':
        return render_template('upload_csv.html', error="No selected file")
    if file:
        # You can process the CSV file here if needed
        add_csv_players(file)
        # For now, just render the template
        return render_template('players.html', ranked_players=retrieve_players(ranked=True), non_ranked_players=retrieve_players(ranked=False))
    return render_template('upload_csv.html', error="File upload failed")

@app.route("/results", methods = ["GET", "POST"])
def results():
    
    if request.method == "POST":
        date = request.form.get('date')
        if not date:
            return render_template('results.html', error="Date is required")
        # This would typically fetch results data from a database based on the date
        whole_results = [
            {"date": "2025-05-01", "classement": {"first": "Alice Gueucier", "second": "Matthieu Deleglise", "third": "Guilhem Jadin"}},
            {"date": "2025-06-02", "classement": {"first": "Nina Rodriguez", "second": "Justin Cuzin", "third": "Clement Prevot"}},
        ]
        if date not in [result['date'] for result in whole_results]:
            return render_template('results.html', error="No results found for the given date")
        
        results_data = [result for result in whole_results if result['date'] == date][0]
        html_str = render_template('results.html', res=results_data, date=date)
    
    else:
        html_str = render_template('results.html')
    return html_str


@app.route("/poules", methods = ["GET"])
def poules():
    list_poules = creation_poule(repartition(retrieve_players(ranked=True)))
    poules_data = [{"id": poule.id, "Joueurs": [f"{joueur.prenom} {joueur.nom}" for joueur in poule.joueurs]} for poule in list_poules]

    html_str = render_template('poules.html', poules=poules_data)
    return html_str

@app.route("/poules/<poule_id>", methods = ["GET", "POST"])
def poule_sheet(poule_id):
    positions = []
    if request.method == "POST":
        positions = calcul_vainqueur(poule_id)
    
    poule_data = {
        "id": poule_id,
        "Joueurs": retrieve_poule_data(poule_id),
        "positions" : positions
    }
    list_parties = deroulement_matchs(poule_data["Joueurs"])
    matchs = retrieve_matchs_from_db(poule_id)
    html_str = render_template('poule_sheet.html', poule=poule_data, parties=list_parties, list_matchs=matchs)
    return html_str

@app.route("/poules/<poule_id>/match/<j1>/<j2>", methods = ["GET", "POST"])
def poule_match(poule_id, j1, j2):
    # This would typically fetch match data from a database
    match_data = {
            "poule_id": poule_id,
            "joueur1": retrieve_player_from_id(j1),
            "joueur2": retrieve_player_from_id(j2),
            "setj1": 0,
            "setj2": 0,
            "set_scores": [],
            "winner": None
        }
    if request.method == "GET":
        html_str = render_template('match.html', match=match_data)
        return html_str
    
    elif request.method == "POST":
        # Récupérer les scores des sets depuis le formulaire
        set_scores = []
        for i in range(1, 6):
            score_j1 = request.form.get(f'set{i}_j1')
            score_j2 = request.form.get(f'set{i}_j2')
            if score_j1 != '' and score_j2 != '':
                score_j1 = int(score_j1)
                score_j2 = int(score_j2)
                set_scores.append((score_j1, score_j2))
            if score_j1 > score_j2 : 
                print("J1 gagne le set")
                match_data["setj1"] += 1
            elif score_j2 > score_j1 : 
                print("J2 gagne le set")
                match_data["setj2"] += 1
        match_data["set_scores"] = set_scores
        save_match_to_db(match_data) 
        
        # Mettre à jour la feuille de poule avec les résultats du match
        poule_data = {
            "id": poule_id,
            "Joueurs": retrieve_poule_data(poule_id)
        }
        list_parties = deroulement_matchs(poule_data["Joueurs"])
        matchs = retrieve_matchs_from_db(poule_id)
        for (j1, j2) in list_parties.values():
            if not matchs.get((j1.ID,j2.ID)):
                matchs[(j1.ID,j2.ID)] = {}
        html_str = render_template('poule_sheet.html', poule=poule_data, parties=list_parties, list_matchs=matchs)
        return html_str

@app.route("/tableau", methods=["GET"])
def final_table():
    # This would typically fetch final table data from a database
    # final_table_data, size_table = create_final_tableau()
    # final_table_data = {k: (v[0], (v[1].prenom + " " + v[1].nom) if v[1] else "TBD") for k, v in final_table_data.items()}
    example_table = {0: "Alice Geucier", 1: "Matthieu Deleglise", 
                     2: "Nina Rodriguez", 3: "Guilhem Jadin", 
                     4: "Justin Cuzin", 5: "Clement Prevot",
                     6: "Man Deibler", 7: "Test guy",
                     8: "Max Mustermann", 9: "Erika Mustermann",
                     10: "John Doe", 11: "Jane Doe",
                     12: "Foo Bar", 13: "Bar Foo",
                     14: "Lorem Ipsum", 15: "Dolor Sit"
    }
    html_str = render_template('final_table.html', table=example_table, size_table=16)
    return html_str