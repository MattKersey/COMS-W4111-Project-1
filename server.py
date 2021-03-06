import os
from sqlalchemy import create_engine
from flask import Flask, request, render_template, g, redirect, session
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = 'lskdjflaskdgjhvncvnklajehfpieuahadjsklfj'

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


@app.route('/', methods=['GET'])
def login_screen():
    if 'user' in session:
        return redirect('/basketball/games/')
    fail = False
    if request.args.get('fail') == "true":
        fail = True
    context = dict(fail=fail)
    return render_template("login.html", **context)


@app.route('/logout/', methods=['GET'])
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect('/')


@app.route('/login/', methods=['POST'])
def login():
    if 'user' in session:
        return redirect('/basketball/games/')
    email = request.form['email']
    password = request.form['pass']
    cursor = g.conn.execute(
        "SELECT username FROM users "
        "WHERE email=%s AND password=%s",
        email,
        password
    )
    if len(cursor.fetchall()) == 0:
        return redirect('/?fail=true')
    else:
        session['user'] = {'email': email}
    cursor.close()
    return redirect('/basketball/games/')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if 'user' in session:
        return redirect('/basketball/games/')
    if request.method == 'POST':
        emailFlag = "false"
        usernameFlag = "false"
        phoneFlag = "false"
        email = request.form['email']
        username = request.form['username']
        phone = request.form['phone']
        bio = request.form['bio']
        password = request.form['pass']

        cursor = g.conn.execute(
            "SELECT email FROM users WHERE email=%s", email
        )
        results = cursor.fetchall()
        if len(results) != 0:
            emailFlag = "true"
        cursor.close()

        cursor = g.conn.execute(
            "SELECT email FROM users WHERE username=%s", username
        )
        results = cursor.fetchall()
        if len(results) != 0:
            usernameFlag = "true"
        cursor.close()

        cursor = g.conn.execute(
            "SELECT email FROM users WHERE phone=%s", phone
        )
        results = cursor.fetchall()
        if len(results) != 0:
            phoneFlag = "true"
        cursor.close()
        if emailFlag == "true" or phoneFlag == "true" or usernameFlag == "true":
            return redirect(
                '/register/?email=' + emailFlag +
                '&phone=' + phoneFlag +
                '&username=' + usernameFlag
            )
        try:
            g.conn.execute(
                "INSERT INTO users VALUES(%s, %s, %s, %s, %s)",
                email,
                username,
                password,
                bio,
                phone
            )
        except Exception as e:
            print(e)

        return redirect('/')
    else:
        emailFlag = False
        if request.args.get('email') == "true":
            emailFlag = True
        usernameFlag = False
        if request.args.get('username') == "true":
            usernameFlag = True
        phoneFlag = False
        if request.args.get('phone') == "true":
            phoneFlag = True
        context = dict(email=emailFlag, username=usernameFlag, phone=phoneFlag)
        return render_template("register.html", **context)


