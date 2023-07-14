from flask import *
from sqlite3 import *
from datetime import timedelta
import pickle

app = Flask(__name__)
app.secret_key = "sanskrutii"

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)


@app.route("/",methods=["GET","POST"])
def home():
	if "un" in session:
		if request.method == "POST":
			f=open("cp.model","rb")
			model = pickle.load(f)
			f.close()
			ni = request.form["ni"]
			phos = request.form["phos"]
			potas = request.form["potas"]
			temp = request.form["temp"]
			humi = request.form["humi"]
			ph = float(request.form["ph"])
			rf = request.form["rf"]
			d = [[ni,phos,potas,temp,humi,ph,rf]]
			result = model.predict(d)
			msg = "Crop suitable for these conditions is : " + str(result[0])
		
			return render_template("home.html" , m=msg)
		else:
			return render_template("home.html")
		
	else:
		return render_template("start.html")
	

@app.route("/login" , methods=["GET","POST"])
def login():
	if "un" in session:
		session.pop("un")
		return redirect(url_for("start"))
	if request.method == "POST":
		un = request.form["un"]
		pw = request.form["pw"]
		con = None
		try:
			con = connect("kc.db")
			sql = "select * from users where un = '%s' and pw = '%s'"
			cursor = con.cursor()
			cursor.execute(sql%(un,pw))
			data = cursor.fetchall()
			if len(data) == 0:
				return render_template("login.html", m="Invalid username or password")
			else:
				session["un"] = un
				return redirect(url_for("home"))
		except Exception as e:
			con.rollback()
			msg = "Issue : " + str(e)
			return render_template("signup.html", m=msg)
		finally:
			if con is not None:
				con.close()
	else:
		return render_template("login.html")

@app.route("/signup" ,methods=["GET","POST"])
def signup():
	if "un" in session:
		session.pop("un")
		return redirect(url_for("start"))	
	if request.method == "POST":
		un=request.form["un"]
		pw1=request.form["pw1"]
		pw2=request.form["pw2"]
		if pw1 == pw2:
			con = None
			try:
				con = connect("kc.db")
				sql = "insert into users values('%s' , '%s')"
				cursor = con.cursor()
				cursor.execute(sql % (un,pw1)) 
				con.commit()
	
				return redirect(url_for("login"))
			except IntegrityError :
				return render_template("signup.html", m="This username already exists")
			except Exception as e:
				con.rollback()
				msg = "Issue : " + str(e)
				return render_template("signup.html", m=msg)
			finally:
				if con is not None:
					con.close()
		else:
			return render_template("signup.html" , m = "passwords did not match")
	else:
		return render_template("signup.html")

@app.route("/changepass",methods=["GET","POST"])
def changepass():
	if "un" in session: 
		if request.method == "POST":
			un2=request.form["un"]
			pw1=request.form["pw1"]
			pw2=request.form["pw2"]
			if pw1 == pw2:
				con = None
				try:
					con = connect("kc.db")
					cursor = con.cursor()
					un1=session["un"]
					if un2 == un1:
						sql1 = "update users set pw = '%s' where un = '%s'"
						cursor.execute(sql1 % (pw1,un1))
						con.commit()
						session.pop("un")
						return redirect(url_for("login"))
												
					else:
						return render_template("changepass.html", m="Please enter your own username")
				except Exception as e:
					con.rollback()
					msg = "Issue : " + str(e)
					return render_template("changepass.html", m=msg)
				finally:
					if con is not None:
						con.close()
			else:
				return render_template("changepass.html" , m = "passwords did not match")
		else:
			return render_template("changepass.html")
	else:
		return render_template("start.html")

@app.route("/about")
def about():
	if "un" in session:
		return render_template("about.html")
	else:
		return render_template("signup.html")
@app.route("/logout")
def logout():
	session.pop("un")
	return redirect(url_for("login"))

@app.route("/start")
def start():
	return render_template("start.html")

@app.after_request
def after_request(response): 
	response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" 
	return response

if __name__ == "__main__":
	app.run(debug=True,use_reloader=True)	