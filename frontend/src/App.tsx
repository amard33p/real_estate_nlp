import React, { useState } from "react";
import { ThemeProvider, createTheme, CssBaseline } from "@mui/material";
import axios from "axios";
import Header from "./components/Header";
import SearchForm from "./components/SearchForm";
import ProjectMap from "./components/ProjectMap";
import ProjectDetails from "./components/ProjectDetails";
import { Project, ProjectDetails as ProjectDetailsType } from "./types";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#007bff",
    },
    secondary: {
      main: "#6c757d",
    },
  },
});

const App: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] =
    useState<ProjectDetailsType | null>(null);

  const handleMarkerClick = async (id: number) => {
    try {
      const response = await axios.get<ProjectDetailsType>(
        `http://localhost:5000/api/project/${id}`,
      );
      setSelectedProject(response.data);
    } catch (error) {
      console.error("Error fetching project details:", error);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Header />
      <SearchForm setProjects={setProjects} />
      <ProjectMap locations={projects} onMarkerClick={handleMarkerClick} />
      {selectedProject && <ProjectDetails project={selectedProject} />}
    </ThemeProvider>
  );
};

export default App;
