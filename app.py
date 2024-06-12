from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy import text

app = Flask(__name__)

# Configuración de la base de datos
server = "191.239.122.127"  # "10.0.0.4"
database = "FNA"
username = "FNA"
password = "D0cUm3nT2024*."
driver = 'ODBC Driver 17 for SQL Server'

connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver.replace(' ', '+')}"
app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definir un modelo de ejemplo
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'

# Ruta para obtener todos los usuarios
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'name': user.name, 'email': user.email} for user in users])

# Ruta para agregar un nuevo usuario
@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = User(name=data['name'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'id': new_user.id, 'name': new_user.name, 'email': new_user.email}), 201

# Ruta para obtener un usuario por ID
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})

# Ruta para actualizar un usuario
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = User.query.get_or_404(id)
    user.name = data['name']
    user.email = data['email']
    db.session.commit()
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})

# Ruta para eliminar un usuario
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

# Ruta para obtener los nombres de todas las tablas
@app.route('/tables', methods=['GET'])
def get_tables():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    return jsonify(tables)

# Ruta para obtener los datos de una tabla específica
@app.route('/view/<view_name>/<int:number>', methods=['GET'])
def get_view_data_filtered(view_name, number):
    try:
        # Verificar si la vista existe en la base de datos
        inspector = inspect(db.engine)
        if view_name not in inspector.get_view_names():
            return jsonify({"error": "View not found"}), 404

        # Construir una consulta SELECT para la vista con el filtro por número
        query = text(f"SELECT * FROM {view_name} WHERE TRY_CAST(d_number AS FLOAT) = :number;")
        
        # Ejecutar la consulta con el número como parámetro
        result_proxy = db.session.execute(query, {"number": number})
        # Obtener los nombres de las columnas
        columns = result_proxy.keys()
        # Convertir los resultados a una lista de diccionarios
        results = [dict(zip(columns, row)) for row in result_proxy]
        # Agregar la consulta al resultado
        results.append({"query": str(query)})

        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    




if __name__ == '__main__':
    # Crear las tablas en la base de datos
    with app.app_context():
        db.create_all()
    app.run(debug=True)

