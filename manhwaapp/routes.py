import bcrypt   
from flask_login import login_manager, login_required, login_user, logout_user, current_user, LoginManager
from flask import render_template, flash, redirect, url_for, request
from manhwaapp import app, db
from manhwaapp.forms import RegisterForm, LoginForm, SearchForm
from manhwaapp.models import User, Manhwa, MYmanhwalist
from manhwaapp.misc import latest_list, popular_list, get_manhwa_byid, get_manhwa_byname


@app.route("/spage")
def startpage():
    return render_template("startpage.html")

@app.route("/register", methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(email = form.email.data, username = form.username.data, password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt()))
        db.session.add(new_user)
        db.session.commit()
        flash("Account Has Been Created!", 'success')
        print('success')
        return redirect(url_for('login'))   
    return render_template("register.html", form = form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter_by(username=username).first()
        if user:
            db_password = user.password if isinstance(user.password, bytes) else user.password.encode('utf-8')
            form_pw = form.password.data.encode('utf-8') 
            if bcrypt.checkpw(form_pw, db_password):
                login_user(user)
                flash("Login Successful", "success")
                return redirect(url_for('home'))

    return render_template('login.html', form=form)


@app.route("/")
@app.route("/home")
def home():
    latest_manhwa_titles = []
    latest = latest_list()
    genre_latest = []
    genre_popular =[]
    for manhwa in latest['response']:
        alttitles =  manhwa['attributes']['altTitles']
        if alttitles:
            en_title = next(iter((title['en'] for title in alttitles if "en" in title)),None)
            if en_title:
               latest_manhwa_titles.append(en_title)
            else:
                latest_manhwa_titles.append(next(iter(manhwa['attributes']['title'].values()),"Title Not Availabe"))
            latest_cover_url = []
            api_ok = latest['api_ok']
            for manga in latest["response"]:
                if (tag['attributes']['name'].get('en', '') for tag in manga['attributes']['tags']):
                    genree = [tag['attributes']['name']['en'] for tag in manga['attributes']['tags'] if tag['attributes']['group'] == 'genre'][:2]
                    genre_latest.append(genree)
                manga_id = manga["id"]
                latest_cover_rel = next((rel for rel in manga['relationships'] if rel['type'] == "cover_art"),None)
                if latest_cover_rel and "attributes" in latest_cover_rel:
                    filename = latest_cover_rel['attributes']['fileName']
                    latest_cover_url.append(f'https://uploads.mangadex.org/covers/{manga_id}/{filename}')
    popular_manhwa_titles = []
    popular = popular_list()
    for manhwa in popular['response']:
        alttitles =  manhwa['attributes']['altTitles']
        if (tag['attributes']['name'].get('en', '') for tag in manga['attributes']['tags']):
            genree = [tag['attributes']['name']['en'] for tag in manga['attributes']['tags'] if tag['attributes']['group'] == 'genre'][:2]
            genre_popular.append(genree)
        if alttitles:
            en_title = next((title['en'] for title in alttitles if "en" in title),None)
            if en_title:
               popular_manhwa_titles.append(en_title)
            else:
                popular_manhwa_titles.append(next(iter(manhwa['attributes']['title'].values()),"Title Not Availabe"))
            popular_cover_url = []
            api_ok = popular['api_ok']
            for manga in popular["response"]:
                manga_id = manga["id"]
                popular_cover_rel = next((rel for rel in manga['relationships'] if rel['type'] == "cover_art"),None)
                if popular_cover_rel and "attributes" in popular_cover_rel:
                    filename = popular_cover_rel['attributes']['fileName']
                    popular_cover_url.append(f'https://uploads.mangadex.org/covers/{manga_id}/{filename}')
    return render_template('home.html', popular_titles = popular_manhwa_titles, latest_titles = latest_manhwa_titles, popular_manhwas = popular["response"], latest_manhwas = latest['response'], api_ok= api_ok,
                            searched = bool(popular), popular_cover_url = popular_cover_url, latest_cover_url = latest_cover_url, genre_popular = genre_popular, genre_latest= genre_latest)

@app.route("/search")
def search():

    form = SearchForm()
    manhwa_name = request.args.get("q", "") 
    search_titles = []
    if manhwa_name:
        data = get_manhwa_byname(manhwa_name)
        genre = []
        for manhwa in data['response']:
            if (tag['attributes']['name'].get('en', '') for tag in manhwa['attributes']['tags']):
                genree = [tag['attributes']['name']['en'] for tag in manhwa['attributes']['tags'] if tag['attributes']['group'] == 'genre'][:2]
                genre.append(genree)
            alttitles =  manhwa['attributes']['altTitles']
            en_title = next((title['en'] for title in alttitles if "en" in title),None)
            if en_title:
               search_titles.append(en_title)
            else:
                search_titles.append(next(iter(manhwa['attributes']['title'].values()),"Title Not Availabe"))
    cover_url = []
    api_ok = data['api_ok']
    for manga in data["response"]:
        manga_id = manga["id"]
        cover_rel = next((rel for rel in manga['relationships'] if rel['type'] == "cover_art"),None)
        if cover_rel and "attributes" in cover_rel:
            filename = cover_rel['attributes']['fileName']
            cover_url.append(f'https://uploads.mangadex.org/covers/{manga_id}/{filename}')
    else:
        api_ok = True


    return render_template("search.html", form = form, manhwas = data["response"], api_ok= api_ok, searched = bool(manhwa_name), cover_url = cover_url, titles = search_titles, genres=genre)

@app.route("/details/<manhwa_id>")
def details(manhwa_id):

    data = get_manhwa_byid(manhwa_id)
    print(data)
    if data['api_ok']:
        manhwa = data['response']
        genre = [ tag['attributes']['name']['en'] for tag in manhwa['attributes']['tags'] if tag['attributes']['group'] == 'genre'][:3]
        alttitles =  manhwa['attributes']['altTitles']
        en_title = next((title['en'] for title in alttitles if "en" in title),None)
        if en_title:
            title = en_title
        else:
            title = next(iter(manhwa['attributes']['title'].values()), "Title Not Available")
        cover_url = []
        api_ok = data['api_ok']
        manga_id = manhwa["id"]
        cover_rel = next((rel for rel in manhwa['relationships'] if rel['type'] == "cover_art"),None)
        author = next(iter(author['attributes']['name'] for author in manhwa['relationships'] if author['type'] == 'artist'),None)
        author_name = author if author else "Author Not Found"
        status = manhwa['attributes'].get('status') or 'N/A'
        chapters = manhwa['attributes'].get('lastChapter') or 'N/A'
        release_date = manhwa['attributes'].get('year') or 'N/A'
        if bool(manhwa['attributes']['description'].get("en")):
            description = manhwa['attributes']['description']['en']
            if "---" in description:
                description,_ = manhwa['attributes']['description']['en'].split("---")
        else:
            description = "No Description Available"
        if cover_rel and "attributes" in cover_rel:
            filename = cover_rel['attributes']['fileName']
            cover_url = f'https://uploads.mangadex.org/covers/{manga_id}/{filename}'
        else:
            api_ok = True
    else:
        api_ok = False
        manhwa = []
        title = []
        description = []
        cover_url = []
        manga_id = []
        author = []
        status = []

    return render_template("anime-details.html",
                            manhwa = manhwa, 
                            cover_url = cover_url, 
                            manga_id=manga_id, 
                            api_ok=api_ok, 
                            title = title,
                            description = description, 
                            genres = genre,
                            author_name = author_name,
                            status = status,
                            chapters = chapters,
                            release_date = release_date
                            )
