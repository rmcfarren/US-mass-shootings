'''
Programmer: Ricky McFarren
CS 230: Section 3
Data: US Mass Shootings
Description:
This program will illustrate many pictures, graphs, and other data visuals regarding where these mass shootings have occurred the most, how many in a selected year, and what type of weapon was used.
'''

import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from PIL import Image
import folium
import mplcursors
from streamlit_folium import folium_static

#title of website
st.title("United States Mass Shootings Since 1982")
#Cover image on website
img = os.path.join(os.path.dirname(__file__), 'police_officer.jpg')
police_officer = Image.open(img)
st.image(police_officer)


df = pd.read_csv('Final project/USMassShootings.csv', encoding='ISO-8859-1')

#Asks user a state code, displays the cities of shootings that occurred in that state
def get_state_data(df):
    states = sorted(df['STATE'].unique())
    state = st.selectbox('Select a state:', states, key='state_selectbox')
    filtered_df = df[df['STATE'] == state]
    grouped_df = filtered_df.groupby(['YEAR'])['FATALITIES'].sum().reset_index()
    grouped_df.columns = ['YEAR', 'FATALITIES']
    grouped_df.index = grouped_df.index + 1
    grouped_df['YEAR'] = grouped_df['YEAR'].astype(int).apply(lambda x: str(x))
    grouped_df['STATE'] = state
    st.write(grouped_df)
get_state_data(df)

# Bar chart that shows the number of shootings by race and by the shooters gender
def create_bar_chart(df, male_color, female_color):
    fig, ax = plt.subplots(figsize=(10, 6))
    df.groupby(['RACE', 'GENDER']).size().unstack().plot(kind='bar', ax=ax, color=[female_color, male_color])
    ax.set_xlabel('Race of Shooter')
    ax.set_ylabel('Number of Shootings')
    ax.legend(title='Gender', loc='upper left')
    return fig

male_color = st.sidebar.color_picker('Choose a color for male', '#1f77b4')
female_color = st.sidebar.color_picker('Choose a color for female', '#ff7f0e')
fig = create_bar_chart(df, male_color, female_color)

st.pyplot(fig)



# A for Loop that prints the shooter's gender, whether they obtained the gun legally, where they got the gun, as well as the case of shooting (What circumstances it happened under)
def create_shooting_dataframe(df):
    data = []
    for index, row in df.iterrows():
        name = row['CASE']
        gender = row["GENDER"]
        legal = row["WEAPONSOBTAINEDLEGALLY"]
        location = row["WHEREWEAPONOBTAINED"]
        if pd.isna(legal):
            legal = "Unknown"
        data.append([name, gender, legal, location])

    columns = ["Case","Gender", "Weapon Legally Obtained", "Where Weapon Was Obtained"]
    df_shooting = pd.DataFrame(data, columns=columns)
    df_shooting.index += 1
    return df_shooting

df_shooting = create_shooting_dataframe(df)
st.dataframe(df_shooting)

#Average number of shootings each year since beginning of data
df['YEAR'] = df['YEAR'].astype(str).str.replace(',', '').astype(int)

# Groups data + finds average number of fatalities per year
avg_fatalities = df.groupby('YEAR')['FATALITIES'].mean()

fig, ax = plt.subplots()
ax.plot(avg_fatalities.index, avg_fatalities.values)
ax.set_xlabel('Year')
ax.set_ylabel('Average number of fatalities')
ax.set_title('Average Number of Fatalities per Year from Shootings')

#No commas at bottom of legend of years
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: int(x)))

#cursor that shows the average number of fatalities when hovering over the line in chart
mplcursors.cursor(ax, hover=True)
def on_add(sel):
    x, y, _ = sel.target
    year = int(x)
    fatalities = round(float(y), 2)
    sel.annotation.set_text(f"Year: {year}\nAvg. fatalities: {fatalities}")
st.pyplot(fig)

#A function that shows the user what weapons were used in each shooting type
def get_gun(shooting_type):
    gun = df[df["SHOOTINGTYPE"] == shooting_type]["WEAPONDETAILS"].values[0]
    return gun

shooting_type = st.selectbox("Select a shooting type", df["SHOOTINGTYPE"].unique())
gun = get_gun(shooting_type)

if gun:
    st.write(f"The gun(s) used for {shooting_type} was/were {gun}.")
else:
    st.write("No data found for selected shooting type.")

