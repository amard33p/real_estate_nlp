import React, { useEffect, useState } from "react";
import axios from "axios";
import { TypeAnimation } from 'react-type-animation';
import Map from "./components/Map";

interface Project {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
}

interface ProjectDetails {
  project_name: string;
  promoter_name: string;
  project_status: string;
  rera_registration_number: string;
  source_of_water: string;
  approving_authority: string;
  project_start_date: string;
  proposed_completion_date: string;
}

const App: React.FC = () => {
  useEffect(() => {
    axios.defaults.baseURL = import.meta.env.API_URL;
  }, []);
  const [query, setQuery] = useState<string>("");
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<ProjectDetails | null>(
    null
  );
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isTyping, setIsTyping] = useState<boolean>(true);

  const sampleQueries = [
    'Show me apartments in Indiranagar',
    'Find villas in Whitefield',
    'List projects by Prestige Group',
    'Display properties near MG Road',
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) {
      alert("Please enter a search query");
      return;
    }
    setIsLoading(true);
    try {
      const response = await axios.post<Project[]>("/api/projects", { query });
      setProjects(response.data);
      setSelectedProject(null);
    } catch (error) {
      console.error("Error fetching projects:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMarkerClick = async (id: number) => {
    try {
      const response = await axios.get<ProjectDetails>(`/api/project/${id}`);
      setSelectedProject(response.data);
    } catch (error) {
      console.error("Error fetching project details:", error);
    }
  };

  return (
    <div className="App">
      <h1>Bangalore Real Estate Projects</h1>
      <form onSubmit={handleSubmit}>
        <div className="input-wrapper">
          <input
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setIsTyping(false);
            }}
            onFocus={() => setIsTyping(false)}
            required
          />
          {isTyping && (
            <div className="type-animation-overlay">
              <TypeAnimation
                sequence={[
                  ...sampleQueries.flatMap(q => [q, 1000]),
                  () => setIsTyping(true),
                ]}
                wrapper="span"
                cursor={true}
                repeat={Infinity}
                speed={75}
                style={{ display: 'inline-block' }}
              />
            </div>
          )}
        </div>
        <button type="submit" disabled={isLoading || !query.trim()}>
          {isLoading ? (
            <>
              <span className="spinner"></span>
              Searching...
            </>
          ) : (
            "Search"
          )}
        </button>
      </form>
      <Map
        locations={projects.map((project) => ({
          ...project,
          key: project.id,
        }))}
        onMarkerClick={handleMarkerClick}
      />
      {selectedProject && (
        <div className="project-details">
          <h2>Project Details</h2>
          <p>
            <strong>Name:</strong> {selectedProject.project_name}
          </p>
          <p>
            <strong>Promoter:</strong> {selectedProject.promoter_name}
          </p>
          <p>
            <strong>Status:</strong> {selectedProject.project_status}
          </p>
          <p>
            <strong>RERA Registration:</strong>{" "}
            {selectedProject.rera_registration_number}
          </p>
          <p>
            <strong>Water Source:</strong> {selectedProject.source_of_water}
          </p>
          <p>
            <strong>Approving Authority:</strong>{" "}
            {selectedProject.approving_authority}
          </p>
          <p>
            <strong>Start Date:</strong> {selectedProject.project_start_date}
          </p>
          <p>
            <strong>Completion Date:</strong>{" "}
            {selectedProject.proposed_completion_date}
          </p>
        </div>
      )}
    </div>
  );
};

export default App;
