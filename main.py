import os

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random as r

API_KEY = os.environ.get('API_KEY')

app = Flask(__name__)


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")
    

@app.route("/random")
def random():
    cafes = db.session.query(Cafe).all()
    random_cafe = r.choice(cafes)
    return jsonify(
        id=random_cafe.id,
        name=random_cafe.name,
        map_url=random_cafe.map_url,
        img_url=random_cafe.img_url,
        location=random_cafe.location,
        has_sockets=random_cafe.has_sockets,
        has_toilet=random_cafe.has_toilet,
        has_wifi=random_cafe.has_wifi,
        can_take_calls=random_cafe.can_take_calls,
        seats=random_cafe.seats,
        coffee_price=random_cafe.coffee_price
    )


@app.route("/all")
def all():
    cafes = db.session.query(Cafe).all()
    return jsonify(
        cafes=[cafe.to_dict() for cafe in cafes]
    )


@app.route("/search")
def search():
    loc = request.args.get('loc')
    cafes = db.session.execute(db.select(Cafe).where(Cafe.location == loc)).scalars().all()
    if cafes:
        return jsonify(
            cafes=[cafe.to_dict() for cafe in cafes]
        )
    else:
        return jsonify(
            error={"Not Found": "Sorry, we don't have a cafe at that location."}
        )


@app.route('/add', methods=['POST'])
def add():
    new_cafe = Cafe(
        name=request.form['name'],
        map_url=request.form['map_url'],
        img_url=request.form['img_url'],
        location=request.form['location'],
        seats=request.form['seats'],
        has_toilet=(not not request.form['has_toilet']),
        has_wifi=(not not request.form['has_wifi']),
        has_sockets=(not not request.form['has_sockets']),
        can_take_calls=(not not request.form['can_take_calls']),
        coffee_price=request.form['coffee_price']
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(
        response={"Success": "Successfully added the new cafe"}
    )


# HTTP PATCH - Update Record
@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
    new_price = request.args.get('new_price')
    db.session.commit()

    if cafe:
        cafe.coffee_price = new_price
        return jsonify(
            response={"Success": "Successfully updated the price."}
        )

    return jsonify(
        error={"Not Found": "Sorry a cafe with that id was not found in the database."}
    ), 404


# HTTP DELETE - Delete Record
@app.route('/report-closed/<int:cafe_id>', methods=['DELETE'])
def report_closed(cafe_id):
    cafe = db.session.query(Cafe).get(cafe_id)
    key = request.args.get('api-key')

    if not key == API_KEY:
        return jsonify(error="Sorry, that's not allowed. Make sure you have the correct api_key."), 403
    elif cafe:
        db.session.delete(cafe)
        db.session.commit()
        return jsonify(response={"Success": "Successfully deleted the cafe from the database."}), 200

    return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


if __name__ == '__main__':
    app.run(debug=True)
