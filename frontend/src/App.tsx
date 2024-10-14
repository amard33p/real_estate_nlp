import React, { useState, useEffect } from "react";
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box,
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import axios from "axios";
import Header from "./components/Header";
import SearchForm from "./components/SearchForm";
import ProjectMap from "./components/ProjectMap";
import ProjectDetails from "./components/ProjectDetails";
import ProjectList from "./components/ProjectList";
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
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(
    null,
  );

  useEffect(() => {
    setSelectedProject(null);
    setSelectedProjectId(null);
  }, [projects]);

  const handleMarkerClick = async (id: number) => {
    try {
      const response = await axios.get<ProjectDetailsType>(
        `http://localhost:5000/api/project/${id}`,
      );
      setSelectedProject(response.data);
      setSelectedProjectId(id);
    } catch (error) {
      console.error("Error fetching project details:", error);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: "flex", flexDirection: "column", height: "100vh" }}>
        <Header />
        <Grid container sx={{ flexGrow: 1 }}>
          <Grid size={3} sx={{ display: "flex", flexDirection: "column" }}>
            <ProjectList
              projects={projects}
              onProjectSelect={handleMarkerClick}
              selectedProjectId={selectedProjectId}
            />
            {selectedProject && <ProjectDetails project={selectedProject} />}
          </Grid>
          <Grid size={6}>
            <ProjectMap
              locations={projects}
              onMarkerClick={handleMarkerClick}
              selectedProjectId={selectedProjectId}
            />
          </Grid>
          <Grid size={3}>
            <SearchForm setProjects={setProjects} />
          </Grid>
        </Grid>
      </Box>
    </ThemeProvider>
  );
};

export default App;
