from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
import os

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
    employees = Employee.query.all()
    return render_template('index.html', employees=employees)

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
            photo_filename = photo.filename
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
            photo.save(photo_path)

            # Resize the image
            image = Image.open(photo_path)
            image = image.resize((150, 150))
            image.save(photo_path)
        else:
            photo_filename = 'default.jpg'

        new_employee = Employee(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile,
            date_of_birth=date_of_birth,
            photo=photo_filename
        )
        db.session.add(new_employee)
        db.session.commit()

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
                photo_filename = photo.filename
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
                photo.save(photo_path)

                # Resize the image
                image = Image.open(photo_path)
                image = image.resize((150, 150))
                image.save(photo_path)

                employee.photo = photo_filename

        db.session.commit()

        return redirect(url_for('index'))
    
    return render_template('edit.html', employee=employee)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