#A pie chart that displays whether the shooter had prior signs of mental illness or not
def plot_mental_illness_pie_chart(df):
    counts = df["PRIORSIGNSOFMENTALILLNESS"].value_counts()
    labels = ["Prior signs of Mental Illness", "No Prior signs of Mental Illness" ]
    values = [counts[0], counts[1]]
    colors = ["#FFA07A", "#ADD8E6"]
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.title("Shooters' Prior Signs of Mental Illness")
    plt.legend(title="Mental Illness", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    st.pyplot(fig)
plot_mental_illness_pie_chart(df)

# A pie chart that shows the user the percentages of where the shootings have happened by type eg. military, schools, etc
def create_pie_chart(df):
    counts = df["LOCATIONTYPE"].value_counts()
    fig, ax = plt.subplots()
    ax.pie(counts.values, labels=counts.index, autopct='%1.1f%%')
    ax.set_title("Shootings by Location Type")
    st.pyplot(fig)
create_pie_chart(df)

# line chart that shows the user how many total victims there are per year from mass shootings
def plot_yearly_total_victims(df):
    yearly_data = df.groupby("YEAR").sum()["TOTALVICTIMS"]
    fig, ax = plt.subplots()
    ax.plot(yearly_data.index, yearly_data.values, color="red", label="Total Victims")
    ax.set_title("Total Victims from Mass Shootings (by Year)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Total Victims")
    ax.legend()
    return fig
fig = plot_yearly_total_victims(df)
st.pyplot(fig)

#A detailed map of all mass shooting locations with dots where every shooting happened + tells you city when hovering over dot
def plot_mass_shooting_map(df):
    m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
    for index, row in df.iterrows():
        lat = row['LATITUDE']
        lon = row['LONGITUDE']
        location = row['LOCATION']
        date = row['DATE']
        shooting_type = row['LOCATIONTYPE']
        if shooting_type == 'School':
            color = 'red'
        elif shooting_type == 'Workplace':
            color = 'blue'
        elif shooting_type == 'Religious':
            color = 'tan'
        elif shooting_type == 'Military':
            color = 'green'
        else:
            color = 'purple'
        popup_html = f'<b>{location}</b><br>{date}<br><b>Location Type:</b> {shooting_type}'
        folium.Marker([lat, lon], popup=popup_html, icon=folium.Icon(color=color)).add_to(m)

    return m

st.title('US Mass Shootings Map')
folium_static(plot_mass_shooting_map(df))

#Function that displays if the shooter had a mental illness, if he/she did then it displays any mental health notes
def display_shooters_with_mental_health_notes(df):
    locations = df['LOCATION'].unique()
    selected_location = st.sidebar.selectbox("Select a location:", locations)
    selected_df = df[df['LOCATION'] == selected_location]
    shooters = []
    for index, row in selected_df.iterrows():
        if row['PRIORSIGNSOFMENTALILLNESS'] == 'Yes':
            notes = row['MENTALHEALTHNOTES']
            shooters.append(f"The Shooting that occurred in {row['LOCATION']} had Mental Health Notes of: {notes}" if notes else f"there was no prior mental illness on record")

    if len(shooters) == 0:
        st.write(f"The shooter at {selected_location} had no mental health notes.")
    else:
        st.write(f"The shooter had mental health notes of:")
        for shooter in shooters:
            st.write(shooter)
display_shooters_with_mental_health_notes(df)

#Allows user to change the background color of the whole website to whatever color they choose - Streamlit widget 1
def set_background_color(color):
    hex_color = '#{}'.format(color.lstrip('#'))
    st.markdown(
        f"""
        <style>
        body {{
            background-color: {hex_color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
color = st.color_picker("Choose a color", "#ffffff")
set_background_color(color)

# A streamlit (2) selectbox dropdown menu with the options "All", "Male", and "Female", when the user chooses one, the code will then display that genders mass shootings
def display_filtered_data(df):
    gender_options = ['All', 'Male', 'Female']
    selected_gender = st.selectbox('Select gender', gender_options)
    if selected_gender == 'All':
        filtered_data = df.reset_index(drop=True)
    else:
        filtered_data = df[df['GENDER'] == selected_gender].reset_index(drop=True)
    filtered_data.index = range(1, len(filtered_data)+1)

    st.write(filtered_data)
display_filtered_data(df)

# Define a function to calculate the total number of fatalities
def calculate_total_fatalities(df):
    total_fatalities = df['FATALITIES'].sum()
    return total_fatalities

st.title('Calculate Total Fatalities')
if df is not None:
    total_fatalities = calculate_total_fatalities(df)
    st.write(f'Total Fatalities: {total_fatalities} from Mass shootings since 1982')

# A streamlit (3) slider that when a person slides it to a specfic year it will tell them how many fatalities had occurred that year due to mass shootings
def display_fatalities_by_year(df):
    year = st.slider('Select a year:', min_value=int(df['YEAR'].min()), max_value=int(df['YEAR'].max()))
    year_data = df[df['YEAR'] == year]
    total_fatalities = year_data['FATALITIES'].sum()
    st.write(f'Total fatalities due to mass shootings in {year}: {total_fatalities}')
display_fatalities_by_year(df)

#A list that displays the locations with less than 7 fatalities in US mass shootings since 1982
def get_locations_less_than_7_fatalities(df):
    df_filtered = df[df['FATALITIES'] < 7]
    df_filtered.index = range(1, len(df_filtered) + 1)
    locations = df_filtered['LOCATION'].tolist()
    locations = [f"{i-1}. {loc}" for i, loc in enumerate(locations, start=1)]
    return locations
locations = get_locations_less_than_7_fatalities(df)
st.write("Locations with less than 7 fatalities in US mass shootings since 1982:")
st.write(locations)

def main():
    #sidebar with some options
    options = ["Location of shootings in selected state", "Bar Chart: by race and gender", "list of gender,legality of gun,where obtained", "what weapon used in shooting type", "Pie chart: signs of mental illness or not",
               "Pie chart: Where shootings have happened", "Line chart: How many total victims per year", "Map of all shooting locations and information", "list of mental illness + note of it",
               "Background color of website", "Dropdown menu of specfic genders' mass shootings", "Total number of fatalities", "Slide to a year which tells you how many fatalities it had",
               "List that displays locations with less than 7 fatalities"]
    selected_option = st.sidebar.selectbox("Select an option", options)

    # Use the selected option in your app
    st.write("You selected:", selected_option)

if __name__ == "__main__":
    main()
    get_state_data(df)
    create_bar_chart(df,male_color,female_color)
    create_shooting_dataframe(df)
    get_gun(shooting_type)
    plot_mental_illness_pie_chart(df)
    create_pie_chart(df)
    plot_yearly_total_victims(df)
    plot_mass_shooting_map(df)
    display_shooters_with_mental_health_notes(df)
    set_background_color(color)
    display_filtered_data(df)
    calculate_total_fatalities(df)
    display_fatalities_by_year(df)
    get_locations_less_than_7_fatalities(df)