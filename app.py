from flask import Flask, render_template, request, redirect, url_for,flash

import MySQLdb
from MySQLdb import cursors
import config
import os
from werkzeug.utils import secure_filename




# Set up the database connection
conn = MySQLdb.connect(
    host="localhost",
    user="root",
    passwd="Allizwell@5",
    db="GymManagement",
    cursorclass=cursors.DictCursor
)

app = Flask(__name__,static_folder='static')
app.secret_key = 'your_secret_key_here'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Database connection function
def get_db_connection():
    return MySQLdb.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        passwd=config.MYSQL_PASSWORD,
        db=config.MYSQL_DB,
        cursorclass=MySQLdb.cursors.DictCursor
    )

@app.route('/')
def index():
    return render_template('home.html')
@app.route('/users')
def list_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetching all users from the Users table, including the role
    cursor.execute("""
        SELECT user_id, name, email, role 
        FROM Users
    """)  # Fetching specific columns (user_id, name, email, role)
    
    users = cursor.fetchall()  # Store all the users in a list

    conn.close()

    return render_template('users.html', users=users)  # Pass the users data to the template
@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name_full = request.form['name_full']
        email = request.form['email']
        role = request.form['role']
        

        # Handle the 'member' role case
        if role == 'member':
            address = request.form['address']
            dob = request.form['dob']

            # Insert into Users table
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Users (name, email, role) VALUES (%s, %s, %s)",
                (name_full, email, role)
            )
            conn.commit()

            # Get the newly inserted user's ID
            cursor.execute("SELECT user_id FROM Users WHERE email = %s", (email,))
            user_id = cursor.fetchone()['user_id']

            # Insert into Members table
            cursor.execute("""
                INSERT INTO Members (user_id, name_full, address, date_of_birth)
                VALUES (%s, %s, %s, %s)
            """, (user_id, name_full, address, dob))  # Including address and dob
            conn.commit()
            conn.close()

            flash("User added successfully!", 'success')
            return redirect(url_for('list_users'))  # Redirect to the users list
        
        # Handle the 'trainer' role case
        elif role == 'trainer':
           
            specialization = request.form['specialization']
            experience = request.form['experience']
            bio = request.form.get('bio')  # Use .get() to handle missing data gracefully

            image = request.files.get('image')  # Get the uploaded image (if any)
            image_filename = None
        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image.save(image_path)  # Save the image to the server

            # Insert into Users table for the trainer
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Users (name, email, role) VALUES (%s, %s, %s)",
                (name_full, email, role)
            )
            conn.commit()

            # Get the newly inserted user's ID
            cursor.execute("SELECT user_id FROM Users WHERE email = %s", (email,))
            user_id = cursor.fetchone()['user_id']

            # Insert into Trainers table and update the image_url for trainers
            cursor.execute("""
                INSERT INTO Trainers (user_id, trainer_name, specialization, experience,bio, image_url)
                VALUES (%s, %s, %s, %s,%s, %s)
            """, (user_id, name_full, specialization, experience, bio, image_filename))  # Store image_url in Trainers table
            conn.commit()
            conn.close()

            flash("Trainer added successfully!", 'success')
            return redirect(url_for('list_users'))  # Redirect to the users list

        else:
            # Handle other roles such as 'trainer' (this part remains unchanged)
            pass

    return render_template('add_user.html')

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the user's data based on user_id
    cursor.execute("""SELECT * FROM Users WHERE user_id = %s""", (user_id,))
    user = cursor.fetchone()

    # If the role is 'member', proceed with updating the Members table as well
    if user['role'] == 'member':
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            address = request.form['address']
            dob = request.form['dob']

            # Update the user's information in the Users table
            cursor.execute("""UPDATE Users SET name = %s, email = %s WHERE user_id = %s""", (name, email, user_id))

            # Update the member's information in the Members table
            cursor.execute("""
                UPDATE Members 
                SET name = %s, email = %s, address = %s, date_of_birth = %s 
                WHERE user_id = %s
            """, (name, email, address, dob, user_id))

            conn.commit()
            conn.close()

            flash("Member updated successfully!", 'success')
            return redirect(url_for('list_members'))  # Redirect to the members list page

    else:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            role = request.form['role']

            # Update non-member user info in Users table
            cursor.execute("""UPDATE Users SET name = %s, email = %s, role = %s WHERE user_id = %s""", (name, email, role, user_id))

            conn.commit()
            conn.close()

            flash("User updated successfully!", 'success')
            return redirect(url_for('list_users'))  # Redirect to the users list page

    conn.close()
    return render_template('edit_user.html', user=user)  # Render the edit user form

