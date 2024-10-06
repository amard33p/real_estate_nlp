from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_db_connection
from query_transformer import transform_query

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})


@app.route("/api/projects", methods=["POST"])
def get_projects():
    user_query = request.json["query"]
    db = get_db_connection()
    sql_query = "SELECT project_id as id, project_name as name, latitude, longitude FROM karnataka_projects where project_name LIKE '%prestige%' AND district like '%bengaluru%' AND project_id > 8900"
    # sql_query = transform_query(user_query, db)
    print(sql_query)
    results = db.run(sql_query)
    print(f"Got {len(results)} results")
    return jsonify(results)


@app.route("/api/project/<int:project_id>", methods=["GET"])
def get_project_details(project_id):
    db = get_db_connection()
    sql_query = f"""
    SELECT project_name, promoter_name, project_status, rera_registration_number, 
           source_of_water, approving_authority, project_start_date, proposed_completion_date
    FROM karnataka_projects
    WHERE project_id = {project_id}
    """
    results = db.run(sql_query)
    if results:
        return jsonify(results[0])
    else:
        return jsonify({"error": "Project not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
