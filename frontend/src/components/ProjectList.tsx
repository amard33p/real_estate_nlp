import React from 'react';
import { List, ListItem, ListItemButton, ListItemText, Typography, Box } from '@mui/material';
import { Project } from '../types';

interface ProjectListProps {
  projects: Project[];
  onProjectSelect: (id: number) => void;
}

const ProjectList: React.FC<ProjectListProps> = ({ projects, onProjectSelect }) => {
  return (
    <Box sx={{ height: '100%', overflowY: 'auto' }}>
      <Typography variant="h6" sx={{ p: 2 }}>Project List</Typography>
      <List>
        {projects.map((project) => (
          <ListItem key={project.id} disablePadding>
            <ListItemButton onClick={() => onProjectSelect(project.id)}>
              <ListItemText primary={project.name} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default ProjectList;