# --- Delete User (and reflect in Members) ---
@app.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the user from the Users table
    cursor.execute("""SELECT * FROM Users WHERE user_id = %s""", (user_id,))
    user = cursor.fetchone()

    if not user:
        flash("User not found.", 'danger')
        return redirect(url_for('list_users'))  # Redirect to the users list if the user is not found

    # Delete the associated member record in the Members table if the user is a member
    cursor.execute("""SELECT member_id FROM Members WHERE user_id = %s""", (user_id,))
    member = cursor.fetchone()
    if member:
        cursor.execute("""DELETE FROM Members WHERE user_id = %s""", (user_id,))
        conn.commit()

    # Delete the user record from the Users table
    cursor.execute("""DELETE FROM Users WHERE user_id = %s""", (user_id,))
    conn.commit()
    
    conn.close()

    flash("User and associated member record deleted successfully!", 'success')
    return redirect(url_for('list_users'))  # Redirect back to the list of users

@app.route('/members')
def list_members():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            m.member_id, 
            u.name AS user_name, 
            u.email, 
            u.role, 
            m.date_of_birth, 
            m.address, 
            ms.type AS membership_type  
        FROM 
            Members m
        JOIN 
            Users u ON m.user_id = u.user_id
        LEFT JOIN 
            Memberships ms ON m.membership_id = ms.membership_id
        WHERE 
            u.role = 'member'
    """)
    members = cursor.fetchall()  # Fetch all members with their membership types
    conn.close()

    return render_template('members.html', members=members)


@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        # Fetch form data
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        dob = request.form['dob']

        try:
            # Insert into the Members table
            conn = get_db_connection()  # Make sure to call your database connection
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Members (name, email, address, date_of_birth)
                VALUES (%s, %s, %s, %s)
            """, (name, email, address, dob))

            # Insert into the Users table (if needed)
            cursor.execute("""
                INSERT INTO Users (name, email)
                VALUES (%s, %s)
            """, (name, email))

            conn.commit()  # Commit the changes to the database

            flash("New member added successfully!", 'success')
            return redirect(url_for('list_members'))  # Redirect to the list of members after success

        except Exception as e:
            flash(f"Error adding member: {str(e)}", 'danger')
            print(f"Error: {str(e)}")  # Log the error for debugging

    return render_template('add_member.html')  # Render the form if GET request




