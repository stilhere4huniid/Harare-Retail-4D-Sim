# 🧠 Simulation Methodology

## 1. The Shopper Agents
The model simulates **1,000 - 3,000 individual agents**. Each agent is assigned:
* **Location:** Randomized using a Gaussian distribution centered on residential hubs (Borrowdale Brooke, Mt Pleasant, Pomona).
* **Income Level:**
    * **High (30%):** Spend capacity ~$135/visit. Price insensitive, Quality sensitive.
    * **Medium (50%):** Spend capacity ~$50/visit. Balanced sensitivity.
    * **Low (20%):** Spend capacity ~$5.50/visit. Highly distance sensitive.

## 2. The Decision Engine (Utility Function)
Agents choose a mall based on **Utility Score**:
`Score = (Mall_Quality + Tenant_Bonuses) / (Distance * Traffic_Friction)`

### Strategic Bonuses
* **Launch Hype (2028):** +15 Base Points.
* **Luxury Anchor:** +25 Points for High-Income agents.
* **Family Play:** +15 Points for All agents.

### Traffic Friction
If "Peak Hour" is active, the distance penalty is multiplied by **2.5x**, simulating the reluctance to drive during school-run congestion.

## 3. Financial Calibration
Revenue estimates are proxies based on 2025 market reports (Simbisa Brands & ZTA):
* **High Income Basket:** $135.00 (Fine Dining/Luxury)
* **Med Income Basket:** $50.00 (Grocery/Retail)
* **Low Income Basket:** $5.50 (Fast Food/Cinema)

*Disclaimer: These figures are for strategic simulation purposes and do not represent audited financial guarantees.*