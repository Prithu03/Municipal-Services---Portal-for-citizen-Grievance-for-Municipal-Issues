"""
app.py
------
Nagar Seva — Citizen Grievance Portal for Municipal Issues (India)

Run with:  streamlit run app.py
"""

import os
import io
from datetime import datetime

import streamlit as st
import pandas as pd

import database as db
import utils
from translations import t

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Nagar Seva | Citizen Grievance Portal", page_icon="🇮🇳", layout="wide")

db.init_db()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ADMIN_PASSWORD = "swachh2026"  # demo only — replace with proper auth & secrets management in production

if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "mobile" not in st.session_state:
    st.session_state.mobile = None
if "name" not in st.session_state:
    st.session_state.name = None
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False


def L(key):
    return t(key, st.session_state.lang)


# ---------------------------------------------------------------------------
# Sidebar — language, login, navigation
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🇮🇳 " + L("app_title"))
    st.caption(L("tagline"))

    lang_choice = st.radio("Language / भाषा", ["English", "हिंदी"], horizontal=True,
                            index=0 if st.session_state.lang == "en" else 1)
    st.session_state.lang = "en" if lang_choice == "English" else "hi"

    st.divider()

    if st.session_state.mobile is None:
        st.markdown(f"**{L('login_name')} / {L('login_mobile')}**")
        name_in = st.text_input(L("login_name"), key="login_name_input")
        mobile_in = st.text_input(L("login_mobile"), max_chars=10, key="login_mobile_input")
        ward_in = st.text_input(L("login_ward"), key="login_ward_input")
        city_in = st.text_input(L("login_city"), key="login_city_input")

        if not st.session_state.otp_sent:
            if st.button("📩 Send OTP / ओटीपी भेजें"):
                if mobile_in and len(mobile_in) == 10 and mobile_in.isdigit() and name_in:
                    st.session_state.otp_sent = True
                    st.session_state.pending_name = name_in
                    st.session_state.pending_mobile = mobile_in
                    st.session_state.pending_ward = ward_in
                    st.session_state.pending_city = city_in
                    st.info("Demo OTP sent: **123456** (In production this would use a "
                            "registered SMS gateway provider.)")
                else:
                    st.warning("Please enter your name and a valid 10-digit mobile number.")
        else:
            otp_in = st.text_input("Enter OTP / ओटीपी दर्ज करें", max_chars=6)
            if st.button(L("login_button")):
                if otp_in == "123456":
                    db.upsert_user(st.session_state.pending_name, st.session_state.pending_mobile,
                                    st.session_state.pending_ward, st.session_state.pending_city,
                                    st.session_state.lang)
                    st.session_state.mobile = st.session_state.pending_mobile
                    st.session_state.name = st.session_state.pending_name
                    st.session_state.otp_sent = False
                    st.rerun()
                else:
                    st.error("Incorrect OTP. (Hint for demo: 123456)")
    else:
        user = db.get_user(st.session_state.mobile)
        st.success(f"{L('welcome')}, {st.session_state.name} 👋")
        if user:
            st.metric(L("your_points"), user["points"])
        if st.button("Logout / लॉगआउट"):
            st.session_state.mobile = None
            st.session_state.name = None
            st.rerun()

    st.divider()
    page = st.radio(
        "Navigate",
        [L("nav_home"), L("nav_report"), L("nav_track"), L("nav_map"),
         L("nav_leaderboard"), L("nav_awareness"), L("nav_admin")],
    )

    st.divider()
    st.caption("🚨 Emergency Numbers")
    for label, number in list(utils.EMERGENCY_NUMBERS.items())[:4]:
        st.caption(f"{label}: **{number}**")


def require_login():
    if st.session_state.mobile is None:
        st.warning("Please log in from the sidebar (name + mobile + OTP) to continue.")
        st.stop()


# ---------------------------------------------------------------------------
# HOME
# ---------------------------------------------------------------------------

if page == L("nav_home"):
    st.title("🇮🇳 " + L("app_title"))
    st.markdown(f"#### {L('tagline')}")

    fest = utils.get_upcoming_festival(days_window=10)
    if fest:
        st.info(f"📅 **Upcoming: {fest['name']}** ({fest['date']}) — {fest['tip']}")

    stats = db.get_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("📋 " + L("total_reported"), stats["total"])
    c2.metric("🟢 " + L("total_resolved"), stats["resolved"])
    c3.metric("🟡 " + L("total_pending"), stats["pending"])

    st.markdown("---")
    st.markdown("""
    ### Why Nagar Seva?
    India's cities and towns run on the active participation of citizens. This portal lets you:
    - 📍 **Pin the exact location** of a civic issue (paste a Google Maps link or enter coordinates)
    - 📸 Attach a photo as evidence
    - 🔄 **Track status** end-to-end: Submitted → Acknowledged → In Progress → Resolved
    - 👍 **Upvote** existing reports instead of duplicating them, so officials see real community impact
    - 🏆 Earn **Swachh Citizen points** and see your ward climb a cleanliness leaderboard
    - 🗣️ Use the portal in **English or Hindi**, with more Indian languages plannable
    """)

    st.markdown("##### Departments & categories covered")
    cols = st.columns(3)
    for i, (cat, dept) in enumerate(utils.CATEGORIES.items()):
        with cols[i % 3]:
            st.caption(f"{cat} → *{dept}*")

