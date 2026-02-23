import os
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 🔑 Supabase Veritabanı Bağlantı Ayarı
db_url = os.environ.get('DATABASE_URL')
# SQLAlchemy bazen 'postgres://' yerine 'postgresql://' ister, bu ufak kod onu otomatik düzeltir
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///local_gymbuu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 🗄️ VERİTABANI MODELLERİ
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

# Tabloları Otomatik Oluştur
with app.app_context():
    db.create_all()

# 🌐 ROTALAR
@app.route("/")
def index():
    return render_template("index.html")

# --- Antrenman API ---
@app.route("/api/entries", methods=["GET", "POST"])
def entries():
    if request.method == "GET":
        items = Entry.query.order_by(Entry.date.desc()).all()
        return jsonify([{'id': i.id, 'date': i.date, 'exercise': i.exercise, 'sets': i.sets, 'reps': i.reps, 'weight': i.weight} for i in items])
    data = request.json
    new_entry = Entry(date=data.get('date'), exercise=data.get('exercise'), sets=data.get('sets'), reps=data.get('reps'), weight=data.get('weight'))
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({"status": "ok"})

@app.route("/api/entries/<int:id>", methods=["DELETE"])
def delete_entry(id):
    item = Entry.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return jsonify({"status": "deleted"})

# --- Kilo Takibi API ---
@app.route("/api/weights", methods=["GET", "POST"])
def weights():
    if request.method == "GET":
        items = BodyWeight.query.order_by(BodyWeight.date.asc()).all()
        return jsonify([{'id': i.id, 'date': i.date, 'kg': i.kg} for i in items])
    data = request.json
    new_weight = BodyWeight(date=data.get('date'), kg=data.get('kg'))
    db.session.add(new_weight)
    db.session.commit()
    return jsonify({"status": "ok"})

@app.route("/api/weights/<int:id>", methods=["DELETE"])
def delete_weight(id):
    item = BodyWeight.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return jsonify({"status": "deleted"})

# --- Notlar API ---
@app.route("/api/notes", methods=["GET", "POST"])
def notes():
    if request.method == "GET":
        items = Note.query.order_by(Note.id.desc()).all()
        return jsonify([{'id': i.id, 'date': i.date, 'content': i.content} for i in items])
    data = request.json
    new_note = Note(date=data.get('date'), content=data.get('content'))
    db.session.add(new_note)
    db.session.commit()
    return jsonify({"status": "ok"})

@app.route("/api/notes/<int:id>", methods=["DELETE"])
def delete_note(id):
    item = Note.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return jsonify({"status": "deleted"})

if __name__ == "__main__":
    # Render'da çalışacağı için port ayarını Gunicorn yapacak, bu satır lokal test için
    app.run(debug=False)