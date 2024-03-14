from flask import Blueprint, render_template, request, redirect, jsonify, url_for
from app.connectors.mysql_connector import engine
from app.models.accounts import Account
from sqlalchemy import select
from app.utils.api_response import api_response
from sqlalchemy import func

from flask_login import current_user, login_required
from sqlalchemy.orm import sessionmaker
from flask_login import login_user, logout_user
from flask_jwt_extended import create_access_token

# Definisikan Blueprint untuk rute-rute terkait produk
account_management_routes = Blueprint('account_management_routes', __name__)

# Tentukan rute untuk URL '/register'
@account_management_routes.route("/accounts", methods=['POST'])
def create_account():
    try:
        # Menerima data dari formulir HTML
        account_type = request.form['account_type']
        account_number = request.form['account_number']
        balance = request.form['balance']

        if not account_type or not account_number or not balance:
            raise ValueError("Data tidak lengkap")
        
        # Membuat objek akun baru
        new_account = Account(user_id=current_user.id, account_type=account_type, account_number=account_number, balance=balance)

        connection = engine.connect()
        Session = sessionmaker(connection)
        # Menggunakan SQLAlchemy untuk menyimpan data
        session = Session()
        session.begin()
        session.add(new_account)
        session.commit()

        # Operasi sukses
        return api_response(
            status_code=201,
            message="Pembuatan data akun baru berhasil diinput",
            data={
                "id": new_account.id,
                "user_id": new_account.user_id,
                "account_type": new_account.account_type,
                "account_number": new_account.account_number,
                "balance": new_account.balance
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
    
@account_management_routes.route("/accounts", methods=['GET'])
@login_required
def accounts_home():
    response_data = dict()
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    try:
        account_query = session.query(Account)

        # Penambahan filter apabila menggunakan search_query
        if request.args.get('query') != None:
            search_query = request.args.get('query')
            account_query = account_query.filter(Account.account_type.like(f'%{search_query}%'))

        accounts = account_query.all()
        response_data['accounts'] = [account.serialize(full=False) for account in accounts]

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

@account_management_routes.route("/accounts/<int:account_id>", methods=['GET'])
@login_required
def get_account_by_id(account_id):
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    try:
        account = session.query(Account).filter(Account.id==account_id).first()
        if account:
            return jsonify(account.serialize(full=True))
        else:
            return jsonify({
                'message': 'Account belum terdaftar di sistem'
            }), 404
        
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e),
            data={}
        )
    
    finally:
        session.close()


@account_management_routes.route("/accounts/<int:account_id>", methods=['PUT'])
@login_required
def update_account_by_id(account_id):
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    session.begin()

    try:
        account_to_update = session.query(Account).filter(Account.id == account_id).first()

        if account_to_update:
            # Periksa apakah user_id dari akun yang akan dihapus cocok dengan user_id pengguna yang masuk
            if account_to_update.user_id != current_user.id:
                return jsonify({
                    "error": f"Anda tidak memiliki izin untuk mengubah data akun ini. Anda login sebagai user_id: {current_user.id}"
                }), 403

            account_to_update.account_type = request.form.get('account_type', account_to_update.account_type)
            account_to_update.account_number = request.form.get('account_number', account_to_update.account_number)
            account_to_update.balance = request.form.get('balance', account_to_update.balance)
            account_to_update.updated_at = func.now()

            session.commit()
            
            # Operasi sukses
            return api_response(
                status_code=201,
                message="Data user berhasil diperbarui",
                data={
                    "account_type": account_to_update.account_type,
                    "account_number": account_to_update.account_number,
                    "balance": account_to_update.balance,
                    "updated_at": account_to_update.updated_at
                }
            )    
        
        else:
            return jsonify({"error": "ID Akun tidak ditemukan"}), 404
        
    except Exception as e:
        session.rollback()
        return api_response(
            status_code=500,
            message=str(e),
            data={}
        )
    
    finally:
        session.close()


@account_management_routes.route("/accounts/<id>", methods=['DELETE'])
@login_required
def delete_account(id):
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()

    try:
        account_to_delete = session.query(Account).filter(Account.id == id).first()
        
        if account_to_delete:
            # Periksa apakah user_id dari akun yang akan dihapus cocok dengan user_id pengguna yang masuk
            if account_to_delete.user_id != current_user.id:
                return jsonify({
                    "error": f"Anda tidak memiliki izin untuk menghapus akun ini. Anda login sebagai user_id: {current_user.id}"
                }), 403
                        
            session.delete(account_to_delete)
            session.commit()
            return api_response(
                status_code=200,
                message="Data akun berhasil dihapus",
                data={
                "id": account_to_delete.id,
                "user_id": account_to_delete.user_id,
                "account_type": account_to_delete.account_type,
                "account_number": account_to_delete.account_number,
                "balance": account_to_delete.balance
                }
            )          
        
        else:
            return jsonify({"error": "ID Akun tidak ditemukan"}), 404
    
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    
    finally:
        session.close()
