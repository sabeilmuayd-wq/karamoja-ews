# ===================================================================
# موزع المساعدات الذكي
# ===================================================================
from risk_calculator import RiskCalculator

class AidDistributor:
    def __init__(self, database):
        self.db = database
    
    def distribute(self, total_aid_kg, min_per_person_kg=0.5):
        villages = self.db.get_all_villages()
        
        if not villages:
            return {"success": False, "error": "لا توجد قرى مسجلة"}
        
        scored_villages = []
        for v in villages:
            village_dict = {
                'id': v[0], 'name': v[1], 'district': v[2],
                'population': v[3], 'food_stock_kg': v[4],
                'days_since_rain': v[5], 'last_aid_date': v[6]
            }
            risk = RiskCalculator.calculate(village_dict)
            village_dict['risk'] = risk
            scored_villages.append(village_dict)
        
        scored_villages.sort(key=lambda x: x['risk']['risk_score'], reverse=True)
        
        total_min_needed = sum(v['population'] * min_per_person_kg for v in scored_villages)
        distributions = []
        remaining = total_aid_kg
        
        if total_aid_kg >= total_min_needed:
            for v in scored_villages:
                min_amount = v['population'] * min_per_person_kg
                remaining -= min_amount
                distributions.append({
                    'village_id': v['id'],
                    'village_name': v['name'],
                    'amount': min_amount,
                    'type': 'كرامة'
                })
            
            total_risk = sum(v['risk']['risk_score'] for v in scored_villages)
            if total_risk > 0 and remaining > 0:
                for v in scored_villages:
                    extra = (v['risk']['risk_score'] / total_risk) * remaining
                    for d in distributions:
                        if d['village_id'] == v['id']:
                            d['amount'] += extra
                            d['type'] = 'كرامة + خطر'
                            break
        else:
            total_risk = sum(v['risk']['risk_score'] for v in scored_villages)
            for v in scored_villages:
                if total_risk > 0:
                    amount = (v['risk']['risk_score'] / total_risk) * total_aid_kg
                else:
                    amount = total_aid_kg / len(scored_villages)
                
                distributions.append({
                    'village_id': v['id'],
                    'village_name': v['name'],
                    'amount': amount,
                    'type': 'طوارئ'
                })
        
        for d in distributions:
            self.db.record_distribution(d['village_id'], d['amount'], 0)
            village = self.db.get_village(d['village_id'])
            new_stock = village[4] + d['amount']
            self.db.update_village(d['village_id'], food_stock_kg=new_stock)
        
        return {
            "success": True,
            "distributions": distributions,
            "total_distributed": sum(d['amount'] for d in distributions)
        }
