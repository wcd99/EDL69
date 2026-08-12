import os
import re
import math
import pandas as pd
import streamlit as st

# 1. Page Configuration for Mobile
st.set_page_config(
    page_title="บัญชียาหลักแห่งชาติ 2569",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Inject Custom CSS
def load_css(css_file):
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles.css")

# 3. Load & Cache Dataset
@st.cache_data
def load_data():
    csv_path = "./EDL69_tables/EDL69_drugs_all.csv"
    if not os.path.exists(csv_path):
        csv_path = "EDL69_tables/EDL69_drugs_all.csv"
    
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    
    # Extract System Code number from Group column (e.g. "กลุ่มยา 1 Gastro-intestinal system" -> 1)
    df["SystemCodeNum"] = df["Group"].str.extract(r'(\d+)')[0].astype(int)
    
    # Format Group label for display
    def format_group_name(g):
        num_match = re.search(r'\d+', g)
        name_match = re.search(r'[A-Za-zก-๙].*$', g)
        num_str = num_match.group(0) if num_match else ""
        name_str = name_match.group(0) if name_match else g
        return f"กลุ่มยา {num_str}: {name_str}"

    df["GroupDisplay"] = df["Group"].apply(format_group_name)
    return df

drugs_df = load_data()

# 4. Helper Function: Category Badge HTML
def get_badge_html(cat_code):
    cat_lower = str(cat_code).strip().lower()
    badge_class = f"badge-{cat_lower}"
    return f'<span class="badge-chip {badge_class}">{cat_code}</span>'

# 5. Mobile Header Banner
header_html = """
<div class="mobile-header">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="title-logo-icon">
        <path d="M 12 8 H 6 A 4 4 0 0 0 2 12 A 4 4 0 0 0 6 16 H 12 Z" fill="#00f2fe" />
        <rect x="2" y="8" width="20" height="8" rx="4" fill="none" stroke="#00f2fe" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round" />
        <line x1="12" y1="8" x2="12" y2="16" stroke="#00f2fe" stroke-width="2.2" stroke-linecap="round" />
    </svg>
    <div>
        <h1 class="header-title-text">บัญชียาหลักแห่งชาติ 2569</h1>
        <div class="header-subtitle">Essential Drug List 2026 • Mobile Search Application</div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# 6. Mode Switcher (Global Search vs Browse by System)
mode = st.radio(
    "โหมดการทำงาน:",
    options=["🔍 ค้นหาข้ามหมวด (Global Search)", "📁 เลือกตามระบบอวัยวะ (Browse by System)"],
    horizontal=True,
    label_visibility="collapsed"
)

# Initialize filtered dataset reference
filtered_df = pd.DataFrame()

if mode == "🔍 ค้นหาข้ามหมวด (Global Search)":
    st.markdown("### 🔍 ค้นหารายการยาข้ามหมวดหมู่")
    
    col_search, col_cat = st.columns([3, 2])
    with col_search:
        search_query = st.text_input(
            "ค้นหาชื่อยา / สารสำคัญ / เงื่อนไข:",
            placeholder="พิมพ์ชื่อยา เช่น Omeprazole, Paracetamol...",
            key="global_search_input"
        ).strip()
    
    with col_cat:
        category_filter = st.selectbox(
            "กรองตามบัญชียา:",
            options=["ทั้งหมด (All)", "b - บัญชีพื้นฐาน", "s - บัญชีทางเลือก", "ex - บัญชีเฉพาะโรค", "R1 - โครงการพิเศษ 1", "R2 - ควบคุมพิเศษ 2"],
            key="cat_filter_select"
        )
    
    # Filter dataset across all tables/categories
    temp_df = drugs_df.copy()
    
    if category_filter != "ทั้งหมด (All)":
        cat_code_selected = category_filter.split(" - ")[0].strip()
        temp_df = temp_df[temp_df["Category Code"].str.strip().str.lower() == cat_code_selected.lower()]
        
    if search_query:
        # Search across Drug Name, Subgroup, Group, Conditions / Notes
        query_lower = search_query.lower()
        mask = (
            temp_df["Drug Name & Form"].str.lower().str.contains(query_lower, na=False) |
            temp_df["Subgroup"].str.lower().str.contains(query_lower, na=False) |
            temp_df["Group"].str.lower().str.contains(query_lower, na=False) |
            temp_df["Conditions / Notes"].str.lower().str.contains(query_lower, na=False)
        )
        filtered_df = temp_df[mask]
    else:
        filtered_df = temp_df

else:
    # Browse by System Mode
    st.markdown("### 📁 เรียกดูตามระบบอวัยวะและหมวดยาย่อย")
    
    # Sorted list of unique systems
    unique_systems = (
        drugs_df[["SystemCodeNum", "GroupDisplay", "Group"]]
        .drop_duplicates()
        .sort_values("SystemCodeNum")
    )
    
    system_options = unique_systems["GroupDisplay"].tolist()
    system_mapping = dict(zip(unique_systems["GroupDisplay"], unique_systems["Group"]))
    
    selected_system_display = st.selectbox(
        "เลือกระบบอวัยวะ (Organ System):",
        options=system_options,
        index=0
    )
    
    selected_group_raw = system_mapping[selected_system_display]
    
    # Get Subgroups for selected system
    subgroups = (
        drugs_df[drugs_df["Group"] == selected_group_raw]["Subgroup"]
        .unique()
        .tolist()
    )
    subgroups.sort()
    
    selected_subgroup = st.selectbox(
        "เลือกหมวดยาย่อย (Subgroup):",
        options=subgroups,
        index=0 if subgroups else None
    )
    
    if selected_subgroup:
        filtered_df = drugs_df[
            (drugs_df["Group"] == selected_group_raw) & 
            (drugs_df["Subgroup"] == selected_subgroup)
        ]
    else:
        filtered_df = pd.DataFrame()

# 7. Render Search Results / Drug List
st.markdown("---")

total_results = len(filtered_df)

if mode == "🔍 ค้นหาข้ามหมวด (Global Search)":
    count_html = f"""
    <div class="search-count-banner">
        <span>ผลการค้นหายาข้ามหมวดหมู่</span>
        <span>พบ <span class="search-count-number">{total_results:,}</span> รายการ</span>
    </div>
    """
    st.markdown(count_html, unsafe_allow_html=True)

if total_results == 0:
    st.info("❌ ไม่พบข้อมูลรายการยาที่ตรงกับเงื่อนไขการค้นหา")
else:
    # Pagination for mobile view to ensure high performance
    ITEMS_PER_PAGE = 15
    total_pages = math.ceil(total_results / ITEMS_PER_PAGE)
    
    if total_pages > 1:
        page = st.number_input("หน้า:", min_value=1, max_value=total_pages, value=1, step=1)
    else:
        page = 1
        
    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, total_results)
    
    page_items = filtered_df.iloc[start_idx:end_idx]
    
    for idx, row in page_items.iterrows():
        drug_name = row["Drug Name & Form"]
        cat_code = row["Category Code"]
        cat_desc = row["Category Description (Thai)"]
        notes = str(row["Conditions / Notes"]).strip()
        group_disp = row["GroupDisplay"]
        subgroup = row["Subgroup"]
        pdf_page = row["Page in PDF"]
        
        badge_html = get_badge_html(cat_code)
        
        note_html = ""
        if notes:
            formatted_notes = notes.replace("\n", "<br/>")
            note_html = f"""
            <div class="condition-box">
                <div class="condition-title">⚠️ คำเตือน / เงื่อนไขการใช้ยา:</div>
                <div>{formatted_notes}</div>
            </div>
            """
            
        card_html = f"""
        <div class="drug-card">
            <div class="drug-card-header">
                <div class="drug-name">{drug_name}</div>
                <div>{badge_html}</div>
            </div>
            <div class="drug-meta">
                <span class="drug-group-tag">📍 {group_disp}</span>
                <span>🔹 {subgroup}</span>
                <span>📄 หน้า PDF: {pdf_page}</span>
            </div>
            {note_html}
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        
    if total_pages > 1:
        st.caption(f"แสดงรายการที่ {start_idx + 1} ถึง {end_idx} จากทั้งหมด {total_results} รายการ (หน้า {page}/{total_pages})")

# 8. Category Legend Section
legend_html = """
<div class="legend-card">
    <div class="legend-title">📖 คำอธิบายประเภทบัญชียา (Category Legend)</div>
    
    <div class="legend-item">
        <div class="legend-item-header">
            <span class="badge-chip badge-b">b</span>
            <span class="legend-item-name">บัญชียาพื้นฐาน (Basic list - b)</span>
        </div>
        <div class="legend-item-desc">รายการยาที่สมควรเลือกใช้เป็นอันดับแรก มีความปลอดภัย ประสิทธิศักย์ชัดเจน และมีความคุ้มค่า (เทียบเท่าบัญชี ก และ ข เดิม)</div>
    </div>
    
    <div class="legend-item">
        <div class="legend-item-header">
            <span class="badge-chip badge-s">s</span>
            <span class="legend-item-name">บัญชียาทางเลือก (Supplemental list - s)</span>
        </div>
        <div class="legend-item-desc">รายการยาที่สมควรเลือกใช้เป็นลำดับรอง ในกรณีที่ผู้ป่วยมีข้อบ่งชี้ที่ไม่สามารถใช้ยาในบัญชีพื้นฐาน (b) ได้ หรือใช้เป็นยาร่วม/ยาเสริม (เทียบเท่าบัญชี ค เดิม)</div>
    </div>
    
    <div class="legend-item">
        <div class="legend-item-header">
            <span class="badge-chip badge-ex">ex</span>
            <span class="legend-item-name">บัญชียาเฉพาะโรค (Exclusive list - ex)</span>
        </div>
        <div class="legend-item-desc">รายการยาที่มีเงื่อนไขการใช้เฉพาะ แนะนำให้ใช้โดยแพทย์ผู้เชี่ยวชาญเฉพาะทางและต้องมีการติดตามผลการใช้ยาอย่างใกล้ชิด (เทียบเท่าบัญชี ง เดิม)</div>
    </div>
    
    <div class="legend-item">
        <div class="legend-item-header">
            <span class="badge-chip badge-r1">R1</span>
            <span class="legend-item-name">ยาโครงการพิเศษ 1 (Restricted list 1 - R1)</span>
        </div>
        <div class="legend-item-desc">รายการยาสำหรับโครงการพิเศษของหน่วยงานภาครัฐ ซึ่งมีหน่วยงานรับผิดชอบโครงการและงบประมาณชัดเจน (เทียบเท่าบัญชี จ (1) เดิม)</div>
    </div>
    
    <div class="legend-item">
        <div class="legend-item-header">
            <span class="badge-chip badge-r2">R2</span>
            <span class="legend-item-name">ยาควบคุมการสั่งใช้เป็นพิเศษ 2 (Restricted list 2 - R2)</span>
        </div>
        <div class="legend-item-desc">รายการยาสำหรับผู้ป่วยที่มีความจำเป็นเฉพาะ ซึ่งต้องการระบบกำกับและอนุมัติการสั่งใช้ยา (Authorized system) เพื่อให้เกิดความเหมาะสมและคุ้มค่า (เทียบเท่าบัญชี จ (2) เดิม)</div>
    </div>
</div>
"""
st.markdown(legend_html, unsafe_allow_html=True)

# 9. Disclaimer Section
disclaimer_html = """
<div class="disclaimer-box">
    <strong>ข้อสงวนสิทธิ์:</strong> แอปพลิเคชันนี้จัดทำขึ้นเพื่อให้สามารถค้นหาข้อมูลได้อย่างรวดเร็ว แต่อาจมีความคลาดเคลื่อนได้ หากมีข้อสงสัยควรตรวจสอบกับเอกสารต้นฉบับ ผู้จัดทำขอปฏิเสธความรับผิดชอบต่อความเสียหายใดๆ ที่เกิดจากข้อมูลนี้
</div>
"""
st.markdown(disclaimer_html, unsafe_allow_html=True)
