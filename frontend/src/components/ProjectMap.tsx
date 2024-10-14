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
  selectedProjectId: number | null;
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
  selectedProjectId,
}) => {
  const bangalorePosition: [number, number] = [12.9716, 77.5946];

  const getMarkerIcon = (isSelected: boolean) => {
    return L.icon({
      iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
      iconSize: isSelected ? [38, 62] : [25, 41],
      iconAnchor: isSelected ? [19, 62] : [12, 41],
    });
  };

  return (
    <Box sx={{ height: "100%", width: "100%" }}>
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
            icon={getMarkerIcon(location.id === selectedProjectId)}
          >
            <Tooltip direction="top" offset={[0, -20]} opacity={1}>
              {location.name}
            </Tooltip>
          </Marker>
        ))}
        <MapUpdater locations={locations} />
      </MapContainer>
    </Box>
  );
};

export default ProjectMap;
