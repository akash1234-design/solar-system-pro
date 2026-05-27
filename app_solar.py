import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import io

st.set_page_config(page_title="Solar System Pro V2", page_icon="🪐", layout="wide")

st.markdown("""
<style>
   .main {background: linear-gradient(135deg, #020617 0%, #0f172a 100%);}
    h1, h2, h3 {color: #ffffff;}
   .stMetric {background: rgba(255,255,255,0.05); padding:15px; border-radius:12px; border:1px solid rgba(255,255,255,0.1);}
</style>
""", unsafe_allow_html=True)

st.title("🪐 Solar System Pro V2 — Full Pro")
st.caption("Real moons • Asteroid belt • Live positions • Missions • Habitable zone")

# Planetary data
planets = {
    'Planet': ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune'],
    'Distance_AU': [0.39, 0.72, 1.0, 1.52, 5.20, 9.58, 19.18, 30.07],
    'Period_days': [88, 225, 365, 687, 4333, 10759, 30687, 60190],
    'Radius_km': [2440, 6052, 6371, 3390, 69911, 58232, 25362, 24622],
    'Mass_10e24kg': [0.33, 4.87, 5.97, 0.642, 1898, 568, 86.8, 102],
    'Gravity': [3.7, 8.9, 9.8, 3.7, 23.1, 9.0, 8.7, 11.0],
    'Moons': [0, 0, 1, 2, 95, 146, 28, 16],
    'Temp_C': [167, 464, 15, -65, -110, -140, -195, -200],
    'Color': ['#8C8C8C', '#E6CDAC', '#2E8B57', '#CD5C5C', '#D8CA9D', '#F7E7CE', '#A4E0E0', '#4169E1']
}
df = pd.DataFrame(planets)

# Moons data - major moons only
moons_data = {
    'Earth': [{'name':'Moon','dist':0.00257,'radius':1737}],
    'Mars': [{'name':'Phobos','dist':0.00006,'radius':11},{'name':'Deimos','dist':0.00015,'radius':6}],
    'Jupiter': [{'name':'Io','dist':0.0028,'radius':1821},{'name':'Europa','dist':0.0045,'radius':1560},
                {'name':'Ganymede','dist':0.0072,'radius':2634},{'name':'Callisto','dist':0.0126,'radius':2410}],
    'Saturn': [{'name':'Titan','dist':0.0082,'radius':2575},{'name':'Enceladus','dist':0.0016,'radius':252}]
}

# Missions
missions = pd.DataFrame({
    'Mission': ['Voyager 1','Voyager 2','Parker Solar Probe','James Webb'],
    'Distance_AU': [164.0, 137.0, 0.05, 0.01],
    'Launch_Year': [1977, 1977, 2018, 2021],
    'Status': ['Active','Active','Active','Active']
})

# Sidebar
st.sidebar.header("🔭 Controls")
selected_planet = st.sidebar.selectbox("Select Planet", df['Planet'], index=2)
show_moons = st.sidebar.checkbox("Show Major Moons", True)
show_asteroids = st.sidebar.checkbox("Show Asteroid Belt", True)
show_habitable = st.sidebar.checkbox("Show Habitable Zone", True)
show_missions = st.sidebar.checkbox("Show Space Missions", True)
time_speed = st.sidebar.slider("Time Speed", 0.1, 5.0, 1.0)
view_mode = st.sidebar.radio("View", ["3D System", "Live Positions", "Missions & Analytics"])

# KPIs
p_row = df[df['Planet']==selected_planet].iloc[0]
c1,c2,c3,c4 = st.columns(4)
c1.metric("Distance", f"{p_row['Distance_AU']} AU")
c2.metric("Period", f"{p_row['Period_days']:,} days")
c3.metric("Moons", f"{int(p_row['Moons'])}")
c4.metric("Temp", f"{p_row['Temp_C']} °C")

st.divider()

