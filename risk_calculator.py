# ===================================================================
# حاسبة مؤشر الخطر
# ===================================================================

class RiskCalculator:
    WEIGHT_FOOD = 0.5
    WEIGHT_RAIN = 0.3
    WEIGHT_AID = 0.2
    
    @staticmethod
    def calculate(village):
        population = village['population']
        food_stock = village['food_stock_kg']
        days_since_rain = village['days_since_rain']
        last_aid = village['last_aid_date']
        
        food_per_person = food_stock / population if population > 0 else 0
        food_score = max(0, 100 - (food_per_person * 20))
        food_score = min(food_score, 100)
        rain_score = min(days_since_rain * 2, 100)
        
        if last_aid is None:
            aid_score = 100
        else:
            from datetime import datetime
            try:
                last_date = datetime.fromisoformat(last_aid)
                days_since_aid = (datetime.now() - last_date).days
                aid_score = min(days_since_aid * 1.5, 100)
            except:
                aid_score = 50
        
        risk_score = (
            food_score * RiskCalculator.WEIGHT_FOOD +
            rain_score * RiskCalculator.WEIGHT_RAIN +
            aid_score * RiskCalculator.WEIGHT_AID
        )
        
        if risk_score >= 75:
            level = "طوارئ"
            color = "red"
        elif risk_score >= 50:
            level = "أزمة"
            color = "orange"
        elif risk_score >= 25:
            level = "ضغط"
            color = "yellow"
        else:
            level = "آمن"
            color = "green"
        
        return {
            "risk_score": round(risk_score, 1),
            "food_score": round(food_score, 1),
            "rain_score": round(rain_score, 1),
            "aid_score": round(aid_score, 1),
            "food_per_person": round(food_per_person, 2),
            "level": level,
            "color": color
        }
