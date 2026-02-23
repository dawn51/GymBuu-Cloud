import os
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 🔑 GÜVENLİK: Kendi şifreni buraya yaz kanka
ADMIN_PASSWORD = "safak_gym_123"

# 🗄️ Veritabanı Ayarları (Supabase Pooler için uyumlu)
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///local_gymbuu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Veritabanı Modelleri
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    exercise = db.Column(db.String(100))
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    weight = db.Column(db.Float)

class BodyWeight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    kg = db.Column(db.Float)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    content = db.Column(db.Text)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

# --- API Rotaları (Herkes Görüntüleyebilir ve Not Ekleyebilir) ---
@app.route("/api/entries", methods=["GET", "POST"])
def entries():
    if request.method == "GET":
        items = Entry.query.order_by(Entry.date.desc()).all()
        return jsonify([{'id': i.id, 'date': i.date, 'exercise': i.exercise, 'sets': i.sets, 'reps': i.reps, 'weight': i.weight} for i in items])
    
    # Antrenman ekleme (Sadece şifre ile)
    user_pass = request.headers.get('Authorization')
    if user_pass != ADMIN_PASSWORD:
        return jsonify({"status": "unauthorized"}), 403
        
    data = request.json
    new_entry = Entry(date=data['date'], exercise=data['exercise'], sets=data['sets'], reps=data['reps'], weight=data['weight'])
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({"status": "ok"})

@app.route("/api/weights", methods=["GET", "POST"])
def weights():
    if request.method == "GET":
        items = BodyWeight.query.order_by(BodyWeight.date.asc()).all()
        return jsonify([{'id': i.id, 'date': i.date, 'kg': i.kg} for i in items])
    
    # Kilo ekleme (Sadece şifre ile)
    user_pass = request.headers.get('Authorization')
    if user_pass != ADMIN_PASSWORD:
        return jsonify({"status": "unauthorized"}), 403

    data = request.json
    new_weight = BodyWeight(date=data['date'], kg=data['kg'])
    db.session.add(new_weight)
    db.session.commit()
    return jsonify({"status": "ok"})

@app.route("/api/notes", methods=["GET", "POST"])
def notes():
    if request.method == "GET":
        items = Note.query.order_by(Note.id.desc()).all()
        return jsonify([{'id': i.id, 'date': i.date, 'content': i.content} for i in items])
    
    # NOT EKLEMEK HERKESE AÇIK
    data = request.json
    new_note = Note(date=data['date'], content=data['content'])
    db.session.add(new_note)
    db.session.commit()
    return jsonify({"status": "ok"})

# --- SİLME İŞLEMLERİ (Sadece Şifre ile) ---
@app.route("/api/delete/<string:type>/<int:id>", methods=["DELETE"])
def delete_item(type, id):
    user_pass = request.headers.get('Authorization')
    if user_pass != ADMIN_PASSWORD:
        return jsonify({"status": "unauthorized"}), 403

    item = None
    if type == "entry": item = Entry.query.get(id)
    elif type == "weight": item = BodyWeight.query.get(id)
    elif type == "note": item = Note.query.get(id)

    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"status": "deleted"})
    return jsonify({"status": "not_found"}), 404

if __name__ == "__main__":
    app.run()
