import os
from sqlalchemy import create_engine
from flask import Flask, request, render_template, g, redirect
from dotenv import load_dotenv
load_dotenv()

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

u = os.getenv("DBUSER")
p = os.getenv("DBPASS")
DATABASEURI = "postgresql://" + u + ":" + p + "@34.75.150.200/proj1part2"
engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
    try:
        g.conn = engine.connect()
    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        print(e)


@app.route('/<string:sport>/games')
def games(sport):
    sport = sport.lower().capitalize()
    cursor = g.conn.execute(
        "SELECT * FROM game_in "
        "WHERE sport=%s "
        "ORDER BY date DESC",
        sport
    )
    games = []
    for result in cursor:
        games.append({
            'name1': result['name1'],
            'location1': result['location1'],
            'name2': result['name2'],
            'location2': result['location2'],
            'winner_name': result['winner_name'],
            'winner_location': result['winner_location'],
            'date': result['date'],
            'time': result['time'],
            'sport': result['sport']
        })
    cursor.close()

    context = dict(data=games)

    return render_template("index.html", **context)


@app.route('/<string:sport>/games/')
def specific_game(sport):
    name1 = request.args.get('n1')
    location1 = request.args.get('l1')
    name2 = request.args.get('n2')
    location2 = request.args.get('l2')
    date = request.args.get('date')
    time = request.args.get('time')
    cursor = g.conn.execute(
        "SELECT * FROM game_in "
        "WHERE "
        "sport=%s "
        "name1=%s "
        "location1=%s "
        "name2=%s "
        "location2=%s "
        "date=%s "
        "time=%s",
        sport,
        name1,
        location1,
        name2,
        location2,
        date,
        time
    )
    # Get players and comments too


@app.route('/<sport>/players')
def players(sport):
    sport = sport.lower().capitalize()
    cursor = g.conn.execute(
        "SELECT * FROM players "
        "WHERE sport=%s "
        "ORDER BY name ASC",
        sport
    )
    players = []
    for result in cursor:
        players.append({
            'id': result['id'],
            'name': result['name'],
            'dob': result['dob'],
            'height': result['height'],
            'weight': result['weight'],
            'sport': result['sport']
        })
    cursor.close()

    # context = dict(data=players)

    return redirect('/' + sport + '/games/')


@app.route('/<sport>/players/')
def specific_player(sport):
    pass


@app.route('/<sport>/teams')
def teams(sport):
    sport = sport.lower().capitalize()
    cursor = g.conn.execute(
        "SELECT * FROM teams "
        "WHERE sport=%s "
        "ORDER BY rank ASC",
        sport
    )
    teams = []
    for result in cursor:
        teams.append({
            'name': result['name'],
            'location': result['location'],
            'rank': result['rank'],
            'sport': result['sport']
        })
    cursor.close()

    # context = dict(data=teams)

    return redirect('/' + sport + '/games/')

@app.route('/<sport>/teams/')
def specific_team(sport):
    pass


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

            python server.py

        Show the help text using:

            python server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()
