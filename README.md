
# 🏋️ Gym Management System

A beginner-friendly full-stack web application built with Flask to manage gym operations such as member registration, trainer management, membership plans, and payments.

---

## 🚀 Features

- Add, edit, delete, and view **gym members**
- Manage **trainers** and assign them to members
- Set up **membership plans**
- Track and manage **payments**
- Clean, interactive UI with HTML, CSS, and JavaScript
- MySQL-powered database integration

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: MySQL
- **Templating**: Jinja2 Templates

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Rakshithaa5/Gym-Management.git
cd Gym-Management
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up MySQL Database

- Install MySQL if not already installed.
- Create a database:

```sql
CREATE DATABASE gym_db;
```

- Update your MySQL credentials and database config inside `app.py`:

```python
app.config['MYSQL_USER'] = 'your_mysql_username'
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
app.config['MYSQL_DB'] = 'gym_db'
```

### 5. Run the app

```bash
python app.py
```

Then open your browser and go to `http://127.0.0.1:5000`

---

## 📁 Project Structure

```bash
Gym-Management/
│
├── static/               # CSS, JS, and images
│   └── script.js         # Your JavaScript functions
├── templates/            # HTML templates
├── app.py                # Main Flask application
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## 🖼️ Screenshots

_Add screenshots from your app here:_

```markdown
![Home Page](screenshots/home.png)
![Members List](screenshots/members.png)
![Trainer Management](screenshots/trainers.png)
```

---

## 🙌 Contributing

Feel free to open issues or pull requests for improvements or new features.

---

## 📜 License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

---

## 📬 Contact

Created by [Rakshithaa](https://github.com/Rakshithaa5)  
Reach out for questions, collaboration, or feedback!
