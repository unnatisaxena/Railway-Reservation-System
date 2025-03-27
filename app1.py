import streamlit as st
import mysql.connector
import datetime
import bcrypt
import plotly.express as px
import pandas as pd
from PIL import Image
import base64
import io
import requests
from io import BytesIO
import time
# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234#u',
    'database': 'railway_db'
}

# Database Connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

# Authentication Functions
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

def img_to_bytes(img_path, is_url=False):
    if is_url:
        response = requests.get(img_path)
        img = Image.open(BytesIO(response.content))
    else:
        img = Image.open(img_path)
    
    # Ensure image has alpha channel for transparency
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    byte_arr = io.BytesIO()
    img.save(byte_arr, format='PNG')
    return base64.b64encode(byte_arr.getvalue()).decode()

def show_loading_animation():
    station_img = img_to_bytes("1299.jpg")
    train_img = img_to_bytes("train1.png")
    
    loading_html = f"""
    <style>
        .loading-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            z-index: 9999;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }}
        .animation-wrapper {{
            width: 80%;
            max-width: 800px;
            position: relative;
            height: 300px;
            overflow: hidden;
        }}
        .station-bg {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .train {{
            height: 150px;
            position: absolute;
            bottom: -4%;
            left: -200px;
            animation: moveTrain 3s ease-in forwards;
        }}
        @keyframes moveTrain {{
            0% {{ transform: translateX(-200px); }}
            100% {{ transform: translateX(calc(100% + 200px)); }}
        }}
        .loading-text {{
            margin-top: 30px;
            color: white;
            font-size: 1.8rem;
        }}
    </style>
    
    <div class="loading-container" id="loadingAnimation">
        <div class="animation-wrapper">
            <img src="data:image/png;base64,{station_img}" class="station-bg">
            <img src="data:image/png;base64,{train_img}" class="train">
        </div>
        <div class="loading-text">All Aboard! Loading Your Journey...</div>
    </div>
    
    <script>
        // Remove animation after it completes
        setTimeout(function() {{
            var element = document.getElementById("loadingAnimation");
            element.parentNode.removeChild(element);
        }}, 3000);
    </script>
    """
    
    st.markdown(loading_html, unsafe_allow_html=True)
    time.sleep(3)

# User Authentication Functions
def user_login():
    st.header("User Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s AND role = 'user'", (username,))
            user = cursor.fetchone()
            
            if user and verify_password(user['password'], password):
                st.session_state.logged_in = True
                st.session_state.user_id = user['user_id']
                st.session_state.username = user['username']
                st.session_state.user_type = 'user'
                st.success("User Login Successful!")
                st.rerun()
            elif user and not verify_password(user['password'], password):
                st.error("Invalid password")
            else:
                st.error("Invalid User Credentials")
            cursor.close()
            conn.close()

def user_register():
    st.header("User Registration")
    new_username = st.text_input("Choose Username")
    new_email = st.text_input("Email")
    new_password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if new_password == confirm_password:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (new_username, new_email))
                existing_user = cursor.fetchone()

                if existing_user:
                    st.error("Username or Email already exists")
                else:
                    hashed_pw = hash_password(new_password).decode('utf-8')
                    cursor.execute(
                        "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, 'user')",
                        (new_username, new_email, hashed_pw)
                    )
                    conn.commit()
                    st.success("User Registration Successful!")
                cursor.close()
                conn.close()
        else:
            st.error("Passwords do not match")

