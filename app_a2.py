import pandas as pd
import plotly.express as px
import streamlit as st

URL = "https://raw.githubusercontent.com/intro-stat-learning/ISLP/main/ISLP/data/Auto.csv"

st.set_page_config(page_title="Fuel efficiency of cars, 1970 to 1982", layout="wide")
st.title("Which cars are the most fuel efficient, and has this changed?")
st.caption("Reader: a car dealer deciding which models to stock. Data: ISLP Auto, 392 cars.")

# Step 1. Load and clean the data once; the result is cached between reruns
@st.cache_data
def load():
    d = pd.read_csv(URL)
    d["horsepower"] = pd.to_numeric(d["horsepower"], errors="coerce")
    d = d.dropna()
    d["origin"] = d["origin"].map({1: "America", 2: "Europe", 3: "Japan"})
    d["year"] = 1900 + d["year"]
    return d

auto = load()

# Step 2. Filters in the sidebar
st.sidebar.header("Filters")
origins = st.sidebar.multiselect("Origin", ["America", "Europe", "Japan"],
                                 default=["America", "Europe", "Japan"])
years = st.sidebar.slider("Model year", 1970, 1982, (1970, 1982))
cyl = st.sidebar.multiselect("Cylinders", sorted(auto["cylinders"].unique()),
                             default=sorted(auto["cylinders"].unique()))

# Step 3. Filter the data; every chart below uses d, so all charts are linked
d = auto[auto["origin"].isin(origins) & auto["year"].between(*years) & auto["cylinders"].isin(cyl)]
if d.empty:
    st.warning("No cars match these filters. Choose more options in the sidebar.")
    st.stop()

colors = {"America": "#0072B2", "Europe": "#E69F00", "Japan": "#009E73"}   # colour-blind safe

# Step 4a. KPI cards
k1, k2, k3, k4 = st.columns(4)
k1.metric("Cars selected", len(d))
k2.metric("Average mpg", f"{d['mpg'].mean():.1f}")
k3.metric("Average weight", f"{d['weight'].mean():,.0f} lb")
k4.metric("Average horsepower", f"{d['horsepower'].mean():.0f}")

# Step 4b. Four linked charts in a 2 x 2 grid
c1, c2 = st.columns(2)
trend = d.groupby(["year", "origin"], as_index=False)["mpg"].mean()
c1.plotly_chart(px.line(trend, x="year", y="mpg", color="origin", markers=True, color_discrete_map=colors,
                        title="Fuel efficiency improved every year",
                        labels={"mpg": "Average mpg", "year": "Model year"}), use_container_width=True)
c2.plotly_chart(px.scatter(d, x="weight", y="mpg", color="origin", hover_name="name", color_discrete_map=colors,
                           title="Heavier cars use more fuel",
                           labels={"weight": "Weight (lb)", "mpg": "Miles per gallon"}), use_container_width=True)
c3, c4 = st.columns(2)
c3.plotly_chart(px.box(d, x="cylinders", y="mpg", title="More cylinders, lower mpg",
                       labels={"mpg": "Miles per gallon", "cylinders": "Cylinders"}), use_container_width=True)
share = d["origin"].value_counts().reset_index()
share.columns = ["origin", "cars"]
c4.plotly_chart(px.bar(share, x="origin", y="cars", color="origin", color_discrete_map=colors,
                       title="Where the selected cars come from",
                       labels={"cars": "Number of cars", "origin": "Origin"}), use_container_width=True)

# Step 4c. The data behind the charts, and a download button
with st.expander("Show the data"):
    st.dataframe(d.sort_values("mpg", ascending=False), use_container_width=True)
    st.download_button("Download as CSV", d.to_csv(index=False), "auto_filtered.csv")
