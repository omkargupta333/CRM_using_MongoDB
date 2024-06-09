import streamlit as st
from pymongo import MongoClient
import gridfs
from PIL import Image
import io
import smtplib
from email.mime.text import MIMEText
import base64
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Fintree Financial Services",
    page_icon="🌳",
)
# MongoDB connection details
mongo_uri = "mongodb://localhost:27017"
database_name = "Fintree_Finance"
collection_name = "customer"
client = MongoClient(mongo_uri)
db = client[database_name]
collection = db[collection_name]
fs = gridfs.GridFS(db)

# Email configuration (replace with your email server details)
SMTP_SERVER = 'smtp.your-email-provider.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'your-email@example.com'
EMAIL_PASSWORD = 'your-email-password'

# Helper functions
def user_exists(username, password):
    user = collection.find_one({"username": username, "password": password})
    return user is not None

def register_user(username, password, contact):
    collection.insert_one({"username": username, "password": password, "contact": contact})

def reset_password(username, new_password):
    collection.update_one({"username": username}, {"$set": {"password": new_password}})

def add_customer_detail(details):
    collection.update_one({"username": details["username"]}, {"$set": details}, upsert=True)

def get_customer_detail(username):
    return collection.find_one({"username": username})

def update_customer_detail(username, updated_details):
    collection.update_one({"username": username}, {"$set": updated_details})

def delete_user(username):
    collection.delete_one({"username": username})

def get_all_users():
    return collection.find({"username": {"$ne": "finadmin"}})

def add_password_reset_request(username, contact):
    collection.update_one({"username": username}, {"$set": {"password_reset_request": True, "reset_contact": contact}})

def get_password_reset_requests():
    return collection.find({"password_reset_request": True})

def delete_password_reset_request(username):
    collection.update_one({"username": username}, {"$unset": {"password_reset_request": "", "reset_contact": ""}})

def send_email(to_email, subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

# Function to display image or PDF
def display_file(file_id):
    if file_id:
        file_data = fs.get(file_id).read()
        file_type = fs.get(file_id).content_type

        if file_type and "image" in file_type:
            image = Image.open(io.BytesIO(file_data))
            st.image(image)
        elif file_type and "pdf" in file_type:
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64.b64encode(file_data).decode()}" width="700" height="900" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.write("Unsupported file type.")
    else:
        st.write("No file uploaded.")