# Admin Authentication Functions
def admin_login():
    st.header("Admin Login")
    admin_username = st.text_input("Admin Username")
    admin_password = st.text_input("Admin Password", type="password")

    if st.button("Admin Login"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s AND role = 'admin'", (admin_username,))
            admin = cursor.fetchone()
            
            if admin and verify_password(admin['password'], admin_password):
                st.session_state.logged_in = True
                st.session_state.user_id = admin['user_id']
                st.session_state.username = admin['username']
                st.session_state.user_type = 'admin'
                st.success("Admin Login Successful!")
                st.rerun()
            else:
                st.error("Invalid Admin Credentials")
            cursor.close()
            conn.close()

def admin_register():
    st.header("Admin Registration")
    new_admin_username = st.text_input("Choose Admin Username")
    new_admin_email = st.text_input("Admin Email")
    new_admin_password = st.text_input("Admin Password", type="password")
    confirm_admin_password = st.text_input("Confirm Admin Password", type="password")
    admin_secret_key = st.text_input("Admin Secret Key", type="password")

    if st.button("Register Admin"):
        if admin_secret_key != "ADMIN2024":
            st.error("Invalid Admin Secret Key")
            return

        if new_admin_password == confirm_admin_password:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (new_admin_username, new_admin_email))
                existing_admin = cursor.fetchone()

                if existing_admin:
                    st.error("Username or Email already exists")
                else:
                    hashed_pw = hash_password(new_admin_password).decode('utf-8')
                    cursor.execute(
                        "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, 'admin')",
                        (new_admin_username, new_admin_email, hashed_pw)
                    )
                    conn.commit()
                    st.success("Admin Registration Successful!")
                cursor.close()
                conn.close()
        else:
            st.error("Passwords do not match")

# Application Pages
def view_trains():
    st.header("Available Trains")
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM trains")
        trains = cursor.fetchall()
        
        cols = st.columns(3)
        for i, train in enumerate(trains):
            with cols[i % 3]:
                with st.container(border=True):
                    st.write(f"**{train['train_name']}**")
                    st.write(f"Source: {train['source']}")
                    st.write(f"Destination: {train['destination']}")
                    st.write(f"Total Seats: {train['total_seats']}")
                    st.write(f"Waiting List Capacity: {train['waiting_list_capacity']}")
                    
                    if st.button(f"Select Train {train['train_id']}", key=f"train_{train['train_id']}"):
                        st.session_state.selected_train_id = train['train_id']
                        st.success(f"Selected Train: {train['train_name']}")

        if hasattr(st.session_state, 'selected_train_id'):
            st.header("Book Ticket")
            cursor.execute("SELECT * FROM trains WHERE train_id = %s", (st.session_state.selected_train_id,))
            selected_train = cursor.fetchone()
            
            if not selected_train:
                st.error("Selected train not found")
                cursor.close()
                conn.close()
                return

            travel_date = st.date_input("Select Travel Date", min_value=datetime.date.today())

            cursor.execute(
                "SELECT * FROM schedule WHERE train_id = %s AND travel_date = %s",
                (selected_train['train_id'], travel_date)
            )
            schedule = cursor.fetchone()

            if not schedule:
                cursor.execute(
                    "INSERT INTO schedule (train_id, travel_date, available_seats, waiting_list) VALUES (%s, %s, %s, 0)",
                    (selected_train['train_id'], travel_date, selected_train['total_seats'])
                )
                conn.commit()
                schedule_id = cursor.lastrowid
            else:
                schedule_id = schedule['schedule_id']

            cursor.execute(
                "SELECT available_seats, waiting_list FROM schedule WHERE schedule_id = %s",
                (schedule_id,)
            )
            schedule_data = cursor.fetchone()
            available_seats = schedule_data['available_seats']
            waiting_list = schedule_data['waiting_list']

            if available_seats > 0:
                passenger_name = st.text_input("Passenger Name")

                if st.button("Confirm Booking"):
                    seat_number = selected_train['total_seats'] - available_seats + 1

                    cursor.execute(
                        "INSERT INTO reservations (user_id, train_id, schedule_id, passenger_name, seat_number, status) VALUES (%s, %s, %s, %s, %s, 'Booked')",
                        (st.session_state.user_id, selected_train['train_id'], schedule_id, passenger_name, seat_number)
                    )
                    cursor.execute(
                        "UPDATE schedule SET available_seats = available_seats - 1 WHERE schedule_id = %s",
                        (schedule_id,)
                    )
                    conn.commit()
                    st.success(f"Ticket Booked! PNR: {cursor.lastrowid}")
                    del st.session_state.selected_train_id
                    cursor.close()
                    conn.close()
                    st.rerun()
            
            elif waiting_list < selected_train['waiting_list_capacity']:
                passenger_name = st.text_input("Passenger Name")

                if st.button("Add to Waiting List"):
                    cursor.execute(
                        "INSERT INTO reservations (user_id, train_id, schedule_id, passenger_name, status) VALUES (%s, %s, %s, %s, 'Waiting')",
                        (st.session_state.user_id, selected_train['train_id'], schedule_id, passenger_name)
                    )
                    cursor.execute(
                        "UPDATE schedule SET waiting_list = waiting_list + 1 WHERE schedule_id = %s",
                        (schedule_id,)
                    )
                    conn.commit()
                    st.success(f"Added to waiting list! PNR: {cursor.lastrowid}")
                    del st.session_state.selected_train_id
                    cursor.close()
                    conn.close()
                    st.rerun()
            else:
                st.warning("No seats available and waiting list is full for selected train and date")
        
        cursor.close()
        conn.close()