if view_mode == "3D System":
    st.subheader("🌌 3D Solar System with Moons & Asteroids")

    fig = go.Figure()

    # Sun
    fig.add_trace(go.Scatter3d(x=[0],y=[0],z=[0],mode='markers',
        marker=dict(size=25,color='yellow'), name='Sun', hovertemplate='Sun<extra></extra>'))

    t = np.linspace(0,2*np.pi,150)
    time_offset = datetime.now().timestamp()*0.00001*time_speed

    # Habitable Zone
    if show_habitable:
        for r in np.linspace(0.95,1.37,3):
            fig.add_trace(go.Scatter3d(
                x=r*np.cos(t), y=r*np.sin(t), z=np.zeros_like(t),
                mode='lines', line=dict(color='green',width=2,dash='dot'),
                opacity=0.3, showlegend=False, hoverinfo='skip'
            ))

    # Asteroid Belt
    if show_asteroids:
        np.random.seed(42)
        n_ast = 500
        r_ast = np.random.uniform(2.2,3.2,n_ast)
        theta_ast = np.random.uniform(0,2*np.pi,n_ast)
        x_ast = r_ast*np.cos(theta_ast)
        y_ast = r_ast*np.sin(theta_ast)
        fig.add_trace(go.Scatter3d(x=x_ast,y=y_ast,z=np.zeros(n_ast),
            mode='markers', marker=dict(size=2,color='gray',opacity=0.5),
            name='Asteroid Belt', hoverinfo='skip'))

    # Planets + Moons
    for i,row in df.iterrows():
        r = row['Distance_AU']
        # Orbit
        fig.add_trace(go.Scatter3d(x=r*np.cos(t),y=r*np.sin(t),z=np.zeros_like(t),
            mode='lines', line=dict(color=row['Color'],width=2), opacity=0.4,
            showlegend=False, hoverinfo='skip'))

        # Planet position
        angle = time_offset * (365/row['Period_days'])
        x_p = r*np.cos(angle)
        y_p = r*np.sin(angle)

        fig.add_trace(go.Scatter3d(x=[x_p],y=[y_p],z=[0],mode='markers+text',
            marker=dict(size=max(6,row['Radius_km']/8000),color=row['Color']),
            text=[row['Planet']], textposition='top center', name=row['Planet']))

        # Moons
        if show_moons and row['Planet'] in moons_data:
            for moon in moons_data[row['Planet']]:
                m_angle = time_offset*10
                x_m = x_p + moon['dist']*np.cos(m_angle)
                y_m = y_p + moon['dist']*np.sin(m_angle)
                fig.add_trace(go.Scatter3d(x=[x_m],y=[y_m],z=[0],mode='markers',
                    marker=dict(size=3,color='lightgray'), name=moon['name'],
                    showlegend=False, hovertemplate=f"{moon['name']}<extra></extra>"))

    # Missions
    if show_missions:
        for _,m in missions.iterrows():
            ang = np.random.uniform(0,2*np.pi)
            x_m = m['Distance_AU']*np.cos(ang)
            y_m = m['Distance_AU']*np.sin(ang)
            fig.add_trace(go.Scatter3d(x=[x_m],y=[y_m],z=[0],mode='markers+text',
                marker=dict(size=5,color='red',symbol='diamond'),
                text=[m['Mission']], textposition='top center', name=m['Mission']))

    fig.update_layout(
        scene=dict(xaxis_title='AU', yaxis_title='AU', zaxis_visible=False,
                   bgcolor='rgba(2,6,23,0.9)'),
        paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
        height=750, legend=dict(bgcolor='rgba(0,0,0,0.5)')
    )
    st.plotly_chart(fig, use_container_width=True)

elif view_mode == "Live Positions":
    st.subheader("📅 Live Planetary Positions Today")
    today = date.today()
    st.info(f"Calculated for: {today.strftime('%d %B %Y')}")

    # Simple mean anomaly calculation
    j2000 = date(2000,1,1)
    days_since = (today - j2000).days

    pos_data = []
    for _,row in df.iterrows():
        mean_motion = 360 / row['Period_days']
        longitude = (mean_motion * days_since) % 360
        pos_data.append({
            'Planet': row['Planet'],
            'Heliocentric Longitude °': round(longitude,1),
            'Distance AU': row['Distance_AU'],
            'Current Season': 'N/A'
        })
    pos_df = pd.DataFrame(pos_data)
    st.dataframe(pos_df, use_container_width=True, hide_index=True)

    # Polar plot
    fig_polar = go.Figure()
    for _,row in df.iterrows():
        lon = pos_data[df['Planet'].tolist().index(row['Planet'])]['Heliocentric Longitude °']
        fig_polar.add_trace(go.Scatterpolar(
            r=[row['Distance_AU']], theta=[lon],
            mode='markers+text', marker=dict(size=15,color=row['Color']),
            text=[row['Planet']], name=row['Planet']
        ))
    fig_polar.update_layout(
        polar=dict(radialaxis=dict(range=[0,32])),
        paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=600,
        showlegend=False
    )
    st.plotly_chart(fig_polar, use_container_width=True)

else:
    st.subheader("🚀 Space Missions Tracker")
    col1,col2 = st.columns([1,1])
    with col1:
        st.dataframe(missions, use_container_width=True, hide_index=True)
        st.metric("Farthest Human Object", "Voyager 1", "164 AU")
    with col2:
        fig_m = px.bar(missions, x='Mission', y='Distance_AU', color='Mission',
                       log_y=True, title='Distance from Sun (log scale)')
        fig_m.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='white'))
        st.plotly_chart(fig_m, use_container_width=True)

    st.subheader("📊 Comparative Analytics")
    fig_comp = px.scatter(df, x='Distance_AU', y='Temp_C', size='Radius_km',
                          color='Planet', hover_data=['Moons','Gravity'],
                          color_discrete_sequence=df['Color'].tolist(),
                          title='Distance vs Temperature')
    fig_comp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,23,42,0.5)',
                           font=dict(color='white'))
    st.plotly_chart(fig_comp, use_container_width=True)

# Export
st.divider()
st.subheader("💾 Export Data")
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download Planetary Data CSV", csv, "solar_system_data.csv", "text/csv")

st.caption("Data: NASA JPL • Moons: Major only • Positions: Approximate • V2 Pro")