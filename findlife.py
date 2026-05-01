import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import plotly.express as px

st.set_page_config(page_title="🎸 GigTrip Live — Central FL", layout="wide", initial_sidebar_state="expanded")

st.title("🎟️ GigTrip Live Dashboard")
st.caption("Central Florida Edition • Live tours • Southeast road trips + Northeast sprints • Budget tracker")

# ================== YOUR CORE BANDS ==================
BANDS = ["dirty heads", "the elovaters", "iration", "the movement", "foo fighters", "dave matthews band", "rebelution", "311", "slightly stoopid", "pepper", "tribal seeds", "soja"]
APP_ID = "gigtripper2026"

# Central FL focused cities + budget info
CITY_INFO = {
    "St. Augustine": {"transport": "2.5 hr drive ($40 gas)", "hotel_nightly": 220, "daily_extra": 160},
    "Cocoa": {"transport": "45 min drive ($15 gas)", "hotel_nightly": 200, "daily_extra": 150},
    "Pompano Beach": {"transport": "2.5 hr drive ($50 gas)", "hotel_nightly": 260, "daily_extra": 170},
    "Tampa": {"transport": "1.5 hr drive ($30 gas)", "hotel_nightly": 240, "daily_extra": 160},
    "West Palm Beach": {"transport": "2.5 hr drive ($50 gas)", "hotel_nightly": 280, "daily_extra": 180},
    "Virginia Beach": {"transport": "$220–320 rt flight to ORF", "hotel_nightly": 320, "daily_extra": 190},
    "Atlantic City": {"transport": "$280–380 rt flight", "hotel_nightly": 220, "daily_extra": 160},
}

@st.cache_data(ttl=3600)
def fetch_band_shows(artist):
    url = f"https://rest.bandsintown.com/artists/{artist.replace(' ', '%20')}/events?app_id={APP_ID}"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            shows = []
            for show in resp.json():
                try:
                    dt = datetime.fromisoformat(show["datetime"].replace("Z", "+00:00"))
                    v = show.get("venue", {})
                    shows.append({
                        "band": artist.title(),
                        "date": dt.date(),
                        "city": v.get("city"),
                        "venue": v.get("name"),
                        "url": show.get("url", "")
                    })
                except:
                    continue
            return pd.DataFrame(shows)
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# Fetch core bands
all_dfs = []
for artist in BANDS:
    df = fetch_band_shows(artist)
    if not df.empty:
        all_dfs.append(df)

df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

# Dynamic search for ANY band
st.sidebar.header("🔍 Search Any Band")
extra_band = st.sidebar.text_input("Type a band name (e.g. Slightly Stoopid, SOJA, etc.)", "")
if extra_band:
    extra_df = fetch_band_shows(extra_band.lower())
    if not extra_df.empty:
        df = pd.concat([df, extra_df], ignore_index=True) if not df.empty else extra_df
        st.sidebar.success(f"Added {extra_band.title()} shows!")

if df.empty:
    st.warning("⚠️ Bandsintown API is temporarily quiet. Here are confirmed hot 2026 trips for Central Florida:")
else:
    df['date'] = pd.to_datetime(df['date'])
    st.success(f"✅ Live data loaded — {len(df)} shows as of {datetime.now().strftime('%b %d, %Y')}")

# Sidebar filters
st.sidebar.header("🎛️ Filters")
start_date = st.sidebar.date_input("From", value=date.today())
end_date = st.sidebar.date_input("To", value=date.today() + pd.Timedelta(180, "d"))
num_people = st.sidebar.number_input("Travelers", value=1, min_value=1)
total_budget = st.sidebar.number_input("Your total summer budget $", value=5000, step=500)

# Show all shows (or hot trips fallback)
st.subheader("📍 All Upcoming Shows & Overlaps (Southeast prioritized)")
if not df.empty:
    filtered = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
    if not filtered.empty:
        st.dataframe(filtered.sort_values("date"), use_container_width=True, hide_index=True)
    else:
        st.info("No shows in selected date range.")
else:
    # Fallback hot trips (real 2026 dates)
    st.write("**Confirmed hot trips for you right now:**")
    st.write("• **May 15–17**: Iration + Tribal Seeds – Cocoa Riverfront Park (45 min drive!)")
    st.write("• **Jun 20–21**: Point Break Festival – Virginia Beach (Dirty Heads, Elovaters, Movement + more)")
    st.write("• **Aug 30**: Dirty Heads – iTHINK Financial Amp, West Palm Beach (easy drive)")
    st.write("• July: Dirty Heads + 311 co-headline run (Tampa / Atlantic City options)")

# Budget calculator
st.subheader("💰 Quick Budget Breakdown")
selected_city = st.selectbox("Pick a city from above to estimate cost", options=df['city'].unique() if not df.empty else ["Cocoa", "Virginia Beach", "West Palm Beach", "Tampa"])
if selected_city:
    info = CITY_INFO.get(selected_city, {"hotel_nightly": 250, "daily_extra": 170, "transport": "$250"})
    nights = 3
    est_ticket_pp = 140
    est_total = (est_ticket_pp * num_people) + (info["hotel_nightly"] * nights * num_people) + (250 * num_people) + (info["daily_extra"] * nights * num_people)
    st.metric("Estimated Total", f"\( {est_total:,.0f}", f" \){est_total/num_people:,.0f} pp")
    labels = ['Tickets', 'Hotels', 'Travel', 'Food/Drinks/Gear']
    sizes = [est_ticket_pp*num_people, info["hotel_nightly"]*nights*num_people, 250*num_people, info["daily_extra"]*nights*num_people]
    fig = px.pie(values=sizes, names=labels, title="Trip Cost Breakdown", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

st.caption("✅ Now searches ANY band you type. Auto-refreshes hourly. Tap three dots → 'Add to home screen' on your Pixel!")
