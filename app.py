import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


@st.cache_data  # Cache to improve performance
def load_data():
    df = pd.read_excel("df_clean.xlsx") 
    df['Year'] = (df['Semester'] // 10).astype(int)
    return df


df = load_data()  # ✅ Load the dataset properly

# ------------------------------
# Streamlit App
# ------------------------------
st.title("📊 Grade Inflation Analysis")
st.write("This dashboard tracks **grade inflation** by analyzing the trend of average grades per year.")

# Add Filters
year_range = st.slider("Select Year Range:",
                       min_value=int(df['Year'].min()),
                       max_value=int(df['Year'].max()),
                       value=(int(df['Year'].min()), int(df['Year'].max())))

filtered_data = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]

filtered_data['RegistrationYear'] = filtered_data['RegistrationYear'].map(lambda x: f"{x:.0f}" if x == int(x) else f"{x:.2f}")
filtered_data['StudentID'] = filtered_data['StudentID'].map(
    lambda x: f"{x:.0f}" if x == int(x) else f"{x:.2f}")
#filtered_data['BirthYear'] = filtered_data['BirthYear'].map(
#    lambda x: f"{x:.0f}" if x == int(x) else f"{x:.2f}")
filtered_data['Year'] = filtered_data['Year'].map(
    lambda x: f"{x:.0f}" if x == int(x) else f"{x:.2f}")
filtered_data['Semester'] = filtered_data['Semester'].map(
    lambda x: f"{x:.0f}" if x == int(x) else f"{x:.2f}")

# Show Filtered Data
st.write("### Filtered Data Table")
st.dataframe(filtered_data)


# Calculate Grade Trends
grade_trends = df.groupby('Year')['Grade'].mean()

# Create a Matplotlib Plot
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(grade_trends.index, grade_trends.values, marker='o', linestyle='-', color='red')
ax.set_xlabel('Year', fontsize=12.5)
ax.set_ylabel('Average Grade', fontsize=12.5)
ax.set_title('Trend of Average Grades', fontsize=15, weight='bold')
ax.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.35)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))  # Forces integer labels

# Display in Streamlit
st.pyplot(fig)

# Compute average grade per major over time
avg_grade_per_major = df.groupby(['Year', 'Major'])['Grade'].mean().reset_index()

# ------------------------------
# Streamlit App
# ------------------------------
st.title("📊 Grade Inflation Dashboard")

st.write("### 📈 Average Grade Per Major Program Over Time")

# Dropdown filter for selecting a major
majors = df['Major'].unique()
selected_major = st.selectbox("Select a Major Program:", majors)

# Filter data based on the selected major
filtered_major_data = avg_grade_per_major[avg_grade_per_major['Major'] == selected_major]

# Plot the trend for the selected major
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(filtered_major_data['Year'], filtered_major_data['Grade'], marker='o', linestyle='-', color='blue')

ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Average Grade", fontsize=12)
ax.set_title(f"Average Grade Trend for {selected_major}", fontsize=14, weight='bold')
ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))  # Forces integer labels

st.pyplot(fig)