@app.route('/user/', methods=['GET', 'POST'])
def userpage():
    if 'user' not in session:
        return redirect('/')
    if request.method == 'POST':
        if request.form['pass'] != '':
            g.conn.execute(
                "UPDATE users "
                "SET bio=%s, password=%s "
                "WHERE email=%s",
                request.form['bio'],
                request.form['pass'],
                session['user']['email']
            )
        else:
            g.conn.execute(
                "UPDATE users "
                "SET bio=%s "
                "WHERE email=%s",
                request.form['bio'],
                session['user']['email']
            )

        if (request.form.get('BasketballPref') is not None):
            try:
                g.conn.execute(
                    "INSERT INTO prefers VALUES(%s, 'Basketball')", session['user']['email']
                )
            except Exception as e:
                print(e)
        else:
            g.conn.execute(
                "DELETE FROM prefers WHERE email=%s AND name='Basketball'", session['user']['email']
            )

        if (request.form.get('FootballPref') is not None):
            try:
                g.conn.execute(
                    "INSERT INTO prefers VALUES(%s, 'Football')", session['user']['email']
                )
            except Exception as e:
                print(e)
        else:
            g.conn.execute(
                "DELETE FROM prefers WHERE email=%s AND name='Football'", session['user']['email']
            )

        if (request.form.get('SoccerPref') is not None):
            try:
                g.conn.execute(
                    "INSERT INTO prefers VALUES(%s, 'Soccer')", session['user']['email']
                )
            except Exception as e:
                print(e)
        else:
            g.conn.execute(
                "DELETE FROM prefers WHERE email=%s AND name='Soccer'", session['user']['email']
            )

        if (request.form.get('BaseballPref') is not None):
            try:
                g.conn.execute(
                    "INSERT INTO prefers VALUES(%s, 'Baseball')", session['user']['email']
                )
            except Exception as e:
                print(e)
        else:
            g.conn.execute(
                "DELETE FROM prefers WHERE email=%s AND name='Baseball'", session['user']['email']
            )
        return redirect('/user/')
    else:
        cursor = g.conn.execute(
            "SELECT email, username, phone, bio FROM users WHERE email=%s",
            session['user']['email']
        )
        results = cursor.fetchall()
        cursor.close()
        if len(results) == 0:
            return redirect('/logout/')

        cursor = g.conn.execute(
            "SELECT name AS sport FROM prefers WHERE email=%s",
            session['user']['email']
        )
        basketball = ''
        football = ''
        soccer = ''
        baseball = ''
        for result in cursor:
            if result['sport'] == 'Basketball':
                basketball = 'true'
            if result['sport'] == 'Football':
                football = 'true'
            if result['sport'] == 'Soccer':
                soccer = 'true'
            if result['sport'] == 'Baseball':
                baseball = 'true'

        context = dict(
            user=results[0],
            basketball=basketball,
            football=football,
            soccer=soccer,
            baseball=baseball
        )
        return render_template('user.html', **context)


@app.route('/basketball/', methods=['GET'])
def basketball():
    if 'user' not in session:
        return redirect('/')
    return redirect('/basketball/games/')


@app.route('/football/', methods=['GET'])
def football():
    if 'user' not in session:
        return redirect('/')
    return redirect('/football/games/')


@app.route('/soccer/', methods=['GET'])
def soccer():
    if 'user' not in session:
        return redirect('/')
    return redirect('/soccer/games/')


@app.route('/baseball/', methods=['GET'])
def baseball():
    return redirect('/baseball/games/')


@app.route('/comments/like/')
def like():
    if 'user' not in session:
        return redirect('/')
    id = request.args.get('id')
    try:
        g.conn.execute("INSERT INTO likes VALUES(%s, %s)", id, session['user']['email'])
    except Exception as e:
        print(e)
        return myRedirect(request)
    return myRedirect(request)


@app.route('/comments/unlike/')
def unlike():
    if 'user' not in session:
        return redirect('/')
    id = request.args.get('id')
    g.conn.execute("DELETE FROM likes WHERE id=%s AND email=%s", id, session['user']['email'])
    return myRedirect(request)


@app.route('/comments/delete/')
def delete():
    if 'user' not in session:
        return redirect('/')
    id = request.args.get('id')
    cursor = g.conn.execute(
        "SELECT id FROM comments_post WHERE id=%s AND email=%s",
        id,
        session['user']['email']
    )
    results = cursor.fetchall()
    cursor.close()
    if len(results) == 0:
        return myRedirect(request)

    g.conn.execute("DELETE FROM game_comment_appears_on WHERE id=%s", id)
    g.conn.execute("DELETE FROM player_comment_appears_on WHERE comment_id=%s", id)
    g.conn.execute("DELETE FROM team_comment_appears_on WHERE id=%s", id)
    g.conn.execute("DELETE FROM likes WHERE id=%s", id)
    g.conn.execute("DELETE FROM comments_post WHERE id=%s", id)

    return myRedirect(request)


def myRedirect(req):
    type = req.args.get("type")
    sport = request.args.get("sport")
    if type == "games":
        name1 = request.args.get('n1')
        location1 = request.args.get('l1')
        name2 = request.args.get('n2')
        location2 = request.args.get('l2')
        date = request.args.get('date')
        time = request.args.get('time')
        return redirect(
            "/" + sport +
            "/games/?n1=" + name1 +
            "&l1=" + location1 +
            "&n2=" + name2 +
            "&l2=" + location2 +
            "&date=" + date +
            "&time=" + time
        )
    if type == "players":
        id = request.args.get('pid')
        return redirect("/" + sport + "/players/?id=" + id)
    if type == "teams":
        name = request.args.get('name')
        loc = request.args.get('loc')
        return redirect("/" + sport + "/teams/?name=" + name + "&loc=" + loc)
    return redirect("/")


