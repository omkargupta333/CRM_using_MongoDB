# CRM_using_MongoDB
Customer Management System with Streamlit and MongoDB
This project is a Customer Management System built using Streamlit, MongoDB, and various Python libraries. The system allows users to register, log in, and manage their details, while the admin can view users, edit details, delete users, handle password reset requests, and perform data analysis.

Key Features:
🌟 User Registration and Login
🔐 Password Management
📊 Data Analysis with Interactive Charts
📧 Email Notifications
Code Breakdown:
Imports and Configuration:

Imported necessary libraries including Streamlit, MongoDB client, GridFS for file handling, PIL for image processing, smtplib for email, and Plotly for data visualization.
Set up the Streamlit page configuration with a title and icon.
MongoDB Connection:

Connect to MongoDB using the connection URI and define the database and collection.
Set up GridFS for handling file uploads.
Email Configuration:

Define SMTP server details for sending emails.
Helper Functions:

Various helper functions for user management, file handling, and email sending:
Check if a user exists with the given username and password.
Register a new user.
Reset user password.
Add customer details.
Retrieve customer details.
Update customer details.
Delete a user.
Handle password reset requests.
Send email notifications.
Display images or PDF files.
Main Interface:

Initialize session state variables to manage login state and user information.
Display the main title and welcome message based on login status.
Admin Panel:

If the logged-in user is an admin, display the admin panel with tabs for various functionalities:
View All Users: Select and view details of any registered user.
Edit User Details: Edit the details of selected users and update the information in the database.
Delete User: Delete selected users from the database.
Request for Password: Display password reset requests in a table format and provide options to delete requests once handled.
Analysis: Show the total number of users and provide options to generate various charts (Bar, Line, Scatter, Histogram, Pie) using Plotly for data analysis.
Customer Management:

If the logged-in user is not an admin, display tabs for managing their own details:
Add Details: Add customer details with mandatory file uploads.
View Details: View the details of the logged-in user.
Update Details: Update the user's details and handle file re-uploads if necessary.
Login and Registration:

Provide tabs for users to log in, register, and request password resets:
Login: Check credentials and log in the user.
Register: Allow new users to register with a username, password, and contact number.
Forgot Password: Allow users to request a password reset by verifying their username and contact number.
Logout Functionality:

Provide a logout button in each tab to allow users to log out and reset the session state.
