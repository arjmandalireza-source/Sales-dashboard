import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import io
import base64

# ============================================================
# 1. تنظیمات صفحه
# ============================================================
st.set_page_config(
    page_title="داشبورد تحلیل فروش شعبات",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. استایل سفارشی (پس‌زمینه سبز پسته‌ای + فونت پررنگ)
# ============================================================
st.markdown("""
<style>
    /* پس‌زمینه اصلی سبز پسته‌ای */
    .stApp {
        background: #F0FFF0 !important;
    }
    
    /* کارت‌های KPI */
    .kpi-card {
        background: white !important;
        padding: 20px !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07) !important;
        border-right: 5px solid #2B6CB0 !important;
        margin: 8px 0 !important;
        transition: transform 0.2s !important;
        text-align: center !important;
    }
    .kpi-card:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.1) !important;
    }
    .kpi-card .value {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #1A365D !important;
        margin: 8px 0 !important;
    }
    .kpi-card .label {
        font-size: 13px !important;
        color: #718096 !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    .kpi-card .change {
        font-size: 13px !important;
        padding: 2px 10px !important;
        border-radius: 20px !important;
        display: inline-block !important;
    }
    .change-up { background: #C6EFCE !important; color: #1A9E42 !important; }
    .change-down { background: #FFC7CE !important; color: #CC2F26 !important; }
    .change-neutral { background: #FFEB9C !important; color: #C07500 !important; }
    
    /* اعداد پررنگ داخل جدول */
    .dataframe td {
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    .dataframe th {
        font-weight: 700 !important;
        font-size: 14px !important;
        background: #1A365D !important;
        color: white !important;
    }
    
    /* هدرها */
    .section-header {
        font-size: 22px !important;
        font-weight: 700 !important;
        color: #1A365D !important;
        margin: 25px 0 15px 0 !important;
        padding-right: 15px !important;
        border-right: 4px solid #2B6CB0 !important;
    }
    
    /* سایدبار */
    .sidebar .sidebar-content {
        background: #FFFFFF !important;
    }
    .css-1d391kg {
        background: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. بارگذاری و پردازش داده
# ============================================================

@st.cache_data
def load_data():
    data = {
        'مرکز فروش': ['البرز', 'تهران جنوب', 'تهران عمده - هورکا', 'ستاد', 'اصفهان', 'اهواز', 
                      'ورامین', 'اردبيل', 'کرمانشاه', 'رشت', 'شيراز', 'مشهد', 'خرم آباد طبیعت',
                      'اراک', 'قزوین', 'همدان', 'پارس آباد', 'مراغه طبيعت', 'بيرجند', 'سقز',
                      'کاشان', 'ساری طبیعت', 'تهران شمال', 'ياسوج', 'بروجرد طبیعت', 'دزفول طبيعت',
                      'بوشهر طبیعت', 'زنجان', 'ساوه طبیعت', 'سنندج هایلی', 'شهرکرد', 'لنگرود طبیعت',
                      'تنکابن طبیعت', 'فسا طبيعت', 'بهبهان طبيعت', 'سنندج طبیعت', 'تبریز طبيعت',
                      'خرم آباد هایلی', 'آباده طبيعت', 'قم', 'بجنورد', 'سبزوار طبیعت', 'بوشهر هایلی',
                      'آمل', 'ارومیه طبيعت', 'خوی طبیعت', 'ایلام طبيعت', 'زاهدان طبیعت',
                      'سمنان طبیعت', 'آبادان هایلی', 'شاهرود طبيعت', 'زابل طبیعت', 'دزفول هایلی',
                      'کرمان هايلي', 'گرگان طبیعت', 'تالش طبیعت', 'بندرعباس طبيعت', 'آبادان طبيعت',
                      'گنبد طبیعت', 'اهواز هایلی', 'یاسوج هایلی', 'یزد', 'کاشان هایلی', 'چابهار طبيعت',
                      'بیرجند هایلی'],
        'Total Sales (RI)': [7984722116359, 7235707809414, 6528053709206, 6290655152974, 5713888366193,
                            5143553653311, 4239499191740, 4054398648345, 3706297321786, 3693552110548,
                            3630087746848, 3205628532428, 3086674742633, 3064430821113, 2787327148360,
                            2733184865036, 2718086290344, 2684181290381, 2630600483927, 2622888608038,
                            2611677114554, 2519132448432, 2487255278690, 2478602345494, 2324003454771,
                            2254070522453, 2220325258726, 2208079284776, 2082886043945, 2038997510487,
                            1940598049437, 1909469535950, 1857931652448, 1841592634407, 1841037503114,
                            1771446208994, 1767250060768, 1766385650656, 1694330479397, 1663880776259,
                            1571249480469, 1478480057708, 1457669910398, 1453876308069, 1443609334355,
                            1380452217201, 1313568717162, 1234236418673, 1200465433142, 1167617799783,
                            1159711180813, 1142160268834, 1115787119671, 1086904444309, 1001092904267,
                            998562855889, 964301229295, 964295609045, 512211925618, 63972642231,
                            49706474063, 3929719429, 0, 0, 0],
        'Net Weight (KG)': [2115899, 1978544, 1809843, 2121634, 1595385, 1403251, 1183599, 1087267,
                           1066021, 1015437, 1024552, 847271, 805905, 798537, 749208, 739030,
                           737977, 684549, 711562, 765521, 723119, 690186, 698202, 711257, 601364,
                           623850, 618560, 572578, 548592, 599181, 527910, 519103, 512053, 494518,
                           492685, 496657, 460178, 493789, 437788, 465398, 410452, 399810, 456938,
                           400501, 403469, 364566, 364320, 332543, 324337, 330503, 311214, 305008,
                           308377, 338516, 273436, 288914, 293610, 273624, 139218, 20723, 16068,
                           1143, 0, 0, 0],
        'Total Invoices': [36099, 49897, 7785, 192, 13282, 17770, 19555, 16953, 22201, 22650,
                           10623, 17114, 14011, 14599, 13664, 9841, 12165, 9948, 12085, 8102,
                           12048, 10758, 16867, 9477, 9225, 6667, 7598, 8250, 7103, 7418, 8072,
                           12973, 14091, 8102, 6756, 8189, 4670, 5105, 6312, 9426, 9281, 7442,
                           4237, 5260, 5589, 6312, 6689, 4393, 4909, 3584, 6040, 3872, 3830,
                           1647, 4269, 7507, 3336, 3138, 2522, 89, 173, 51, 0, 0, 0],
        'Strike Rate': [34.9, 33.5, 12.3, 75.3, 31.6, 32.4, 33.1, 39.9, 40.7, 37.2,
                        21.1, 29.0, 63.9, 59.0, 41.6, 32.4, 45.9, 46.4, 33.7, 30.4,
                        34.8, 31.8, 22.6, 40.1, 49.8, 50.9, 31.9, 35.2, 46.7, 43.1,
                        39.3, 39.9, 65.2, 50.1, 47.5, 29.7, 13.8, 27.9, 57.5, 33.2,
                        53.8, 50.2, 38.8, 32.2, 27.1, 41.8, 61.2, 43.7, 53.8, 35.4,
                        43.6, 43.9, 32.3, 17.9, 28.1, 39.0, 42.1, 29.0, 30.7, 8.2,
                        23.8, 46.8, 0.0, 0.0, 0.0],
        'Retention Rate': [77.5, 82.4, 69.1, 43.4, 77.3, 93.6, 85.4, 94.4, 86.0, 85.7,
                           80.6, 80.8, 93.3, 93.2, 85.0, 85.6, 89.9, 87.7, 89.8, 86.2,
                           94.4, 82.4, 75.3, 95.1, 95.8, 94.9, 87.3, 91.3, 92.7, 93.2,
                           89.6, 84.9, 93.3, 90.6, 95.5, 88.8, 65.6, 75.2, 90.5, 87.9,
                           93.6, 94.0, 79.6, 70.3, 82.8, 92.2, 94.5, 84.7, 84.7, 91.1,
                           92.6, 88.5, 84.1, 82.6, 77.1, 82.0, 81.9, 88.2, 69.9, 10.2,
                           19.8, 0.0, 0.0, 0.0, 0.0],
        'Churn Rate': [22.5, 17.6, 30.9, 56.6, 22.7, 6.4, 14.6, 5.6, 14.0, 14.3,
                       19.4, 19.2, 6.7, 6.8, 15.0, 14.4, 10.1, 12.3, 10.2, 13.8,
                       5.6, 17.6, 24.7, 4.9, 4.2, 5.1, 12.7, 8.7, 7.3, 6.8,
                       10.4, 15.1, 6.7, 9.4, 4.5, 11.2, 34.4, 24.8, 9.5, 12.1,
                       6.4, 6.0, 20.4, 29.7, 17.2, 7.8, 5.5, 15.3, 15.3, 8.9,
                       7.4, 11.5, 15.9, 17.4, 22.9, 18.0, 18.1, 11.8, 30.1, 89.8,
                       80.2, 100.0, 0.0, 0.0, 0.0],
        'Drop size (RI)': [221189565, 145012883, 838542545, 32763828922, 430197889, 289451528,
                           216798731, 239155232, 166942810, 163070733, 341719641, 187310303,
                           220303672, 209906899, 203990570, 277734464, 223434960, 269821199,
                           217674844, 323733474, 216772669, 234163641, 147462814, 261538709,
                           251924494, 338093674, 292224962, 267645974, 293240327, 274871598,
                           240411057, 147187970, 131852363, 227300992, 272504071, 216320211,
                           378426137, 346010901, 268430051, 176520345, 169297434, 198667033,
                           344033493, 276402340, 258294746, 218702823, 196377443, 280955251,
                           244543783, 325786216, 192005162, 294979408, 291328230, 659929839,
                           234502906, 133017564, 289059121, 307296243, 203097512, 718793733,
                           287320659, 77053322, 0, 0, 0],
        'Drop size (KG)': [59, 40, 232, 11050, 120, 79, 61, 64, 48, 45, 96, 50, 58, 55, 55,
                           75, 61, 69, 59, 94, 60, 64, 41, 75, 65, 94, 81, 69, 77, 81, 65,
                           40, 36, 61, 73, 61, 99, 97, 69, 49, 44, 54, 108, 76, 72, 58, 54,
                           76, 66, 92, 52, 79, 81, 206, 64, 38, 88, 87, 55, 233, 93, 22, 0, 0, 0],
        'Frequency': [5.7, 5.6, 4.2, 2.4, 4.2, 5.4, 7.3, 6.9, 7.3, 6.1,
                      4.2, 4.7, 8.8, 9.2, 5.8, 5.9, 9.3, 6.2, 6.1, 5.2,
                      7.5, 5.1, 3.3, 7.9, 6.8, 7.0, 4.9, 6.2, 7.2, 3.8,
                      6.1, 7.1, 8.3, 6.8, 6.7, 4.1, 3.3, 3.1, 7.1, 6.3,
                      6.9, 5.4, 2.9, 3.5, 4.1, 5.3, 7.9, 6.0, 6.5, 5.1,
                      6.2, 6.6, 4.5, 2.7, 3.6, 7.3, 4.1, 3.9, 3.4, 1.1,
                      1.0, 1.0, 0, 0, 0],
        'Sales per Visitor (RI)': [107901650221, 66382640453, 120889883504, 483896550229,
                                   139363130883, 109437311773, 128469672477, 144799951727,
                                   142549896992, 136798226317, 82501994247, 74549500754,
                                   280606794785, 127684617546, 92910904945, 143851835002,
                                   159887428844, 167761330649, 105224019357, 104915544322,
                                   113551178894, 119958688021, 30332381447, 107765319369,
                                   154933563651, 187839210204, 138770328670, 147205285652,
                                   173573836995, 226555278943, 129373203296, 146882271996,
                                   142917819419, 153466052867, 153419791926, 84354581381,
                                   84154764798, 176638565066, 211791309925, 110925385084,
                                   104749965365, 123206671476, 145766991040, 96925087205,
                                   90225583397, 115037684767, 262713743432, 112203310788,
                                   109133221195, 233523559957, 115971118081, 103832751712,
                                   139473389959, 135863055539, 62568306517, 90778441444,
                                   96430122930, 107143956561, 36586566116, 10662107039,
                                   9941294813, 654953238, 0, 0, 0],
        'Visitor': [74, 109, 54, 13, 41, 47, 33, 28, 26, 27, 44, 43, 11, 24, 30, 19, 17, 16, 25, 25,
                    23, 21, 82, 23, 15, 12, 16, 15, 12, 9, 15, 13, 13, 12, 12, 21, 21, 10, 8, 15,
                    15, 12, 10, 15, 16, 12, 5, 11, 11, 5, 10, 11, 8, 8, 16, 11, 10, 9, 14, 6, 5, 6, 0, 0, 0],
        'Customer': [6334, 8950, 1846, 79, 3163, 3277, 2673, 2461, 3025, 3721, 2550, 3616, 1594,
                     1586, 2340, 1680, 1308, 1602, 1985, 1564, 1600, 2092, 5129, 1197, 1359, 957,
                     1536, 1340, 990, 1955, 1321, 1818, 1705, 1194, 1003, 1990, 1410, 1626, 888,
                     1503, 1351, 1389, 1449, 1495, 1370, 1196, 850, 729, 753, 708, 978, 587, 851,
                     620, 1201, 1028, 814, 807, 750, 81, 167, 49, 0, 0, 0]
    }
    
    df = pd.DataFrame(data)
    df = df[df['Total Sales (RI)'] > 0].reset_index(drop=True)
    
    # ستون استان
    province_map = {
        'البرز': 'البرز', 'تهران جنوب': 'تهران', 'تهران عمده - هورکا': 'تهران', 'ستاد': 'تهران',
        'اصفهان': 'اصفهان', 'اهواز': 'خوزستان', 'ورامین': 'تهران', 'اردبيل': 'اردبیل',
        'کرمانشاه': 'کرمانشاه', 'رشت': 'گیلان', 'شيراز': 'فارس', 'مشهد': 'خراسان رضوی',
        'خرم آباد طبیعت': 'لرستان', 'اراک': 'مرکزی', 'قزوین': 'قزوین', 'همدان': 'همدان',
        'پارس آباد': 'اردبیل', 'مراغه طبيعت': 'آذربایجان شرقی', 'بيرجند': 'خراسان جنوبی',
        'سقز': 'کردستان', 'کاشان': 'اصفهان', 'ساری طبیعت': 'مازندران', 'تهران شمال': 'تهران',
        'ياسوج': 'کهگیلویه و بویراحمد', 'بروجرد طبیعت': 'لرستان', 'دزفول طبيعت': 'خوزستان',
        'بوشهر طبیعت': 'بوشهر', 'زنجان': 'زنجان', 'ساوه طبیعت': 'مرکزی', 'سنندج هایلی': 'کردستان',
        'شهرکرد': 'چهارمحال و بختیاری', 'لنگرود طبیعت': 'گیلان', 'تنکابن طبیعت': 'مازندران',
        'فسا طبيعت': 'فارس', 'بهبهان طبيعت': 'خوزستان', 'سنندج طبیعت': 'کردستان',
        'تبریز طبيعت': 'آذربایجان شرقی', 'خرم آباد هایلی': 'لرستان', 'آباده طبيعت': 'فارس',
        'قم': 'قم', 'بجنورد': 'خراسان شمالی', 'سبزوار طبیعت': 'خراسان رضوی',
        'بوشهر هایلی': 'بوشهر', 'آمل': 'مازندران', 'ارومیه طبيعت': 'آذربایجان غربی',
        'خوی طبیعت': 'آذربایجان غربی', 'ایلام طبيعت': 'ایلام', 'زاهدان طبیعت': 'سیستان و بلوچستان',
        'سمنان طبیعت': 'سمنان', 'آبادان هایلی': 'خوزستان', 'شاهرود طبيعت': 'سمنان',
        'زابل طبیعت': 'سیستان و بلوچستان', 'دزفول هایلی': 'خوزستان', 'کرمان هايلي': 'کرمان',
        'گرگان طبیعت': 'گلستان', 'تالش طبیعت': 'گیلان', 'بندرعباس طبيعت': 'هرمزگان',
        'آبادان طبيعت': 'خوزستان', 'گنبد طبیعت': 'گلستان', 'اهواز هایلی': 'خوزستان',
        'یاسوج هایلی': 'کهگیلویه و بویراحمد', 'یزد': 'یزد'
    }
    df['استان'] = df['مرکز فروش'].map(province_map).fillna('سایر')
    
    # محاسبه Churn Rate از Retention Rate
    df['Churn Rate'] = 100 - df['Retention Rate']
    
    return df

df = load_data()

# ============================================================
# 4. سایدبار - فیلترها
# ============================================================
st.sidebar.title("🔍 فیلترهای تحلیل")

branches = ['همه'] + sorted(df['مرکز فروش'].unique().tolist())
selected_branch = st.sidebar.selectbox("🏢 انتخاب شعبه", branches)

drop_size_range = st.sidebar.slider(
    "📦 محدوده Drop Size (KG)",
    min_value=int(df['Drop size (KG)'].min()),
    max_value=int(df['Drop size (KG)'].max()),
    value=(int(df['Drop size (KG)'].min()), int(df['Drop size (KG)'].max()))
)

strike_range = st.sidebar.slider(
    "🎯 محدوده Strike Rate (%)",
    min_value=float(df['Strike Rate'].min()),
    max_value=float(df['Strike Rate'].max()),
    value=(float(df['Strike Rate'].min()), float(df['Strike Rate'].max()))
)

spv_range = st.sidebar.slider(
    "💰 محدوده Sales per Visitor (RI)",
    min_value=float(df['Sales per Visitor (RI)'].min()),
    max_value=float(df['Sales per Visitor (RI)'].max()),
    value=(float(df['Sales per Visitor (RI)'].min()), float(df['Sales per Visitor (RI)'].max()))
)

filtered_df = df.copy()
if selected_branch != 'همه':
    filtered_df = filtered_df[filtered_df['مرکز فروش'] == selected_branch]
filtered_df = filtered_df[
    (filtered_df['Drop size (KG)'] >= drop_size_range[0]) &
    (filtered_df['Drop size (KG)'] <= drop_size_range[1]) &
    (filtered_df['Strike Rate'] >= strike_range[0]) &
    (filtered_df['Strike Rate'] <= strike_range[1]) &
    (filtered_df['Sales per Visitor (RI)'] >= spv_range[0]) &
    (filtered_df['Sales per Visitor (RI)'] <= spv_range[1])
]

# ============================================================
# 5. منوی اصلی
# ============================================================
selected = option_menu(
    menu_title=None,
    options=["📊 نمای کلی", "📈 تحلیل فروش", "🎯 تحلیل عملکرد", "🗺️ نقشه", "📋 رتبه‌بندی", "📤 خروجی"],
    icons=["house", "bar-chart", "target", "map", "list-ol", "download"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "white"},
        "icon": {"color": "#1A365D", "font-size": "18px"},
        "nav-link": {"font-size": "14px", "text-align": "center", "margin": "0px", "padding": "10px 20px"},
        "nav-link-selected": {"background-color": "#2B6CB0", "color": "white"},
    }
)

# ============================================================
# 6. صفحه: نمای کلی
# ============================================================
if selected == "📊 نمای کلی":
    st.markdown('<div class="section-header">📊 نمای کلی عملکرد شعبات</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    total_sales_b = filtered_df['Total Sales (RI)'].sum() / 1e9
    total_weight_t = filtered_df['Net Weight (KG)'].sum() / 1000
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="label">💰 کل فروش</div>
            <div class="value">{total_sales_b:.1f} B</div>
            <span class="change change-up">▲ {len(filtered_df)} شعبه</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="label">📦 وزن کل</div>
            <div class="value">{total_weight_t:.1f} تن</div>
            <span class="change change-neutral">وزن خالص</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="label">📄 تعداد فاکتورها</div>
            <div class="value">{filtered_df['Total Invoices'].sum():,.0f}</div>
            <span class="change change-up">▲ کل</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_strike = filtered_df['Strike Rate'].mean()
        color = 'change-up' if avg_strike > 35 else 'change-down'
        st.markdown(f"""
        <div class="kpi-card">
            <div class="label">🎯 میانگین Strike Rate</div>
            <div class="value">{avg_strike:.1f}%</div>
            <span class="change {color}">{"▲ خوب" if avg_strike > 35 else "▼ نیاز به بهبود"}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        avg_retention = filtered_df['Retention Rate'].mean()
        color = 'change-up' if avg_retention > 80 else 'change-down'
        st.markdown(f"""
        <div class="kpi-card">
            <div class="label">🔄 میانگین Retention</div>
            <div class="value">{avg_retention:.1f}%</div>
            <span class="change {color}">{"▲ عالی" if avg_retention > 80 else "▼ نیاز به بهبود"}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        total_visitor = filtered_df['Visitor'].sum()
        st.markdown(f"""
        <div class="kpi-card">
            <div class="label">👥 تعداد ویزیتور</div>
            <div class="value">{total_visitor:,}</div>
            <span class="change change-up">▲ کل ویزیتورها</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Top 10 فروش
    st.subheader("🏆 ۱۰ شعبه برتر فروش")
    top10_sales = filtered_df.nlargest(10, 'Total Sales (RI)')[['مرکز فروش', 'Total Sales (RI)']]
    top10_sales['فروش (میلیارد)'] = top10_sales['Total Sales (RI)'] / 1e9
    
    fig = px.bar(top10_sales, x='مرکز فروش', y='فروش (میلیارد)',
                 title='۱۰ شعبه برتر بر اساس فروش (میلیارد ریال)',
                 color='فروش (میلیارد)', color_continuous_scale=['#1A365D', '#2B6CB0'],
                 text='فروش (میلیارد)')
    fig.update_traces(texttemplate='%{text:.1f} B', textposition='outside',
                      textfont=dict(size=14, color='#1A365D', family='Arial Black'))
    fig.update_layout(
        xaxis_tickangle=-45, 
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1A365D', size=12)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # توزیع Strike Rate
    st.subheader("📊 توزیع Strike Rate")
    fig = px.histogram(filtered_df, x='Strike Rate', nbins=20,
                       title='توزیع Strike Rate در شعبات',
                       color_discrete_sequence=['#2B6CB0'])
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 7. صفحه: تحلیل فروش
# ============================================================
elif selected == "📈 تحلیل فروش":
    st.markdown('<div class="section-header">📈 تحلیل فروش شعبات</div>', unsafe_allow_html=True)
    
    filtered_df['وزن (تن)'] = filtered_df['Net Weight (KG)'] / 1000
    df_sales_b = filtered_df.copy()
    df_sales_b['فروش (میلیارد)'] = df_sales_b['Total Sales (RI)'] / 1e9
    
    # فروش
    st.subheader("💰 مقایسه فروش شعبات (میلیارد ریال)")
    fig = px.bar(df_sales_b, x='مرکز فروش', y='فروش (میلیارد)',
                 title='فروش کل بر اساس شعبه (میلیارد ریال)',
                 color='فروش (میلیارد)', color_continuous_scale='Viridis')
    fig.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # وزن
    st.subheader("📦 مقایسه وزن فروش (تن)")
    fig = px.bar(filtered_df, x='مرکز فروش', y='وزن (تن)',
                 title='وزن کل فروش بر اساس شعبه (تن)',
                 color='وزن (تن)', color_continuous_scale='Plasma')
    fig.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Bubble: Strike Rate vs وزن
    st.subheader("🫧 تحلیل رابطه Strike Rate و وزن فروش")
    fig = px.scatter(filtered_df, x='وزن (تن)', y='Strike Rate',
                     size='Strike Rate', color='Strike Rate',
                     hover_name='مرکز فروش',
                     title='رابطه Strike Rate و وزن فروش (تن)',
                     size_max=60, color_continuous_scale='RdYlGn')
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 8. صفحه: تحلیل عملکرد
# ============================================================
elif selected == "🎯 تحلیل عملکرد":
    st.markdown('<div class="section-header">🎯 تحلیل عملکرد شعبات</div>', unsafe_allow_html=True)
    
    # Heatmap
    st.subheader("🗺️ Heatmap عملکرد بر اساس استان")
    heatmap_data = filtered_df.groupby('استان').agg({
        'Strike Rate': 'mean',
        'Retention Rate': 'mean',
        'Churn Rate': 'mean',
        'Total Sales (RI)': 'sum',
    }).reset_index()
    heatmap_data['Strike Rate'] = heatmap_data['Strike Rate'].round(1)
    heatmap_data['Retention Rate'] = heatmap_data['Retention Rate'].round(1)
    heatmap_data['Churn Rate'] = heatmap_data['Churn Rate'].round(1)
    
    fig = px.imshow(heatmap_data.set_index('استان')[['Strike Rate', 'Retention Rate', 'Churn Rate']],
                    text_auto=True, aspect='auto',
                    title='Heatmap عملکرد استان‌ها (Strike Rate, Retention Rate, Churn Rate)',
                    color_continuous_scale='RdYlGn')
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Bubble ترکیبی با Retention + Churn
    st.subheader("🫧 تحلیل ترکیبی (Strike Rate، Retention Rate، فروش)")
    
    # ایجاد ستون ترکیبی برای نمایش
    filtered_df['نرخ نگهداشت خالص'] = filtered_df['Retention Rate'] - filtered_df['Churn Rate']
    
    fig = px.scatter(filtered_df, x='Strike Rate', y='Retention Rate',
                     size='Total Sales (RI)', color='Churn Rate',
                     hover_name='مرکز فروش',
                     title='رابطه Strike Rate، Retention Rate و فروش (رنگ = Churn Rate)',
                     size_max=60, color_continuous_scale='RdYlGn_r')
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 9. صفحه: نقشه
# ============================================================
elif selected == "🗺️ نقشه":
    st.markdown('<div class="section-header">🗺️ نقشه عملکرد شعبات</div>', unsafe_allow_html=True)
    
    coords = {
        'تهران': [35.6892, 51.3890], 'اصفهان': [32.6546, 51.6680], 'خوزستان': [31.3183, 48.6706],
        'فارس': [29.5918, 52.5837], 'خراسان رضوی': [36.2605, 59.6168], 'مازندران': [36.2262, 52.5319],
        'گیلان': [37.2809, 49.5925], 'آذربایجان شرقی': [38.0800, 46.2919], 'آذربایجان غربی': [37.5553, 45.0585],
        'کرمانشاه': [34.3142, 47.0650], 'لرستان': [33.4872, 48.3538], 'مرکزی': [34.0954, 49.6904],
        'همدان': [34.7608, 48.3982], 'قزوین': [36.2688, 50.0041], 'زنجان': [36.6764, 48.4963],
        'سمنان': [35.5761, 53.3959], 'یزد': [31.8974, 54.3569], 'کرمان': [30.2839, 57.0834],
        'سیستان و بلوچستان': [29.4975, 60.8684], 'هرمزگان': [27.1860, 56.2744], 'بوشهر': [28.9234, 50.8203],
        'چهارمحال و بختیاری': [32.3275, 50.8458], 'کهگیلویه و بویراحمد': [30.6500, 51.6000],
        'گلستان': [36.8386, 54.4344], 'خراسان شمالی': [37.4800, 57.3300], 'خراسان جنوبی': [32.8500, 59.2200],
        'اردبیل': [38.2500, 48.3000], 'ایلام': [33.6400, 46.4200], 'کردستان': [35.3100, 46.9900],
        'قم': [34.6400, 50.8800]
    }
    
    map_data = filtered_df.groupby('استان').agg({
        'Total Sales (RI)': 'sum',
        'Strike Rate': 'mean',
        'Retention Rate': 'mean',
        'Drop size (KG)': 'mean',
        'Churn Rate': 'mean'
    }).reset_index()
    
    map_data['Total Sales (B)'] = map_data['Total Sales (RI)'] / 1e9
    map_data['lat'] = map_data['استان'].map(lambda x: coords.get(x, [35.0, 51.0])[0])
    map_data['lon'] = map_data['استان'].map(lambda x: coords.get(x, [35.0, 51.0])[1])
    map_data = map_data.dropna(subset=['lat', 'lon'])
    
    fig = px.scatter_mapbox(map_data,
                            lat='lat', lon='lon',
                            size='Total Sales (RI)',
                            color='Strike Rate',
                            hover_name='استان',
                            hover_data={
                                'Total Sales (B)': ':.1f',
                                'Drop size (KG)': ':.1f',
                                'Strike Rate': ':.1f%',
                                'Retention Rate': ':.1f%',
                                'Churn Rate': ':.1f%'
                            },
                            title='نقشه عملکرد استان‌ها',
                            color_continuous_scale='RdYlGn',
                            size_max=60,
                            zoom=4,
                            height=600)
    fig.update_layout(mapbox_style='carto-positron')
    fig.update_layout(margin={'r': 0, 't': 40, 'l': 0, 'b': 0})
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 10. صفحه: رتبه‌بندی
# ============================================================
elif selected == "📋 رتبه‌بندی":
    st.markdown('<div class="section-header">📋 رتبه‌بندی شعبات</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Top 10 فروش", "🎯 Top 10 Strike Rate", "🔄 Top 10 Retention", "⚠️ Bottom 10"])
    
    with tab1:
        st.subheader("🏆 ۱۰ شعبه برتر بر اساس فروش")
        top_sales = filtered_df.nlargest(10, 'Total Sales (RI)')[['مرکز فروش', 'Total Sales (RI)', 'Net Weight (KG)', 'Strike Rate']]
        top_sales['Total Sales (RI)'] = top_sales['Total Sales (RI)'] / 1e9
        st.dataframe(top_sales.style.format({
            'Total Sales (RI)': '{:.2f} B',
            'Net Weight (KG)': '{:,.0f}',
            'Strike Rate': '{:.1f}%'
        }), use_container_width=True)
    
    with tab2:
        st.subheader("🎯 ۱۰ شعبه برتر بر اساس Strike Rate")
        top_strike = filtered_df.nlargest(10, 'Strike Rate')[['مرکز فروش', 'Strike Rate', 'Total Sales (RI)', 'Retention Rate']]
        top_strike['Total Sales (RI)'] = top_strike['Total Sales (RI)'] / 1e9
        st.dataframe(top_strike.style.format({
            'Strike Rate': '{:.1f}%',
            'Total Sales (RI)': '{:.2f} B',
            'Retention Rate': '{:.1f}%'
        }), use_container_width=True)
    
    with tab3:
        st.subheader("🔄 ۱۰ شعبه برتر بر اساس Retention Rate")
        top_retention = filtered_df.nlargest(10, 'Retention Rate')[['مرکز فروش', 'Retention Rate', 'Total Sales (RI)', 'Strike Rate']]
        top_retention['Total Sales (RI)'] = top_retention['Total Sales (RI)'] / 1e9
        st.dataframe(top_retention.style.format({
            'Retention Rate': '{:.1f}%',
            'Total Sales (RI)': '{:.2f} B',
            'Strike Rate': '{:.1f}%'
        }), use_container_width=True)
    
    with tab4:
        st.subheader("⚠️ ۱۰ شعبه با ضعیف‌ترین عملکرد (بر اساس ترکیب شاخص‌ها)")
        filtered_df['Performance Score'] = (
            filtered_df['Strike Rate'] * 0.3 +
            filtered_df['Retention Rate'] * 0.3 +
            (filtered_df['Total Sales (RI)'] / filtered_df['Total Sales (RI)'].max()) * 40
        )
        bottom_performers = filtered_df.nsmallest(10, 'Performance Score')[['مرکز فروش', 'Strike Rate', 'Retention Rate', 'Total Sales (RI)', 'Performance Score']]
        bottom_performers['Total Sales (RI)'] = bottom_performers['Total Sales (RI)'] / 1e9
        st.dataframe(bottom_performers.style.format({
            'Strike Rate': '{:.1f}%',
            'Retention Rate': '{:.1f}%',
            'Total Sales (RI)': '{:.2f} B',
            'Performance Score': '{:.1f}'
        }), use_container_width=True)

# ============================================================
# 11. صفحه: خروجی
# ============================================================
elif selected == "📤 خروجی":
    st.markdown('<div class="section-header">📤 خروجی داده‌ها</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 دانلود Excel")
        if st.button("📥 دانلود فایل Excel", use_container_width=True):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, sheet_name='داده_شعبات', index=False)
                filtered_df.nlargest(10, 'Total Sales (RI)').to_excel(writer, sheet_name='Top10_فروش', index=False)
                filtered_df.nlargest(10, 'Strike Rate').to_excel(writer, sheet_name='Top10_Strike', index=False)
                filtered_df.nlargest(10, 'Retention Rate').to_excel(writer, sheet_name='Top10_Retention', index=False)
            output.seek(0)
            b64 = base64.b64encode(output.read()).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="تحلیل_شعبات.xlsx">📥 دانلود فایل Excel</a>'
            st.markdown(href, unsafe_allow_html=True)
    
    with col2:
        st.subheader("📊 دانلود HTML (گزارش کامل)")
        if st.button("📥 دانلود گزارش HTML", use_container_width=True):
            html_content = f"""
            <html dir='rtl'>
            <head>
                <meta charset='UTF-8'>
                <title>گزارش تحلیل شعبات</title>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, sans-serif; padding: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; }}
                    h1 {{ color: #1A365D; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    th {{ background: #2B6CB0; color: white; padding: 12px; text-align: right; }}
                    td {{ padding: 10px; border-bottom: 1px solid #eee; }}
                </style>
            </head>
            <body>
                <div class='container'>
                    <h1>📊 گزارش تحلیل عملکرد شعبات</h1>
                    <p>تاریخ: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</p>
                    <p>تعداد شعبات: {len(filtered_df)}</p>
                    <hr>
                    <h2>📋 خلاصه داده‌ها</h2>
                    {filtered_df.to_html(index=False, classes='table')}
                </div>
            </body>
            </html>
            """
            b64 = base64.b64encode(html_content.encode()).decode()
            href = f'<a href="data:text/html;base64,{b64}" download="گزارش_تحلیل_شعبات.html">📥 دانلود گزارش HTML</a>'
            st.markdown(href, unsafe_allow_html=True)
    
    st.subheader("📋 جدول کامل داده‌ها")
    display_df = filtered_df.copy()
    display_df['Total Sales (RI)'] = display_df['Total Sales (RI)'] / 1e9
    display_df['Net Weight (KG)'] = display_df['Net Weight (KG)'] / 1000
    st.dataframe(display_df.style.format({
        'Total Sales (RI)': '{:.2f} B',
        'Net Weight (KG)': '{:.2f} تن',
        'Total Invoices': '{:,.0f}',
        'Strike Rate': '{:.1f}%',
        'Retention Rate': '{:.1f}%',
        'Churn Rate': '{:.1f}%',
        'Drop size (RI)': '{:,.0f}',
        'Drop size (KG)': '{:,.0f}',
        'Sales per Visitor (RI)': '{:,.0f}',
        'Frequency': '{:.1f}'
    }), use_container_width=True)

# ============================================================
# 12. فوتر
# ============================================================
st.markdown("""
<style>
    .footer {
        text-align: center;
        color: #A0AEC0;
        font-size: 12px;
        padding: 20px 0;
        margin-top: 30px;
        border-top: 1px solid #e2e8f0;
    }
</style>
<div class='footer'>
    🚀 توسعه‌یافته با Streamlit • داده‌های فروش شعبات • گزارش روزانه
</div>
""", unsafe_allow_html=True)