@app.route('/comments/new/', methods=['POST'])
def post_comment():
    type = request.args.get('type')
    if type is not None:
        contents = request.form['contents']
        cursor = g.conn.execute(
            "SELECT c1.id "
            "FROM comments_post c1 "
            "GROUP BY c1.id "
            "HAVING c1.id>=all(SELECT c2.id FROM comments_post c2)"
        )
        id = 0
        results = cursor.fetchall()
        if len(results) > 0:
            result = results[0]
            id = int(result['id']) + 1
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().strftime("%H:%M:%S")

        try:
            g.conn.execute(
                "INSERT INTO comments_post VALUES(%s, %s, %s, %s, %s)",
                id,
                today,
                now,
                contents,
                session['user']['email']
            )
        except Exception as e:
            print(e)

        if type == "games":
            name1 = request.args.get('n1')
            location1 = request.args.get('l1')
            name2 = request.args.get('n2')
            location2 = request.args.get('l2')
            date = request.args.get('date')
            time = request.args.get('time')
            try:
                g.conn.execute(
                    "INSERT INTO game_comment_appears_on "
                    "VALUES(%s, %s, %s, %s, %s, %s, %s)",
                    id,
                    date,
                    time,
                    name1,
                    name2,
                    location1,
                    location2
                )
            except Exception as e:
                print(e)
        if type == "players":
            pid = request.args.get('pid')
            try:
                g.conn.execute(
                    "INSERT INTO player_comment_appears_on "
                    "VALUES(%s, %s)",
                    id,
                    pid
                )
            except Exception as e:
                print(e)
        if type == "teams":
            name = request.args.get('name')
            loc = request.args.get('loc')
            try:
                g.conn.execute(
                    "INSERT INTO team_comment_appears_on "
                    "VALUES(%s, %s, %s)",
                    id,
                    name,
                    loc
                )
            except Exception as e:
                print(e)
        return myRedirect(request)
    else:
        return redirect('/')
        pass


@app.route('/search/', methods=['POST'])
def search():
    query = request.form['query']
    like_query = '%' + query.lower() + '%'
    cursor = g.conn.execute(
        "SELECT DISTINCT p.id, p.name, p.sport, "
        "(SELECT COUNT(*) "
        "FROM player_comment_appears_on pc "
        "WHERE p.id=pc.player_id) AS count "
        "FROM players p, teammem_of_plays_for t "
        "WHERE LOWER(p.name) LIKE %s OR "
        "LOWER(p.sport) LIKE %s OR "
        "(t.id = p.id AND "
        "(LOWER(t.name) LIKE %s OR "
        "LOWER(t.location) LIKE %s))",
        like_query,
        like_query,
        like_query,
        like_query
    )
    results = []
    for result in cursor:
        results.append({
            "type": "player",
            "name": result["name"],
            "sport": result["sport"],
            "id": result["id"],
            "count": int(result["count"])
        })
    cursor.close()

    cursor = g.conn.execute(
        "SELECT DISTINCT t.name, t.location, t.sport, "
        "(SELECT COUNT(*) "
        "FROM team_comment_appears_on tc "
        "WHERE t.name=tc.name AND "
        "t.location=tc.location) AS count "
        "FROM teams t, teammem_of_plays_for tm, players p "
        "WHERE LOWER(t.name) LIKE %s OR "
        "LOWER(t.location) LIKE %s OR "
        "LOWER(t.sport) LIKE %s OR "
        "(t.name=tm.name AND "
        "t.location=tm.location AND "
        "p.id=tm.id AND "
        "(LOWER(p.name) LIKE %s))",
        like_query,
        like_query,
        like_query,
        like_query
    )
    for result in cursor:
        results.append({
            "type": "team",
            "name": result["name"],
            "location": result["location"],
            "sport": result["sport"],
            "count": int(result["count"])
        })
    cursor.close()

    cursor = g.conn.execute(
        "SELECT DISTINCT g.name1, g.location1, g.name2, g.location2, g.date, g.time, g.sport, "
        "(SELECT COUNT(*) "
        "FROM game_comment_appears_on gc "
        "WHERE gc.name1=g.name1 AND "
        "gc.location1=g.location1 AND "
        "gc.name2=g.name2 AND "
        "gc.location2=g.location2 AND "
        "gc.date=g.date AND "
        "gc.time=g.time) AS count "
        "FROM game_in g, teammem_of_plays_for t, players p "
        "WHERE LOWER(g.name1) LIKE %s OR "
        "LOWER(g.location1) LIKE %s OR "
        "LOWER(g.name2) LIKE %s OR "
        "LOWER(g.location2) LIKE %s OR "
        "LOWER(g.sport) LIKE %s OR "
        "(g.name1=t.name AND "
        "g.location1=t.location AND "
        "t.id=p.id AND "
        "t.since<g.date AND "
        "t.until>g.date AND "
        "(LOWER(p.name) LIKE %s)) OR "
        "(g.name2=t.name AND "
        "g.location2=t.location AND "
        "t.id=p.id AND "
        "t.since<g.date AND "
        "t.until>g.date AND "
        "(LOWER(p.name) LIKE %s))",
        like_query,
        like_query,
        like_query,
        like_query,
        like_query,
        like_query,
        like_query
    )
    for result in cursor:
        results.append({
            "type": "game",
            "name1": result["name1"],
            "location1": result["location1"],
            "name2": result["name2"],
            "location2": result["location2"],
            "date": result["date"],
            "time": result["time"],
            "sport": result["sport"],
            "count": int(result["count"])
        })
    cursor.close()

    results.sort(key=sortResults, reverse=True)

    context = dict(results=results)

    return render_template("search.html", **context)