# ---------------------------------------------------------------------------
# REPORT A GRIEVANCE
# ---------------------------------------------------------------------------

elif page == L("nav_report"):
    st.title(L("nav_report"))
    require_login()

    category = st.selectbox(L("category"), list(utils.CATEGORIES.keys()))
    description = st.text_area(L("description"), height=120,
                                placeholder="e.g., Garbage has not been collected for 5 days near Shastri Nagar bus stop...")

    suggested_priority = utils.detect_priority(description)
    if suggested_priority == "High":
        st.warning("⚠️ This sounds safety-critical — priority auto-set to **High**. "
                    "If this is a life-threatening emergency, please also call 112 immediately.")
    priority = st.select_slider("Priority", options=["Low", "Medium", "High"],
                                 value=suggested_priority)

    st.markdown(f"**{L('location_method')}**")
    loc_tab1, loc_tab2 = st.tabs(["📎 Paste Google Maps Link", "✍️ Enter Manually"])

    lat = lng = None
    with loc_tab1:
        maps_link = st.text_input("Paste a Google Maps share link or 'lat,lng' "
                                   "(e.g., shared via WhatsApp)")
        if maps_link:
            parsed = utils.parse_google_maps_link(maps_link)
            if parsed:
                lat, lng = parsed
                st.success(f"📍 Location detected: {lat}, {lng}")
                st.map(pd.DataFrame([{"lat": lat, "lon": lng}]), zoom=14)
            else:
                st.error("Could not read coordinates from that link/text. Try the Manual tab.")

    with loc_tab2:
        col_a, col_b = st.columns(2)
        man_lat = col_a.number_input("Latitude", value=0.0, format="%.6f", key="man_lat")
        man_lng = col_b.number_input("Longitude", value=0.0, format="%.6f", key="man_lng")
        if man_lat != 0.0 and man_lng != 0.0:
            lat, lng = man_lat, man_lng

    address = st.text_input("Landmark / Address (optional, helps the field team)")
    col1, col2 = st.columns(2)
    _user = db.get_user(st.session_state.mobile) if st.session_state.mobile else None
    ward = col1.text_input(L("login_ward"), value=(_user.get("ward", "") if _user else ""))
    city = col2.text_input(L("login_city"), value=(_user.get("city", "") if _user else ""))

    photo = st.file_uploader("📸 Attach a photo (optional)", type=["jpg", "jpeg", "png"])

    # Duplicate / nearby-issue check
    if lat and lng:
        nearby = db.find_nearby(lat, lng, category, radius_km=0.3)
        if nearby:
            st.info(f"ℹ️ {len(nearby)} similar open report(s) found within ~300m. "
                     "Consider upvoting instead of creating a duplicate:")
            for n in nearby[:3]:
                cols = st.columns([4, 1])
                cols[0].write(f"**{n['grievance_code']}** — {n['description'][:80]}... "
                               f"({utils.STATUS_COLORS.get(n['status'],'')} {n['status']}, "
                               f"👍 {n['upvote_count']})")
                if cols[1].button("👍 Upvote", key=f"up_{n['grievance_code']}"):
                    if db.add_upvote(n["grievance_code"], st.session_state.mobile):
                        db.add_points(st.session_state.mobile, utils.POINTS_FOR_UPVOTE)
                        st.success("Upvoted! Thanks for confirming this is a real, ongoing issue.")
                        st.rerun()
                    else:
                        st.warning("You've already upvoted this report.")

    if st.button(L("submit"), type="primary"):
        if not description.strip():
            st.error("Please describe the issue.")
        else:
            department = utils.CATEGORIES[category]
            code = db.create_grievance(
                mobile=st.session_state.mobile, name=st.session_state.name, category=category,
                description=description, lat=lat, lng=lng, address=address,
                ward=ward, city=city, photo_path=None, priority=priority, department=department,
            )
            if photo is not None:
                ext = os.path.splitext(photo.name)[1] or ".jpg"
                save_path = os.path.join(UPLOAD_DIR, f"{code}{ext}")
                with open(save_path, "wb") as f:
                    f.write(photo.getbuffer())
                db.update_photo_path(code, save_path)

            db.add_points(st.session_state.mobile, utils.POINTS_FOR_REPORT)
            st.success(f"✅ Grievance registered! Your tracking ID is **{code}**. "
                       f"Save this ID — you'll need it to track status. "
                       f"You've earned {utils.POINTS_FOR_REPORT} Swachh Citizen points!")
            st.balloons()

