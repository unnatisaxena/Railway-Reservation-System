# 🚂 Railway Reservation System

A web application for booking train tickets with user and admin portals, real-time seat availability, and interactive animations.

## 🎯 Core Features
1. Dual-Role Access
 - 👥 User Portal: Book tickets, view schedules, manage bookings
 - 👨‍💼 Admin Portal: Manage trains, view all bookings, access analytics
2. Booking Management
 - 🚉 Real-time seat availability
 - ⏳ Waiting list system (auto-promotes to confirmed on cancellations)
 - ❌ Cancellation with seat reallocation
3. Visual & Interactive Elements
 - 🚄 Animated loading screen (train crosses station on first visit)
 - 📊 Analytics dashboard with Plotly charts
 - 🛡️ Security & Reliability
4. Secure Auth
 - 🔐 Bcrypt password hashing
 - 🔑 Session-based access control
5. Data Integrity
 - 🗄️ MySQL transactions for bookings/cancellations
 - 📉 Overbooking prevention
 - 🛠️ Technical Highlights
## Feature	Technology Used
 - Responsive UI	Streamlit components
 - Animations	CSS/HTML + Base64 images
 - Database	MySQL with connector-python
 - Visualization	Plotly + Pandas
 ### ✨ Unique Touches
  - First-Load Animation
  - 🎬 Plays only once per session (uses st.session_state)
  - 🖼️ Transparent PNG handling for seamless train overlay
### Admin Analytics
  - 📈 Popular routes ranking
  - 📅 Booking trends over time
 ### User Experience
  - 📱 Mobile-friendly interface
  - 🔄 Real-time seat updates
  - 🔍 Validation Test Cases
  - Cancel a booking → Waiting list promotion
  - Admin deletes train with bookings → Blocked
### User Portal
- 🚉 Browse available trains with schedules
- 🎫 Book/Cancel tickets with seat selection
- 📊 View booking history
- 🔒 Secure authentication (bcrypt password hashing)
### Admin Portal
- 🛤️ Add/Edit/Delete trains
- 👥 Manage user bookings
- 📈 Analytics dashboard (booking trends, popular routes)
### Special Effects
- 🚄 Animated train loading screen (first visit only)
- 🎨 Responsive UI with Streamlit components
## 🛠️ Tech Stack
| Component       | Technology |
|-----------------|------------|
| Frontend        | Streamlit  |
| Backend         | Python     |
| Database        | MySQL      |
| Authentication  | Bcrypt     |
| Animations      | HTML/CSS   |