def sortResults(val):
    return val['count']

#####################################################################


@app.route('/<string:sport>/games/', methods=['GET'])
def games(sport):
    if 'user' not in session:
        return redirect('/')
    sport = sport.lower().capitalize()
    name1 = request.args.get('n1')
    location1 = request.args.get('l1')
    name2 = request.args.get('n2')
    location2 = request.args.get('l2')
    date = request.args.get('date')
    time = request.args.get('time')
    if(
        name1 is None and
        location1 is None and
        name2 is None and
        location2 is None and
        date is None and
        time is None
    ):
        return all_games(sport)
    elif(
        name1 is None or
        location1 is None or
        name2 is None or
        location2 is None or
        date is None or
        time is None
    ):
        ##################################################################################
        # Invalid args
        return redirect('/')
    else:
        return specific_game(sport, name1, location1, name2, location2, date, time)


def all_games(sport):
    if 'user' not in session:
        return redirect('/')
    cursor = g.conn.execute(
        "SELECT * FROM game_in "
        "WHERE sport=%s "
        "ORDER BY date DESC",
        sport
    )
    games = []
    for result in cursor:
        won = True
        if result['winner_name'] is None:
            won = False
        games.append({
            'name1': result['name1'],
            'location1': result['location1'],
            'name2': result['name2'],
            'location2': result['location2'],
            'winner_name': result['winner_name'],
            'winner_location': result['winner_location'],
            'date': result['date'],
            'time': result['time'],
            'sport': result['sport'],
            'won': won
        })
    cursor.close()

    context = dict(sport=sport, games=games)

    return render_template("games.html", **context)


