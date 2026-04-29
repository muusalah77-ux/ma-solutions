import streamlit as st
from supabase import create_client
import pandas as pd
import hashlib, io, datetime

 
try:
    import plotly.express as px
    import plotly.graph_objects as go
    has_plotly = True
except ImportError:
    has_plotly = False
 
# ══════════════════════════════════════════
# الاتصال بـ Supabase
# ══════════════════════════════════════════
URL = "https://rsqzdzgjdoavhxbbpelx.supabase.co"
KEY = "sb_secret_Hdvq3VDFnR-EUwoebK5pRQ_GoL2B5ff"
supabase = create_client(URL, KEY)
 
st.set_page_config(page_title="قاصد خير HR", layout="wide", page_icon="🚢",
                   initial_sidebar_state="expanded")
 
# ══════════════════════════════════════════
# CSS عالمي — ثيم فاتح نظيف
# ══════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
 
/* تطبيق الخط العربي على النصوص فقط */
body, p, h1, h2, h3, h4, h5, h6, label, .stMarkdown, .stButton {
    font-family: 'Cairo', sans-serif !important;
    line-height: 1.7 !important;
}

/* استثناء الأيقونات الخاصة بـ Streamlit عشان ماتظهرش كنص */
.stIcon, .material-symbols-rounded, [data-testid="stExpanderToggleIcon"] {
    font-family: 'Material Symbols Rounded' !important;
}
 
/* إخفاء عناصر Streamlit الزيادة */
#MainMenu, footer { visibility: hidden; }

