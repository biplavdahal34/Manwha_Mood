
import bcrypt, time, hmac
from flask_login import login_manager, login_required, login_user, logout_user, current_user, LoginManager
from flask import render_template, flash, redirect, url_for, request, session
from manhwaapp import app, db
from manhwaapp.forms import RegisterForm, LoginForm, SearchForm, OTPForm
from manhwaapp.models import User, Manhwa, MYmanhwalist
from manhwaapp.misc import latest_list, popular_list, get_manhwa_byid, get_manhwa_byname, stats, chapter_all, get_page_id, otp_send, get_latest_popular

@app.route("/spage")
def startpage():
    return render_template("startpage.html")
@app.route("/", methods=['GET', 'POST'])
@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        session['otp'] = otp_send(form.email.data)
        session['otp_made_time'] = time.time()
        session['email'] = form.email.data
        session['username'] = form.username.data
        session['password'] = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return redirect(url_for('otp_filling_page'))
    return render_template("register.html", form = form)

@app.route("/fill_otp", methods=['POST','GET'])
def otp_filling_page():
    form = OTPForm()
    otp_expiry_time = 500
    email = session.get("email")
    otp_making_time = session.get('otp_made_time')
    otp = session.get('otp')
    if request.method == 'POST':
        if form.validate_on_submit(): 
            if (otp_making_time - time.time()) < otp_expiry_time:
                comapare = hmac.compare_digest(form.otp.data, otp)
                if comapare == True:
                    new_user = User(email = session.get("email"), username = session.get('username'), password = session.get('password') )
                    db.session.add(new_user)
                    db.session.commit()
                    login_user(new_user)
                    flash("Account Has Been Created!", 'success')
                    session.pop('email', None)
                    session.pop('username', None)
                    session.pop('password', None)
                    session.pop('otp', None)
                    return redirect(url_for('home'))
                else:
                  flash("Inccorect OTP", 'danger')
            else:
                flash('Sorry The OTP Time has Expired', 'danger')

    return render_template('otp_input_page.html', form = form, email = email)

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
        genree = [tag['attributes']['name']['en'] for tag in manhwa['attributes']['tags'] if tag['attributes']['group'] == 'genre'][:2]
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


    trending_titles = []
    genres_trending = []
    latest_popular = get_latest_popular(limit=10,days_back=7)
    for manhwa in latest_popular:
        alttitles =  manhwa['attributes']['altTitles']
        genre_trending= [tag['attributes']['name']['en'] for tag in manhwa['attributes']['tags'] if tag['attributes']['group'] == 'genre'][:2]
        genres_trending.append(genre_trending)
        if alttitles:
            en_title_trending = next((title['en'] for title in alttitles if "en" in title),None)
            if en_title_trending:
               trending_titles.append(en_title_trending)
            else:
                trending_titles.append(next(iter(manhwa['attributes']['title'].values()),"Title Not Availabe"))
            trending_cover_url = []
            for manga in latest_popular:
                manga_id_popular = manga["id"]
                trending_cover_rel = next((rel for rel in manga['relationships'] if rel['type'] == "cover_art"), None)
                if trending_cover_rel and "attributes" in trending_cover_rel:
                    filename = trending_cover_rel['attributes']['fileName']
                    trending_cover_url.append(f'https://uploads.mangadex.org/covers/{manga_id_popular}/{filename}')

    return render_template('home.html', popular_titles = popular_manhwa_titles, latest_titles = latest_manhwa_titles, trending_titles = trending_titles, popular_manhwas = popular["response"], latest_manhwas = latest['response'], trending_manhwas = latest_popular, api_ok= api_ok,
                            searched = bool(popular), popular_cover_url = popular_cover_url, latest_cover_url = latest_cover_url, trending_cover_url = trending_cover_url, genre_popular = genre_popular, genre_latest= genre_latest, genre_trending = genre_trending)

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
        chapter_info = chapter_all(manhwa_id)
        chapter_resp = chapter_info['response']
        chap_id = []
        for chap in chapter_resp['data']:
            chap_id.append(chap['id'])
        genres_trending = []
        chap_list = chapter_info['chap_num']
        rate = stats(manhwa_id)
        rating = str(rate['rating']['average']) if rate else 'N/A'
        if rating != 'N/A':
            try:
                ratings = rating[:rating.index('.') +2]
            except ValueError:  
                ratings = 'N/A'
        if bool(manhwa['attributes']['description'].get("en")):
            description = manhwa['attributes']['description']['en']
            if "---" in description:
                try:
                    description,_ = manhwa['attributes']['description']['en'].split("---")
                except ValueError:
                    description = manhwa['attributes']['description']['en']
        else:
            description = "No Description Available"
        if cover_rel and "attributes" in cover_rel:
            filename = cover_rel['attributes']['fileName']
            cover_url = f'https://uploads.mangadex.org/covers/{manga_id}/{filename}'
        else:
            api_ok = True
        trending_titles = []
        latest_popular = get_latest_popular(limit=10,days_back=7)
        for manhwa in latest_popular:
            alttitles =  manhwa['attributes']['altTitles']
            genre_trending= [tag['attributes']['name']['en'] for tag in manhwa['attributes']['tags'] if tag['attributes']['group'] == 'genre'][:2]
            genres_trending.append(genre_trending)
            if alttitles:
                en_title_trending = next((title['en'] for title in alttitles if "en" in title),None)
                if en_title_trending:
                    trending_titles.append(en_title_trending)
                else:
                    trending_titles.append(next(iter(manhwa['attributes']['title'].values()),"Title Not Availabe"))
                trending_cover_url = []
                for manga in latest_popular:
                    manga_id_popular = manga["id"]
                    trending_cover_rel = next((rel for rel in manga['relationships'] if rel['type'] == "cover_art"), None)
                    print("Cover relationship:", trending_cover_rel)
                    if trending_cover_rel and "attributes" in trending_cover_rel:
                        filename = trending_cover_rel['attributes']['fileName']
                        trending_cover_url.append(f'https://uploads.mangadex.org/covers/{manga_id_popular}/{filename}')
                print(trending_cover_url)
    else:
        api_ok = False
        manhwa = []
        title = []
        description = []
        cover_url = []
        manga_id = []
        author = []
        status = []
        ratings = 'N/A'
        genre = []
        author_name = "N/A"
        chapters = 'N/A'
        release_date = 'N/A'
        chap_list = []
        chap_id = []
        id = []
        trending_titles = []
        trending_cover_url = []
        latest_popular = []
        genre_trending = []
        

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
                            release_date = release_date,
                            rating = ratings,
                            chap_list = chap_list,
                            chap_id = chap_id,
                            id =manga_id, trending_titles = trending_titles, trending_manhwas = latest_popular, trending_cover_url = trending_cover_url, genre_trending = genre_trending
                            )


@app.route("/chapter/<chapter_id>")
def chapter_read(chapter_id):
    page_data = get_page_id(chapter_id)
    chap_hash = page_data['chap_hash']
    host = page_data['host']
    page_urls = page_data['data']
    manhwa_title = request.args.get('manhwa_title')
    chapter_num = request.args.get('chapter_num')
    manhwa_id = request.args.get('id')
    return render_template("chapter_read.html", id=manhwa_id, title = manhwa_title, chapter_num = chapter_num, host = host, page_urls = page_urls, chap_hash =chap_hash)

@app.route("/api/refresh-host/<chapter_id>")
def refresh_host(chapter_id):
    page_data = get_page_id(chapter_id)
    return {"host": page_data["host"], "chap_hash": page_data["chap_hash"]}