def specific_game(sport, name1, location1, name2, location2, date, time):
    cursor = g.conn.execute(
        "SELECT * FROM game_in "
        "WHERE "
        "sport=%s AND "
        "name1=%s AND "
        "location1=%s AND "
        "name2=%s AND "
        "location2=%s AND "
        "date=%s AND "
        "time=%s",
        sport,
        name1,
        location1,
        name2,
        location2,
        date,
        time
    )
    results = cursor.fetchall()
    if len(results) == 0:
        print("Game not found")
        return redirect('/')
    result = results[0]
    game = {
        'name1': result['name1'],
        'location1': result['location1'],
        'name2': result['name2'],
        'location2': result['location2'],
        'winner_name': result['winner_name'],
        'winner_location': result['winner_location'],
        'date': result['date'],
        'time': result['time'],
        'sport': result['sport']
    }
    cursor.close()

    # Players from team 1
    cursor = g.conn.execute(
        "SELECT p.id, p.name, tm.number "
        "FROM players p, teammem_of_plays_for tm "
        "WHERE tm.name=%s AND "
        "tm.location=%s AND "
        "tm.since<%s AND "
        "tm.until>%s AND "
        "tm.id=p.id",
        name1,
        location1,
        date,
        date
    )
    players1 = []
    for result in cursor:
        players1.append({
            'id': result['id'],
            'name': result['name'],
            'number': result['number'],
        })
    cursor.close()

    # Players from team 2
    cursor = g.conn.execute(
        "SELECT p.id, p.name, tm.number "
        "FROM players p, teammem_of_plays_for tm "
        "WHERE tm.name=%s AND "
        "tm.location=%s AND "
        "tm.since<%s AND "
        "tm.until>%s AND "
        "tm.id=p.id",
        name2,
        location2,
        date,
        date
    )
    players2 = []
    for result in cursor:
        players2.append({
            'id': result['id'],
            'name': result['name'],
            'number': result['number'],
        })
    cursor.close()

    cursor = g.conn.execute(
        "SELECT c.id, c.date, c.time, c.contents, c.email "
        "FROM game_comment_appears_on g, comments_post c "
        "WHERE g.name1=%s AND "
        "g.location1=%s AND "
        "g.name2=%s AND "
        "g.location2=%s AND "
        "g.date=%s AND "
        "g.time=%s AND "
        "g.id=c.id",
        name1,
        location1,
        name2,
        location2,
        date,
        time
    )
    comments = []
    for result in cursor:
        mine = False
        if result['email'] == session['user']['email']:
            mine = True
        comments.append({
            'id': result['id'],
            'date': result['date'],
            'time': result['time'],
            'contents': result['contents'],
            'email': result['email'],
            'likes': [],
            'mine': mine,
            'liked': False
        })
    cursor.close()

    for comment in comments:
        cursor = g.conn.execute(
            "SELECT email "
            "FROM likes "
            "WHERE id=%s",
            comment['id']
        )
        for result in cursor:
            if result['email'] == session['user']['email']:
                comment['liked'] = True
            comment['likes'].append(result['email'])
        cursor.close()

    context = dict(
        sport=sport,
        game=game,
        players1=players1,
        players2=players2,
        comments=comments
    )

    return render_template("game.html", **context)

#########################################################################


@app.route('/<sport>/players/', methods=['GET'])
def players(sport):
    if 'user' not in session:
        return redirect('/')
    sport = sport.lower().capitalize()
    id = request.args.get('id')
    if id is None:
        return all_players(sport)
    else:
        return specific_player(sport, id)


def all_players(sport):
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

    context = dict(sport=sport, players=players)

    return render_template("players.html", **context)


def specific_player(sport, id):
    cursor = g.conn.execute(
        "SELECT * FROM players "
        "WHERE sport=%s AND id=%s",
        sport,
        id
    )
    results = cursor.fetchall()
    if len(results) == 0:
        print("Player not found")
        return redirect('/')
    result = results[0]
    player = {
        'id': result['id'],
        'name': result['name'],
        'dob': result['dob'],
        'height': result['height'],
        'weight': result['weight'],
        'teams': [],
        'games': []
    }
    cursor.close()

    cursor = g.conn.execute(
        "SELECT * "
        "FROM teammem_of_plays_for "
        "WHERE id=%s",
        id
    )
    for result in cursor:
        player['teams'].append({
            'name': result['name'],
            'location': result['location'],
            'number': result['number'],
            'since': result['since'],
            'until': result['until']
        })
    cursor.close()

    cursor = g.conn.execute(
        "SELECT t.name, t.location, g.name1, g.location1, g.name2, "
        "g.location2, g.date, g.time, g.winner_name, g.winner_location "
        "FROM teammem_of_plays_for t, game_in g "
        "WHERE t.id=%s AND "
        "((t.name=g.name1 AND t.location=g.location1) OR "
        "(t.name=g.name2 AND t.location=g.location2)) AND "
        "t.since<g.date AND "
        "t.until>g.date",
        id
    )
    for result in cursor:
        won = False
        if (
            result['name'] == result['winner_name'] and
            result['location'] == result['winner_location']
        ):
            won = True
        player['games'].append({
            'name1': result['name1'],
            'location1': result['location1'],
            'name2': result['name2'],
            'location2': result['location2'],
            'date': result['date'],
            'time': result['time'],
            'won': won
        })
    cursor.close()

    cursor = g.conn.execute(
        "SELECT c.id, c.date, c.time, c.contents, c.email "
        "FROM player_comment_appears_on p, comments_post c "
        "WHERE p.player_id=%s AND p.comment_id=c.id",
        id
    )
    comments = []
    for result in cursor:
        mine = False
        if result['email'] == session['user']['email']:
            mine = True
        comments.append({
            'id': result['id'],
            'date': result['date'],
            'time': result['time'],
            'contents': result['contents'],
            'email': result['email'],
            'likes': [],
            'mine': mine,
            'liked': False
        })
    cursor.close()

    for comment in comments:
        cursor = g.conn.execute(
            "SELECT email "
            "FROM likes "
            "WHERE id=%s",
            comment['id']
        )
        for result in cursor:
            if result['email'] == session['user']['email']:
                comment['liked'] = True
            comment['likes'].append(result['email'])
        cursor.close()

    context = dict(sport=sport, player=player, comments=comments)

    return render_template("player.html", **context)

