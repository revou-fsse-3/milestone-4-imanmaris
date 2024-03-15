from flask import Blueprint, render_template, request, redirect, jsonify, url_for, flash
from app.connectors.mysql_connector import engine
from app.models.users import User
from sqlalchemy import select
from app.utils.api_response import api_response
from sqlalchemy import func

from flask_login import current_user, login_required
from sqlalchemy.orm import sessionmaker
from flask_login import login_user, logout_user
from flask_jwt_extended import create_access_token

# Definisikan Blueprint untuk rute-rute terkait produk
user_management_routes = Blueprint('user_management_routes', __name__)

# Tentukan rute untuk URL '/register'
@user_management_routes.route("/users", methods=['POST'])
def do_registration():
    try:
        # Menerima data dari formulir HTML
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Membuat objek user baru
        new_user = User(username=username, email=email)
        new_user.set_password(password)

        connection = engine.connect()
        Session = sessionmaker(connection)
        # Menggunakan SQLAlchemy untuk menyimpan data
        session = Session()
        session.begin()
        session.add(new_user)
        session.commit()

        # Operasi sukses
        return api_response(
            status_code=201,
            message= "Pembuatan data user baru berhasil diinput",
            data={
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email
            }
        )    
    
    except Exception as e:
        # Operasi jika gagal
        session.rollback()
        return api_response(
            status_code=500,
            message=str(e),
            data={}
        )

# Pakai authentikasi token "Login Manager"
@user_management_routes.route("/userlogin", methods=['POST'])
def do_user_login():
    
    connection = engine.connect()
    Session = sessionmaker(connection)
    # Menggunakan SQLAlchemy untuk menyimpan data
    session = Session()

    try:
        user = session.query(User).filter(User.username==request.form['username']).first()

        if user is None:
            # flash("Username anda belum terdaftar", "error")
            # return redirect(url_for('user_management_routes.login_page'))
            return jsonify({"message": "Username anda belum terdaftar"}), 401

        # Check password
        if not user.check_password(request.form['password']):
            # flash("Kombinasi nama pengguna dan kata sandi tidak cocok.", "error")
            # return redirect(url_for('user_management_routes.login_page'))
            return jsonify({"message": "Kombinasi username dan password tidak cocok."}), 401

        login_user(user, remember=False)
        # flash("Login berhasil", "success")  # Tambahkan pesan sukses
        # return redirect('/users') # Redirect ke halaman pengguna setelah login berhasil
        # return jsonify({"message": ("Login berhasil", "success")}), 200   
        return jsonify({"message": "Selamat login anda succsess", "username": user.username}), 200

    except Exception as e:
        # flash("Login gagal. Silakan coba lagi.", "error")
        # return redirect(url_for('user_management_routes.login_page'))
        return jsonify({"message": "Login gagal. Silakan coba lagi."}), 500

@user_management_routes.route("/users", methods=['GET'])
@login_required
def users_home():
    response_data = dict()
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    try:
        user_query = session.query(User)

        # Penambahan filter apabila menggunakan search_query
        if request.args.get('query') != None:
            search_query = request.args.get('query')
            user_query = user_query.filter(User.username.like(f'%{search_query}%'))

        users = user_query.all()
        response_data['users'] = [user.serialize(full=False) for user in users]

        # Mengembalikan data dalam format JSON
        return jsonify(response_data)

    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e),
            data={}
        )
    finally:
        session.close()

@user_management_routes.route("/users/<int:user_id>", methods=['GET'])
@login_required
def get_user_by_id(user_id):
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    try:
        user = session.query(User).filter(User.id==user_id).first()
        if user:
            return jsonify(user.serialize(full=True))
        else:
            return jsonify({
                'message': 'User belum terdaftar'
            }), 404
        
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e),
            data={}
        )
    
    finally:
        session.close()


@user_management_routes.route("/users/<int:user_id>", methods=['PUT'])
@login_required
def update_user_by_id(user_id):
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    session.begin()

    try:
        user_to_update = session.query(User).filter(User.id == user_id).first()

        if not user_to_update:
            return api_response(
                status_code=404,
                message="User tidak ditemukan",
                data={}
            )

        user_to_update.username = request.form.get('username', user_to_update.username)
        user_to_update.email = request.form.get('email', user_to_update.email)
        new_password = request.form.get('password')
        if new_password:
            user_to_update.set_password(new_password)
        user_to_update.updated_at = func.now()

        session.commit()
        
        # Operasi sukses
        return api_response(
            status_code=201,
            message="Data user berhasil diperbarui",
            data={
                "username": user_to_update.username,
                "email": user_to_update.email,
                "password": new_password
            }
        )    
    except Exception as e:
        session.rollback()
        return api_response(
            status_code=500,
            message=str(e),
            data={}
        )
    
    finally:
        session.close()


@user_management_routes.route("/userlogout", methods=['GET'])
def do_user_logout():
    logout_user()
    return redirect('/')


# Pakai authentikasi token "JWT Manager"

@user_management_routes.route("/loginjwt", methods=['GET'])
def user_login_jwt():
    return render_template("users/login_jwt.html")

@user_management_routes.route("/logoutjwt", methods=['GET'])
def do_user_logout_jwt():
    logout_user()
    return redirect('/')

@user_management_routes.route("/loginjwt", methods=['POST'])
def do_user_login_jwt():
    connection = engine.connect()
    Session = sessionmaker(bind=connection)
    session = Session()

    try:
        user = session.query(User).filter(User.email==request.form['email']).first()

        if user == None:
            return jsonify ({"message": "Email belum terdaftar"}), 404
        
        # Check password
        if not user.check_password(request.form['password']):
            return jsonify ({"message": "Password salah"}), 401
        
        access_token = create_access_token(identity=user.name)
        return jsonify({"access_token": access_token}), 200
        
    except Exception as e:
        print(e)  # Untuk mencatat pengecualian untuk tujuan debugging
        return jsonify({"message": "Login belum berhasil"}), 500
    
    finally:
        session.close()