# ---------------------------------------------------------------------------
# TRACK MY GRIEVANCE
# ---------------------------------------------------------------------------

elif page == L("nav_track"):
    st.title(L("nav_track"))

    tab1, tab2 = st.tabs(["🔎 Search by Tracking ID", "📜 My Grievance History"])

    with tab1:
        code_in = st.text_input("Enter Grievance ID (e.g., MCG-2026-000001)").strip().upper()
        if code_in:
            g = db.get_grievance_by_code(code_in)
            if not g:
                st.error("No grievance found with that ID.")
            else:
                st.subheader(f"{g['category']}  —  {utils.STATUS_COLORS.get(g['status'],'')} {g['status']}")
                st.write(f"**Description:** {g['description']}")
                st.write(f"**Department:** {g['department']}  |  **Priority:** {g['priority']}  "
                         f"|  **Upvotes:** 👍 {g['upvote_count']}")
                if g["lat"] and g["lng"]:
                    st.map(pd.DataFrame([{"lat": g["lat"], "lon": g["lng"]}]), zoom=14)
                if g["photo_path"] and os.path.exists(g["photo_path"]):
                    st.image(g["photo_path"], caption="Citizen-submitted photo", width=300)

                st.markdown("##### Status Timeline")
                for h in db.get_status_history(code_in):
                    st.write(f"{utils.STATUS_COLORS.get(h['status'],'')} **{h['status']}** "
                             f"— {h['timestamp']} ({h['updated_by']})")
                    if h["remark"]:
                        st.caption(f"📝 {h['remark']}")

                if st.session_state.mobile and st.session_state.mobile != g["mobile"]:
                    if st.button("👍 I'm facing this too — Upvote"):
                        if db.add_upvote(code_in, st.session_state.mobile):
                            db.add_points(st.session_state.mobile, utils.POINTS_FOR_UPVOTE)
                            st.success("Upvoted!")
                            st.rerun()
                        else:
                            st.info("You've already upvoted this.")

    with tab2:
        require_login()
        my_grievances = db.get_grievances_by_mobile(st.session_state.mobile)
        if not my_grievances:
            st.info("You haven't filed any grievances yet.")
        else:
            df = pd.DataFrame(my_grievances)[["grievance_code", "category", "status", "priority",
                                               "upvote_count", "created_at"]]
            st.dataframe(df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# COMMUNITY MAP & ISSUES
# ---------------------------------------------------------------------------

elif page == L("nav_map"):
    st.title(L("nav_map"))

    colf1, colf2, colf3 = st.columns(3)
    f_category = colf1.selectbox(L("category"), ["All"] + list(utils.CATEGORIES.keys()))
    f_status = colf2.selectbox(L("status"), ["All"] + utils.STATUS_FLOW)
    f_city = colf3.text_input("City filter (optional)")

    results = db.list_grievances(category=f_category, status=f_status, city=f_city)
    st.caption(f"{len(results)} grievance(s) found")

    geo_points = [{"lat": r["lat"], "lon": r["lng"]} for r in results if r["lat"] and r["lng"]]
    if geo_points:
        st.map(pd.DataFrame(geo_points), zoom=11)
    else:
        st.info("No geo-tagged grievances match these filters yet.")

    if results:
        df = pd.DataFrame(results)[["grievance_code", "category", "status", "priority", "ward",
                                     "city", "upvote_count", "created_at"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download as CSV", df.to_csv(index=False).encode("utf-8"),
                            file_name="nagar_seva_grievances.csv", mime="text/csv")

# ---------------------------------------------------------------------------
# LEADERBOARD
# ---------------------------------------------------------------------------

elif page == L("nav_leaderboard"):
    st.title(L("nav_leaderboard"))
    st.caption("Inspired by India's annual Swachh Survekshan cleanliness rankings — "
               "healthy competition between wards drives real civic improvement.")

    st.markdown("#### 🏘️ Top Wards")
    wards = db.ward_leaderboard()
    if wards:
        medals = ["🥇", "🥈", "🥉"]
        for i, w in enumerate(wards):
            medal = medals[i] if i < 3 else f"{i+1}."
            st.write(f"{medal} **{w['ward']}** — {w['total_points']} points "
                     f"({w['citizen_count']} active citizens)")
    else:
        st.info("No ward data yet — be the first to put your ward on the map!")

    st.markdown("#### 🙋 Top Citizens")
    users = db.user_leaderboard()
    if users:
        df = pd.DataFrame(users)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No citizens registered yet.")

# ---------------------------------------------------------------------------
# AWARENESS CORNER
# ---------------------------------------------------------------------------

elif page == L("nav_awareness"):
    st.title(L("nav_awareness"))

    st.markdown("#### 📅 Festival & Civic Awareness Calendar (2026)")
    for f in utils.FESTIVALS_2026:
        f_date = datetime.strptime(f["date"], "%Y-%m-%d").date()
        is_past = f_date < datetime.now().date()
        with st.expander(f"{'✅' if is_past else '📌'} {f['name']} — {f_date.strftime('%d %b %Y')}"):
            st.write(f["tip"])

    st.markdown("---")
    st.markdown("#### ♻️ Waste Segregation Guide (Swachh Bharat Mission)")
    for k, v in utils.waste_segregation_guide().items():
        st.write(f"**{k}**")
        st.caption(v)

    st.markdown("---")
    st.markdown("#### 🚨 Emergency & Public Helplines")
    cols = st.columns(2)
    items = list(utils.EMERGENCY_NUMBERS.items())
    half = len(items) // 2 + 1
    for i, (label, number) in enumerate(items):
        cols[0 if i < half else 1].write(f"{label}: **{number}**")

# ---------------------------------------------------------------------------
# ADMIN PANEL
# ---------------------------------------------------------------------------

elif page == L("nav_admin"):
    st.title(L("nav_admin"))
    st.caption("For municipal officers / ward officials. (Demo password-only auth — "
               "use proper role-based auth such as SSO in a real deployment.)")

    pwd = st.text_input("Admin password", type="password")
    if pwd != ADMIN_PASSWORD:
        if pwd:
            st.error("Incorrect password.")
        st.stop()

    st.success("Authenticated as Municipal Admin")

    tab1, tab2 = st.tabs(["📋 Manage Grievances", "📊 Analytics"])

    with tab1:
        colf1, colf2 = st.columns(2)
        f_status = colf1.selectbox("Filter by status", ["All"] + utils.STATUS_FLOW, key="admin_status")
        f_category = colf2.selectbox("Filter by category", ["All"] + list(utils.CATEGORIES.keys()),
                                      key="admin_cat")
        grievances = db.list_grievances(category=f_category, status=f_status)
        st.caption(f"{len(grievances)} grievance(s)")

        for g in grievances:
            with st.expander(f"{utils.STATUS_COLORS.get(g['status'],'')} {g['grievance_code']} — "
                              f"{g['category']} ({g['priority']} priority, 👍 {g['upvote_count']})"):
                st.write(f"**Description:** {g['description']}")
                st.write(f"**Location:** {g['address'] or '—'}, Ward: {g['ward'] or '—'}, "
                         f"City: {g['city'] or '—'}")
                st.write(f"**Filed by:** {g['name']} ({g['mobile']}) on {g['created_at']}")

                new_status = st.selectbox("Update status", utils.STATUS_FLOW,
                                           index=utils.STATUS_FLOW.index(g["status"])
                                           if g["status"] in utils.STATUS_FLOW else 0,
                                           key=f"status_{g['grievance_code']}")
                remark = st.text_input("Remark", key=f"remark_{g['grievance_code']}")
                new_dept = st.text_input("Department", value=g["department"] or "",
                                          key=f"dept_{g['grievance_code']}")

                if st.button("💾 Save update", key=f"save_{g['grievance_code']}"):
                    db.update_status(g["grievance_code"], new_status, remark, "Municipal Admin")
                    db.update_department(g["grievance_code"], new_dept)
                    if new_status == "Resolved" and g["mobile"]:
                        db.add_points(g["mobile"], utils.POINTS_FOR_RESOLVED_BONUS)
                    st.success("Updated.")
                    st.rerun()

    with tab2:
        stats = db.get_stats()
        c1, c2, c3 = st.columns(3)
        c1.metric("Total", stats["total"])
        c2.metric("Resolved", stats["resolved"])
        c3.metric("Pending", stats["pending"])

        if stats["by_category"]:
            cat_df = pd.DataFrame(stats["by_category"]).set_index("category")
            st.markdown("##### By Category")
            st.bar_chart(cat_df)

        if stats["by_status"]:
            status_df = pd.DataFrame(stats["by_status"]).set_index("status")
            st.markdown("##### By Status")
            st.bar_chart(status_df)

        all_g = db.list_grievances()
        if all_g:
            df = pd.DataFrame(all_g)
            st.download_button("⬇️ Export full dataset (CSV)", df.to_csv(index=False).encode("utf-8"),
                                file_name="nagar_seva_full_export.csv", mime="text/csv")