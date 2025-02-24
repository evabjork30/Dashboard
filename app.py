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
filtered_data['BirthYear'] = filtered_data['BirthYear'].map(
    lambda x: f"{x:.0f}" if x == int(x) else f"{x:.2f}")
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

# Compute average grade per department over time
avg_grade_per_department = df.groupby(['Year', 'Department'])['Grade'].mean().reset_index()

# ------------------------------
# Streamlit App
# ------------------------------
st.title("📊 Grade Inflation Dashboard")

st.write("### 📈 Average Grade Per Department Program Over Time")

# Dropdown filter for selecting a department
departments = df['Department'].unique()
selected_department = st.selectbox("Select a Department:", departments)

# Filter data based on the selected department
filtered_department_data = avg_grade_per_department[avg_grade_per_department['Department'] == selected_department]

# Plot the trend for the selected department
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(filtered_department_data['Year'], filtered_department_data['Grade'], marker='o', linestyle='-', color='blue')

ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Average Grade", fontsize=12)
ax.set_title(f"Average Grade Trend for {selected_department}", fontsize=14, weight='bold')
ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))  # Forces integer labels

st.pyplot(fig)

# ------------------------------
# Calculate Average Grade Per Major Type Over Time
# ------------------------------
avg_grade_per_major_type = df.groupby(['Year', 'Major_Type'])['Grade'].mean().reset_index()

## New plot

st.write("### 📈 Average Grade Per Major Type Over Time")

# Get unique major types
major_types = avg_grade_per_major_type['Major_Type'].unique()

# Create the multi-line plot
fig, ax = plt.subplots(figsize=(10, 5))

for major_type in major_types:
    # Filter data for each major type
    major_type_data = avg_grade_per_major_type[avg_grade_per_major_type['Major_Type'] == major_type]

    # Plot each major type as a separate line
    ax.plot(major_type_data['Year'], major_type_data['Grade'], marker='o', linestyle='-', label=major_type)

# Customize the plot
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Average Grade", fontsize=12)
ax.set_title("Average Grade Trend Per Major Type", fontsize=14, weight='bold')
ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)

# Add legend
ax.legend(title="Major Type")

# Display in Streamlit
st.pyplot(fig)

