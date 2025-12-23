# 📚 Technical Documentation & Methodology

## 1. Simulation Logic
The core of this project is an **Agent-Based Model (ABM)** built using the `Mesa` framework.

### The Agents (Shoppers)
We instantiate **1,000 - 3,000 agents** with specific attributes:
* **Location:** Distributed using a Gaussian (Normal) distribution centered on key residential hubs (Borrowdale Brooke, Mt Pleasant, Pomona).
* **Income Segmentation:**
    * **High Income (30%):** Low price sensitivity, High quality sensitivity.
    * **Medium Income (50%):** Balanced sensitivity.
    * **Low Income (20%):** High distance sensitivity.

### The Decision Engine
Every "step" of the simulation, agents calculate a **Utility Score** for every mall:
`Utility = (Base_Quality + Strategy_Bonus) / (Distance * Traffic_Factor)`

## 2. Strategic Variables

### A. Tenant Mix Bonuses
| Tenant Type | Target Segment | Effect |
| :--- | :--- | :--- |
| **Luxury Fashion** | High Income | +25 Attractiveness Score |
| **Fine Dining** | Med/High Income | +20 Attractiveness Score |
| **Co-working** | Med Income | +15 Attractiveness Score |
| **Family Play** | All Segments | +15 Attractiveness Score |

### B. Traffic Friction (The "School Run")
If the `Peak Hour Traffic` toggle is active, the model applies a **2.5x Multiplier** to the distance.
* *Effect:* Agents will refuse to travel long distances (e.g., Mt Pleasant to Borrowdale) because the "cost" of travel is too high.

## 3. Financial Assumptions
Revenue is projected using "Basket Size" proxies derived from 2025 Market Data (Simbisa Brands / Tourism Reports):
* **High Income Basket:** $135.00
* **Medium Income Basket:** $50.00
* **Low Income Basket:** $5.50

## 4. Timeline Logic
* **Construction (2026-27):** Mall Quality set to 0. Market Share = 0%.
* **Launch (2028):** Mall Quality gets a **+15 Point "Hype" Bonus**.
* **Stabilization (2029):** Bonus removed. Mall runs on organic quality.