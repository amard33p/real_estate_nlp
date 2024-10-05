import React, { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Tooltip,
  useMap,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix for default marker icon
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

interface Location {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  key: number;
}

interface MapProps {
  locations: Location[];
  onMarkerClick: (id: number) => void;
}

const ChangeView: React.FC<{ locations: Location[] }> = ({ locations }) => {
  const map = useMap();

  useEffect(() => {
    if (locations.length > 0) {
      const bounds = L.latLngBounds(
        locations.map((loc) => [loc.latitude, loc.longitude])
      );
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [locations, map]);

  return null;
};

const Map: React.FC<MapProps> = ({ locations, onMarkerClick }) => {
  const bangalorePosition: [number, number] = [12.9716, 77.5946]; // Bangalore coordinates

  return (
    <MapContainer
      center={bangalorePosition}
      zoom={12}
      style={{ height: "400px", width: "100%" }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      <ChangeView locations={locations} />
      {locations.map((location) => (
        <Marker
          key={location.id}
          position={[location.latitude, location.longitude]}
          eventHandlers={{
            click: () => onMarkerClick(location.id),
          }}
        >
          <Tooltip direction="top" offset={[0, -20]} opacity={1}>
            {location.name}
          </Tooltip>
          <Popup>{location.name}</Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default Map;
