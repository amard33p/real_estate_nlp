import React from "react";
import {
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
  Box,
} from "@mui/material";
import { Project } from "../types";

interface ProjectListProps {
  projects: Project[];
  onProjectSelect: (id: number) => void;
  selectedProjectId: number | null;
}

const ProjectList: React.FC<ProjectListProps> = ({
  projects,
  onProjectSelect,
  selectedProjectId,
}) => {
  return (
    <Box sx={{ flexGrow: 1, overflowY: "auto", maxHeight: "50vh" }}>
      <Typography variant="h6" sx={{ p: 2 }}>
        Project List
      </Typography>
      <List>
        {projects.map((project) => (
          <ListItem key={project.id} disablePadding>
            <ListItemButton
              onClick={() => onProjectSelect(project.id)}
              selected={project.id === selectedProjectId}
              sx={{
                "&.Mui-selected": {
                  backgroundColor: "primary.light",
                  "&:hover": {
                    backgroundColor: "primary.main",
                  },
                },
              }}
            >
              <ListItemText primary={project.name} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default ProjectList;
