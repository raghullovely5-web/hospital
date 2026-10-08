# Hospital Appointment System

Technology:
- Python Flask
- MySQL
- HTML/CSS
- Bootstrap/CDN where used

## Project files
- app.py - Flask backend
- hospital.sql - MySQL database schema
- templates/ - HTML/Jinja pages
- static/style.css - basic local styling
- uploads/ - doctor images
- requirements.txt - Python packages

## Important
The uploaded `sql.txt` did not contain a MySQL CREATE TABLE schema; it contained Flask/Python backend code. Therefore `hospital.sql` is a small schema reconstructed from the table/column names actually used by that backend. Review it before using it for a real deployment.

## Run on Windows
1. Install Python.
2. Install MySQL/WAMP/XAMPP and start MySQL.
3. Open Command Prompt in this project folder.
4. Run:
   pip install -r requirements.txt
5. Open MySQL/phpMyAdmin and import `hospital.sql`.
6. If your MySQL root password is not empty, edit `db_config` in `app.py`.
7. Run:
   python app.py
8. Open:
   http://127.0.0.1:5000

The original large HTML file contained multiple pages in one text file. The relevant pages were separated into individual files for Flask templates. Some missing pages were added as simple templates so the Flask routes have matching template files.
