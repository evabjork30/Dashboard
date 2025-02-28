import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns


st.set_page_config(layout="wide")  # Expands the dashboard width


@st.cache_data  # Cache to improve performance
def load_data():
    df = pd.read_excel("df_27feb.xlsx")
    df['Year'] = (df['Semester'] // 10).astype(int)
    return df


df = load_data()  # ✅ Load the dataset properly

# Load the logo (Make sure the image is in the same folder OR use a URL)
logo_path = "HR_logo.jpeg"  # Local file

# Create two columns for title & logo
col1, col2 = st.columns([3, 1])  # Adjust ratio to balance text & image

with col1:
    st.title("Grade Inflation Analysis")
    st.markdown("<h3>Reykjavík University</h3>", unsafe_allow_html=True)

with col2:
    st.image(logo_path, width=200)  # Adjust width as needed


# ------------------------------
# Streamlit App
# ------------------------------
#st.title("📊 Grade Inflation Analysis - Reykjavík University")
st.write("This dashboard tracks **grade inflation** by analyzing the trend of average grades per year.")

# Add Filters
year_range = st.slider("Select Year Range:",
                       min_value=int(df['Year'].min()),
                       max_value=int(df['Year'].max()),
                       value=(int(df['Year'].min()), int(df['Year'].max())))

filtered_data = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]

# Remove Unnecessary Columns
filtered_data = filtered_data.drop(columns=['MajorID', 'Reg_Status', 'reg_birth_diff', 'Year'], errors='ignore')

# Group Data by Student ID
grouped_data = filtered_data.groupby('StudentID').agg(
    RegistrationYear=('RegistrationYear', 'first'),  # Keep the first Registration Year
    BirthYear=('BirthYear', 'first'),  # Keep the first Birth Year
    Gender=('Gender', 'first'),
    Origin=('Origin', 'first'),
    Department=('Department', 'first'),
    Major_Type=('Major_Type', 'first'),
    Major=('Major', 'first'),
    Number_of_Semesters=('Semester', 'count'),  # Count number of semesters per student
    Total_Credits=('Credits', 'sum'),  # Calculate total credits per student
    Average_Grade=('Grade', 'mean')  # Calculate average grade per student
).reset_index()

grouped_data['RegistrationYear'] = grouped_data['RegistrationYear'].map(lambda x: f"{x:.0f}" if x == int(x) else f"{x:.2f}")
grouped_data['StudentID'] = grouped_data['StudentID'].map(
    lambda x: f"{x:.0f}" if x == int(x) else f"{x:.2f}")
grouped_data['BirthYear'] = grouped_data['BirthYear'].map(
    lambda x: f"{x:.0f}" if x == int(x) else f"{x:.2f}")
grouped_data['Average_Grade'] = grouped_data['Average_Grade'].round(2)


# ------------------------------
# 📌 Add Dynamic Filters in Sidebar
# ------------------------------
st.sidebar.write("### 🔍 Filter Data")

# Department Filter
selected_departments = st.sidebar.multiselect(
    "Filter by Department",
    options=grouped_data['Department'].unique(),
    default=grouped_data['Department'].unique()  # Preselect all options by default
)

# Major Filter
selected_major_types = st.sidebar.multiselect(
    "Filter by Major Type",
    options=grouped_data['Major_Type'].unique(),
    default=grouped_data['Major_Type'].unique()
)

# Apply Filters
filtered_grouped_data = grouped_data[
    (grouped_data['Department'].isin(selected_departments)) &
    (grouped_data['Major_Type'].isin(selected_major_types))
]

# ------------------------------
# 📌 Display the Dynamically Filtered Table
# ------------------------------
st.write("### Filtered and Grouped Data Table")
st.dataframe(filtered_grouped_data, height=400, width=1500)

st.write("")  # Add one blank line
st.write("")  # Add another blank line
st.write("")  # Add one blank line
st.write("")  # Add another blank line
st.write("")  # Add one blank line
st.write("")  # Add another blank line

# Calculate Grade Trends
grade_trends = df.groupby('Year')['Grade'].mean()

# Split the layout: First plot on the left, extra content on the right
col_left, col_right = st.columns([1.5, 1])  # Adjust column widths

