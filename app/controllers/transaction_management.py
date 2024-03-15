from flask import Blueprint, render_template, request, redirect, jsonify, url_for

from app.connectors.mysql_connector import engine
from app.models.transactions import Transaction
from app.models.accounts import Account

from sqlalchemy import select
from app.utils.api_response import api_response
from sqlalchemy import func

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from flask_login import current_user, login_required
from flask_jwt_extended import create_access_token

# Definisikan Blueprint untuk rute-rute terkait produk
transaction_management_routes = Blueprint('transaction_management_routes', __name__)

@transaction_management_routes.route('/transactions', methods=['POST'])
@login_required
def create_transaction():
    connection = engine.connect()
    Session = sessionmaker(connection)
    # Menggunakan SQLAlchemy untuk menyimpan data
    session = Session()

    try:
        # Menerima data dari formulir HTML atau payload JSON
        from_account_id = request.form.get('from_account_id')
        to_account_id = request.form.get('to_account_id')
        amount = request.form.get('amount')
        type = request.form.get('type')
        description = request.form.get('description')

        # Validasi input
        if not from_account_id or not to_account_id or not amount or not type or not description:
            raise ValueError("Mohon untuk mengisi 'data secara lengkap'")

        # Pastikan from_account_id dimiliki oleh pengguna yang sedang login
        from_account = session.query(Account).filter_by(id=from_account_id, user_id=current_user.id).first()
        if not from_account:
            raise ValueError("from_account_id tidak valid untuk pengguna yang sedang login")

        # Membuat objek transaksi baru
        new_transaction = Transaction(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            type=type,
            description=description
        )

        # # Membuat sesi
        # connection = engine.connect()
        # Session = sessionmaker(connection)
        # session = Session()
        # Menggunakan SQLAlchemy untuk menyimpan data
        session.add(new_transaction)
        session.commit()

        # Mengembalikan respons sukses
        return jsonify({
            'message': 'Transaksi berhasil dibuat',
            'transaction_id': new_transaction.id
        }), 201
    
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({
            'error': 'Gagal membuat transaksi',
            'message': str(e)
        }), 500
    
    except ValueError as e:
        return jsonify({
            'error': 'Gagal membuat transaksi',
            'message': str(e)
        }), 400
    
    except Exception as e:
        return jsonify({
            'error': 'Gagal membuat transaksi',
            'message': str(e)
        }), 500        


