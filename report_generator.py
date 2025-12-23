from fpdf import FPDF
import os

class SimulationReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Mall of Zimbabwe: Strategic Forecast Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf(results, n_shoppers, inputs, map_fig):
    pdf = SimulationReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # 1. TIMELINE
    sim_year = inputs.get('year', 2028)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"1. Forecast Year: {sim_year}", 0, 1)
    pdf.set_font("Arial", size=11)
    
    if sim_year < 2028: phase = "CONSTRUCTION (Mall Closed)"
    elif sim_year == 2028: phase = "GRAND OPENING (Launch Hype)"
    else: phase = "STABILIZATION"
    pdf.cell(0, 8, f"Project Phase: {phase}", 0, 1)
    pdf.ln(2)

    # 2. STRATEGY
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. Strategy Configuration", 0, 1)
    pdf.set_font("Arial", size=11)
    
    traffic_status = "PEAK HOUR (High Friction)" if inputs.get('traffic') else "NORMAL FLOW"
    clean_tenants = [t.split('(')[0].strip() for t in inputs.get('tenants', [])]
    tenants_list = ", ".join(clean_tenants) if clean_tenants else "None Selected"
    
    pdf.cell(0, 8, f"Traffic Condition: {traffic_status}", 0, 1)
    pdf.cell(0, 8, f"Destination Pillars: {tenants_list}", 0, 1)
    pdf.ln(5)

   # 3. FINANCIAL PERFORMANCE
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "3. Projected Financial Performance", 0, 1)
    pdf.set_font("Arial", size=11)

    counts = results["counts"]
    revenue = results["revenue"]
    sorted_malls = sorted(revenue.items(), key=lambda x: x[1], reverse=True)
    
    # UPDATED HEADER: Added 'SHARE' column
    pdf.cell(0, 8, f"{'MALL NAME':<30} {'SHARE':<10} {'VISITORS':<12} {'REVENUE':<15}", 0, 1)
    pdf.line(10, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(2)

    for mall, rev in sorted_malls:
        count = counts[mall]
        share = (count / n_shoppers) * 100
        share_str = f"{share:.1f}%"
        rev_str = f"${rev:,.0f}"
        
        if mall == "Mall of Zimbabwe":
            pdf.set_font("Arial", 'B', 11)
            pdf.set_text_color(0, 128, 0)
            # UPDATED ROW
            pdf.cell(0, 8, f"{mall:<30} {share_str:<10} {count:<12} {rev_str:<15}", 0, 1)
            pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", size=11)
        else:
            pdf.cell(0, 8, f"{mall:<30} {share_str:<10} {count:<12} {rev_str:<15}", 0, 1)
    pdf.ln(5)

    # 4. MAP
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "4. Geospatial Analysis", 0, 1)
    pdf.ln(2)
    temp_img = "temp_map_capture.jpg"
    map_fig.savefig(temp_img, dpi=100, bbox_inches='tight')
    pdf.image(temp_img, x=10, w=190)
    if os.path.exists(temp_img): os.remove(temp_img)

    # 5. VERDICT
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "5. Executive Verdict", 0, 1)
    pdf.set_font("Arial", size=11)
    
    moz_share = (counts["Mall of Zimbabwe"] / n_shoppers) * 100
    if sim_year < 2028: verdict = "CAPITAL DEPLOYMENT PHASE. Asset under construction."
    elif moz_share > 45: verdict = "DOMINANT LAUNCH. The mixed-use strategy successfully captures the market."
    elif moz_share > 30: verdict = "COMPETITIVE ENTRY. Launch successful but incumbents are resilient."
    else: verdict = "WEAK LAUNCH WARNING. Projected revenue below targets."
        
    pdf.multi_cell(0, 8, verdict)
    return pdf.output(dest='S').encode('latin-1')
