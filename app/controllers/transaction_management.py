from flask import Blueprint, render_template, request, redirect, jsonify, url_for
from app.connectors.mysql_connector import engine
from app.models.transactions import Transaction
from sqlalchemy import select
from app.utils.api_response import api_response
from sqlalchemy import func

from flask_login import current_user, login_required
from sqlalchemy.orm import sessionmaker
from flask_login import login_user, logout_user
from flask_jwt_extended import create_access_token

# Definisikan Blueprint untuk rute-rute terkait produk
transaction_management_routes = Blueprint('transaction_management_routes', __name__)

# Tentukan rute untuk URL '/register'
@transaction_management_routes.route("/transactions", methods=['POST'])
def create_transaction():
    try:
        # Menerima data dari formulir HTML
        to_account_id = request.form['to_account_id']
        amount = request.form['amount']
        type = request.form['type']
        description = request.form['description']


        if not to_account_id or not amount or not type or not description:
            raise ValueError("Mohon untuk mengisi data secara lengkap")
        
        # Membuat objek transaksi baru
        new_transaction = Transaction(
            from_account_id=current_user.id,  # Menggunakan ID pengguna yang sedang login
            to_account_id=to_account_id,
            amount=amount,
            type=type,
            description=description
        )


        connection = engine.connect()
        Session = sessionmaker(connection)

        # Menggunakan SQLAlchemy untuk menyimpan data
        session = Session()
        session.add(new_transaction)
        session.commit()

        # Operasi sukses
        return api_response(
            status_code=201,
            message="Pembuatan data transaksi baru berhasil diinput",
            data={
                "id": new_transaction.id,
                "from_account_id": new_transaction.from_account_id,
                "to_account_id": new_transaction.to_account_id,
                "amount": new_transaction.amount,
                "type": new_transaction.type,
                "description": new_transaction.description,
                "created_at": new_transaction.created_at.strftime("%Y-%m-%d %H:%M:%S")
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
    
@transaction_management_routes.route("/transactions", methods=['GET'])
@login_required
def transactions_home():
    response_data = dict()
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    try:
        transaction_query = session.query(Transaction)

        # Penambahan filter apabila menggunakan search_query
        if request.args.get('query') != None:
            search_query = request.args.get('query')
            transaction_query = transaction_query.filter(Transaction.from_account_id.like(f'%{search_query}%'))

        transactions = transaction_query.all()
        response_data['transactions'] = [transaction.serialize(full=False) for transaction in transactions]

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

@transaction_management_routes.route("/transactions/<int:transaction_id>", methods=['GET'])
@login_required
def get_transaction_by_id(transaction_id):
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    try:
        transaction = session.query(Transaction).filter(Transaction.id==transaction_id).first()
        if transaction:
            return jsonify(transaction.serialize(full=True))
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