@app.route('/members/edit/<int:member_id>', methods=['GET', 'POST'])
def edit_member(member_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the member details along with name, email from Users table
    cursor.execute("""
        SELECT Members.*, Users.name, Users.email
        FROM Members
        JOIN Users ON Members.user_id = Users.user_id
        WHERE Members.member_id = %s
    """, (member_id,))
    
    member = cursor.fetchone()

    if not member:
        flash("Member not found.", 'danger')
        return redirect(url_for('list_members'))  # Redirect to members list if not found

    if request.method == 'POST':
        # Logic for updating a member's information
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        dob = request.form['dob']

        try:
            # Update the member's information in the Members table
            cursor.execute("""
                UPDATE Members
                SET address=%s, date_of_birth=%s
                WHERE member_id=%s
            """, (address, dob, member_id))

            # Update the user's name and email in the Users table
            cursor.execute("""
                UPDATE Users
                SET name=%s, email=%s
                WHERE user_id=%s
            """, (name, email, member['user_id']))

            conn.commit()
            flash("Member details updated successfully!", 'success')
        except Exception as e:
            flash(f"Error updating member details: {str(e)}", 'danger')
            print(f"Error: {str(e)}")  # Log the error for debugging

        return redirect(url_for('list_members'))  # Redirect after successful update

    conn.close()
    return render_template('edit_member.html', member=member)

@app.route('/memberships', methods=['GET', 'POST'])
def list_memberships():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Handle search query for member names
    search_query = request.args.get('search', '')

    # Handle membership filter
    membership_filter = request.args.get('membership_filter', '')

    # Fetch all memberships for filtering
    cursor.execute("SELECT * FROM Memberships")
    memberships = cursor.fetchall()

    # Base query to get only members (not  trainers)
    base_query = """
        SELECT m.* FROM Members m
        JOIN Users u ON m.user_id = u.user_id
        WHERE u.role = 'Member'
    """

    params = ()

    # Add search filter if provided
    if search_query:
        base_query += " AND m.name_full LIKE %s"
        params = ('%' + search_query + '%',)

    # Add membership filter if provided
    if membership_filter:
        base_query += " AND m.membership_id = %s"
        params = params + (membership_filter,)

    cursor.execute(base_query, params)
    members = cursor.fetchall()

    if request.method == 'POST':
        member_id = request.form['member_id']
        membership_id = request.form['membership_type']  # We expect membership_id here

        try:
            # Step 1: Verify the member exists and is valid
            cursor.execute("""
                SELECT m.member_id 
                FROM Members m
                JOIN Users u ON m.user_id = u.user_id
                WHERE m.member_id = %s AND u.role = 'Member'
            """, (member_id,))

            if not cursor.fetchone():
                flash("Only members can have memberships assigned!", 'danger')
            else:
                # Step 2: Update the member's membership_id in the Members table
                cursor.execute("""
                    UPDATE Members
                    SET membership_id = %s
                    WHERE member_id = %s
                """, (membership_id, member_id))
                conn.commit()
                flash("Membership updated successfully!", 'success')

        except Exception as e:
            conn.rollback()
            flash(f"Error updating membership: {str(e)}", 'danger')
        finally:
            conn.close()
            return redirect(url_for('list_memberships', 
                                   search=search_query,
                                   membership_filter=membership_filter))

    conn.close()
    return render_template('memberships.html', 
                          memberships=memberships, 
                          members=members, 
                          search_query=search_query, 
                          membership_filter=membership_filter)


@app.route('/attendance/mark', methods=['GET', 'POST'])
def mark_attendance():
    search_query = request.args.get('search', '')  # Get search query from URL (default: empty string)

    # Initialize database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Modify the query to filter members by name if a search query exists
    query = "SELECT member_id, name_full FROM Members WHERE name_full LIKE %s"
    cursor.execute(query, ('%' + search_query + '%',))  # '%search%' allows partial matching

    members = cursor.fetchall()  # Fetch matching members

    if request.method == 'POST':
        member_id = request.form['member_id']
        check_in = request.form['check_in']  # Capture check-in time

        try:
            # Insert attendance record with check-in time
            cursor.execute("""
                INSERT INTO Attendance (member_id, check_in)
                VALUES (%s, %s)
            """, (member_id, check_in))
            conn.commit()
            flash("Attendance (check-in) marked successfully!", 'success')
        except Exception as e:
            flash(f"Error marking attendance: {str(e)}", 'danger')
        finally:
            conn.close()

        return redirect(url_for('list_attendance'))  # Redirect to the attendance list

    conn.close()

    # Pass the list of members and search query to the template
    return render_template('mark_attendance.html', members=members, search_query=search_query)


@app.route('/attendance/checkout/<int:attendance_id>', methods=['POST'])
def check_out(attendance_id):
    # Capture the current time to set as the checkout time
    from datetime import datetime
    check_out_time = datetime.now()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if the attendance record exists and if checkout hasn't been done yet
        cursor.execute("""
            SELECT * FROM Attendance WHERE attendance_id = %s AND check_out IS NULL
        """, (attendance_id,))
        attendance = cursor.fetchone()

        if not attendance:
            flash("This member has already checked out or the record doesn't exist.", 'danger')
        else:
            # Update the checkout timestamp
            cursor.execute("""
                UPDATE Attendance 
                SET check_out = %s 
                WHERE attendance_id = %s
            """, (check_out_time, attendance_id))
            conn.commit()

            flash(f"Checkout successful at {check_out_time.strftime('%Y-%m-%d %H:%M:%S')}", 'success')

    except Exception as e:
        flash(f"Error checking out: {str(e)}", 'danger')
    finally:
        conn.close()

    return redirect(url_for('list_attendance'))  # Redirect to the attendance list


@app.route('/attendance', methods=['GET'])
def list_attendance():
    search_query = request.args.get('search', '')  # Get search query from URL (default: empty string)
    date_filter = request.args.get('date', '')  # Optional date filter

    conn = get_db_connection()
    cursor = conn.cursor()

    # Base query to fetch attendance records
    query = """
        SELECT a.attendance_id, m.name_full as member_name, a.check_in, a.check_out
        FROM Attendance a
        JOIN Members m ON a.member_id = m.member_id
        WHERE m.name_full LIKE %s
    """
    
    # Add date filter if provided
    if date_filter:
        query += " AND a.check_in LIKE %s"
        cursor.execute(query, ('%' + search_query + '%', '%' + date_filter + '%'))
    else:
        cursor.execute(query, ('%' + search_query + '%',))

    # Fetch the filtered records
    attendance_records = cursor.fetchall()
    conn.close()

    return render_template('attendance.html', attendance_records=attendance_records, search_query=search_query, date_filter=date_filter)
@app.route('/attendance/details/<int:attendance_id>', methods=['GET'])
def view_attendance_details(attendance_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to fetch details of the attendance record by attendance_id
    cursor.execute("""
        SELECT a.attendance_id, m.name_full, a.check_in, a.check_out
        FROM Attendance a
        JOIN Members m ON a.member_id = m.member_id
        WHERE a.attendance_id = %s
    """, (attendance_id,))
    
    record = cursor.fetchone()
    conn.close()

    if record:
        return render_template('attendance_details.html', record=record)
    else:
        flash("Attendance record not found.", 'danger')
       
        return redirect(url_for('list_attendance'))  # Redirect to the attendance list if not found
@app.route('/payments/add', methods=['GET', 'POST'])
def add_payment():
    # Fetch members for the payment form
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT member_id, name_full FROM Members")  # Fetch members for dropdown
    members = cursor.fetchall()

    if request.method == 'POST':
        member_id = request.form['member_id']
        amount = request.form['amount']
        method = request.form['method']

        try:
            # Insert payment record
            cursor.execute("""
                INSERT INTO Payments (member_id, amount, method)
                VALUES (%s, %s, %s)
            """, (member_id, amount, method))
            conn.commit()
            flash("Payment recorded successfully!", 'success')
        except Exception as e:
            flash(f"Error recording payment: {str(e)}", 'danger')
        finally:
            conn.close()

        return redirect(url_for('list_payments'))  # Redirect to the payments list

    conn.close()
    return render_template('add_payment.html', members=members)
@app.route('/payments', methods=['GET'])
def list_payments():
    search_query = request.args.get('search', '')  # Get search query from URL (default: empty string)
    date_filter = request.args.get('date', '')  # Optional date filter

    conn = get_db_connection()
    cursor = conn.cursor()

    # Base query to fetch payments records
    query = """
        SELECT p.payment_id, m.name_full as member_name, p.amount, p.payment_date, p.method
        FROM Payments p
        JOIN Members m ON p.member_id = m.member_id
        WHERE m.name_full LIKE %s
    """
    
    # Add date filter if provided
    if date_filter:
        query += " AND p.payment_date LIKE %s"
        cursor.execute(query, ('%' + search_query + '%', '%' + date_filter + '%'))
    else:
        cursor.execute(query, ('%' + search_query + '%',))

    # Fetch the filtered records
    payments_records = cursor.fetchall()
    conn.close()

    return render_template('view_payments.html', payments_records=payments_records, search_query=search_query, date_filter=date_filter)
@app.route('/payments/delete/<int:payment_id>', methods=['GET', 'POST'])
def delete_payment(payment_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Delete the payment record with the specified payment_id
        cursor.execute("DELETE FROM Payments WHERE payment_id = %s", (payment_id,))
        conn.commit()
        flash("Payment deleted successfully!", 'success')
    except Exception as e:
        flash(f"Error deleting payment: {str(e)}", 'danger')
    finally:
        conn.close()

    return redirect(url_for('list_payments'))  # Redirect back to the payments list

# --- List Equipment ---
@app.route('/equipment')
def list_equipment():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all equipment
    cursor.execute("""SELECT * FROM Equipment""")
    equipment = cursor.fetchall()  # Store all the equipment in a list

    conn.close()
    return render_template('equipment.html', equipment=equipment)  # Pass the equipment data to the template
@app.route('/equipment/add', methods=['GET', 'POST'])
def add_equipment():
    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        purchase_date = request.form['purchase_date']
        status = request.form['status']
        
        equipment_image_url = None  # Initialize variable to store image URL
        
        # Handle image upload
        equipment_image = request.files.get('equipment_image')
        
        if equipment_image and allowed_file(equipment_image.filename):
            # Save the file to the upload folder
            filename = secure_filename(equipment_image.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            equipment_image.save(file_path)

            # Save the file path as the equipment image URL (relative to static folder)
            equipment_image_url = f"uploads/{filename}"

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Insert new equipment, including the image URL or path
            cursor.execute("""
                INSERT INTO Equipment (name, type, purchase_date, status, equipment_image_url)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, type, purchase_date, status, equipment_image_url))
            conn.commit()

            flash("Equipment added successfully!", 'success')

        except Exception as e:
            flash(f"Error adding equipment: {str(e)}", 'danger')
        finally:
            conn.close()

        return redirect(url_for('home'))  # Redirect after adding equipment

    return render_template('add_equipment.html')  # Render the form for adding equipment

# --- Delete Equipment ---
@app.route('/equipment/delete/<int:equipment_id>', methods=['POST'])
def delete_equipment(equipment_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete the equipment record from the Equipment table
    cursor.execute("""DELETE FROM Equipment WHERE equipment_id = %s""", (equipment_id,))
    conn.commit()

    conn.close()

    flash("Equipment deleted successfully!", 'success')
    return redirect(url_for('list_equipment'))  # Redirect to the equipment list after deletion

@app.route('/trainers')
def list_trainers():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch trainer data from the Trainers table, joining with Users to get the name
    cursor.execute("""
        SELECT t.trainer_name, t.bio, t.experience, t.specialization, u.email, t.user_id, t.image_url
        FROM Trainers t
        JOIN Users u ON t.user_id = u.user_id
    """)
    trainers = cursor.fetchall()  # Get all trainer data



    conn.close()

    return render_template('trainers.html', trainers=trainers)

@app.route('/trainers/edit/<int:trainer_id>', methods=['GET', 'POST'])
def edit_trainer(trainer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the trainer data based on the trainer_id
    cursor.execute("""
        SELECT t.user_id, t.trainer_name, t.bio, t.experience, t.specialization, t.image_url, u.email
        FROM Trainers t
        JOIN Users u ON t.user_id = u.user_id
        WHERE t.user_id = %s
    """, (trainer_id,))
    trainer = cursor.fetchone()

    if request.method == 'POST':
        # Get form data to update trainer details
        trainer_name = request.form['trainer_name']
        bio = request.form['bio']
        experience = request.form['experience']
        specialization = request.form['specialization']
        email = request.form['email']
        image = request.files.get('image')  # Get the uploaded image (if any)

        # Handle the image upload
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)  # Save the image to the server
            
            # Update the image URL in the database (relative path)
            cursor.execute("""
                UPDATE Trainers
                SET image_url = %s
                WHERE user_id = %s
            """, (filename, trainer_id))

        # Update the trainer data in the Users table
        cursor.execute("""
            UPDATE Users SET email = %s WHERE user_id = %s
        """, (email, trainer_id))

        # Update the trainer data in the Trainers table
        cursor.execute("""
            UPDATE Trainers
            SET trainer_name = %s, bio = %s, experience = %s, specialization = %s
            WHERE user_id = %s
        """, (trainer_name, bio, experience, specialization, trainer_id))

        conn.commit()
        conn.close()

        flash("Trainer updated successfully!", 'success')
        return redirect(url_for('list_trainers'))

    conn.close()
    return render_template('edit_trainer.html', trainer=trainer)


# --- Home Route ---
@app.route('/home')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