with col_left:
    # Ensure "student id" and "department" columns exist
    if 'StudentID' in df.columns and 'Department' in df.columns:
        # Remove duplicate student records (keeping only the first row per student)
        unique_students = df.drop_duplicates(subset=['StudentID'])

        # Count number of unique students per department
        student_counts = unique_students['Department'].value_counts().reset_index()
        student_counts.columns = ['Department', 'Number of Students']

        # Display as a table
        st.write("### 📊 Number of Students per Department")

        # Create a bar chart
        fig_students, ax_students = plt.subplots(figsize=(6, 3))  # Mini bar chart size
        ax_students.bar(student_counts['Department'], student_counts['Number of Students'], color='lightcoral')

        ax_students.tick_params(axis='x', rotation=60, labelsize=8)  # Rotate labels for readability
        ax_students.set_xticklabels([label.replace(" ", "\n") for label in student_counts['Department']])
        ax_students.set_xticklabels(student_counts['Department'], rotation=45, ha="right", fontsize=8)

        plt.subplots_adjust(bottom=0.3)  # Pushes labels down to make space

        st.pyplot(fig_students)  # Display the bar chart
    else:
        st.warning("⚠️ 'Student ID' or 'Department' column not found in dataset! Please check your data.")


with col_right:
    st.write("### 📊 Key Statistics")
    #st.metric("📈 Average Grade", round(df['Grade'].mean(), 2))
    #st.metric("📉 Lowest Grade", round(df['Grade'].min(), 2))
    #st.metric("🏆 Highest Grade", round(df['Grade'].max(), 2))

    total_students = df['StudentID'].nunique()
    largest_department = df.groupby('Department')['StudentID'].nunique().idxmax()
    largest_department_count = df.groupby('Department')['StudentID'].nunique().max()
    smallest_department = df.groupby('Department')['StudentID'].nunique().idxmin()
    smallest_department_count = df.groupby('Department')['StudentID'].nunique().min()
    largest_dept_percentage = (largest_department_count / total_students) * 100
    avg_students_per_dept = df.groupby('Department')['StudentID'].nunique().mean()

    sub_col1, sub_col2 = st.columns(2)

    with sub_col1:

        # Total number of students
        st.metric("Total students", total_students)

        # Largest department
        st.metric(largest_department, largest_department_count)

        # Smallest department
        st.metric(smallest_department, smallest_department_count)

    with sub_col2:
        # % of students in largest department
        st.metric("% of students in largest department", f"{round(largest_dept_percentage)}%")

        # Average students per department
        st.metric("Average students per department", round(avg_students_per_dept))


st.write("")  # Add one blank line
st.write("")  # Add another blank line
st.write("")  # Add one blank line
st.write("")  # Add another blank line
st.write("")  # Add one blank line
st.write("")  # Add another blank line

col5, col6 = st.columns(2)

with col5:
    st.write("### 📊 Key Statistics")
    overall_avg_grade = df['Grade'].mean()
    min_avg_grade = df.groupby('Year')['Grade'].mean().min()
    min_avg_year = df.groupby('Year')['Grade'].mean().idxmin()
    max_avg_grade = df.groupby('Year')['Grade'].mean().max()
    max_avg_year = df.groupby('Year')['Grade'].mean().idxmax()
    yearly_grade_change = df.groupby('Year')['Grade'].mean().pct_change().mean() * 100
    avg_grade_2019 = df[df['Year'] == 2019]['Grade'].mean()
    avg_grade_latest = df[df['Year'] == df['Year'].max()]['Grade'].mean()
    inflation_since_2019 = ((avg_grade_latest - avg_grade_2019) / avg_grade_2019) * 100

    sub_col3, sub_col4 = st.columns(2)

    with sub_col3:

        st.metric("Overall avg grade", round(overall_avg_grade, 2))

        #print(f'Lowest avg grade: {round(min_avg_grade, 2)} ({min_avg_year})')
        st.metric("Lowest avg grade", round(min_avg_grade, 2))

        #print(f'Highest avg grade: {round(max_avg_grade, 2)} ({max_avg_year})')
        st.metric("Highest avg grade", round(max_avg_grade, 2))

    with sub_col4:
        # Print avg yearly change with % in st.metric
        st.metric("Avg Yearly Change", f"{round(yearly_grade_change, 2)}%", delta=f"{round(yearly_grade_change, 2)}%")

        # Print grade inflation since 2019 with %
        st.metric("Grade Inflation Since 2019", f"{round(inflation_since_2019, 2)}%",
                  delta=f"{round(inflation_since_2019, 2)}%")

with col6:
    st.write("### 📈 Trend of Average Grades")
    # Create a smaller figure for the trend plot
    fig, ax = plt.subplots(figsize=(10, 5))  # Reduce plot size
    ax.plot(grade_trends.index, grade_trends.values, marker='o', linestyle='-', color='red')
    ax.set_xlabel("Year", fontsize=10)
    ax.set_ylabel("Average Grade", fontsize=10)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))  # Forces integer labels

    st.pyplot(fig)  # Display the smaller plot

