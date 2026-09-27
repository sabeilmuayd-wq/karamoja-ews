# ===================================================================
# نظام الإنذار المبكر لكاراموجا - التطبيق الرئيسي
# ===================================================================
from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import Database
from risk_calculator import RiskCalculator
from distributor import AidDistributor

app = Flask(__name__)
db = Database('karamoja.db')
distributor = AidDistributor(db)

def seed_data():
    if not db.get_all_villages():
        db.add_village("لوكورو", "كاراموجا", 5000, 2000, 15)
        db.add_village("مويالي", "كاراموجا", 3500, 800, 25)
        db.add_village("كوتيدو", "كاراموجا", 7000, 5000, 5)
        db.add_village("نامالو", "كاراموجا", 2000, 200, 30)
        print("✅ تم إضافة بيانات تجريبية")

@app.route('/')
def index():
    villages = db.get_all_villages()
    village_data = []
    for v in villages:
        village_dict = {
            'id': v[0], 'name': v[1], 'district': v[2],
            'population': v[3], 'food_stock_kg': v[4],
            'days_since_rain': v[5], 'last_aid_date': v[6]
        }
        risk = RiskCalculator.calculate(village_dict)
        village_dict['risk'] = risk
        village_data.append(village_dict)
    village_data.sort(key=lambda x: x['risk']['risk_score'], reverse=True)
    return render_template('index.html', villages=village_data)

@app.route('/add_village', methods=['GET', 'POST'])
def add_village():
    if request.method == 'POST':
        name = request.form.get('name')
        district = request.form.get('district')
        population = int(request.form.get('population', 0))
        food_stock = float(request.form.get('food_stock', 0))
        days_rain = int(request.form.get('days_rain', 0))
        db.add_village(name, district, population, food_stock, days_rain)
        return redirect(url_for('index'))
    return render_template('add_village.html')

@app.route('/update_village/<int:village_id>', methods=['POST'])
def update_village(village_id):
    food_stock = request.form.get('food_stock')
    days_rain = request.form.get('days_rain')
    db.update_village(village_id,
                     food_stock_kg=float(food_stock) if food_stock else None,
                     days_since_rain=int(days_rain) if days_rain else None)
    return redirect(url_for('index'))

@app.route('/distribute', methods=['GET', 'POST'])
def distribute():
    if request.method == 'POST':
        total_aid = float(request.form.get('total_aid', 0))
        min_per_person = float(request.form.get('min_per_person', 0.5))
        result = distributor.distribute(total_aid, min_per_person)
        if not result['success']:
            return render_template('distribute.html', error=result.get('error'))
        return render_template('distribute.html', result=result, villages=db.get_all_villages())
    return render_template('distribute.html', villages=db.get_all_villages())

@app.route('/distributions')
def distributions():
    return render_template('distributions.html', distributions=db.get_distributions())

if __name__ == '__main__':
    seed_data()
    app.run(host='0.0.0.0', port=5000, debug=True)
