import React, { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Tooltip,
  useMap,
} from "react-leaflet";
import { Box } from "@mui/material";
import { Project } from "../types";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

interface ProjectMapProps {
  locations: Project[];
  onMarkerClick: (id: number) => void;
}

// This component will handle updating the map view
const MapUpdater: React.FC<{ locations: Project[] }> = ({ locations }) => {
  const map = useMap();

  useEffect(() => {
    if (locations.length > 0) {
      const bounds = L.latLngBounds(
        locations.map((loc) => [loc.latitude, loc.longitude]),
      );
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [locations, map]);

  return null;
};

const ProjectMap: React.FC<ProjectMapProps> = ({
  locations,
  onMarkerClick,
}) => {
  const bangalorePosition: [number, number] = [12.9716, 77.5946];

  return (
    <Box sx={{ height: 400, width: "100%", my: 2 }}>
      <MapContainer
        center={bangalorePosition}
        zoom={12}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
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
        <MapUpdater locations={locations} />
      </MapContainer>
    </Box>
  );
};

export default ProjectMap;