# Main interface
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.is_admin = False
        st.session_state.new_user = False  # Track if the user is newly registered

    st.title("Customer Management System")

    if st.session_state.logged_in:
        st.subheader(f"Welcome, {st.session_state.username}")
        
        if st.session_state.is_admin:
            st.subheader("Admin Panel")
            admin_tabs = st.tabs(["View All Users", "Edit User Details", "Delete User", "Request for Password", "Analysis"])

            with admin_tabs[0]:
                st.subheader("View All Users")
                users = get_all_users()
                user_list = [user["username"] for user in users]
                selected_user = st.selectbox("Select User to view details", user_list, key="view_user", index=0)

                if selected_user:
                    user_details = get_customer_detail(selected_user)
                    if user_details:
                        st.write("Username:", user_details.get("username", "N/A"))
                        st.write("Contact:", user_details.get("contact", "N/A"))
                        st.write("Email:", user_details.get("email", "N/A"))
                        st.write("Product:", user_details.get("product", "N/A"))
                        st.write("Type:", user_details.get("type", "N/A"))
                        st.write("Location:", user_details.get("location", "N/A"))
                        st.write("Name:", user_details.get("name", "N/A"))
                        st.write("Type of Entity:", user_details.get("type_of_entity", "N/A"))
                        st.write("Contact Person:", user_details.get("contact_person", "N/A"))
                        st.write("Mobile 1:", user_details.get("mobile_1", "N/A"))
                        st.write("Mobile 2:", user_details.get("mobile_2", "N/A"))
                        for key in ["Signed Agreement", "PAN", "Cancelled Cheque", "GST", "Shop Establishment Certificate", "Partnership Deed", "Certificate of Incorporation"]:
                            if key in user_details:
                                display_file(user_details[key])

                st.markdown('<div class="logout-button">', unsafe_allow_html=True)
                if st.button("Logout", key="logout_view"):
                    st.session_state.logged_in = False
                    st.session_state.username = ""
                    st.session_state.is_admin = False
                    st.session_state.new_user = False
                    st.experimental_rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with admin_tabs[1]:
                st.subheader("Edit User Details")
                users = get_all_users()
                user_list = [user["username"] for user in users]
                selected_user = st.selectbox("Select User to edit details", user_list, key="edit_user", index=0)

                if selected_user:
                    user_details = get_customer_detail(selected_user)
                    if user_details:
                        username = user_details.get("username", "")
                        contact = st.text_input("Contact", user_details.get("contact", ""))
                        email = st.text_input("Email", user_details.get("email", ""))
                        product = st.selectbox("Product", ["Secured", "Unsecured"], index=["Secured", "Unsecured"].index(user_details.get("product", "Secured")), key="edit_product")
                        type_ = st.selectbox("Type", ["Referral", "Connector"], index=["Referral", "Connector"].index(user_details.get("type", "Referral")), key="edit_type")
                        location = st.selectbox("Location", ["Mumbai", "Kalyan", "Panvel"], index=["Mumbai", "Kalyan", "Panvel"].index(user_details.get("location", "Mumbai")), key="edit_location")
                        name = st.text_input("Name", value=user_details.get("name", ""), key="edit_name")
                        type_of_entity = st.selectbox("Type of Entity", ["Individual", "Proprietor", "Partnership", "LLP", "Pvt Ltd"], index=["Individual", "Proprietor", "Partnership", "LLP", "Pvt Ltd"].index(user_details.get("type_of_entity", "Individual")), key="edit_type_of_entity")
                        contact_person = st.text_input("Contact Person", value=user_details.get("contact_person", ""), key="edit_contact_person")
                        mobile_1 = st.text_input("Mobile 1", value=user_details.get("mobile_1", ""), key="edit_mobile_1")
                        mobile_2 = st.text_input("Mobile 2", value=user_details.get("mobile_2", ""), key="edit_mobile_2")

                        uploads = {
                            "Signed Agreement": st.file_uploader("Signed Agreement (Compulsory)", type=["jpg", "jpeg", "png", "pdf"], key="edit_signed_agreement"),
                            "PAN": st.file_uploader("PAN (Compulsory)", type=["jpg", "jpeg", "png", "pdf"], key="edit_pan"),
                            "Cancelled Cheque": st.file_uploader("Cancelled Cheque (Compulsory)", type=["jpg", "jpeg", "png", "pdf"], key="edit_cancelled_cheque"),
                            "GST": st.file_uploader("GST (Optional)", type=["jpg", "jpeg", "png", "pdf"], key="edit_gst"),
                            "Shop Establishment Certificate": st.file_uploader("Shop Establishment Certificate (Optional)", type=["jpg", "jpeg", "png", "pdf"], key="edit_shop_establishment"),
                            "Partnership Deed": st.file_uploader("Partnership Deed (Optional)", type=["jpg", "jpeg", "png", "pdf"], key="edit_partnership_deed"),
                            "Certificate of Incorporation": st.file_uploader("Certificate of Incorporation (Optional)", type=["jpg", "jpeg", "png", "pdf"], key="edit_certificate_of_incorporation"),
                        }

                        if st.button("Update User"):
                            updated_details = {
                                "contact": contact,
                                "email": email,
                                "product": product,
                                "type": type_,
                                "location": location,
                                "name": name,
                                "type_of_entity": type_of_entity,
                                "contact_person": contact_person,
                                "mobile_1": mobile_1,
                                "mobile_2": mobile_2
                            }
                            for key, file in uploads.items():
                                if file:
                                    file_id = fs.put(file.getvalue(), filename=file.name, content_type=file.type)
                                    updated_details[key] = file_id
                            update_customer_detail(username, updated_details)
                            st.success("User details updated successfully!")

                st.markdown('<div class="logout-button">', unsafe_allow_html=True)
                if st.button("Logout", key="logout_edit"):
                    st.session_state.logged_in = False
                    st.session_state.username = ""
                    st.session_state.is_admin = False
                    st.session_state.new_user = False
                    st.experimental_rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with admin_tabs[2]:
                st.subheader("Delete User")
                users = get_all_users()
                user_list = [user["username"] for user in users]
                selected_user = st.selectbox("Select User to delete", user_list, key="delete_user", index=0)

                if selected_user:
                    if st.button("Delete User"):
                        delete_user(selected_user)
                        st.success("User deleted successfully!")

                st.markdown('<div class="logout-button">', unsafe_allow_html=True)
                if st.button("Logout", key="logout_delete"):
                    st.session_state.logged_in = False
                    st.session_state.username = ""
                    st.session_state.is_admin = False
                    st.session_state.new_user = False
                    st.experimental_rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with admin_tabs[3]:
                st.subheader("Request for Password")
                requests = get_password_reset_requests()
                requests_list = list(requests)
                if requests_list:
                    df_requests = pd.DataFrame(requests_list)
                    df_requests = df_requests[['username', 'contact']]  # Select relevant columns
                    st.write(df_requests)
                    for index, row in df_requests.iterrows():
                        if st.button(f"Delete {row['username']}", key=f"delete_{row['username']}"):
                            delete_password_reset_request(row['username'])
                            st.experimental_rerun()
                else:
                    st.write("No password reset requests found.")

                st.markdown('<div class="logout-button">', unsafe_allow_html=True)
                if st.button("Logout", key="logout_requests"):
                    st.session_state.logged_in = False
                    st.session_state.username = ""
                    st.session_state.is_admin = False
                    st.session_state.new_user = False
                    st.experimental_rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with admin_tabs[4]:
                st.subheader("Analysis")
                users = get_all_users()
                users_list = list(users)
                if users_list:
                    df = pd.DataFrame(users_list)
                    st.write(f"Total number of users: {len(df)}")

                    columns = df.columns.tolist()
                    selected_columns = st.multiselect("Select columns for analysis", columns, placeholder="Select columns")
                    chart_type = st.selectbox("Select chart type", ["Bar", "Line", "Scatter", "Histogram", "Pie"], placeholder="Select chart type")

                    if selected_columns:
                        if chart_type == "Bar":
                            fig = px.bar(df, x=selected_columns[0], y=selected_columns[1])
                        elif chart_type == "Line":
                            fig = px.line(df, x=selected_columns[0], y=selected_columns[1])
                        elif chart_type == "Scatter":
                            fig = px.scatter(df, x=selected_columns[0], y=selected_columns[1])
                        elif chart_type == "Histogram":
                            fig = px.histogram(df, x=selected_columns[0])
                        elif chart_type == "Pie":
                            fig = px.pie(df, names=selected_columns[0], values=selected_columns[1])

                        st.plotly_chart(fig)
                    else:
                        st.write("Please select columns for analysis")

                st.markdown('<div class="logout-button">', unsafe_allow_html=True)
                if st.button("Logout", key="logout_analysis"):
                    st.session_state.logged_in = False
                    st.session_state.username = ""
                    st.session_state.is_admin = False
                    st.session_state.new_user = False
                    st.experimental_rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.subheader("Customer Management")
            details = get_customer_detail(st.session_state.username)
            
            if st.session_state.new_user or not details:
                tabs = st.tabs(["Add Details", "View Details", "Update Details"])
            else:
                tabs = st.tabs(["View Details", "Update Details"])

            if len(tabs) == 3:  # Check if the "Add Details" tab is present
                with tabs[0]:
                    st.subheader("Add Details")
                    product = st.selectbox("Product", ["Secured", "Unsecured"], key="add_product")
                    type_ = st.selectbox("Type", ["Referral", "Connector"], key="add_type")
                    location = st.selectbox("Location", ["Mumbai", "Kalyan", "Panvel"], key="add_location")
                    name = st.text_input("Name", key="add_name")
                    type_of_entity = st.selectbox("Type of Entity", ["Individual", "Proprietor", "Partnership", "LLP", "Pvt Ltd"], key="add_type_of_entity")
                    contact_person = st.text_input("Contact Person", key="add_contact_person")
                    mobile_1 = st.text_input("Mobile 1", key="add_mobile_1")
                    mobile_2 = st.text_input("Mobile 2", key="add_mobile_2")
                    
                    uploads = {
                        "Signed Agreement": st.file_uploader("Signed Agreement (Compulsory)", type=["jpg", "jpeg", "png", "pdf"], key="add_signed_agreement"),
                        "PAN": st.file_uploader("PAN (Compulsory)", type=["jpg", "jpeg", "png", "pdf"], key="add_pan"),
                        "Cancelled Cheque": st.file_uploader("Cancelled Cheque (Compulsory)", type=["jpg", "jpeg", "png", "pdf"], key="add_cancelled_cheque"),
                        "GST": st.file_uploader("GST (Optional)", type=["jpg", "jpeg", "png", "pdf"], key="add_gst"),
                        "Shop Establishment Certificate": st.file_uploader("Shop Establishment Certificate (Optional)", type=["jpg", "jpeg", "png", "pdf"], key="add_shop_establishment"),
                        "Partnership Deed": st.file_uploader("Partnership Deed (Optional)", type=["jpg", "jpeg", "png", "pdf"], key="add_partnership_deed"),
                        "Certificate of Incorporation": st.file_uploader("Certificate of Incorporation (Optional)", type=["jpg", "jpeg", "png", "pdf"], key="add_certificate_of_incorporation"),
                    }

                    if st.button("Submit", key="add_submit"):
                        if not (mobile_1.isdigit() and len(mobile_1) == 10 and mobile_2.isdigit() and len(mobile_2) == 10):
                            st.error("Both mobile numbers must be 10-digit numerical values.")
                        elif not (uploads["Signed Agreement"] and uploads["PAN"] and uploads["Cancelled Cheque"]):
                            st.error("Signed Agreement, PAN, and Cancelled Cheque are compulsory.")
                        else:
                            details = {
                                "username": st.session_state.username,
                                "product": product,
                                "type": type_,
                                "location": location,
                                "name": name,
                                "type_of_entity": type_of_entity,
                                "contact_person": contact_person,
                                "mobile_1": mobile_1,
                                "mobile_2": mobile_2,
                            }
                            for key, file in uploads.items():
                                if file:
                                    file_id = fs.put(file.getvalue(), filename=file.name, content_type=file.type)
                                    details[key] = file_id
                            add_customer_detail(details)
                            st.success("Details submitted successfully!")
                            st.experimental_rerun()

            with tabs[1 if len(tabs) == 3 else 0]:
                st.subheader("View Details")
                details = get_customer_detail(st.session_state.username)
                if details:
                    st.write("Product:", details.get("product", "N/A"))
                    st.write("Type:", details.get("type", "N/A"))
                    st.write("Location:", details.get("location", "N/A"))
                    st.write("Name:", details.get("name", "N/A"))
                    st.write("Type of Entity:", details.get("type_of_entity", "N/A"))
                    st.write("Contact Person:", details.get("contact_person", "N/A"))
                    st.write("Mobile 1:", details.get("mobile_1", "N/A"))
                    st.write("Mobile 2:", details.get("mobile_2", "N/A"))
                    for key in ["Signed Agreement", "PAN", "Cancelled Cheque", "GST", "Shop Establishment Certificate", "Partnership Deed", "Certificate of Incorporation"]:
                        if key in details:
                            display_file(details[key])
                else:
                    st.write("No details found.")

            with tabs[2 if len(tabs) == 3 else 1]:
                st.subheader("Update Details")
                details = get_customer_detail(st.session_state.username)
                if details:
                    product = st.selectbox("Product", ["Secured", "Unsecured"], index=["Secured", "Unsecured"].index(details.get("product", "Secured")), key="update_product")
                    type_ = st.selectbox("Type", ["Referral", "Connector"], index=["Referral", "Connector"].index(details.get("type", "Referral")), key="update_type")
                    location = st.selectbox("Location", ["Mumbai", "Kalyan", "Panvel"], index=["Mumbai", "Kalyan", "Panvel"].index(details.get("location", "Mumbai")), key="update_location")
                    name = st.text_input("Name", value=details.get("name", ""), key="update_name")
                    type_of_entity = st.selectbox("Type of Entity", ["Individual", "Proprietor", "Partnership", "LLP", "Pvt Ltd"], index=["Individual", "Proprietor", "Partnership", "LLP", "Pvt Ltd"].index(details.get("type_of_entity", "Individual")), key="update_type_of_entity")
                    contact_person = st.text_input("Contact Person", value=details.get("contact_person", ""), key="update_contact_person")
                    mobile_1 = st.text_input("Mobile 1", value=details.get("mobile_1", ""), key="update_mobile_1")
                    mobile_2 = st.text_input("Mobile 2", value=details.get("mobile_2", ""), key="update_mobile_2")

                    uploads = {
                        "Signed Agreement": st.file_uploader("Signed Agreement (Compulsory)", type=["jpg", "jpeg", "png", "pdf"], key="update_signed_agreement"),
                        "PAN": st.file_uploader("PAN (Compulsory)", type=["jpg", "jpeg", "png", "pdf"], key="update_pan"),
                        "Cancelled Cheque": st.file_uploader("Cancelled Cheque (Compulsory)", type=["jpg", "jpeg", "png", "pdf"], key="update_cancelled_cheque"),
                        "GST": st.file_uploader("GST (Optional)", type=["jpg", "jpeg", "png", "pdf"], key="update_gst"),
                        "Shop Establishment Certificate": st.file_uploader("Shop Establishment Certificate (Optional)", type=["jpg", "jpeg", "png", "pdf"], key="update_shop_establishment"),
                        "Partnership Deed": st.file_uploader("Partnership Deed (Optional)", type=["jpg", "jpeg", "png", "pdf"], key="update_partnership_deed"),
                        "Certificate of Incorporation": st.file_uploader("Certificate of Incorporation (Optional)", type=["jpg", "jpeg", "png", "pdf"], key="update_certificate_of_incorporation"),
                    }

                    if st.button("Update", key="update_submit"):
                        if not (mobile_1.isdigit() and len(mobile_1) == 10 and mobile_2.isdigit() and len(mobile_2) == 10):
                            st.error("Both mobile numbers must be 10-digit numerical values.")
                        else:
                            updated_details = {
                                "product": product,
                                "type": type_,
                                "location": location,
                                "name": name,
                                "type_of_entity": type_of_entity,
                                "contact_person": contact_person,
                                "mobile_1": mobile_1,
                                "mobile_2": mobile_2,
                            }
                            for key, file in uploads.items():
                                if file:
                                    file_id = fs.put(file.getvalue(), filename=file.name, content_type=file.type)
                                    updated_details[key] = file_id
                            update_customer_detail(st.session_state.username, updated_details)
                            st.success("Your details have been updated successfully!")
                            st.experimental_rerun()
                            

            st.markdown('<div class="logout-button">', unsafe_allow_html=True)
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.is_admin = False
                st.session_state.new_user = False
                st.experimental_rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.subheader("Login or Register")
        login_tab, register_tab, reset_tab, admin_login_tab = st.tabs(["Login", "Register", "Forgot Password", "Admin Login"])

        with login_tab:
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", key="login_submit"):
                if username.strip() and password.strip():
                    if user_exists(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.experimental_rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please provide both username and password")

        with register_tab:
            new_username = st.text_input("New Username", key="register_username")
            new_password = st.text_input("New Password", type="password", key="register_password")
            contact = st.text_input("Contact (10-digit number)", key="register_contact")
            if st.button("Register", key="register_submit"):
                if new_username.strip() and new_password.strip() and contact.strip():
                    if not contact.isdigit() or len(contact) != 10:
                        st.error("Contact number must be a 10-digit numerical value")
                    else:
                        existing_user = collection.find_one({"username": new_username})
                        if existing_user:
                            st.error("Username already exists")
                        else:
                            register_user(new_username, new_password, contact)
                            st.success("You have registered successfully!")
                            st.session_state.logged_in = True
                            st.session_state.username = new_username
                            st.session_state.new_user = True  # Mark as a new user
                            st.experimental_rerun()
                else:
                    st.error("Please provide username, password, and contact")

        with reset_tab:
            reset_username = st.text_input("Username to Reset Password", key="reset_username")
            reset_contact = st.text_input("Contact to verify", key="reset_contact")
            if st.button("Reset Password Request", key="reset_submit"):
                if reset_username.strip() and reset_contact.strip() and reset_contact.isdigit() and len(reset_contact) == 10:
                    user = collection.find_one({"username": reset_username, "contact": reset_contact})
                    if user:
                        add_password_reset_request(reset_username, reset_contact)
                        st.success("Password reset request sent to the admin!")
                    else:
                        st.error("Invalid username or contact number")
                else:
                    st.error("Please provide valid username and 10-digit contact number")

        with admin_login_tab:
            admin_username = st.text_input("Admin Username", key="admin_login_username")
            admin_password = st.text_input("Admin Password", type="password", key="admin_login_password")
            if st.button("Admin Login", key="admin_login_submit"):
                if admin_username.strip() and admin_password.strip():
                    if admin_username == "f" and admin_password == "f":
                        st.session_state.logged_in = True
                        st.session_state.username = admin_username
                        st.session_state.is_admin = True
                        st.experimental_rerun()
                    else:
                        st.error("Invalid admin username or password")
                else:
                    st.error("Please provide both admin username and password")

if __name__ == '__main__':
    main()
