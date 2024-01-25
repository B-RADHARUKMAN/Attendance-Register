import streamlit as st
import pandas as pd

def load_credentials():
    return st.secrets["login"]["username"], st.secrets["login"]["password"]

def authenticate(username, password):
    stored_username, stored_password = load_credentials()
    return username == stored_username and password == stored_password

def submit_attendance(df, name, date, present):
    # Check if an entry for the EMPID on the given date already exists
    existing_entry = df[(df['EMPID'] == name) & (df['Date'] == date)]

    if not existing_entry.empty:
        st.warning(f"Attendance for {name} on {date} already submitted.")
    else:
        new_entry = {"Date": date, "EMPID": name, "Present": present}
        df = df.append(new_entry, ignore_index=True)
        df.to_csv("attendance_data.csv", index=False)
        st.success(f"Attendance submitted for {name} on {date}")

    return df

def search_attendance(df, search_name):
    return df[df["EMPID"] == search_name]

def teaching_attendance(df, selected_date):
    # Filter attendance data for the selected date
    selected_date_data = df[df["Date"] == selected_date]

    # Number of persons present and absent
    total_present = selected_date_data["Present"].sum()
    total_absent = len(df["EMPID"].unique()) - total_present

    # Details of absentees
    all_empids = set(df["EMPID"].unique())
    present_empids = set(selected_date_data["EMPID"].unique())
    absent_empids = all_empids - present_empids

    # Display attendance details
    st.subheader(f"Teaching Attendance on {selected_date}")
    st.write(f"Number of Persons Present: {total_present}")
    st.write(f"Number of Persons Absent: {total_absent}")

    if total_absent > 0:
        st.subheader("Details of Absentees:")
        absentees_details = df[df["EMPID"].isin(absent_empids)][["EMPID", "Present", "Date"]]
        st.write(absentees_details)

def main():
    # Check if 'login' key exists in session state
    if 'login' not in st.session_state:
        st.session_state.login = False

    # Authentication (in sidebar)
    with st.sidebar:
        st.header("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(username, password):
                st.session_state.login = True
                st.experimental_set_query_params(logged_in=True)  # Set query parameter for page reload
                st.success("Login successful!")

    if st.session_state.login:
        # Load or create the attendance data DataFrame
        try:
            df = pd.read_csv("attendance_data.csv", parse_dates=["Date"])
        except FileNotFoundError:
            df = pd.DataFrame(columns=["Date", "EMPID", "Present"])

        # Load the REGISTER data
        try:
            register_df = pd.read_csv("REGISTER.csv")
        except FileNotFoundError:
            register_df = pd.DataFrame(columns=["EMPID", "Name", "Department", "Position"])

        # Merge attendance data with details from the REGISTER data
        df_merged = pd.merge(df, register_df, on="EMPID", how="left")

        # Tabs
        tabs = ["Submit Attendance", "Download Attendance", "Search Attendance"]
        selected_tab = st.radio("Select Option", tabs)

        if selected_tab == "Submit Attendance":
            st.header("Submit Attendance")
            # Get user input for EMPID, date, and attendance
            name = st.text_input("EMPID")
            date = st.date_input("Select Date", pd.to_datetime("today"))
            present = st.checkbox("Present")

            if st.button("Submit Attendance"):
                df = submit_attendance(df, name, date, present)

        elif selected_tab == "Download Attendance":
            st.header("Download Attendance")
            # Export data button
            if st.button("Download CSV"):
                df.to_csv("exported_attendance_data.csv", index=False)
                st.success("Attendance data downloaded successfully!")

        elif selected_tab == "Search Attendance":
            st.header("Search Attendance")
            # Search for attendance records based on EMPID
            search_name = st.text_input("Search by EMPID")
            if st.button("Search"):
                search_result = search_attendance(df_merged, search_name)
                st.write(search_result)




        # Show the attendance data with person details below
        st.header("Attendance Data with Person Details")
        st.write(df_merged)

    else:
        if 'login' in st.session_state and st.session_state.login:
            st.warning("Invalid username or password. Please try again.")

if __name__ == "__main__":
    main()