def my_bookings():
    st.header("My Bookings")
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.*, t.train_name, s.travel_date 
            FROM reservations r
            JOIN trains t ON r.train_id = t.train_id
            JOIN schedule s ON r.schedule_id = s.schedule_id
            WHERE r.user_id = %s
            ORDER BY r.status
        """, (st.session_state.user_id,))
        bookings = cursor.fetchall()

        for booking in bookings:
            with st.container(border=True):
                st.write(f"**PNR:** {booking['pnr_id']}")
                st.write(f"**Train:** {booking['train_name']}")
                st.write(f"**Passenger:** {booking['passenger_name']}")
                st.write(f"**Status:** {booking['status']}")
                if booking['seat_number']:
                    st.write(f"**Seat Number:** {booking['seat_number']}")
                st.write(f"**Travel Date:** {booking['travel_date']}")
                
                if booking['status'] in ['Booked', 'Waiting']:
                    if st.button(f"Cancel Booking {booking['pnr_id']}", key=f"cancel_{booking['pnr_id']}"):
                        if booking['status'] == 'Booked':
                            # Free up the seat
                            cursor.execute(
                                "UPDATE schedule SET available_seats = available_seats + 1 WHERE schedule_id = %s",
                                (booking['schedule_id'],)
                            )
                            
                            # Check for waiting list passengers to promote
                            cursor.execute(
                                "SELECT * FROM reservations WHERE schedule_id = %s AND status = 'Waiting' ORDER BY pnr_id LIMIT 1",
                                (booking['schedule_id'],)
                            )
                            waiting_reservation = cursor.fetchone()
                            
                            if waiting_reservation:
                                cursor.execute(
                                    "UPDATE reservations SET status = 'Booked', seat_number = %s WHERE pnr_id = %s",
                                    (booking['seat_number'], waiting_reservation['pnr_id'])
                                )
                                cursor.execute(
                                    "UPDATE schedule SET waiting_list = waiting_list - 1 WHERE schedule_id = %s",
                                    (booking['schedule_id'],)
                                )
                                st.success(f"Seat {booking['seat_number']} has been assigned to waiting passenger {waiting_reservation['passenger_name']}")
                        
                        elif booking['status'] == 'Waiting':
                            cursor.execute(
                                "UPDATE schedule SET waiting_list = waiting_list - 1 WHERE schedule_id = %s",
                                (booking['schedule_id'],)
                            )
                        
                        # Cancel the booking
                        cursor.execute(
                            "UPDATE reservations SET status = 'Cancelled' WHERE pnr_id = %s",
                            (booking['pnr_id'],)
                        )
                        conn.commit()
                        st.success("Booking cancelled successfully!")
                        cursor.close()
                        conn.close()
                        st.rerun()
        
        cursor.close()
        conn.close()

def logout():
    st.session_state.logged_in = False
    if 'user_id' in st.session_state:
        del st.session_state.user_id
    if 'username' in st.session_state:
        del st.session_state.username
    if 'user_type' in st.session_state:
        del st.session_state.user_type
    if 'selected_train_id' in st.session_state:
        del st.session_state.selected_train_id
    st.rerun()

# Admin Functions
def manage_trains():
    st.header("Manage Trains")
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        action = st.radio("Choose Action", ["View All Trains", "Add New Train", "Update Train", "Delete Train"])
        
        if action == "View All Trains":
            cursor.execute("SELECT * FROM trains")
            trains = cursor.fetchall()
            for train in trains:
                with st.container(border=True):
                    st.write(f"**Train ID:** {train['train_id']}")
                    st.write(f"**Name:** {train['train_name']}")
                    st.write(f"**Source:** {train['source']}")
                    st.write(f"**Destination:** {train['destination']}")
                    st.write(f"**Total Seats:** {train['total_seats']}")
                    st.write(f"**Waiting List Capacity:** {train['waiting_list_capacity']}")
        
        elif action == "Add New Train":
            with st.form("add_train_form"):
                train_name = st.text_input("Train Name")
                source = st.text_input("Source Station")
                destination = st.text_input("Destination Station")
                total_seats = st.number_input("Total Seats", min_value=1, value=5)
                waiting_capacity = st.number_input("Waiting List Capacity", min_value=1, value=1)
                
                if st.form_submit_button("Add Train"):
                    cursor.execute(
                        "INSERT INTO trains (train_name, source, destination, total_seats, waiting_list_capacity) VALUES (%s, %s, %s, %s, %s)",
                        (train_name, source, destination, total_seats, waiting_capacity)
                    )
                    conn.commit()
                    st.success("Train added successfully!")
        
        elif action == "Update Train":
            cursor.execute("SELECT * FROM trains")
            trains = cursor.fetchall()
            train_options = {f"{train['train_id']} - {train['train_name']}": train['train_id'] for train in trains}
            selected_train = st.selectbox("Select Train to Update", options=list(train_options.keys()))
            
            if selected_train:
                train_id = train_options[selected_train]
                cursor.execute("SELECT * FROM trains WHERE train_id = %s", (train_id,))
                train = cursor.fetchone()
                
                with st.form("update_train_form"):
                    new_name = st.text_input("Train Name", value=train['train_name'])
                    new_source = st.text_input("Source Station", value=train['source'])
                    new_destination = st.text_input("Destination Station", value=train['destination'])
                    new_seats = st.number_input("Total Seats", min_value=1, value=train['total_seats'])
                    new_waiting = st.number_input("Waiting List Capacity", min_value=1, value=train['waiting_list_capacity'])
                    
                    if st.form_submit_button("Update Train"):
                        cursor.execute(
                            "UPDATE trains SET train_name = %s, source = %s, destination = %s, total_seats = %s, waiting_list_capacity = %s WHERE train_id = %s",
                            (new_name, new_source, new_destination, new_seats, new_waiting, train_id)
                        )
                        conn.commit()
                        st.success("Train updated successfully!")
        
        elif action == "Delete Train":
            cursor.execute("SELECT * FROM trains")
            trains = cursor.fetchall()
            train_options = {f"{train['train_id']} - {train['train_name']}": train['train_id'] for train in trains}
            selected_train = st.selectbox("Select Train to Delete", options=list(train_options.keys()))
            
            if selected_train and st.button("Delete Train"):
                train_id = train_options[selected_train]
                # Check if there are any reservations for this train
                cursor.execute("SELECT COUNT(*) as count FROM reservations WHERE train_id = %s", (train_id,))
                reservations = cursor.fetchone()['count']
                if reservations > 0:
                    st.error("Cannot delete train with existing reservations")
                else:
                    cursor.execute("DELETE FROM schedule WHERE train_id = %s", (train_id,))
                    cursor.execute("DELETE FROM trains WHERE train_id = %s", (train_id,))
                    conn.commit()
                    st.success("Train deleted successfully!")
        
        cursor.close()
        conn.close()

def manage_bookings():
    st.header("Manage Bookings")
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        action = st.radio("Choose Action", ["View All Bookings", "Cancel Booking"])
        
        if action == "View All Bookings":
            cursor.execute("""
                SELECT r.*, t.train_name, u.username, s.travel_date 
                FROM reservations r
                JOIN trains t ON r.train_id = t.train_id
                JOIN users u ON r.user_id = u.user_id
                JOIN schedule s ON r.schedule_id = s.schedule_id
                ORDER BY r.status
            """)
            bookings = cursor.fetchall()
            for booking in bookings:
                with st.container(border=True):
                    st.write(f"**PNR:** {booking['pnr_id']}")
                    st.write(f"**Train:** {booking['train_name']}")
                    st.write(f"**User:** {booking['username']}")
                    st.write(f"**Passenger:** {booking['passenger_name']}")
                    st.write(f"**Status:** {booking['status']}")
                    if booking['seat_number']:
                        st.write(f"**Seat Number:** {booking['seat_number']}")
                    st.write(f"**Travel Date:** {booking['travel_date']}")
        
        elif action == "Cancel Booking":
            cursor.execute("""
                SELECT r.*, t.train_name 
                FROM reservations r
                JOIN trains t ON r.train_id = t.train_id
                WHERE r.status IN ('Booked', 'Waiting')
            """)
            bookings = cursor.fetchall()
            
            booking_options = {
                f"{b['pnr_id']} - {b['passenger_name']} - {b['train_name']}": b['pnr_id'] 
                for b in bookings
            }
            selected_booking = st.selectbox("Select Booking to Cancel", options=list(booking_options.keys()))
            
            if selected_booking and st.button("Cancel Booking"):
                pnr_id = booking_options[selected_booking]
                cursor.execute("SELECT * FROM reservations WHERE pnr_id = %s", (pnr_id,))
                booking = cursor.fetchone()
                
                if booking['status'] == 'Booked':
                    # Free up the seat
                    cursor.execute(
                        "UPDATE schedule SET available_seats = available_seats + 1 WHERE schedule_id = %s",
                        (booking['schedule_id'],)
                    )
                    
                    # Check for waiting list passengers to promote
                    cursor.execute(
                        "SELECT * FROM reservations WHERE schedule_id = %s AND status = 'Waiting' ORDER BY pnr_id LIMIT 1",
                        (booking['schedule_id'],)
                    )
                    waiting_reservation = cursor.fetchone()
                    
                    if waiting_reservation:
                        cursor.execute(
                            "UPDATE reservations SET status = 'Booked', seat_number = %s WHERE pnr_id = %s",
                            (booking['seat_number'], waiting_reservation['pnr_id'])
                        )
                        cursor.execute(
                            "UPDATE schedule SET waiting_list = waiting_list - 1 WHERE schedule_id = %s",
                            (booking['schedule_id'],)
                        )
                        st.success(f"Seat {booking['seat_number']} assigned to waiting passenger {waiting_reservation['passenger_name']}")
                
                elif booking['status'] == 'Waiting':
                    cursor.execute(
                        "UPDATE schedule SET waiting_list = waiting_list - 1 WHERE schedule_id = %s",
                        (booking['schedule_id'],)
                    )
                
                # Cancel the booking
                cursor.execute(
                    "UPDATE reservations SET status = 'Cancelled' WHERE pnr_id = %s",
                    (pnr_id,)
                )
                conn.commit()
                st.success("Booking cancelled successfully!")
                st.rerun()
        
        cursor.close()
        conn.close()

def reservation_analytics():
    st.header("📊 Reservation Analytics")
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Calculate metrics
            cursor.execute("SELECT COUNT(*) as count FROM reservations")
            total_bookings = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM reservations WHERE status = 'Booked'")
            active_bookings = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM reservations WHERE status = 'Cancelled'")
            cancelled_bookings = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM reservations WHERE status = 'Waiting'")
            waiting_list = cursor.fetchone()['count']
            
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Bookings", total_bookings)
            col2.metric("Active Bookings", active_bookings)
            col3.metric("Cancelled Bookings", cancelled_bookings)
            col4.metric("Waiting List", waiting_list)
            
            # Bookings by status pie chart
            st.subheader("Bookings by Status")
            status_data = pd.DataFrame({
                'Status': ['Booked', 'Cancelled', 'Waiting'],
                'Count': [active_bookings, cancelled_bookings, waiting_list]
            })
            fig = px.pie(
                status_data,
                names='Status',
                values='Count',
                title='Booking Status Distribution'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Time series chart of bookings - using schedule.travel_date instead of created_at
            st.subheader("Bookings Over Time")
            cursor.execute("""
                SELECT s.travel_date as date, COUNT(r.pnr_id) as count 
                FROM reservations r
                JOIN schedule s ON r.schedule_id = s.schedule_id
                GROUP BY s.travel_date 
                ORDER BY date
            """)
            bookings_by_date = cursor.fetchall()
            
            if bookings_by_date:
                df = pd.DataFrame(bookings_by_date)
                fig = px.line(
                    df,
                    x='date',
                    y='count',
                    labels={'date': 'Date', 'count': 'Number of Bookings'},
                    title="Daily Bookings Trend (by Travel Date)"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No booking data available for time series analysis")
            
            # Popular trains analysis
            st.subheader("Most Popular Trains")
            cursor.execute("""
                SELECT t.train_name, COUNT(r.pnr_id) as bookings
                FROM trains t
                LEFT JOIN reservations r ON t.train_id = r.train_id
                GROUP BY t.train_name
                ORDER BY bookings DESC
                LIMIT 5
            """)
            popular_trains = cursor.fetchall()
            
            if popular_trains:
                df = pd.DataFrame(popular_trains)
                fig = px.bar(
                    df,
                    x='train_name',
                    y='bookings',
                    labels={'train_name': 'Train', 'bookings': 'Number of Bookings'},
                    title="Top 5 Most Booked Trains"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No booking data available for train popularity analysis")
        
        except Exception as e:
            st.error(f"Error generating analytics: {e}")
        finally:
            cursor.close()
            conn.close()

# Main Application
def main():
    # Check if this is the first load using session state
    if 'first_load' not in st.session_state:
        show_loading_animation()
        st.session_state.first_load = True
        st.rerun()
    st.markdown("""
    <style>
        .header-container {
            background-size: cover;
            background-position: center;
            padding: 3rem 2rem;
            text-align: center;
            border-radius: 0 0 20px 20px;
            margin-bottom: 2rem;
            position: relative;
        }
        .header-overlay {
            background-color: rgba(0, 0, 0, 0.5);
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 0 0 20px 20px;
        }
        .header-content {
            position: relative;
            z-index: 2;
            color: white;
        }
        .app-title {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        .tagline {
            font-size: 1.5rem;
            font-style: italic;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
        }
    </style>
    """, unsafe_allow_html=True)

    # Convert your image to base64
    station_image = img_to_bytes("landscape2.png")  # Replace with your image path

    # Top bar with background image
    st.markdown(
        f"""
        <div class="header-container" style="background-image: url('data:image/png;base64,{station_image}');">
            <div class="header-overlay"></div>
            <div class="header-content">
                <h1 class="app-title">Railway Reservation System</h1>
                <p class="tagline">Your Journey Begins Here</p>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )


    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        auth_menu = st.sidebar.radio("Authentication", 
            ["User Login", "User Register", "Admin Login", "Admin Register"]
        )
        
        if auth_menu == "User Login":
            user_login()
        elif auth_menu == "User Register":
            user_register()
        elif auth_menu == "Admin Login":
            admin_login()
        elif auth_menu == "Admin Register":
            admin_register()

    if st.session_state.logged_in:
        if st.session_state.user_type == 'user':
            user_icon = img_to_bytes("logo.png")
            st.sidebar.markdown(
                f"""
                <div style="display:flex; align-items:center; margin-bottom:20px;">
                    <img src="data:image/png;base64,{user_icon}" width="40" style="border-radius:50%; margin-right:10px;">
                    <h3>Welcome, {st.session_state.username}</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:  # admin
            admin_icon = img_to_bytes("admin.png")
            st.sidebar.markdown(
                f"""
                <div style="display:flex; align-items:center; margin-bottom:20px;">
                    <img src="data:image/png;base64,{admin_icon}" width="40" style="border-radius:50%; margin-right:10px;">
                    <h3>Welcome, {st.session_state.username}</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        try:
            if 'user_id' not in st.session_state:
                st.error("User session is invalid. Please log in again.")
                st.session_state.logged_in = False
                st.rerun()
            else:
                if st.session_state.user_type == 'user':
                    menu = st.sidebar.radio("Menu", 
                        ["View Trains", "My Bookings", "Logout"]
                    )
                    
                    if menu == "View Trains":
                        view_trains()
                    elif menu == "My Bookings":
                        my_bookings()
                    elif menu == "Logout":
                        logout()
                        
                elif st.session_state.user_type == 'admin':
                    menu = st.sidebar.radio("Admin Menu", 
                        ["Manage Trains", "Manage Bookings", "Reservation Analytics", "Logout"]
                    )
                    
                    if menu == "Manage Trains":
                        manage_trains()
                    elif menu == "Manage Bookings":
                        manage_bookings()
                    elif menu == "Reservation Analytics":
                        reservation_analytics()
                    elif menu == "Logout":
                        logout()
                else:
                    st.error("Invalid user role")
                    logout()
                
                if "selected_train_id" in st.session_state and menu != "View Trains":
                    del st.session_state.selected_train_id

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.session_state.logged_in = False
            st.rerun()

if __name__ == "__main__":
    main()