@transaction_management_routes.route('/transactions/deposit', methods=['POST'])
@login_required
def create_deposit_transaction():
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()

    try:
        # Menerima data dari formulir HTML atau payload JSON
        from_account_id = request.form.get('from_account_id')
        to_account_id = request.form.get('to_account_id')
        amount = request.form.get('amount')

        # Validasi input
        if not to_account_id or not amount:
            raise ValueError("Mohon untuk mengisi 'to_account_id' dan 'amount'")

        # Pastikan from_account_id dimiliki oleh pengguna yang sedang login
        from_account = session.query(Account).filter_by(id=from_account_id, user_id=current_user.id).first()
        if not from_account:
            raise ValueError("from_account_id tidak valid untuk pengguna yang sedang login")


        # Membuat objek transaksi deposit baru
        new_deposit_transaction = Transaction(
            from_account_id=from_account_id,  # ID akun sumber dana eksternal
            to_account_id=to_account_id,
            amount=amount,
            type='deposit',
            description='pengiriman dana'
        )

        session.add(new_deposit_transaction)
        session.commit()

        # # Mengembalikan respons sukses
        # return jsonify({
        #     'message': 'Transaksi deposit berhasil dibuat',
        #     'transaction_id': new_deposit_transaction.id
        # }), 201
                # Operasi sukses
        return api_response(
            status_code=201,
            message="Pembuatan data transaksi deposit berhasil diinput",
            data={
                "id": new_deposit_transaction.id,
                "from_account_id": new_deposit_transaction.from_account_id,
                "to_account_id": new_deposit_transaction.to_account_id,
                "amount": new_deposit_transaction.amount,
                "type": new_deposit_transaction.type,
                "description": new_deposit_transaction.description,
                "created_at": new_deposit_transaction.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        )  
    
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({
            'error': 'Gagal membuat transaksi deposit',
            'message': str(e)
        }), 500
    
    except ValueError as e:
        return jsonify({
            'error': 'Gagal membuat transaksi deposit',
            'message': str(e)
        }), 400
    
    except Exception as e:
        return jsonify({
            'error': 'Gagal membuat transaksi deposit',
            'message': str(e)
        }), 500

@transaction_management_routes.route('/transactions/withdrawal', methods=['POST'])
@login_required
def create_withdrawal_transaction():
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()

    try:
        # Menerima data dari formulir HTML atau payload JSON
        from_account_id = request.form.get('from_account_id')
        to_account_id = request.form.get('to_account_id')
        amount = request.form.get('amount')

        # Validasi input
        if not from_account_id or not amount:
            raise ValueError("Mohon untuk mengisi 'from_account_id' dan 'amount'")

        # Pastikan to_account_id dimiliki oleh pengguna yang sedang login
        to_account = session.query(Account).filter_by(id=to_account_id, user_id=current_user.id).first()
        if not to_account:
            raise ValueError("to_account_id tidak valid untuk pengguna yang sedang login")


        # Membuat objek transaksi penarikan baru
        new_withdrawal_transaction = Transaction(
            from_account_id=from_account_id,
            to_account_id=to_account_id,  # ID akun tujuan dana eksternal
            amount=amount,
            type='withdrawal',
            description='pengembalian dana'
        )

        session.add(new_withdrawal_transaction)
        session.commit()

        # # Mengembalikan respons sukses
        # return jsonify({
        #     'message': 'Transaksi penarikan berhasil dibuat',
        #     'transaction_id': new_withdrawal_transaction.id
        # }), 201
        return api_response(
            status_code=201,
            message="Pembuatan data transaksi deposit berhasil diinput",
            data={
                "id": new_withdrawal_transaction.id,
                "from_account_id": new_withdrawal_transaction.from_account_id,
                "to_account_id": new_withdrawal_transaction.to_account_id,
                "amount": new_withdrawal_transaction.amount,
                "type": new_withdrawal_transaction.type,
                "description": new_withdrawal_transaction.description,
                "created_at": new_withdrawal_transaction.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        )  
    
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({
            'error': 'Gagal membuat transaksi penarikan',
            'message': str(e)
        }), 500
    
    except ValueError as e:
        return jsonify({
            'error': 'Gagal membuat transaksi penarikan',
            'message': str(e)
        }), 400
    
    except Exception as e:
        return jsonify({
            'error': 'Gagal membuat transaksi penarikan',
            'message': str(e)
        }), 500


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


# -------------------------- backup ---------------------->
        
# Tentukan rute untuk URL '/register'
# @transaction_management_routes.route("/transactions", methods=['POST'])
# def create_transaction():
#     try:
#          # Menerima data dari formulir HTML
#         to_account_id = request.form['to_account_id']
#         amount = request.form['amount']
#         type = request.form['type']
#         description = request.form['description']


#         if not to_account_id or not amount or not type or not description:
#             raise ValueError("Mohon untuk mengisi data secara lengkap")
        
#         # Membuat objek transaksi baru
#         new_transaction = Transaction(
#             from_account_id=current_user.id,  # Menggunakan ID pengguna yang sedang login
#             to_account_id=to_account_id,
#             amount=amount,
#             type=type,
#             description=description
#         )


#         connection = engine.connect()
#         Session = sessionmaker(connection)

#         # Menggunakan SQLAlchemy untuk menyimpan data
#         session = Session()
#         session.add(new_transaction)
#         session.commit()

        # # Operasi sukses
        # return api_response(
        #     status_code=201,
        #     message="Pembuatan data transaksi baru berhasil diinput",
        #     data={
        #         "id": new_transaction.id,
        #         "from_account_id": new_transaction.from_account_id,
        #         "to_account_id": new_transaction.to_account_id,
        #         "amount": new_transaction.amount,
        #         "type": new_transaction.type,
        #         "description": new_transaction.description,
        #         "created_at": new_transaction.created_at.strftime("%Y-%m-%d %H:%M:%S")
        #     }
        # )    
    
#     except Exception as e:
#         # Operasi jika gagal
#         session.rollback()
#         return api_response(
#             status_code=500,
#             message=str(e),
#             data={}
#         )

# @transaction_management_routes.route('/transactions/deposit', methods=['POST'])
# def create_deposit_transaction():
#     try:
#         # Menerima data dari formulir HTML atau payload JSON
#         to_account_id = request.form.get('to_account_id')
#         amount = request.form.get('amount')

#         # Validasi input
#         if not to_account_id or not amount:
#             raise ValueError("Mohon untuk mengisi 'to_account_id' dan 'amount'")

#         # Membuat objek transaksi deposit baru
#         new_deposit_transaction = Transaction(
#             from_account_id="external_source_id",  # ID akun sumber dana eksternal
#             to_account_id=to_account_id,
#             amount=amount,
#             type='deposit'
#         )

#         connection = engine.connect()
#         Session = sessionmaker(connection)
#         # Menggunakan SQLAlchemy untuk menyimpan data
#         session = Session()
#         session.add(new_deposit_transaction)
#         session.commit()

#         # Mengembalikan respons sukses
#         return jsonify({
#             'message': 'Transaksi deposit berhasil dibuat',
#             'transaction_id': new_deposit_transaction.id
#         }), 201
    
#     except Exception as e:
#         # Tangani kesalahan dan kembalikan respons yang sesuai
#         return jsonify({
#             'error': 'Gagal membuat transaksi deposit',
#             'message': str(e)
#         }), 500

# @transaction_management_routes.route('/transactions/withdrawal', methods=['POST'])
# def create_withdrawal_transaction():
#     try:
#         # Menerima data dari formulir HTML atau payload JSON
#         from_account_id = request.form.get('from_account_id')
#         amount = request.form.get('amount')

#         # Validasi input
#         if not from_account_id or not amount:
#             raise ValueError("Mohon untuk mengisi 'from_account_id' dan 'amount'")

#         # Membuat objek transaksi penarikan baru
#         new_withdrawal_transaction = Transaction(
#             from_account_id=from_account_id,
#             to_account_id="external_destination_id",  # ID akun tujuan dana eksternal
#             amount=amount,
#             type='withdrawal'
#         )

#         connection = engine.connect()
#         Session = sessionmaker(connection)

#         # Menggunakan SQLAlchemy untuk menyimpan data
#         session = Session()
#         session.add(new_withdrawal_transaction)
#         session.commit()

#         # Mengembalikan respons sukses
#         return jsonify({
#             'message': 'Transaksi penarikan berhasil dibuat',
#             'transaction_id': new_withdrawal_transaction.id
#         }), 201
    
#     except Exception as e:
#         # Tangani kesalahan dan kembalikan respons yang sesuai
#         return jsonify({
#             'error': 'Gagal membuat transaksi penarikan',
#             'message': str(e)
#         }), 500