st.write("")  # Add one blank line
st.write("")  # Add another blank line
st.write("")  # Add one blank line
st.write("")  # Add another blank line
st.write("")  # Add one blank line
st.write("")  # Add another blank line

col1, col2 = st.columns(2)

with col1:

    # Compute average grade per department over time
    avg_grade_per_department = df.groupby(['Year', 'Department'])['Grade'].mean().reset_index()

    ## New plot

    st.write("### 📈 Average Grade Per Department Over Time")

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
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))  # Forces integer labels

    st.pyplot(fig)

with col2:
    st.write("### 📊 Key Statistics")
    # Breytan heitir hér, selected department, sem er þá valda deildin úr dropdown menu.
    max_avg_grade_d = df[df['Department'] == selected_department].groupby('Year')['Grade'].mean().max()
    max_avg_year_d = df[df['Department'] == selected_department].groupby('Year')['Grade'].mean().idxmax()

    min_avg_grade_d = df[df['Department'] == selected_department].groupby('Year')['Grade'].mean().min()
    min_avg_year_d = df[df['Department'] == selected_department].groupby('Year')['Grade'].mean().idxmin()

    dept_grade_change = df[df['Department'] == selected_department].groupby('Year')[
                            'Grade'].mean().pct_change().mean() * 100

    dept_rank = df.groupby('Department')['Grade'].mean().rank(ascending=False)

    sub_col5, sub_col6 = st.columns(2)

    with sub_col5:

        st.metric("Highest avg grade", round(max_avg_grade_d, 2))

        st.metric("Lowest avg grade", round(min_avg_grade_d, 2))

    with sub_col6:

        st.metric("Avg Yearly Change", f"{round(dept_grade_change, 2)}%", delta=f"{round(dept_grade_change, 2)}%")

        if selected_department in dept_rank.index:
            st.metric(f"{selected_department} Rank in Avg Grade", int(dept_rank.loc[selected_department]))
        else:
            st.warning("⚠️ Selected department not found in ranking.")

        avg_students_per_year_d = df[df['Department'] == selected_department].groupby('Year')['StudentID'].nunique().mean()
        st.metric("Avg students per year:", round(avg_students_per_year_d))


st.write("")  # Add one blank line
st.write("")  # Add another blank line
st.write("")  # Add one blank line
st.write("")  # Add another blank line
st.write("")  # Add one blank line
st.write("")  # Add another blank line

col3, col4 = st.columns(2)

with col3:
    st.write("### 📊 Key Statistics")
    latest_year = df['Year'].max()
    total_students = df['StudentID'].nunique()
    students_per_major = df.groupby('Major_Type')['StudentID'].nunique()
    percentage_students_per_major = (students_per_major / total_students) * 100

    latest_avg_grade_per_major = df[df['Year'] == latest_year].groupby('Major_Type')['Grade'].mean()
    min_avg_grade_per_major = df.groupby(['Major_Type', 'Year'])['Grade'].mean().groupby(level=0).min()
    min_avg_year_per_major = df.groupby(['Major_Type', 'Year'])['Grade'].mean().groupby(level=0).idxmin()
    max_avg_grade_per_major = df.groupby(['Major_Type', 'Year'])['Grade'].mean().groupby(level=0).max()
    max_avg_year_per_major = df.groupby(['Major_Type', 'Year'])['Grade'].mean().groupby(level=0).idxmax()
    avg_yearly_change_per_major = df.groupby(['Major_Type', 'Year'])['Grade'].mean().groupby(
        level=0).pct_change().groupby(level=0).mean() * 100
    rank_per_major = df.groupby('Major_Type')['Grade'].mean().rank(ascending=False)

    table_data = pd.DataFrame({
        "Latest Avg Grade": latest_avg_grade_per_major.round(2),
        "Lowest Avg Grade (Year)": [f"{min_avg_grade_per_major[i]:.2f} ({min_avg_year_per_major[i][1]})" for i in
                                    min_avg_grade_per_major.index],
        "Highest Avg Grade (Year)": [f"{max_avg_grade_per_major[i]:.2f} ({max_avg_year_per_major[i][1]})" for i in
                                     max_avg_grade_per_major.index],
        "Avg Yearly Change (%)": avg_yearly_change_per_major.round(2).astype(str) + "%",
        "% of Total Students": percentage_students_per_major.round(2).astype(str) + "%",
        "Rank in Avg Grade": rank_per_major.astype(int)
    })

    # Transpose the table for better readability
    table_data_transposed = table_data.T  # Makes majors columns instead of rows

    # 🔹 Fix: Only Apply Formatting to Numeric Columns
    numeric_columns = ["Latest Avg Grade", "Rank in Avg Grade"]  # Only format numerical columns
    formatted_table = table_data_transposed.copy()
    for col in numeric_columns:
        formatted_table[col] = formatted_table[col].astype(float).map("{:.2f}".format)

    # Display the table with better formatting
    st.write("#### 📋 Summary Statistics by Major Type")
    st.dataframe(
        formatted_table.style.format("{:.2f}"),  # Ensures 2 decimal places
        height=300, width=900  # Adjusts the table size to avoid excessive scrolling
    )

