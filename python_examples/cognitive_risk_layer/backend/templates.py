# backend/templates.py

def generate_analysis_html(bps, portfolio_name, total_pv, pnl_str, pnl_raw, details, story_title, story_text, story_color):
    """
    Hesaplama sonuçlarını alır ve şık bir HTML Dashboard döndürür.
    """
    
    # --- RENK MANTIĞI ---
    is_neg = pnl_raw < 0
    
    # P&L Kutusu Renkleri (Kırmızı/Yeşil)
    if is_neg:
        pnl_border = "#ef4444"
        pnl_bg = "rgba(239, 68, 68, 0.1)"
        pnl_text = "#ef4444"
    else:
        pnl_border = "#10b981"
        pnl_bg = "rgba(16, 185, 129, 0.1)"
        pnl_text = "#10b981"

    # Toplam PV Kutusu (Mavi)
    pv_style = "background:rgba(59, 130, 246, 0.1); border:1px solid #3b82f6; color:#3b82f6;"
    pnl_style = f"background:{pnl_bg}; border:1px solid {pnl_border}; color:{pnl_text};"

    # --- TABLO SATIRLARI ---
    rows_html = ""
    for pos in details[:10]: # İlk 10
        chg = pos.get('change', 0)
        row_css = "text-red" if chg < 0 else "text-green"
        pos_id = pos.get('positionId', 'N/A')
        cpv = f"{pos.get('cashflowPv', 0):,.0f}"
        chg_fmt = f"{chg:,.0f}"
        
        rows_html += f"""
        <tr>
            <td class='text-blue' style='font-weight:500;'>{pos_id}</td>
            <td>{cpv}</td>
            <td class='text-right {row_css}' style='font-weight:bold;'>{chg_fmt}</td>
        </tr>
        """

    # --- HTML ŞABLONU ---
    html = f"""
        <div class="report-header">
            <div class="report-title">✅ Analiz Tamamlandı</div>
            <div class="report-subtitle">Şok: {bps} bps | <span style='background:#3b82f6; color:white; padding:2px 6px; border-radius:4px; font-size:0.7rem;'>{portfolio_name}</span></div>
        </div>
        
        <div style="display:flex; gap:10px; margin-bottom:20px;">
            <div style="flex:1; {pv_style} padding:15px; border-radius:8px; text-align:center;">
                <div style="font-size:0.75rem; margin-bottom:5px; font-weight:bold; opacity:0.8;">TOPLAM PORTFÖY</div>
                <div style="font-size:1.1rem; font-weight:bold;">{total_pv} TL</div>
            </div>
            <div style="flex:1; {pnl_style} padding:15px; border-radius:8px; text-align:center;">
                <div style="font-size:0.75rem; margin-bottom:5px; font-weight:bold; opacity:0.8;">P&L ETKİSİ</div>
                <div style="font-size:1.2rem; font-weight:bold;">{pnl_str} TL</div>
            </div>
        </div>
        
        <div class="report-section-title">EN ÇOK ETKİLENEN 10 POZİSYON</div>
        <table class="report-table">
            <thead>
                <tr>
                    <th>Pozisyon</th>
                    <th>Nominal</th>
                    <th class="text-right">P&L</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        
        <div style="margin-top:15px; background:rgba(255,255,255,0.05); border-left:4px solid {story_color}; padding:15px; border-radius:0 8px 8px 0;">
            <div style="font-size:0.85rem; font-weight:bold; color:{story_color}; margin-bottom:5px;">📋 {story_title}</div>
            <div style="font-size:0.85rem; color:#e2e8f0; line-height:1.6;">{story_text}</div>
        </div>
    """
    return html

def generate_ai_response_html(source_name, ai_content):
    """
    Sadece Yapay Zeka (RAG) cevapları için şablon.
    """
    return f"""
        <div class="report-header">
            <div class="report-title">🤖 Yapay Zeka Analizi</div>
            <div class="report-subtitle">Kaynak: {source_name}</div>
        </div>
        
        <div style="background:rgba(139, 92, 246, 0.1); border:1px solid rgba(139, 92, 246, 0.3); border-radius:12px; padding:20px; margin-top:10px;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:15px; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:10px;">
                <div style="width:32px; height:32px; background:#8b5cf6; border-radius:50%; display:flex; align-items:center; justify-content:center; color:white;">
                    <i class="fa-solid fa-brain"></i>
                </div>
                <div style="font-weight:bold; color:#a78bfa; font-size:0.95rem;">Risk Asistanı Görüşü</div>
            </div>
            <div style="font-size:0.95rem; color:#e2e8f0; line-height:1.7;">
                {ai_content}
            </div>
        </div>
    """