from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from PIL import Image
import os
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
db = SQLAlchemy(app)

# Employee Model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    photo = db.Column(db.String(200))  # Path to the resized photo

    def __repr__(self):
        return f"<Employee {self.first_name} {self.last_name}>"

# Resize Image Function
def resize_image(image_path):
    with Image.open(image_path) as img:
        img.thumbnail((150, 150))
        img.save(image_path)

# Routes
@app.route('/employees', methods=['GET'])
def get_employees():
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'first_name')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    # Sorting and searching logic
    if sort == 'first_name':
        employees = Employee.query.filter(Employee.first_name.like(f'%{search}%')).order_by(Employee.first_name).paginate(page, per_page, False)
    elif sort == 'email':
        employees = Employee.query.filter(Employee.email.like(f'%{search}%')).order_by(Employee.email).paginate(page, per_page, False)
    else:
        employees = Employee.query.paginate(page, per_page, False)

    return render_template('employee_list.html', employees=employees, search=search, sort=sort)

@app.route('/employee/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        mobile = request.form['mobile']
        dob = request.form['dob']
        photo = request.files['photo']
        filename = None

        if photo:
            filename = secure_filename(photo.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(filepath)
            resize_image(filepath)

        new_employee = Employee(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile,
            dob=date.fromisoformat(dob),
            photo=filename
        )
        db.session.add(new_employee)
        db.session.commit()
        flash("Employee added successfully!")
        return redirect(url_for('get_employees'))

    return render_template('employee_add.html')

@app.route('/employee/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    if request.method == 'POST':
        employee.first_name = request.form['first_name']
        employee.last_name = request.form['last_name']
        employee.email = request.form['email']
        employee.mobile = request.form['mobile']
        employee.dob = date.fromisoformat(request.form['dob'])

        photo = request.files['photo']
        if photo:
            filename = secure_filename(photo.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(filepath)
            resize_image(filepath)
            employee.photo = filename

        db.session.commit()
        flash("Employee updated successfully!")
        return redirect(url_for('get_employees'))

    return render_template('employee_edit.html', employee=employee)

@app.route('/employee/delete/<int:id>', methods=['POST'])
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash("Employee deleted successfully!")
    return redirect(url_for('get_employees'))

if __name__ == '__main__':
    app.run(debug=True)
