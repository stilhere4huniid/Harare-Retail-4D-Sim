import mesa
import numpy as np

# 1. THE SHOPPER AGENT
class ShopperAgent(mesa.Agent):
    def __init__(self, model, pos, income):
        super().__init__(model)
        self.pos = pos
        self.income = income # 1=Low, 2=Med, 3=High
        self.chosen_mall = None

    def step(self):
        self.choose_mall()

    def choose_mall(self):
        best_score = -float('inf')
        best_mall = None

        for mall in self.model.malls:
            dist = self.get_distance(self.pos, mall["pos"])
            if dist == 0: dist = 0.1

            # --- 1. TRAFFIC SIMULATOR (Friction) ---
            # If Traffic is ON, distance feels 2.5x longer
            dist_weight = 2.5 if self.model.traffic_on else 1.0
            effective_dist = dist * dist_weight

            # --- 2. "EAT, SHOP, WORK, PLAY" STRATEGY ---
            score = mall["attractiveness"]
            
            if mall["name"] == "Mall of Zimbabwe":
                tenants = self.model.moz_tenants
                
                # A. SHOP: Luxury Fashion (High Income Draw)
                if "Luxury Fashion (Shop)" in tenants:
                    if self.income == 3: score += 25
                
                # B. EAT: Fine Dining Precinct (High Income Draw)
                if "Fine Dining (Eat)" in tenants:
                    if self.income >= 2: score += 20
                
                # C. WORK: Co-working Hub (Med Income Draw)
                if "Co-working Hub (Work)" in tenants:
                    if self.income == 2: score += 15
                    score += 5 
                
                # D. PLAY: Family Entertainment (Mass Appeal)
                if "Family Entertainment (Play)" in tenants:
                    score += 15 

            # --- 3. UTILITY CALCULATION ---
            if self.income == 3: # Rich (Care about Quality)
                final_utility = (score * 3.0) / (effective_dist * 0.5)
            elif self.income == 2: # Middle Class
                final_utility = (score * 1.0) / (effective_dist * 1.0)
            else: # Low Income (Care about Distance)
                final_utility = (score * 0.5) / (effective_dist * 2.0)

            if final_utility > best_score:
                best_score = final_utility
                best_mall = mall["name"]

        self.chosen_mall = best_mall

    def get_distance(self, pos1, pos2):
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

# 2. THE MARKET MODEL
class HarareMarketModel(mesa.Model):
    def __init__(self, n_shoppers, sam_q, arundel_q, groombridge_q, highland_q, zim_q, traffic_on, moz_tenants):
        super().__init__()
        self.num_agents = n_shoppers
        self.traffic_on = traffic_on
        self.moz_tenants = moz_tenants
        
        self.malls = [
            {"name": "Sam Levy's Village", "pos": (9, 9), "attractiveness": sam_q},
            {"name": "Highland Park",      "pos": (10, 5), "attractiveness": highland_q},
            {"name": "Arundel Village",    "pos": (4, 8), "attractiveness": arundel_q},
            {"name": "Groombridge",        "pos": (6, 7), "attractiveness": groombridge_q},
            {"name": "Mall of Zimbabwe",   "pos": (7, 8), "attractiveness": zim_q}, 
        ]

        for _ in range(self.num_agents):
            x = np.random.normal(6.5, 2.0)
            y = np.random.normal(7.5, 2.0)
            x = max(0, min(x, 12)); y = max(0, min(y, 12))
            income = np.random.choice([1, 2, 3], p=[0.2, 0.5, 0.3])
            ShopperAgent(self, (x, y), income)

    def step(self):
        self.agents.shuffle_do("step")
    
    def get_results(self):
        # Track Headcount
        counts = {m["name"]: 0 for m in self.malls}
        # Track Revenue ($)
        revenue = {m["name"]: 0 for m in self.malls}
        
        # --- NEW SPEND MAP (Based on 2025 Market Data) ---
        # Low: $5.50 (Simbisa Avg Spend)
        # Med: $50.00 (Standard Grocery Basket)
        # High: $135.00 (Premium Lifestyle Spend)
        spend_map = {1: 5.50, 2: 50.00, 3: 135.00}

        for agent in self.agents:
            if agent.chosen_mall:
                counts[agent.chosen_mall] += 1
                revenue[agent.chosen_mall] += spend_map[agent.income]
                
        return {"counts": counts, "revenue": revenue}