################################################################################


@app.route('/<sport>/teams/', methods=['GET'])
def teams(sport):
    print(session)
    if 'user' not in session:
        return redirect('/')
    sport = sport.lower().capitalize()
    name = request.args.get('name')
    loc = request.args.get('loc')
    if name is None and loc is None:
        return all_teams(sport)
    elif name is None or loc is None:
        return redirect('/')
    else:
        return specific_team(sport, name, loc)


def all_teams(sport):
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

    context = dict(sport=sport, teams=teams)

    return render_template("teams.html", **context)


def specific_team(sport, name, loc):
    cursor = g.conn.execute(
        "SELECT * FROM teams "
        "WHERE sport=%s AND "
        "name=%s AND "
        "location=%s",
        sport,
        name,
        loc
    )
    results = cursor.fetchall()
    if len(results) == 0:
        print("Team not found")
        return redirect('/')
    result = results[0]
    team = {
        'name': result['name'],
        'location': result['location'],
        'rank': result['rank'],
        'players': [],
        'games': []
    }
    cursor.close()

    cursor = g.conn.execute(
        "SELECT p.id, p.name, t.number, t.since, t.until "
        "FROM players p, teammem_of_plays_for t "
        "WHERE t.name=%s AND "
        "t.location=%s AND "
        "p.id=t.id "
        "ORDER BY t.until",
        name,
        loc
    )
    for result in cursor:
        team['players'].append({
            'id': result['id'],
            'name': result['name'],
            'number': result['number'],
            'since': result['since'],
            'until': result['until']
        })
    cursor.close()

    cursor = g.conn.execute(
        "SELECT winner_name, winner_location, name1, location1, name2, location2, date, time "
        "FROM game_in "
        "WHERE (name1=%s AND location1=%s) OR "
        "(name2=%s AND location2=%s) "
        "ORDER BY date DESC",
        name,
        loc,
        name,
        loc
    )
    for result in cursor:
        team['games'].append({
            'winner_name': result['winner_name'],
            'winner_location': result['winner_location'],
            'name1': result['name1'],
            'location1': result['location1'],
            'name2': result['name2'],
            'location2': result['location2'],
            'date': result['date'],
            'time': result['time']
        })
    cursor.close()

    cursor = g.conn.execute(
        "SELECT c.id, c.date, c.time, c.contents, c.email "
        "FROM team_comment_appears_on t, comments_post c "
        "WHERE t.name=%s AND t.location=%s AND t.id=c.id",
        name,
        loc
    )
    comments = []
    for result in cursor:
        mine = False
        if result['email'] == session['user']['email']:
            mine = True
        comments.append({
            'id': result['id'],
            'date': result['date'],
            'time': result['time'],
            'contents': result['contents'],
            'email': result['email'],
            'likes': [],
            'mine': mine,
            'liked': False
        })
    cursor.close()

    for comment in comments:
        cursor = g.conn.execute(
            "SELECT email "
            "FROM likes "
            "WHERE id=%s",
            comment['id']
        )
        for result in cursor:
            if result['email'] == session['user']['email']:
                comment['liked'] = True
            comment['likes'].append(result['email'])
        cursor.close()

    context = dict(sport=sport, team=team, comments=comments)

    return render_template("team.html", **context)


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
