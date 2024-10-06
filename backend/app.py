import math
from flask import Flask, request, jsonify
from flask_cors import CORS

from query_transformer import transform_query, extract_location_and_query
from database import get_db_connection
from geocoding import geocode_location

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

BLR_LAT, BLR_LON = 12.9716, 77.5946  # Default to Bangalore center
BLR_RADIUS = 100
ZONAL_RADIUS = 10


def create_app():
    return app


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


def filter_results_by_distance(results, center_lat, center_lon, max_distance_km):
    return [
        result
        for result in results
        if haversine_distance(
            center_lat,
            center_lon,
            float(result["latitude"]),
            float(result["longitude"]),
        )
        <= max_distance_km
    ]


@app.route("/api/projects", methods=["POST"])
def get_projects():
    try:
        user_query = request.json["query"]
        db = get_db_connection()

        extracted_info = extract_location_and_query(user_query)
        location, main_query = extracted_info["location"], extracted_info["query"]

        center_lat, center_lon, max_distance_km = get_zonal_search_parameters(location)

        print(f"User query: {user_query}")
        sql_query = transform_query(main_query, db)
        print(f"Transformed SQL query: \n{sql_query}")
        results = db.run(sql_query)

        print(f"Got {len(results)} results before distance filtering")
        filtered_results = filter_results_by_distance(
            results, center_lat, center_lon, max_distance_km
        )

        print(f"Got {len(filtered_results)} results after distance filtering")
        return jsonify(filtered_results)
    except Exception as e:
        return handle_error(str(e))


def get_zonal_search_parameters(location):
    if location:
        print(f"Extracted location from user query: {location}")
        coordinates = geocode_location(location)
        if coordinates:
            print(f"{location} coordinates: {coordinates}")
            return *coordinates, ZONAL_RADIUS
    return BLR_LAT, BLR_LON, BLR_RADIUS


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


@app.route("/api/geocode", methods=["POST"])
def geocode():
    location = request.json.get("location")
    if not location:
        return jsonify({"error": "Location is required"}), 400

    coordinates = geocode_location(location)
    if coordinates:
        lat, lng = coordinates
        return jsonify(
            {"location": location, "coordinates": {"latitude": lat, "longitude": lng}}
        )
    else:
        return jsonify({"error": "Unable to geocode the location"}), 404


def handle_error(error_message):
    print(f"An error occurred: {error_message}")
    return jsonify({"error": f"An error occurred: {error_message}"}), 500


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
