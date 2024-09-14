from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
import os
from sqlalchemy import or_

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    mobile = db.Column(db.String(20))
    date_of_birth = db.Column(db.String(10))
    photo = db.Column(db.String(100))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')

    sort_by = request.args.get('sort', 'first_name')
    sort_order = request.args.get('order', 'asc')

    if search_query:
        search = f"%{search_query}%"
        employees = Employee.query.filter(
            or_(Employee.first_name.like(search), Employee.last_name.like(search), Employee.email.like(search))
        ).order_by(getattr(Employee, sort_by).asc() if sort_order == 'asc' else getattr(Employee, sort_by).desc()).paginate(page=page, per_page=10)
    else:
        employees = Employee.query.order_by(getattr(Employee, sort_by).asc() if sort_order == 'asc' else getattr(Employee, sort_by).desc()).paginate(page=page, per_page=10)

    return render_template('index.html', employees=employees, search_query=search_query, sort_by=sort_by, sort_order=sort_order)

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        mobile = request.form['mobile']
        date_of_birth = request.form['date_of_birth']
        photo = request.files['photo']

        if photo:
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
            photo.save(photo_path)
            img = Image.open(photo_path)
            img = img.resize((200, 200))
            img.save(photo_path)

        new_employee = Employee(first_name=first_name, last_name=last_name, email=email, 
                                mobile=mobile, date_of_birth=date_of_birth, photo=photo.filename)
        db.session.add(new_employee)
        db.session.commit()
        flash('Employee added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    if request.method == 'POST':
        employee.first_name = request.form['first_name']
        employee.last_name = request.form['last_name']
        employee.email = request.form['email']
        employee.mobile = request.form['mobile']
        employee.date_of_birth = request.form['date_of_birth']

        if 'photo' in request.files:
            photo = request.files['photo']
            if photo:
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
                photo.save(photo_path)
                img = Image.open(photo_path)
                img = img.resize((200, 200))
                img.save(photo_path)
                employee.photo = photo.filename

        db.session.commit()
        flash('Employee updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', employee=employee)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash('Employee deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
