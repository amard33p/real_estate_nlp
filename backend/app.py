import math

from flask import Flask, request, jsonify
from flask_cors import CORS

from query_transformer import transform_query
from database import get_db_connection


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    return R * c


@app.route("/api/projects", methods=["POST"])
def get_projects():
    user_query = request.json["query"]
    db = get_db_connection()

    CENTER_LAT, CENTER_LON = 12.9716, 77.5946
    MAX_DISTANCE_KM = 50

    sql_query = """
    SELECT project_id as id, project_name as name, latitude, longitude
    FROM karnataka_projects
    WHERE project_name LIKE '%prestige%'
      AND district LIKE '%bengaluru%'
      AND project_id > 8900
    """
    # sql_query = transform_query(user_query, db)

    # Execute the query using our custom SQLiteDatabase
    results = db.run(sql_query)

    # Filter results based on haversine distance
    filtered_results = [
        result
        for result in results
        if haversine_distance(
            CENTER_LAT,
            CENTER_LON,
            float(result["latitude"]),
            float(result["longitude"]),
        )
        <= MAX_DISTANCE_KM
    ]

    print(f"Got {len(filtered_results)} results after distance filtering")
    return jsonify(filtered_results)


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