/* خلفية فاتحة نظيفة */
.stApp { background: #f4f6fb !important; }
/* Sidebar Premium Styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e3a8a 100%) !important;
    border-left: 1px solid rgba(255,255,255,0.05) !important;
}
section[data-testid="stSidebar"] * { color: #f8fafc !important; }
section[data-testid="stSidebar"] .stSelectbox label {
    color: #94a3b8 !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 8px !important;
}

/* Fix Dropdown styling in sidebar */
section[data-testid="stSidebar"] div[data-baseweb="select"] * {
    color: #1e293b !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] {
    background-color: rgba(255,255,255,0.95) !important;
    border: none !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
}

/* Sidebar Buttons Styling (Logout) */
section[data-testid="stSidebar"] .stButton button {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    padding: 10px !important;
    transition: all 0.3s ease !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(239, 68, 68, 0.9) !important; /* Red hover for logout */
    border-color: #ef4444 !important;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4) !important;
    transform: translateY(-2px) !important;
}
section[data-testid="stSidebar"] .stButton button * {
    color: white !important;
}
/* KPI Cards — فاتح واضح */
.kpi-card {
    background: white;
    border-radius: 14px;
    padding: 18px 14px;
    border: 1px solid #e2e8f0;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.kpi-value { font-size: 30px; font-weight: 900; line-height: 1.1; }
.kpi-label { color: #64748b; font-size: 12px; margin-top: 6px; font-weight: 600; }
 
/* بادجات الحالة */
.badge-admin  { background:#e0fdf4; color:#065f46; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:700; }
.badge-user   { background:#eff6ff; color:#1d4ed8; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:700; }
 
/* رسالة الرفض */
.denied-box {
    background:#fff1f2; border:2px solid #fda4af;
    border-radius:14px; padding:40px;
    text-align:center; color:#be123c; font-size:18px; font-weight:700;
}
 
/* عناوين الأقسام Premium */
.section-header {
    background: linear-gradient(90deg, rgba(30, 58, 95, 0.04) 0%, rgba(37, 99, 235, 0.04) 100%);
    color: #0f172a;
    font-size: 24px;
    font-weight: 900;
    padding: 16px 22px;
    border-right: 6px solid #2563eb;
    border-radius: 12px;
    margin-bottom: 30px;
    display: flex;
    align-items: center;
    gap: 15px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,1);
}
 
/* كارت المعلومات العام */
.info-card {
    background: white; border-radius: 14px;
    padding: 20px 24px; border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)
 
# ══════════════════════════════════════════
# دوال مساعدة
# ══════════════════════════════════════════
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
 
def fetch(table):
    try:
        user = st.session_state.get("user")
        query = supabase.table(table).select("*")
        if user and "company_id" in user:
            query = query.eq("company_id", user["company_id"])
        return pd.DataFrame(query.execute().data)
    except Exception as e:
        st.error(f"خطأ في جلب {table}: {e}")
        return pd.DataFrame()
 
def can(perm):
    u = st.session_state.get("user", {})
    if u.get("role") == "admin": return True
    return perm in (u.get("permissions") or [])
 
def denied():
    st.markdown('<div class="denied-box">🔒 ليس لديك صلاحية الوصول<br><small>تواصل مع المسؤول</small></div>',
                unsafe_allow_html=True)
 
def ensure_admin():
    try:
        r = supabase.table("app_users").select("id").eq("username","admin").execute()
        if not r.data:
            supabase.table("app_users").insert({
                "username":"admin","password":hash_pw("admin123"),
                "full_name":"المسؤول العام","role":"admin",
                "permissions":[],"is_active":True,"branch_filter":None
            }).execute()
    except: pass
 
# ══════════════════════════════════════════
# حساب بيانات الحضور (المنطق الأساسي)
# ══════════════════════════════════════════
def calc_attendance(df_logs, emp_branch, work_hours=8, late_threshold=15):
    """
    يحسب: ساعات العمل، التأخير، الإضافي، العجز، الحالة
    work_hours      : ساعات العمل الرسمية (افتراضي 8)
    late_threshold  : دقائق السماح قبل اعتباره متأخر (افتراضي 15 دقيقة)
    """
    if df_logs.empty: return pd.DataFrame()
 
    df = df_logs.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date']      = df['timestamp'].dt.date
 
    records = []
    for date, grp in df.groupby('date'):
        grp = grp.sort_values('timestamp')
        first, last = grp['timestamp'].iloc[0], grp['timestamp'].iloc[-1]
        stamps = len(grp)
        loc    = grp['location'].iloc[0] if 'location' in grp.columns else emp_branch
 
        if stamps == 1:
            records.append({
                'التاريخ': date, 'حضور': first, 'انصراف': None,
                'الساعات': 0.0, 'تأخير_دقائق': 0, 'إضافي': 0.0,
                'عجز': work_hours, 'بصمات': stamps,
                'فرع_البصمة': loc, 'تقاطع_فروع': loc != emp_branch,
                'حالة': 'بصمة_واحدة'
            })
            continue
 
        hrs     = (last - first).total_seconds() / 3600
        # حساب التأخير (بعد 8 صباحاً + مهلة)
        expected_in  = first.replace(hour=8, minute=0, second=0)
        late_min     = max(0, (first - expected_in).total_seconds() / 60 - late_threshold)
        extra        = max(0, hrs - work_hours)
        deficit      = max(0, work_hours - hrs)
 
        if   stamps == 1:          status = 'بصمة_واحدة'
        elif late_min > 0:         status = 'متأخر'
        elif hrs >= work_hours:    status = 'مكتمل'
        else:                      status = 'عجز'
 
        records.append({
            'التاريخ': date, 'حضور': first, 'انصراف': last,
            'الساعات': round(hrs, 2), 'تأخير_دقائق': round(late_min),
            'إضافي': round(extra, 2), 'عجز': round(deficit, 2),
            'بصمات': stamps, 'فرع_البصمة': loc,
            'تقاطع_فروع': loc != emp_branch, 'حالة': status
        })
 
    return pd.DataFrame(records).sort_values('التاريخ', ascending=False)
 
def detect_absent_days(summary_df, start_date, end_date, device_id):
    """يكتشف أيام الغياب ويتحقق من وجود إجازات أو مأموريات معتمدة"""
    all_days  = pd.date_range(start=start_date, end=end_date, freq='B')  # أيام العمل الرسمية
    logged    = set(summary_df['التاريخ'].astype(str)) if not summary_df.empty else set()
    
    # جلب الإجازات المعتمدة لهذا الموظف في هذه الفترة مع تصفية الشركة
    leaves_df = pd.DataFrame()
    try:
        user_c_id = st.session_state.user['company_id']
        res = supabase.table("leaves_missions").select("*") \
            .eq("device_id", device_id) \
            .eq("company_id", user_c_id) \
            .eq("status", "Approved") \
            .execute()
        leaves_df = pd.DataFrame(res.data)
    except: pass

    records = []
    for d in all_days:
        d_str = str(d.date())
        if d_str not in logged:
            reason = "غياب"
            category = "Absent"
            
            # التحقق من وجود مأمورية أو إجازة تغطي هذا التاريخ
            if not leaves_df.empty:
                for _, leaf in leaves_df.iterrows():
                    if str(leaf['start_date']) <= d_str <= str(leaf['end_date']):
                        reason = leaf['category']
                        category = "Leave"
                        break
            
            records.append({'date': d.date(), 'reason': reason, 'type': category})
            
    return records

# ══════════════════════════════════════════
# محرك حساب الرواتب (Payroll Engine)
# ══════════════════════════════════════════
def calculate_monthly_payroll(device_id, month, year):
    """حساب مستحقات الموظف عن شهر معين"""
    start_date = datetime.date(year, month, 1)
    if month == 12: end_date = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
    else: end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    
    # جلب إعدادات الراتب بتصفية الشركة
    user_c_id = st.session_state.user['company_id']
    salary_res = supabase.table("salaries").select("*").eq("device_id", device_id).eq("company_id", user_c_id).execute()
    if not salary_res.data: return None
    sal = salary_res.data[0]
    
    # جلب الحضور والغياب بتصفية الشركة
    res = supabase.table("attendance_logs").select("*") \
        .eq("device_id", device_id) \
        .eq("company_id", user_c_id) \
        .gte("timestamp", str(start_date)) \
        .lte("timestamp", str(end_date) + "T23:59:59") \
        .execute()
    df_logs = pd.DataFrame(res.data)
    
    summary = calc_attendance(df_logs, "")
    absent_records = detect_absent_days(summary, start_date, end_date, device_id)
    real_absences = [d for d in absent_records if d['type'] == 'Absent']
    
    # التجميع المالي
    total_ot_hrs   = summary['إضافي'].sum() if not summary.empty else 0
    total_late_min = summary['تأخير_دقائق'].sum() if not summary.empty else 0
    total_def_hrs  = summary['عجز'].sum() if not summary.empty else 0
    
    ot_val   = total_ot_hrs * float(sal['overtime_rate'])
    late_val = total_late_min * float(sal['late_rate'])
    def_val  = total_def_hrs * float(sal['hourly_rate'])
    
    # خصم الغياب (راتب اليوم = الأساسي / 30)
    day_rate = float(sal['base_salary']) / 30
    abs_val  = len(real_absences) * day_rate
    
    gross = float(sal['base_salary']) + float(sal['transport_allowance']) + ot_val
    deductions = late_val + def_val + abs_val
    net = gross - deductions
    
    return {
        'base': float(sal['base_salary']),
        'allowance': float(sal['transport_allowance']),
        'ot_value': round(ot_val, 2),
        'late_deduction': round(late_val, 2),
        'deficit_deduction': round(def_val, 2),
        'absent_deduction': round(abs_val, 2),
        'gross': round(gross, 2),
        'total_deductions': round(deductions, 2),
        'net': round(net, 2),
        'absent_days': len(real_absences),
        'ot_hours': total_ot_hrs
    }
 
# ══════════════════════════════════════════
# مولّد PDF الاحترافي
# ══════════════════════════════════════════
def generate_pdf(emp, summary, absent_days, report_type="شهري"):
    total_hrs    = summary['الساعات'].sum() if not summary.empty else 0
    total_extra  = summary['إضافي'].sum()   if not summary.empty else 0
    total_deficit= summary['عجز'].sum()      if not summary.empty else 0
    total_late   = summary[summary['حالة']=='متأخر'].shape[0] if not summary.empty else 0
    complete     = summary[summary['حالة']=='مكتمل'].shape[0] if not summary.empty else 0
 
    # صفوف الجدول
    rows_html = ""
    if not summary.empty:
        for _, r in summary.iterrows():
            status_map = {
                'مكتمل':      ('<span style="color:#16a34a">✅ مكتمل</span>',     '#f0fdf4'),
                'متأخر':      ('<span style="color:#d97706">⏰ متأخر</span>',     '#fffbeb'),
                'عجز':        ('<span style="color:#dc2626">❌ عجز</span>',       '#fef2f2'),
                'بصمة_واحدة': ('<span style="color:#7c3aed">⚠️ بصمة واحدة</span>','#faf5ff'),
            }
            s_html, s_bg = status_map.get(r['حالة'], (r['حالة'], 'white'))
            cross = ' <span style="color:#d97706">🔀</span>' if r.get('تقاطع_فروع') else ''
            late  = f"<span style='color:#d97706'>{r['تأخير_دقائق']} د</span>" if r['تأخير_دقائق'] > 0 else "—"
            انصراف = r['انصراف'].strftime('%I:%M %p') if r['انصراف'] is not None else "—"
            rows_html += f"""
            <tr style="background:{s_bg}">
                <td>{r['التاريخ']}</td>
                <td>{r['حضور'].strftime('%I:%M %p')}</td>
                <td>{انصراف}</td>
                <td><b>{r['الساعات']}</b></td>
                <td style="color:#16a34a">{r['إضافي'] if r['إضافي'] > 0 else '—'}</td>
                <td style="color:#dc2626">{r['عجز'] if r['عجز'] > 0 else '—'}</td>
                <td>{late}</td>
                <td>{s_html}{cross}</td>
            </tr>"""
 
    # صفوف الغياب
    absent_html = ""
    if absent_days:
        for d in absent_days[:10]:
            absent_html += f'<tr style="background:#fef2f2"><td>{d}</td><td colspan="7" style="color:#dc2626;text-align:center">🔴 غائب</td></tr>'
        if len(absent_days) > 10:
            absent_html += f'<tr><td colspan="8" style="text-align:center;color:#64748b">... و {len(absent_days)-10} أيام أخرى</td></tr>'
 
    html = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
  * {{ font-family: 'Cairo', Arial, sans-serif; margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:white; padding:30px; direction:rtl; color:#1e293b; font-size:13px; line-height: 1.7; }}
 
  /* Header */
  .header {{ display:flex; justify-content:space-between; align-items:center;
             background:linear-gradient(135deg,#004aad,#0077cc);
             color:white; padding:24px 28px; border-radius:16px; margin-bottom:24px; }}
  .company {{ font-size:22px; font-weight:900; }}
  .report-title {{ font-size:14px; opacity:0.85; margin-top:4px; }}
  .logo {{ font-size:48px; }}
 
  /* Employee card */
  .emp-card {{ background:#f8fafc; border:2px solid #e2e8f0; border-radius:12px;
               padding:18px 22px; margin-bottom:20px;
               display:flex; justify-content:space-between; align-items:center; }}
  .emp-name {{ font-size:20px; font-weight:900; color:#004aad; }}
  .emp-info {{ color:#64748b; font-size:13px; margin-top:4px; }}
  .emp-code {{ background:#004aad; color:white; padding:6px 16px;
               border-radius:8px; font-size:18px; font-weight:700; }}
 
  /* KPIs */
  .kpis {{ display:grid; grid-template-columns:repeat(5,1fr); gap:12px; margin-bottom:20px; }}
  .kpi  {{ background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px;
           padding:14px; text-align:center; }}
  .kpi-v {{ font-size:24px; font-weight:900; }}
  .kpi-l {{ font-size:11px; color:#64748b; margin-top:3px; }}
 
  /* Table */
  .section-title {{ font-size:15px; font-weight:700; color:#1e293b;
                    border-right:4px solid #004aad; padding-right:10px;
                    margin:20px 0 12px; }}
  table  {{ width:100%; border-collapse:collapse; font-size:12px; }}
  thead  {{ background:#004aad; color:white; }}
  th     {{ padding:10px 8px; text-align:right; font-weight:600; }}
  td     {{ padding:8px; border-bottom:1px solid #f1f5f9; text-align:right; }}
  tr:hover {{ background:#f8fafc; }}
 
  /* Absent box */
  .absent-box {{ background:#fef2f2; border:1px solid #fecaca; border-radius:10px;
                 padding:14px; margin-top:16px; }}
  .absent-title {{ color:#dc2626; font-weight:700; margin-bottom:8px; }}
  .absent-tags {{ display:flex; flex-wrap:wrap; gap:6px; }}
  .absent-tag  {{ background:#dc2626; color:white; padding:3px 10px;
                  border-radius:20px; font-size:11px; }}
 
  /* Footer */
  .footer {{ margin-top:30px; padding-top:16px; border-top:1px solid #e2e8f0;
             display:flex; justify-content:space-between; color:#94a3b8; font-size:11px; }}
</style>
</head>
<body>
 
<!-- Header -->
<div class="header">
  <div>
    <div class="company">🚢 شركة قاصد خير</div>
    <div class="report-title">تقرير الحضور والانصراف — {report_type}</div>
    <div class="report-title">تاريخ الإصدار: {datetime.date.today().strftime('%Y-%m-%d')}</div>
  </div>
</div>
 
<!-- Employee -->
<div class="emp-card">
  <div>
    <div class="emp-name">{emp.get('name','—')}</div>
    <div class="emp-info">🏢 {emp.get('branch','—')} &nbsp;|&nbsp; 👤 {emp.get('role','موظف')}</div>
  </div>
  <div class="emp-code">#{emp.get('device_id','—')}</div>
</div>
 
<!-- KPIs -->
<div class="kpis">
  <div class="kpi"><div class="kpi-v" style="color:#004aad">{len(summary)}</div><div class="kpi-l">أيام العمل</div></div>
  <div class="kpi"><div class="kpi-v" style="color:#16a34a">{complete}</div><div class="kpi-l">أيام مكتملة</div></div>
  <div class="kpi"><div class="kpi-v" style="color:#0077cc">{round(total_hrs,1)}</div><div class="kpi-l">إجمالي الساعات</div></div>
  <div class="kpi"><div class="kpi-v" style="color:#d97706">{total_late}</div><div class="kpi-l">أيام تأخير</div></div>
  <div class="kpi"><div class="kpi-v" style="color:#dc2626">{len(absent_days)}</div><div class="kpi-l">أيام غياب</div></div>
</div>
 
<!-- Attendance Table -->
<div class="section-title">📋 سجل الحضور التفصيلي</div>
<table>
  <thead>
    <tr>
      <th>التاريخ</th><th>حضور</th><th>انصراف</th>
      <th>الساعات</th><th>إضافي</th><th>عجز</th><th>تأخير</th><th>الحالة</th>
    </tr>
  </thead>
  <tbody>
    {rows_html}
    {absent_html}
  </tbody>
</table>
 
<!-- Absent Days Summary -->
{'<div class="absent-box"><div class="absent-title">🔴 أيام الغياب (' + str(len(absent_days)) + ' يوم)</div><div class="absent-tags">' + "".join([f'<span class="absent-tag">{d}</span>' for d in absent_days[:20]]) + '</div></div>' if absent_days else ''}
 
<!-- Summary Box -->
<div style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:10px;padding:16px;margin-top:20px;">
  <div style="font-weight:700;color:#0077cc;margin-bottom:10px;">📊 ملخص الفترة</div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;font-size:13px;">
    <div>⏱️ إجمالي ساعات الإضافي: <b style="color:#16a34a">{round(total_extra,1)} ساعة</b></div>
    <div>⬇️ إجمالي ساعات العجز: <b style="color:#dc2626">{round(total_deficit,1)} ساعة</b></div>
    <div>⏰ إجمالي دقائق التأخير: <b style="color:#d97706">{int(summary['تأخير_دقائق'].sum()) if not summary.empty else 0} دقيقة</b></div>
  </div>
</div>
 
<!-- Footer -->
<div class="footer">
  <span>🚢 منظومة قاصد خير الذكية — نظام إدارة الحضور</span>
  <span>تم الإنشاء: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
</div>
 
</body>
</html>
"""
    buf = io.BytesIO()
    HTML(string=html).write_pdf(buf)
    return buf.getvalue()
 
def page_home_dashboard():
    st.markdown('<div class="section-header">🏠 الشاشة الرئيسية - ملخص اليوم</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 3])
    selected_date = c1.date_input("📅 اختر التاريخ", value=datetime.date.today())
    st.write("")

    # 1. جلب البيانات بتصفية الشركة
    user_c_id = st.session_state.user['company_id']
    df_e = fetch("employees")
    res = supabase.table("attendance_logs").select("*") \
        .eq("company_id", user_c_id) \
        .gte("timestamp", str(selected_date)) \
        .lte("timestamp", str(selected_date) + "T23:59:59") \
        .execute()
    df_l = pd.DataFrame(res.data)
    
    if df_e.empty:
        st.warning("⚠️ لا توجد بيانات موظفين مسجلة."); return

    # 2. الحسابات
    total_emp = len(df_e)
    if not df_l.empty:
        df_l['timestamp'] = pd.to_datetime(df_l['timestamp'])
        # أول بصمة لكل موظف اليوم
        first_punches = df_l.sort_values('timestamp').groupby('device_id').first().reset_index()
        present_ids = first_punches['device_id'].tolist()
        present_count = len(present_ids)
        
        # حساب المتأخرين (بعد 8:15 صباحاً)
        threshold = datetime.time(8, 15)
        late_df = first_punches[first_punches['timestamp'].dt.time > threshold].copy()
        late_count = len(late_df)
    else:
        present_count = 0
        late_count = 0
        late_df = pd.DataFrame()
        present_ids = []

    absent_count = total_emp - present_count

    # 3. عرض المؤشرات (KPIs)
    k1, k2, k3, k4 = st.columns(4)
    metrics = [
        ("إجمالي الموظفين", total_emp, "👤", "#1e3a5f"),
        ("حضور اليوم", present_count, "✅", "#059669"),
        ("غياب اليوم", absent_count, "🔴", "#dc2626"),
        ("تأخير اليوم", late_count, "⏰", "#d97706"),
    ]
    for col, (label, val, icon, color) in zip([k1, k2, k3, k4], metrics):
        col.markdown(f"""
        <div class="kpi-card">
            <div style="font-size:14px; color:#64748b; font-weight:600; margin-bottom:5px;">{icon} {label}</div>
            <div style="font-size:32px; font-weight:900; color:{color};">{val}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # 4. الرسوم البيانية
    if has_plotly:
        c1, c2 = st.columns(2)
        with c1:
            # Donut Chart
            fig_donut = go.Figure(data=[go.Pie(
                labels=['حضور', 'غياب'],
                values=[present_count, absent_count],
                hole=.6,
                marker_colors=['#059669', '#dc2626']
            )])
            fig_donut.update_layout(title_text="📊 نسبة الحضور اليوم", height=350)
            st.plotly_chart(fig_donut, use_container_width=True)
        
        with c2:
            # Bar Chart by Branch
            if not df_l.empty:
                df_l_merged = df_l.merge(df_e[['device_id', 'branch']], on='device_id', how='left')
                branch_counts = df_l_merged.groupby('branch')['device_id'].nunique().reset_index()
                branch_counts.columns = ['الفرع', 'عدد الحضور']
                fig_bar = px.bar(branch_counts, x='الفرع', y='عدد الحضور', color='الفرع',
                                 title="🏢 الحضور حسب الفرع اليوم")
                fig_bar.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("لا توجد بيانات رسم بياني لليوم بعد.")

    # 5. جدول المتأخرين
    st.markdown("<h4 style='color: #d97706; margin-top:30px;'>⚠️ وصول متأخر اليوم (بعد 08:15 ص)</h4>", unsafe_allow_html=True)
    if not late_df.empty:
        # ربط البيانات للحصول على الأسماء والفروع
        late_report = late_df.merge(df_e[['device_id', 'name', 'branch']], on='device_id', how='left')
        late_report['وقت الحضور'] = late_report['timestamp'].dt.strftime('%I:%M %p')
        st.dataframe(
            late_report[['name', 'branch', 'وقت الحضور']].rename(columns={'name':'الاسم', 'branch':'الفرع'}),
            use_container_width=True, hide_index=True
        )
    else:
        st.success("✅ لا يوجد متأخرين اليوم حتى الآن.")

# ══════════════════════════════════════════
# صفحة: إدارة الإجازات والمأموريات
# ══════════════════════════════════════════
def page_manage_leaves():
    if not can("admin"): denied(); return
    
    st.markdown('<div class="section-header">🛳️ إدارة الإجازات والمأموريات</div>', unsafe_allow_html=True)
    
    tab_new, tab_pending = st.tabs(["🆕 تسجيل طلب جديد", "⏳ الطلبات المعلقة والإدارة"])
    
    df_e = fetch("employees")
    
    with tab_new:
        with st.form("new_leave_form"):
            col1, col2 = st.columns(2)
            # اختيار الموظف
            emp_list = {f"{e['device_id']} - {e['name']}": e['device_id'] for _, e in df_e.iterrows()}
            emp_label = col1.selectbox("👤 الموظف:", options=list(emp_list.keys()))
            
            category = col2.selectbox("📂 النوع:", ["مأمورية", "إجازة سنوية", "إجازة مرضية", "إجازة عارضة", "أخرى"])
            
            col3, col4 = st.columns(2)
            s_date = col3.date_input("📅 تاريخ البدء:", value=datetime.date.today())
            e_date = col4.date_input("📅 تاريخ الانتهاء:", value=datetime.date.today())
            
            notes = st.text_area("📝 ملاحظات إضافية:", placeholder="مثال: مأمورية على مركب كذا...")
            
            submit = st.form_submit_button("✅ حفظ الطلب", use_container_width=True)
            
            if submit:
                if s_date > e_date:
                    st.error("❌ تاريخ البدء لا يمكن أن يكون بعد تاريخ الانتهاء")
                else:
                    try:
                        user_c_id = st.session_state.user['company_id']
                        supabase.table("leaves_missions").insert({
                            "device_id": emp_list[emp_label],
                            "start_date": str(s_date),
                            "end_date": str(e_date),
                            "category": category,
                            "notes": notes,
                            "status": "Approved", # المضافة من قبل الأدمن تعتمد مباشرة
                            "company_id": user_c_id
                        }).execute()
                        st.success(f"✅ تم تسجيل {category} للموظف بنجاح!")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"خطأ أثناء الحفظ: {ex}")

    with tab_pending:
        try:
            res = supabase.table("leaves_missions").select("*, employees(name)").order("created_at", desc=True).execute()
            leaves_data = res.data
            
            if not leaves_data:
                st.info("لا توجد طلبات مسجلة حالياً.")
            else:
                for leaf in leaves_data:
                    with st.expander(f"📄 {leaf['employees']['name']} - {leaf['category']} ({leaf['start_date']})"):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        c1.write(f"**الفترة:** من {leaf['start_date']} إلى {leaf['end_date']}")
                        c1.write(f"**الملاحظات:** {leaf['notes'] or 'لا يوجد'}")
                        
                        status_color = "#f59e0b" if leaf['status'] == 'Pending' else "#10b981" if leaf['status'] == 'Approved' else "#ef4444"
                        c2.markdown(f"الحالة: <span style='color:{status_color}; font-weight:bold;'>{leaf['status']}</span>", unsafe_allow_html=True)
                        
                        if leaf['status'] == 'Approved':
                            if c3.button("🗑️ حذف", key=f"del_{leaf['id']}"):
                                supabase.table("leaves_missions").delete().eq("id", leaf['id']).execute()
                                st.rerun()
                        else:
                            btn_col1, btn_col2 = c3.columns(2)
                            if btn_col1.button("✅", key=f"app_{leaf['id']}"):
                                supabase.table("leaves_missions").update({"status": "Approved"}).eq("id", leaf['id']).execute()
                                st.rerun()
                            if btn_col2.button("❌", key=f"rej_{leaf['id']}"):
                                supabase.table("leaves_missions").update({"status": "Rejected"}).eq("id", leaf['id']).execute()
                                st.rerun()
        except Exception as ex:
            st.error(f"خطأ في تحميل البيانات: {ex}")

# ══════════════════════════════════════════
# صفحة: ملخص الموظف + تقرير PDF
# ══════════════════════════════════════════
def page_summary():
    if not can("summary"): denied(); return
 
    st.markdown('<div class="section-header">📄 ملخص وتقرير الموظف</div>', unsafe_allow_html=True)
    user = st.session_state["user"]

    # جلب بيانات الموظفين للاختيار منها
    df_e_all = fetch("employees")
    if df_e_all.empty:
        st.warning("⚠️ قاعدة بيانات الموظفين فارغة."); return

    # تصفية الموظفين حسب الفرع إذا لزم الأمر
    branch_filter = user.get("branch_filter")
    if branch_filter and user["role"] != "admin":
        df_e_all = df_e_all[df_e_all['branch'] == branch_filter]

    # إنشاء قائمة الاختيارات: الاسم - #الكود
    emp_options = {f"{e['name']} - #{e['device_id']}": str(e['device_id']) for _, e in df_e_all.iterrows()}
    
    st.markdown("<h4 style='color: #1e3a5f; margin-bottom: 15px;'>🔍 معايير الاستعلام</h4>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.5, 1, 1])
    
    selected_option = col1.selectbox("👤 ابحث عن الموظف:", options=[""] + list(emp_options.keys()), 
                                     placeholder="اختر موظفاً أو ابحث بالاسم...")
    
    start_date = col2.date_input("📅 من تاريخ:", value=datetime.date.today().replace(day=1))
    end_date   = col3.date_input("📅 إلى تاريخ:", value=datetime.date.today())

    st.markdown("<hr style='border: 1px solid #e2e8f0; margin-top: 5px; margin-bottom: 25px;'>", unsafe_allow_html=True)

    if not selected_option:
        st.info("👈 يرجى اختيار موظف من القائمة أعلاه لعرض السجل التفصيلي والتقارير.")
        return

    # استخراج كود الموظف من الاختيار
    emp_code = emp_options[selected_option]
 
    filt = df_e_all[df_e_all['device_id'].astype(str) == emp_code]
    if filt.empty:
        st.error("بيانات الموظف غير متوفرة."); return
 
    emp = filt.iloc[0].to_dict()
 
    # جلب السجلات في النطاق الزمني بتصفية الشركة
    user_c_id = st.session_state.user['company_id']
    res = supabase.table("attendance_logs").select("*") \
        .eq("device_id", emp['device_id']) \
        .eq("company_id", user_c_id) \
        .gte("timestamp", str(start_date)) \
        .lte("timestamp", str(end_date) + "T23:59:59") \
        .execute()
    df_logs = pd.DataFrame(res.data)
 
    summary     = calc_attendance(df_logs, emp.get('branch',''))
    # تصحيح الخطأ بتمرير emp['device_id']
    absent_days = detect_absent_days(summary, start_date, end_date, emp['device_id'])
    
    # استخراج بيانات الغياب والإجازات للعرض في الـ KPIs
    real_absent = [d for d in absent_days if d['type'] == 'Absent']
    leaves_days = [d for d in absent_days if d['type'] == 'Leave']
 
    # كارت الموظف
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1e3a5f,#2563eb);border:none;
                border-radius:16px;padding:20px 24px;margin-bottom:20px;
                display:flex;justify-content:space-between;align-items:center;
                box-shadow:0 4px 166px rgba(37,99,235,0.25);">
      <div>
        <div style="color:white;font-size:22px;font-weight:900;">{emp.get('name','—')}</div>
        <div style="color:#bfdbfe;font-size:13px;margin-top:5px;">
          🏢 {emp.get('branch','—')} &nbsp;|&nbsp; 👤 {emp.get('role','موظف')}
        </div>
      </div>
      <div style="background:white;color:#2563eb;padding:10px 20px;border-radius:12px;
                  font-size:22px;font-weight:900;">#{emp.get('device_id','—')}</div>
    </div>
    """, unsafe_allow_html=True)
 
    if summary.empty and not absent_days:
        st.info("لا توجد سجلات في هذه الفترة.")
        return
 
    # KPIs
    total_hrs     = summary['الساعات'].sum() if not summary.empty else 0
    total_extra   = summary['إضافي'].sum() if not summary.empty else 0
    total_deficit = summary['عجز'].sum() if not summary.empty else 0
    total_late    = summary[summary['حالة']=='متأخر'].shape[0] if not summary.empty else 0
    complete_days = summary[summary['حالة']=='مكتمل'].shape[0] if not summary.empty else 0
    late_mins     = int(summary['تأخير_دقائق'].sum()) if not summary.empty else 0
 
    k = st.columns(6)
    metrics = [
        ("أيام العمل",     len(summary),        "#0099ff"),
        ("أيام مكتملة",   complete_days,        "#00d4aa"),
        ("إجمالي الساعات", f"{round(total_hrs,1)}h", "#00d4aa"),
        ("أيام تأخير",    total_late,           "#f59e0b"),
        ("دقائق التأخير", f"{late_mins}د",       "#f59e0b"),
        ("أيام غياب",     len(real_absent),     "#ef4444"),
    ]
    for col, (label, val, color) in zip(k, metrics):
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-value" style="color:{color}">{val}</div>
          <div class="kpi-label">{label}</div>
        </div>""", unsafe_allow_html=True)
 
    st.write("")
 
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 الرسوم البيانية", "📋 السجل التفصيلي",
                                        "🔴 الغياب", "📄 تصدير PDF"])
 
    with tab1:
        if summary.empty:
            st.info("لا توجد بيانات رسومية لهذه الفترة.")
        elif has_plotly:
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(summary.sort_values('التاريخ'), x='التاريخ', y='الساعات',
                             color='حالة', title="ساعات العمل اليومية",
                             color_discrete_map={'مكتمل':'#00d4aa','متأخر':'#f59e0b',
                                                 'عجز':'#ef4444','بصمة_واحدة':'#a855f7'})
                fig.add_hline(y=8, line_dash="dash", line_color="#94a3b8", annotation_text="8h")
                fig.update_layout(paper_bgcolor='white', plot_bgcolor='#f8fafc',
                                  font_color='#1e293b')
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                status_counts = summary['حالة'].value_counts().reset_index()
                status_counts.columns = ['الحالة','العدد']
                fig2 = px.pie(status_counts, values='العدد', names='الحالة',
                              title="توزيع الحالات",
                              color_discrete_sequence=['#00d4aa','#f59e0b','#ef4444','#a855f7'])
                fig2.update_layout(paper_bgcolor='white', font_color='#1e293b')
                st.plotly_chart(fig2, use_container_width=True)
 
            # تأخير تراكمي
            late_df = summary[summary['تأخير_دقائق'] > 0].sort_values('التاريخ')
            if not late_df.empty:
                fig3 = px.bar(late_df, x='التاريخ', y='تأخير_دقائق',
                              title="دقائق التأخير اليومية",
                              color_discrete_sequence=['#f59e0b'])
                fig3.update_layout(paper_bgcolor='white', plot_bgcolor='#f8fafc',
                                   font_color='#1e293b')
                st.plotly_chart(fig3, use_container_width=True)
 
    with tab2:
        if summary.empty:
            st.info("لا توجد سجلات حضور.")
        else:
            disp = summary.copy()
            disp['حضور']    = disp['حضور'].dt.strftime('%I:%M %p')
            disp['انصراف'] = disp.apply(
                lambda x: x['انصراف'].strftime('%I:%M %p') if x['انصراف'] is not None else "—", axis=1)
            disp['تأخير']  = disp['تأخير_دقائق'].apply(lambda x: f"{x} د" if x > 0 else "—")
            disp['فرع']    = disp.apply(
                lambda x: f"🔀 {x['فرع_البصمة']}" if x['تقاطع_فروع'] else x['فرع_البصمة'], axis=1)
    
            st.dataframe(
                disp[['التاريخ','حضور','انصراف','الساعات','إضافي','عجز','تأخير','حالة','فرع']],
                use_container_width=True, hide_index=True)
 
    with tab3:
        if absent_days:
            # عرض أيام الغياب الفعلي
            if real_absent:
                st.error(f"🔴 أيام الغياب الفعلي: **{len(real_absent)} يوم**")
            
            # عرض الإجازات والمأموريات
            if leaves_days:
                st.info(f"🛳️ أيام الإجازات والمأموريات المعتمدة: **{len(leaves_days)} يوم**")

            absent_df = pd.DataFrame(absent_days)
            absent_df['اليوم'] = pd.to_datetime(absent_df['date']).dt.strftime('%A')
            day_ar = {'Monday':'الاثنين','Tuesday':'الثلاثاء','Wednesday':'الأربعاء',
                      'Thursday':'الخميس','Friday':'الجمعة'}
            absent_df['اليوم'] = absent_df['اليوم'].map(day_ar).fillna(absent_df['اليوم'])
            
            st.dataframe(
                absent_df.rename(columns={'date':'التاريخ', 'reason':'الحالة / السبب'}).drop(columns=['type']),
                use_container_width=True, hide_index=True)
        else:
            st.success("✅ لا توجد أيام غياب أو إجازات في هذه الفترة!")
 
    with tab4:
        st.write("### 📄 تصدير تقرير احترافي PDF")
        report_type = st.selectbox("نوع التقرير", ["شهري","أسبوعي","مخصص"])
        if st.button("🖨️ توليد PDF الآن", type="primary"):
            with st.spinner("جاري إنشاء التقرير..."):
                pdf_bytes = generate_pdf(emp, summary, absent_days, report_type)
            fname = f"تقرير_{emp.get('name','موظف')}_{start_date}_{end_date}.pdf"
            st.download_button("📥 تحميل التقرير", pdf_bytes, fname, mime="application/pdf")
            st.success("✅ التقرير جاهز للتحميل!")
 
        # تقرير Excel
        if not summary.empty:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as w:
                ex = summary.copy()
                ex['حضور']    = ex['حضور'].dt.tz_localize(None)
                ex['انصراف'] = ex['انصراف'].apply(
                    lambda x: x.tz_localize(None) if x is not None else None)
                ex.to_excel(w, index=False, sheet_name='الحضور')
                if absent_days:
                    pd.DataFrame([{'التاريخ': d['date'], 'الحالة': d['reason']} for d in absent_days]).to_excel(
                        w, index=False, sheet_name='الغياب')
            st.download_button("📊 تحميل Excel", buf.getvalue(), f"سجل_{emp['name']}.xlsx")
        else:
            st.info("لا توجد بيانات حضور لتصديرها كـ Excel في هذه الفترة.")
 
# ══════════════════════════════════════════
# صفحة: تقارير الفروع الذكية
# ══════════════════════════════════════════
def page_branch_reports():
    if not can("stats"): denied(); return
 
    st.markdown('<div class="section-header">🏢 لوحة تحكم الفروع</div>', unsafe_allow_html=True)
 
    user          = st.session_state["user"]
    branch_filter = user.get("branch_filter")
 
    df_e = fetch("employees")
    df_l = fetch("attendance_logs")
    if df_e.empty or df_l.empty:
        st.info("لا توجد بيانات كافية."); return
 
    if branch_filter and user["role"] != "admin":
        df_e = df_e[df_e['branch'] == branch_filter]
 
    branches = sorted(df_e['branch'].dropna().unique().tolist()) if 'branch' in df_e.columns else []
 
    col1, col2 = st.columns([2,1])
    selected_branches = col1.multiselect("اختر الفروع", branches, default=branches[:3] if len(branches)>=3 else branches)
    period = col2.selectbox("الفترة", ["آخر 30 يوم","آخر 7 أيام","هذا الشهر"])
 
    end_date   = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30 if "30" in period else 7)
 
    if not selected_branches:
        st.info("اختر فرعاً واحداً على الأقل."); return
 
    # حساب إحصائيات كل فرع
    branch_stats = []
    for branch in selected_branches:
        emp_ids = df_e[df_e['branch']==branch]['device_id'].astype(str).tolist()
        b_logs  = df_l[df_l['device_id'].astype(str).isin(emp_ids)].copy()
        b_logs  = b_logs[b_logs['timestamp'] >= str(start_date)] if not b_logs.empty else b_logs
 
        emp_count   = len(emp_ids)
        total_stamps= len(b_logs)
        cross_stamps= len(b_logs[b_logs['location'] != branch]) if 'location' in b_logs.columns and not b_logs.empty else 0
 
        branch_stats.append({
            'الفرع':       branch,
            'الموظفون':    emp_count,
            'حركات البصمة':total_stamps,
            'تبصيم خارجي': cross_stamps,
        })
 
    df_stats = pd.DataFrame(branch_stats)
 
    # KPIs المقارنة
    st.write("#### مقارنة الفروع")
    k = st.columns(len(selected_branches))
    for col, (_, row) in zip(k, df_stats.iterrows()):
        col.markdown(f"""
        <div class="kpi-card">
          <div style="font-size:15px;font-weight:900;color:#1e3a5f;margin-bottom:8px;">{row['الفرع']}</div>
          <div class="kpi-value" style="color:#2563eb;font-size:26px;">{row['الموظفون']}</div>
          <div class="kpi-label">موظف</div>
          <hr style="border-color:#e2e8f0;margin:10px 0;">
          <div style="color:#059669;font-size:13px;font-weight:700;">{row['حركات البصمة']} بصمة</div>
          <div style="color:#d97706;font-size:12px;margin-top:4px;">{row['تبصيم خارجي']} خارج الفرع</div>
        </div>""", unsafe_allow_html=True)
 
    st.write("")
 
    if has_plotly:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(df_stats, x='الفرع', y='الموظفون',
                         title="عدد الموظفين لكل فرع",
                         color='الفرع', color_discrete_sequence=['#0099ff','#00d4aa','#f59e0b','#a855f7','#ef4444'])
            fig.update_layout(paper_bgcolor='white', plot_bgcolor='#f8fafc', font_color='#1e293b')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.bar(df_stats, x='الفرع', y='حركات البصمة',
                          title="نشاط البصمة لكل فرع",
                          color='الفرع', color_discrete_sequence=['#00d4aa','#0099ff','#f59e0b','#a855f7','#ef4444'])
            fig2.update_layout(paper_bgcolor='white', plot_bgcolor='#f8fafc', font_color='#1e293b')
            st.plotly_chart(fig2, use_container_width=True)
 
    # جدول التبصيم الخارجي (تنبيه)
    if df_l is not None and 'location' in df_l.columns and not df_l.empty:
        cross = df_l.copy()
        cross['device_id'] = cross['device_id'].astype(str)
        cross = cross.merge(df_e[['device_id','name','branch']].astype({'device_id':str}),
                            on='device_id', how='left')
        cross = cross[cross['location'] != cross['branch']].dropna(subset=['branch'])
        if not cross.empty:
            st.write("#### ⚠️ حالات التبصيم خارج الفرع")
            st.dataframe(cross[['name','branch','location','timestamp']].rename(
                columns={'name':'الاسم','branch':'فرع الموظف',
                         'location':'فرع البصمة','timestamp':'الوقت'}
            ).head(50), use_container_width=True, hide_index=True)
 
# ══════════════════════════════════════════
# صفحة: تقرير التأخير والغياب الجماعي
# ══════════════════════════════════════════
def page_smart_reports():
    if not can("stats"): denied(); return
 
    st.markdown('<div class="section-header">📊 التقارير الذكية</div>', unsafe_allow_html=True)
 
    user = st.session_state["user"]
    df_e = fetch("employees")
    df_l = fetch("attendance_logs")
 
    if df_e.empty or df_l.empty:
        st.info("لا توجد بيانات كافية."); return
 
    branch_filter = user.get("branch_filter")
    if branch_filter and user["role"] != "admin":
        df_e = df_e[df_e['branch'] == branch_filter]
 
    col1, col2, col3 = st.columns(3)
    branches = ["الكل"] + sorted(df_e['branch'].dropna().unique().tolist())
    sel_branch = col1.selectbox("الفرع", branches)
    start_date = col2.date_input("من", value=datetime.date.today().replace(day=1))
    end_date   = col3.date_input("إلى", value=datetime.date.today())
 
    report_choice = st.radio("نوع التقرير", ["تقرير التأخير","تقرير الغياب","تقرير الإضافي","ملخص شامل"],
                             horizontal=True)
 
    if sel_branch != "الكل":
        df_e = df_e[df_e['branch'] == sel_branch]
 
    if st.button("🔍 توليد التقرير", type="primary"):
        results = []
        progress = st.progress(0)
        emps = df_e.to_dict('records')
 
        for i, emp in enumerate(emps):
            emp_id  = str(emp['device_id'])
            emp_logs= df_l[df_l['device_id'].astype(str) == emp_id].copy()
            emp_logs= emp_logs[
                (emp_logs['timestamp'] >= str(start_date)) &
                (emp_logs['timestamp'] <= str(end_date) + "T23:59:59")
            ]
            summ   = calc_attendance(emp_logs, emp.get('branch',''))
            absent = detect_absent_days(summ, start_date, end_date, emp_id)
 
            results.append({
                'الاسم':           emp.get('name','—'),
                'الفرع':           emp.get('branch','—'),
                'الكود':           emp_id,
                'أيام العمل':      len(summ),
                'أيام مكتملة':     summ[summ['حالة']=='مكتمل'].shape[0] if not summ.empty else 0,
                'أيام تأخير':      summ[summ['حالة']=='متأخر'].shape[0] if not summ.empty else 0,
                'دقائق التأخير':   int(summ['تأخير_دقائق'].sum()) if not summ.empty else 0,
                'إجمالي الساعات':  round(summ['الساعات'].sum(),1) if not summ.empty else 0,
                'ساعات إضافي':     round(summ['إضافي'].sum(),1) if not summ.empty else 0,
                'ساعات عجز':       round(summ['عجز'].sum(),1) if not summ.empty else 0,
                'أيام غياب':       len(absent),
                'نسبة الالتزام':   f"{round(summ[summ['حالة']=='مكتمل'].shape[0]/max(len(summ),1)*100)}%" if not summ.empty else "0%",
            })
            progress.progress((i+1)/len(emps))
 
        df_result = pd.DataFrame(results)
 
        # عرض حسب نوع التقرير
        if report_choice == "تقرير التأخير":
            df_show = df_result[df_result['أيام تأخير'] > 0] \
                        .sort_values('دقائق التأخير', ascending=False)
            st.error(f"⏰ {len(df_show)} موظف لديهم تأخير")
        elif report_choice == "تقرير الغياب":
            df_show = df_result[df_result['أيام غياب'] > 0] \
                        .sort_values('أيام غياب', ascending=False)
            st.error(f"🔴 {len(df_show)} موظف لديهم غياب")
        elif report_choice == "تقرير الإضافي":
            df_show = df_result[df_result['ساعات إضافي'] > 0] \
                        .sort_values('ساعات إضافي', ascending=False)
            st.success(f"⬆️ {len(df_show)} موظف لديهم ساعات إضافي")
        else:
            df_show = df_result.sort_values('نسبة الالتزام', ascending=False)
 
        st.dataframe(df_show, use_container_width=True, hide_index=True)
 
        # تصدير Excel
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as w:
            df_show.to_excel(w, index=False, sheet_name=report_choice)
        st.download_button(f"📥 تحميل {report_choice} Excel",
                           buf.getvalue(), f"{report_choice}.xlsx")
 
# ══════════════════════════════════════════
# صفحات: استيراد / موظفين / مستخدمين
# ══════════════════════════════════════════
def page_import():
    if not can("import"): denied(); return
    st.markdown('<div class="section-header">📥 استيراد بيانات الماكينة</div>', unsafe_allow_html=True)
 
    up = st.file_uploader("ارفع ملف XLS من جهاز البصمة", type=['xlsx','xls','csv'])
    if not up: return
    try:
        df_raw = pd.read_csv(up, header=None) if up.name.endswith('.csv') else pd.read_excel(up, header=None)
        idx    = next((i for i, row in df_raw.iterrows()
                       if 'No.' in [str(v).strip() for v in row.values]), None)
        if idx is None: st.error("لم يُعثر على رأس الجدول (No.)"); return
 
        df_zk = df_raw.iloc[idx:].copy()
        df_zk.columns = df_zk.iloc[0]
        df_zk = df_zk.iloc[1:].reset_index(drop=True)
 
        st.info(f"تم قراءة **{len(df_zk)}** سجل")
        st.dataframe(df_zk.head(8), use_container_width=True)
 
        if st.button("🚀 نقل إلى السحابة", type="primary"):
            with st.spinner("جاري الرفع..."):
                logs = []
                for _, row in df_zk.iterrows():
                    if pd.isna(row.get('No.')): continue
                    dt = row.get('Date/Time')
                    if pd.notna(dt):
                        logs.append({
                            "device_id": str(row['No.']).split('.')[0].strip(),
                            "timestamp": pd.to_datetime(dt).isoformat(),
                            "location":  str(row.get('Area', row.get('Location','غير محدد')))
                        })
                user_c_id = st.session_state.user['company_id']
                for i in range(0, len(logs), 400):
                    # حقن معرف الشركة في كل سجل
                    chunk = logs[i:i+400]
                    for item in chunk: item['company_id'] = user_c_id
                    supabase.table("attendance_logs").insert(chunk).execute()
                    bar.progress(min((i+400)/len(logs), 1.0))
                st.success(f"✅ تم ترحيل {len(logs)} حركة!")
    except Exception as e:
        st.error(f"خطأ: {e}")
 
def page_upload_employees():
    if not can("upload_employees"): denied(); return
    st.markdown('<div class="section-header">👥 رفع بيانات الموظفين</div>', unsafe_allow_html=True)
 
    up = st.file_uploader("ارفع ملف الموظفين", type=['xlsx','xls','csv'])
    if not up:
        tmpl = pd.DataFrame({'No':['101'],'Name':['محمد أحمد'],'Branch':['فرع القاهرة']})
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as w: tmpl.to_excel(w, index=False)
        st.download_button("📥 تحميل قالب", buf.getvalue(), "template.xlsx")
        return
 
    df_new = pd.read_csv(up) if up.name.endswith('.csv') else pd.read_excel(up)
    st.dataframe(df_new.head(6), use_container_width=True)
 
    cols_l = {str(c).strip().lower(): c for c in df_new.columns}
    def fc(kws):
        for kw in kws:
            for k, v in cols_l.items():
                if kw in k: return v
        return None
 
    id_col = fc(['no','id','كود','رقم','device'])
    nm_col = fc(['name','اسم'])
    br_col = fc(['branch','فرع','location','موقع','area'])
 
    with st.expander("⚙️ تحديد الأعمدة"):
        ac = list(df_new.columns)
        id_col = st.selectbox("كود", ac, index=ac.index(id_col) if id_col in ac else 0)
        nm_col = st.selectbox("الاسم", ac, index=ac.index(nm_col) if nm_col in ac else 0)
        br_col = st.selectbox("الفرع", ac, index=ac.index(br_col) if br_col in ac else 0)
 
    prev = df_new[[id_col,nm_col,br_col]].copy()
    prev.columns = ['كود','اسم','فرع']
    prev['كود'] = prev['كود'].astype(str).str.split('.').str[0].str.strip()
    prev = prev[prev['كود'].str.len()>0].drop_duplicates('كود')
 
    df_ex = fetch("employees")
    if not df_ex.empty and 'device_id' in df_ex.columns:
        ex = set(df_ex['device_id'].astype(str))
        nw = set(prev['كود'])
        st.info(f"➕ جديد: {len(nw-ex)} | 🔄 تحديث: {len(nw&ex)}")
 
    st.dataframe(prev, use_container_width=True, hide_index=True)
    if st.button("🚀 رفع", type="primary"):
        bar, ok = st.progress(0), 0
        user_c_id = st.session_state.user['company_id']
        for i,(_, row) in enumerate(prev.iterrows()):
            try:
                supabase.table("employees").upsert(
                    {"device_id":row['كود'],"name":row['اسم'],"branch":row['فرع'], "company_id": user_c_id},
                    on_conflict="device_id").execute()
                ok += 1
            except: pass
            bar.progress((i+1)/max(len(prev),1))
        st.success(f"✅ تم رفع {ok} موظف!")
 
def page_manage_users():
    if st.session_state["user"]["role"] != "admin": denied(); return
    st.markdown('<div class="section-header">👤 إدارة المستخدمين والصلاحيات</div>', unsafe_allow_html=True)
 
    ALL_PERMS = {
        "summary":          "🔍 ملخص الموظف",
        "import":           "📥 استيراد بيانات الماكينة",
        "upload_employees": "👥 رفع بيانات الموظفين",
        "stats":            "📊 التقارير والإحصائيات",
    }
 
    tab1, tab2 = st.tabs(["📋 المستخدمون", "➕ إضافة مستخدم"])
 
    with tab1:
        df_u = fetch("app_users")
        if df_u.empty: st.info("لا يوجد مستخدمون."); return
        for _, u in df_u.iterrows():
            with st.expander(f"{'👑' if u['role']=='admin' else '👤'} {u['full_name']} (@{u['username']}) — {'✅' if u.get('is_active') else '🔴'}"):
                c1, c2 = st.columns([2,1])
                with c1:
                    if u['role'] != 'admin':
                        curr = u.get('permissions') or []
                        nw   = []
                        pc   = st.columns(2)
                        for ii,(pk,pl) in enumerate(ALL_PERMS.items()):
                            if pc[ii%2].checkbox(pl, value=(pk in curr), key=f"p_{u['id']}_{pk}"):
                                nw.append(pk)
                        df_e2  = fetch("employees")
                        brs    = ["جميع الفروع"] + (sorted(df_e2['branch'].dropna().unique().tolist())
                                                    if not df_e2.empty and 'branch' in df_e2.columns else [])
                        cb     = u.get('branch_filter') or "جميع الفروع"
                        sb     = st.selectbox("🏢 الفرع", brs,
                                             index=brs.index(cb) if cb in brs else 0,
                                             key=f"b_{u['id']}")
                        if st.button("💾 حفظ", key=f"sv_{u['id']}"):
                            supabase.table("app_users").update({
                                "permissions": nw,
                                "branch_filter": None if sb=="جميع الفروع" else sb
                            }).eq("id",u['id']).execute()
                            st.success("✅ تم!"); st.rerun()
                with c2:
                    act = bool(u.get('is_active',True))
                    if u['username']!='admin' and st.button("🔴 إيقاف" if act else "🟢 تفعيل", key=f"t_{u['id']}"):
                        supabase.table("app_users").update({"is_active":not act}).eq("id",u['id']).execute()
                        st.rerun()
                    npw = st.text_input("🔑 كلمة مرور جديدة", type="password", key=f"pw_{u['id']}")
                    if npw and st.button("تحديث", key=f"upw_{u['id']}"):
                        supabase.table("app_users").update({"password":hash_pw(npw)}).eq("id",u['id']).execute()
                        st.success("✅ تم!")
 
    with tab2:
        with st.form("add_user"):
            c1,c2 = st.columns(2)
            fn  = c1.text_input("الاسم الكامل")
            un  = c2.text_input("اسم المستخدم")
            pw  = c1.text_input("كلمة المرور", type="password")
            rl  = c2.selectbox("الدور", ["user","admin"])
            df_e3 = fetch("employees")
            brs2 = ["جميع الفروع"] + (sorted(df_e3['branch'].dropna().unique().tolist())
                                       if not df_e3.empty and 'branch' in df_e3.columns else [])
            sb2  = st.selectbox("الفرع", brs2)
            ip   = []
            pc2  = st.columns(3)
            for ii2,(pk,pl) in enumerate(ALL_PERMS.items()):
                if pc2[ii2%3].checkbox(pl, key=f"np_{pk}"): ip.append(pk)
            sub  = st.form_submit_button("➕ إنشاء", use_container_width=True)
        if sub:
            if not fn or not un or not pw: st.error("أكمل الحقول المطلوبة")
            else:
                try:
                    supabase.table("app_users").insert({
                        "username":un.strip(),"password":hash_pw(pw),
                        "full_name":fn.strip(),"role":rl,
                        "permissions":[] if rl=="admin" else ip,
                        "is_active":True,
                        "branch_filter": None if sb2=="جميع الفروع" else sb2
                    }).execute()
                    st.success(f"✅ تم إنشاء @{un}!"); st.rerun()
                except Exception as e:
                    st.error(f"خطأ: {e}")
 
# ══════════════════════════════════════════
# صفحة تسجيل الدخول
# ══════════════════════════════════════════
def login_page():
    st.markdown("""
    <style>
    /* Full dark premium background for login only */
    .stApp {
        background: #0f172a !important;
        background-image: radial-gradient(circle at 50% 0%, #1e3a8a 0%, #0f172a 70%) !important;
    }
    
    /* Hide top padding to center the card vertically */
    .block-container {
        padding-top: 5rem !important;
    }
    
    /* Floating Login Card */
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.98) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 24px !important;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5) !important;
        padding: 45px 40px !important;
        backdrop-filter: blur(20px) !important;
    }
    
    /* Inputs Styling */
    .stTextInput label p {
        font-weight: 700 !important;
        color: #475569 !important;
        font-size: 15px !important;
        margin-bottom: 2px !important;
    }
    .stTextInput input {
        background: #f8fafc !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        padding: 14px 16px !important;
        transition: all 0.2s ease;
    }
    .stTextInput input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 4px rgba(37,99,235,0.15) !important;
        background: #ffffff !important;
    }
    
    /* Premium Gold Button */
    .stButton button {
        background: linear-gradient(135deg, #d4af37, #b8860b) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        padding: 12px !important;
        margin-top: 15px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(184, 134, 11, 0.3) !important;
    }
    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(184, 134, 11, 0.5) !important;
        color: white !important;
    }
    .stButton button * {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("login"):
            st.markdown("""
            <div style="text-align:center; margin-bottom: 35px;">
                <div style="font-size:65px; margin-bottom: 5px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">🚢</div>
                <div style="color:#0f172a; font-size:38px; font-weight:900; letter-spacing: -0.5px;">قاصد خير</div>
                <div style="color:#64748b; font-size:14px; font-weight:700; margin-top:5px; text-transform: uppercase; letter-spacing: 1.5px;">
                    Enterprise Fleet & HR Management
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            u  = st.text_input("👤 اسم المستخدم", placeholder="أدخل اسم المستخدم هنا")
            p  = st.text_input("🔑 كلمة المرور",  type="password", placeholder="••••••••")
            
            ok = st.form_submit_button("تسجيل الدخول", use_container_width=True)
            
        if ok:
            if not u or not p: 
                st.error("⚠️ برجاء إدخال اسم المستخدم وكلمة المرور")
                return
            try:
                # تفعيل التعددية: جلب المستخدم مع بيانات الشركة المرتبطة به
                r = supabase.table("app_users").select("*, companies(name, logo_url)") \
                    .eq("username",u.strip()).eq("password",hash_pw(p)) \
                    .eq("is_active",True).execute()
                if r.data:
                    user_data = r.data[0]
                    st.session_state["user"] = {
                        "id": user_data["id"],
                        "username": user_data["username"],
                        "full_name": user_data["full_name"],
                        "role": user_data["role"],
                        "permissions": user_data["permissions"] or [],
                        "branch_filter": user_data.get("branch_filter"),
                        "company_id": user_data["company_id"],
                        "company_name": user_data["companies"]["name"] if user_data.get("companies") else "MA SOLUTIONS",
                        "company_logo": user_data["companies"]["logo_url"] if user_data.get("companies") else None
                    }
                    st.session_state["logged_in"] = True
                    try:
                        supabase.table("app_users").update(
                            {"last_login": datetime.datetime.now().isoformat()}
                        ).eq("id", user_data["id"]).execute()
                    except: pass
                    st.rerun()
                else:
                    st.error("❌ بيانات الدخول غير صحيحة أو الحساب موقوف")
            except Exception as e:
                st.error(f"خطأ في الاتصال: {e}")
                
        st.markdown(f"""
        <div style="text-align: center; margin-top: 25px; color: #94a3b8; font-size: 13px; font-weight: 600;">
            للدخول الأول: admin / admin123<br>
            <span style="opacity: 0.5;">© 2026 MA SOLUTIONS Automation Systems</span>
        </div>
        """, unsafe_allow_html=True)
 
# ══════════════════════════════════════════
# التطبيق الرئيسي
# ══════════════════════════════════════════
def main():
    ensure_admin()
    if not st.session_state.get("logged_in"):
        login_page(); return
 
    user  = st.session_state["user"]
    role  = user.get("role","user")
    perms = user.get("permissions") or []
 
    with st.sidebar:
        # الهوية الديناميكية للشركة
        c_name = user.get("company_name", "MA SOLUTIONS")
        c_logo = user.get("company_logo", "📊") # افتراضي إذا لم يوجد شعار
        
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 30px; margin-top: 10px;">
            <div style="font-size: 55px; line-height: 1; margin-bottom: 10px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.4));">{c_logo if c_logo and len(c_logo) < 5 else '📊'}</div>
            <div style="font-size: 26px; font-weight: 900; color: white; letter-spacing: -0.5px;">{c_name}</div>
            <div style="font-size: 11px; color: #94a3b8; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 4px; font-weight: 700;">Automation & HR Systems</div>
        </div>
        """, unsafe_allow_html=True)

        badge = "linear-gradient(135deg, #d4af37, #b8860b)" if role=="admin" else "rgba(255,255,255,0.1)"
        label = "أدمن"       if role=="admin" else "مستخدم"
        br_note = f'<div style="color:#cbd5e1; font-size:11px; margin-top:6px; display:flex; align-items:center; gap:4px;"><span>📍</span> {user["branch_filter"]}</div>' if user.get("branch_filter") else ""
        
        st.markdown(f"""
        <div style="padding: 18px; background: rgba(255, 255, 255, 0.04); border-radius: 16px;
                    margin-bottom: 30px; border: 1px solid rgba(255, 255, 255, 0.08);
                    box-shadow: 0 10px 25px rgba(0,0,0,0.2); backdrop-filter: blur(10px);">
          <div style="display: flex; align-items: center; margin-bottom: 14px;">
              <div style="font-size: 32px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2)); margin-left: 12px;">{'👑' if role=='admin' else '👤'}</div>
              <div>
                  <div style="color: white; font-weight: 900; font-size: 15px; letter-spacing: 0.3px;">
                    {user.get('full_name','—')}
                  </div>
                  <div style="color: #94a3b8; font-size: 12px; margin-top: 2px;">@{user.get('username','—')}</div>
              </div>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 12px;">
            <span style="background: {badge}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 800; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
                {label}
            </span>
            {br_note}
          </div>
        </div>
        """, unsafe_allow_html=True)

        pages = []
        if role=="admin" or "summary"          in perms: pages.append("🏠 الشاشة الرئيسية")
        if role=="admin" or "summary"          in perms: pages.append("👤 ملخص الموظف")
        if role=="admin" or "stats"            in perms: pages.append("🏢 لوحة الفروع")
        if role=="admin" or "stats"            in perms: pages.append("📈 التقارير الذكية")
        if role=="admin" or "import"           in perms: pages.append("📥 استيراد البيانات")
        if role=="admin" or "upload_employees" in perms: pages.append("👥 بيانات الموظفين")
        if role=="admin":                                 pages.append("🛳️ الإجازات والمأموريات")
        if role=="admin":                                 pages.append("💰 الأجور والرواتب")
        if role=="admin":                                 pages.append("⚙️ إدارة المستخدمين")

        if not pages:
            st.warning("لا توجد صلاحيات. تواصل مع الأدمن.")
            if st.button("🚪 خروج"): st.session_state.clear(); st.rerun()
            return

        st.markdown("<div style='color: #94a3b8; font-size: 12px; font-weight: 700; margin-bottom: 8px; margin-right: 4px;'>القائمة الرئيسية</div>", unsafe_allow_html=True)
        choice = st.selectbox("الصفحة:", pages, label_visibility="collapsed")
        
        st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.05); margin-top: 30px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.clear(); st.rerun()
 
    routing = {
        "🏠 الشاشة الرئيسية":          page_home_dashboard,
        "👤 ملخص الموظف":            page_summary,
        "🏢 لوحة الفروع":             page_branch_reports,
        "📈 التقارير الذكية":          page_smart_reports,
        "📥 استيراد البيانات":         page_import,
        "👥 بيانات الموظفين":          page_upload_employees,
        "🛳️ الإجازات والمأموريات":      page_manage_leaves,
        "💰 الأجور والرواتب":          page_payroll,
        "⚙️ إدارة المستخدمين":         page_manage_users,
    }
    routing.get(choice, page_home_dashboard)()

# ══════════════════════════════════════════
# صفحة: الأجور والرواتب
# ══════════════════════════════════════════
def page_payroll():
    if not can("admin"): denied(); return
    
    st.markdown('<div class="section-header">💰 إدارة الأجور والرواتب</div>', unsafe_allow_html=True)
    
    tab_settings, tab_process, tab_payslip = st.tabs(["⚙️ إعدادات الرواتب", "📊 مسير الرواتب الشهري", "📄 مفردات مرتب"])
    
    df_e = fetch("employees")
    
    with tab_settings:
        st.subheader("تعديل البيانات المالية للموظف")
        emp_list = {f"{e['device_id']} - {e['name']}": e['device_id'] for _, e in df_e.iterrows()}
        selected_emp = st.selectbox("اختر الموظف:", options=list(emp_list.keys()), key="sal_emp")
        
        # جلب البيانات الحالية
        dev_id = emp_list[selected_emp]
        res = supabase.table("salaries").select("*").eq("device_id", dev_id).execute()
        curr = res.data[0] if res.data else {"base_salary":0, "transport_allowance":0, "overtime_rate":0, "late_rate":0, "hourly_rate":0}
        
        with st.form("salary_form"):
            c1, c2 = st.columns(2)
            base = c1.number_input("الراتب الأساسي (جم):", value=float(curr['base_salary']))
            trans = c2.number_input("بدل انتقال (جم):", value=float(curr['transport_allowance']))
            
            c3, c4, c5 = st.columns(3)
            ot_r = c3.number_input("سعر ساعة الإضافي:", value=float(curr['overtime_rate']))
            late_r = c4.number_input("سعر دقيقة التأخير:", value=float(curr['late_rate']))
            def_r = c5.number_input("سعر ساعة العجز:", value=float(curr['hourly_rate']))
            
            if st.form_submit_button("💾 حفظ الإعدادات المالية"):
                user_c_id = st.session_state.user['company_id']
                supabase.table("salaries").upsert({
                    "device_id": dev_id, "base_salary": base, "transport_allowance": trans,
                    "overtime_rate": ot_r, "late_rate": late_r, "hourly_rate": def_r,
                    "company_id": user_c_id
                }).execute()
                st.success("✅ تم تحديث البيانات المالية بنجاح")
                st.rerun()

    with tab_process:
        c1, c2, c3 = st.columns([1, 1, 2])
        month = c1.selectbox("الشهر:", range(1, 13), index=datetime.date.today().month - 1)
        year = c2.selectbox("السنة:", range(2024, 2030), index=datetime.date.today().year - 2024)
        
        if c3.button("🚀 توليد مسير الرواتب", use_container_width=True, type="primary"):
            results = []
            with st.spinner("جاري حساب الرواتب لجميع الموظفين..."):
                for _, emp in df_e.iterrows():
                    pay = calculate_monthly_payroll(emp['device_id'], month, year)
                    if pay:
                        results.append({
                            "الكود": emp['device_id'],
                            "الاسم": emp['name'],
                            "الأساسي": pay['base'],
                            "إضافي": pay['ot_value'],
                            "إجمالي الاستحقاقات": pay['gross'],
                            "إجمالي الاستقطاعات": pay['total_deductions'],
                            "صافي المرتب": pay['net']
                        })
            
            if results:
                st.write(f"### 📋 مسير رواتب شهر {month} / {year}")
                st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
                
                # إحصائيات سريعة
                pdf = pd.DataFrame(results)
                k1, k2, k3 = st.columns(3)
                k1.metric("إجمالي الصافي", f"{round(pdf['صافي المرتب'].sum(), 2)} جم")
                k2.metric("إجمالي الإضافي", f"{round(pdf['إضافي'].sum(), 2)} جم")
                k3.metric("إجمالي الخصومات", f"{round(pdf['إجمالي الاستقطاعات'].sum(), 2)} جم")
            else:
                st.warning("لا توجد بيانات مالية مسجلة للموظفين. يرجى ضبط الإعدادات أولاً.")

    with tab_payslip:
        c1, c2, c3 = st.columns([2, 1, 1])
        ps_emp = c1.selectbox("اختر الموظف للمعاينة:", options=list(emp_list.keys()), key="ps_emp")
        ps_month = c2.selectbox("الشهر:", range(1, 13), index=datetime.date.today().month - 1, key="ps_m")
        ps_year = c3.selectbox("السنة:", range(2024, 2030), index=datetime.date.today().year - 2024, key="ps_y")
        
        if st.button("🔍 عرض بيان المرتب"):
            dev_id = emp_list[ps_emp]
            pay = calculate_monthly_payroll(dev_id, ps_month, ps_year)
            if not pay:
                st.error("لا توجد بيانات مالية لهذا الموظف.")
            else:
                st.markdown(f"""
                <div style="background: white; border: 2px solid #1e3a5f; border-radius: 12px; padding: 30px; color: #1e293b; direction: rtl;">
                    <div style="text-align: center; border-bottom: 2px solid #1e3a5f; padding-bottom: 15px; margin-bottom: 20px;">
                        <h2 style="color: #1e3a5f; margin: 0;">شركة قاصد خير للمقاولات والتوريدات البحرية</h2>
                        <h3 style="margin: 5px 0;">بيان مفردات مرتب عن شهر {ps_month} / {ps_year}</h3>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                        <div>
                            <b>الاسم:</b> {ps_emp.split(' - ')[1]} <br>
                            <b>كود الموظف:</b> {dev_id}
                        </div>
                        <div style="text-align: left;">
                            <b>تاريخ الإصدار:</b> {datetime.date.today()}
                        </div>
                    </div>
                    
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px;">
                        <tr style="background: #f1f5f9;">
                            <th style="border: 1px solid #cbd5e1; padding: 10px; text-align: right;">الاستحقاقات (Earnings)</th>
                            <th style="border: 1px solid #cbd5e1; padding: 10px; text-align: left;">المبلغ</th>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #cbd5e1; padding: 10px;">الراتب الأساسي</td>
                            <td style="border: 1px solid #cbd5e1; padding: 10px; text-align: left;">{pay['base']} جم</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #cbd5e1; padding: 10px;">بدل انتقال</td>
                            <td style="border: 1px solid #cbd5e1; padding: 10px; text-align: left;">{pay['allowance']} جم</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #cbd5e1; padding: 10px;">عمل إضافي ({pay['ot_hours']} ساعة)</td>
                            <td style="border: 1px solid #cbd5e1; padding: 10px; text-align: left;">{pay['ot_value']} جم</td>
                        </tr>
                        <tr style="background: #f8fafc; font-weight: bold;">
                            <td style="border: 1px solid #cbd5e1; padding: 10px;">إجمالي الاستحقاقات</td>
                            <td style="border: 1px solid #cbd5e1; padding: 10px; text-align: left;">{pay['gross']} جم</td>
                        </tr>
                    </table>
                    
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px;">
                        <tr style="background: #fff1f2;">
                            <th style="border: 1px solid #cbd5e1; padding: 10px; text-align: right; color: #be123c;">الاستقطاعات (Deductions)</th>
                            <th style="border: 1px solid #cbd5e1; padding: 10px; text-align: left; color: #be123c;">المبلغ</th>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #cbd5e1; padding: 10px;">تأخيرات</td>
                            <td style="border: 1px solid #cbd5e1; padding: 10px; text-align: left;">{pay['late_deduction']} جم</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #cbd5e1; padding: 10px;">ساعات عجز</td>
                            <td style="border: 1px solid #cbd5e1; padding: 10px; text-align: left;">{pay['deficit_deduction']} جم</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #cbd5e1; padding: 10px;">غياب غير مبرر ({pay['absent_days']} يوم)</td>
                            <td style="border: 1px solid #cbd5e1; padding: 10px; text-align: left;">{pay['absent_deduction']} جم</td>
                        </tr>
                        <tr style="background: #fff1f2; font-weight: bold;">
                            <td style="border: 1px solid #cbd5e1; padding: 10px;">إجمالي الاستقطاعات</td>
                            <td style="border: 1px solid #cbd5e1; padding: 10px; text-align: left;">{pay['total_deductions']} جم</td>
                        </tr>
                    </table>
                    
                    <div style="background: #1e3a5f; color: white; padding: 20px; border-radius: 8px; text-align: center; font-size: 24px; font-weight: bold;">
                        صافي الراتب المستحق: {pay['net']} جم
                    </div>
                </div>
                """, unsafe_allow_html=True)
 
if __name__ == "__main__":
    main()