with col4:

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
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))  # Forces integer labels

    # Add legend
    ax.legend(title="Major Type")

    # Display in Streamlit
    st.pyplot(fig)

st.write("")  # Add one blank line
st.write("")  # Add another blank line
st.write("")  # Add one blank line
st.write("")  # Add another blank line
st.write("")  # Add one blank line
st.write("")  # Add another blank line

col7, col8 = st.columns(2)

with col7:
    st.write("### 📈 Grade Distribution by Gender")
    # Filter dataset for relevant genders
    filtered_df = df[df['Gender'].isin(['Karl', 'Kona'])]

    # Create the box plot
    fig, ax = plt.subplots(figsize=(10, 6))  # Keep consistent sizing
    sns.boxplot(x='Gender', y='Grade', data=filtered_df, palette=['green', 'yellow'], ax=ax)

    # Customize plot appearance
    ax.set_xlabel('Gender', fontsize=12.5)
    ax.set_ylabel('Grade', fontsize=12.5)
    ax.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.35, axis='y')

    # Display the plot in Streamlit
    st.pyplot(fig)

with col8:
    st.write("### 📊 Key Statistics by Gender")

    # Filter dataset (Exclude 'Kynsegin/annað')
    filtered_df = df[df['Gender'].isin(['Karl', 'Kona'])]

    # Compute descriptive statistics
    gender_stats = filtered_df.groupby('Gender')['Grade'].describe().round(2)

    # Rename columns for clarity
    gender_stats.rename(columns={
        "count": "Number of Students",
        "mean": "Mean Grade",
        "std": "Std Dev (Variation)",
        "25%": "25th Percentile (Q1)",
        "50%": "Median Grade",
        "75%": "75th Percentile (Q3)",
    }, inplace=True)

    # Select and transpose the table for better readability
    gender_table_data = gender_stats[
        ["Mean Grade", "Median Grade", "Std Dev (Variation)",
         "25th Percentile (Q1)", "75th Percentile (Q3)", "Number of Students"]
    ].T  # Transpose: Rows → Columns

    # Display table with better formatting
    st.write("#### 📋 Summary Statistics")

    st.dataframe(
        gender_table_data.style.format("{:.2f}"),  # Ensures 2 decimal places
        height=250, width=600  # Adjusts the table size
    )

st.write("")  # Add one blank line
st.write("")  # Add another blank line
st.write("")  # Add one blank line
st.write("")  # Add another blank line
st.write("")  # Add one blank line
st.write("")  # Add another blank line

# ------------------------------
# 📌 COVID Time: Compare Average Grades Per Department (2019-2022)
# ------------------------------
st.write("### 📈 Compare Average Grades Per Department (2019-2022)")

# Filter data for COVID years
covid_df = df[(df['Year'] >= 2019) & (df['Year'] <= 2022)]

# Compute average grade per department over time
covid_avg_grade = covid_df.groupby(['Year', 'Department'])['Grade'].mean().reset_index()

# Multi-select dropdown to choose multiple departments
departments = covid_avg_grade['Department'].unique()
selected_departments = st.multiselect(
    "Select Departments to Compare:", departments, default=departments[:3]  # Pre-select first 3 departments
)

# Ensure at least one department is selected
if selected_departments:
    # Create the multi-line plot
    fig, ax = plt.subplots(figsize=(10, 5))

    # Loop through selected departments and plot each one
    for department in selected_departments:
        department_data = covid_avg_grade[covid_avg_grade['Department'] == department]
        ax.plot(department_data['Year'], department_data['Grade'], marker='o', linestyle='-', label=department)

    # Customize the plot
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Average Grade", fontsize=12)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))  # Force integer labels

    # Add a legend
    ax.legend(title="Department", bbox_to_anchor=(1.05, 1), loc='upper left')  # Moves legend outside for better visibility

    # Display in Streamlit
    st.pyplot(fig)
else:
    st.warning("⚠ Please select at least one department to display the comparison.")
