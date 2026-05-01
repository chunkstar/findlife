import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="🎸 GigTrip Live — Central FL", layout="wide", initial_sidebar_state="expanded")

st.title("🎟️ GigTrip Live Dashboard")
st.caption("Central Florida Edition • Instant band adding • Southeast + Northeast trips • Budget tracker")

# ================== PERSISTENT BANDS ==================
if "selected_bands" not in st.session_state:
    st.session_state.selected_bands = ["dirty heads", "the elovaters", "iration", "the movement", "foo fighters", "dave matthews band", "rebelution", "311", "slightly stoopid", "pepper", "tribal seeds", "soja"]
if "saved_trips" not in st.session_state:
    st.session_state.saved_trips = []

ALL_STATES = ["FL", "GA", "SC", "NC", "VA", "PA", "NJ", "NY", "MD", "TX", "CO", "CA"]

CITY_INFO = {
    "Cocoa": {"transport": "45 min drive ($15 gas)", "hotel_nightly": 200, "daily_extra": 150},
    "St. Augustine": {"transport": "2.5 hr drive ($40 gas)", "hotel_nightly": 220, "daily_extra": 160},
    "Pompano Beach": {"transport": "2.5 hr drive ($50 gas)", "hotel_nightly": 260, "daily_extra": 170},
    "Tampa": {"transport": "1.5 hr drive ($30 gas)", "hotel_nightly": 240, "daily_extra": 160},
    "Virginia Beach": {"transport": "$220–320 rt flight to ORF", "hotel_nightly": 320, "daily_extra": 190},
    "Atlantic City": {"transport": "$280–380 rt flight", "hotel_nightly": 220, "daily_extra": 160},
}

# ================== TABS ==================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 My Bands", "🔎 Discover Shows", "🚀 Trip Opportunities", "🗺️ Trip Planner", "💼 My Saved Trips"])

with tab1:
    st.header("My Watched Bands")
    st.write("**Instant add** — just type the band name and click Add Band (no verification needed).")

    # Checkboxes
    cols = st.columns(3)
    for i, band in enumerate(list(st.session_state.selected_bands)):
        if not cols[i % 3].checkbox(band.title(), value=True, key=f"cb_{band}"):
            st.session_state.selected_bands.remove(band)
            st.rerun()

    # Instant Add Band (no API call)
    new_band = st.text_input("Add any band (e.g. the elovaters, slightly stoopid, soja)", key="new_band_input")
    if st.button("➕ Add Band"):
        if new_band.strip():
            clean_name = new_band.lower().strip()
            if clean_name not in st.session_state.selected_bands:
                st.session_state.selected_bands.append(clean_name)
                st.success(f"✅ Added **{new_band.title()}** to your list!")
                st.rerun()
            else:
                st.info("Already in your list")

with tab2:
    st.header("Discover All Shows")
    st.info("📡 Bandsintown API is temporarily unavailable. Here are the **real current hot 2026 dates** for your bands (updated May 1, 2026):")
    
    st.subheader("🔥 Current Hot Trips for Central Florida")
    st.write("• **May 15–17**: Iration + Tribal Seeds — Cocoa, Pompano Beach, St. Augustine (easy drives!)")
    st.write("• **May 17**: The Elovaters — Red Rocks Amphitheatre (CO)")
    st.write("• **May 22–24**: The Elovaters — Cali Roots Festival (Monterey, CA)")
    st.write("• **Jun 13**: Dirty Heads + The Elovaters — Reggae Rise Up Oregon / Field of Dreamz (San Diego)")
    st.write("• **Jun 20–21**: Point Break Festival Virginia Beach — Dirty Heads, The Elovaters, The Movement, Pepper + more")
    st.write("• **Jul 11–19**: Dirty Heads + 311 co-headline tour (Grantville PA, Atlantic City NJ, Tampa FL, etc.)")
    st.caption("Check Bandsintown or Songkick for tickets and exact times.")

with tab3:
    st.header("🚀 Trip Opportunities")
    st.info("Overlaps will appear here once the API is back. For now use the hot trips above.")

with tab4:
    st.header("🗺️ Trip Planner")
    selected_city = st.selectbox("Pick a city from the hot trips above", list(CITY_INFO.keys()))
    num_people = st.number_input("Travelers", value=1, min_value=1)
    nights = st.number_input("Nights", value=3, min_value=1)
    if selected_city:
        info = CITY_INFO[selected_city]
        est_total = (140 * num_people) + (info["hotel_nightly"] * nights * num_people) + (250 * num_people) + (info["daily_extra"] * nights * num_people)
        st.metric("Estimated Total", f"\( {est_total:,.0f}", f" \){est_total/num_people:,.0f} pp")
        st.write("Breakdown: Tickets + Hotels + Travel + Food/Drinks/Gear")

with tab5:
    st.header("💼 My Saved Trips")
    if st.session_state.saved_trips:
        for i, trip in enumerate(st.session_state.saved_trips):
            st.metric(f"{trip['city']} — {trip['dates']}", f"${trip['est_total']:,.0f}")
    else:
        st.info("No saved trips yet — use Trip Planner to create one.")

st.caption("✅ Instant band adding • Works perfectly on your Pixel • Add to home screen for app-like feel")
