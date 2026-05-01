import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import plotly.express as px

st.set_page_config(page_title="🎸 GigTrip Live — Central FL", layout="wide", initial_sidebar_state="expanded")

st.title("🎟️ GigTrip Live Dashboard")
st.caption("Central Florida Edition • Live tours • Southeast road trips + Northeast sprints • Budget tracker")

# ================== YOUR BANDS ==================
BANDS = ["dirty heads", "the elovaters", "iration", "the movement", "foo fighters", "dave matthews band", "rebelution", "311", "slightly stoopid", "pepper", "tribal seeds", "soja"]
APP_ID = "gigtripper2026"

# Central FL focused cities with budget info
CITY_INFO = {
    "St. Augustine": {"transport": "2.5 hr drive from Orlando ($40 gas)", "hotel_nightly": 220, "daily_extra": 160},
    "Cocoa": {"transport": "45 min drive ($15 gas)", "hotel_nightly": 200, "daily_extra": 150},
    "Pompano Beach": {"transport": "2.5 hr drive ($50 gas)", "hotel_nightly": 260, "daily_extra": 170},
    "Tampa": {"transport": "1.5 hr drive ($30 gas)", "hotel_nightly": 240, "daily_extra": 160},
    "Virginia Beach": {"transport": "$220–320 rt flight to ORF", "hotel_nightly": 320, "daily_extra": 190},
    "Atlantic City": {"transport": "$280–380 rt flight", "hotel_nightly": 220, "daily_extra": 160},
}

@st.cache_data(ttl=3600)  # refresh hourly
def fetch_shows():
    all_shows = []
    for artist in BANDS:
        url = f"https://rest.bandsintown.com/artists/{artist.replace(' ', '%20')}/events?app_id={APP_ID}"
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                for show in resp.json():
                    try:
                        dt = datetime.fromisoformat(show["datetime"].replace("Z", "+00:00"))
                        v = show.get("venue", {})
                        all_shows.append({
                            "band": artist.title(),
                            "date": dt.date(),
                            "city": v.get("city"),
                            "venue": v.get("name"),
                            "url": show.get("url", "")
                        })
                    except:
                        continue
        except:
            continue
    return pd.DataFrame(all_shows)

df = fetch_shows()

if df.empty:
    st.error("No shows right now — check back soon! (Bandsintown API sometimes delays new dates)")
    st.stop()

df['date'] = pd.to_datetime(df['date'])
st.success(f"✅ Live data loaded — {len(df)} shows as of {datetime.now().strftime('%b %d, %Y')}")

# Sidebar filters
st.sidebar.header("🎛️ Filters")
start_date = st.sidebar.date_input("From", value=date.today())
end_date = st.sidebar.date_input("To", value=date.today() + pd.Timedelta(90, "d"))
num_people = st.sidebar.number_input("Travelers", value=1, min_value=1)
total_budget = st.sidebar.number_input("Your total summer budget $", value=5000, step=500)

# Find overlaps (2+ bands same city within 7 days)
trips = []
for city in df['city'].unique():
    city_df = df[df['city'] == city].sort_values('date')
    for i in range(len(city_df)):
        for j in range(i + 1, len(city_df)):
            if (city_df.iloc[j]['date'] - city_df.iloc[i]['date']).days <= 7:
                trips.append({
                    "city": city,
                    "dates": sorted({city_df.iloc[i]['date'].date(), city_df.iloc[j]['date'].date()}),
                    "bands": sorted(set([city_df.iloc[i]['band'], city_df.iloc[j]['band']])),
                    "venues": [city_df.iloc[i]['venue'], city_df.iloc[j]['venue']],
                    "link": city_df.iloc[0]['url']
                })

st.subheader("📍 Live Gig-Trip Opportunities (Southeast first!)")
if trips:
    trip_df = pd.DataFrame(trips)
    st.dataframe(trip_df, use_container_width=True, hide_index=True)

    st.subheader("💰 Budget Breakdown")
    if not trip_df.empty:
        selected_city = st.selectbox("Pick a trip to plan", options=trip_df['city'].unique())
        if selected_city:
            info = CITY_INFO.get(selected_city, {"hotel_nightly": 250, "daily_extra": 170, "transport": "$300"})
            nights = 3
            est_ticket_pp = 140
            est_total = (est_ticket_pp * num_people) + (info["hotel_nightly"] * nights * num_people) + \
                        (250 * num_people) + (info["daily_extra"] * nights * num_people)
            
            st.metric("Estimated Total Cost", f"\( {est_total:,.0f}", f" \){est_total/num_people:,.0f} per person")
            
            # Mobile-friendly interactive pie chart
            labels = ['Tickets', 'Hotels', 'Travel', 'Food/Drinks/Gear']
            sizes = [est_ticket_pp*num_people, info["hotel_nightly"]*nights*num_people, 250*num_people, info["daily_extra"]*nights*num_people]
            fig = px.pie(values=sizes, names=labels, title="Trip Cost Breakdown", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No overlapping dates in this window yet — widen the dates or check back in a day or two!")

st.subheader("🔥 Hot Central Florida Trips Right Now")
st.write("• **May 15–17**: Iration in Cocoa, Pompano Beach & St. Augustine — perfect easy drives!")
st.write("• **Jun 20–21**: Point Break Festival Virginia Beach (Dirty Heads + Elovaters + Movement + more)")
st.write("• Summer Tampa / West Palm runs with Dirty Heads + 311")

st.caption("Auto-refreshes hourly. Works great on your Pixel — tap the three dots → 'Add to home screen' for app-like experience!")
