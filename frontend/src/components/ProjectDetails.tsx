import React from "react";
import { Box, Typography } from "@mui/material";
import Grid from "@mui/material/Grid2";
import { ProjectDetails as ProjectDetailsType } from "../types";

interface ProjectDetailsProps {
  project: ProjectDetailsType;
}

const ProjectDetails: React.FC<ProjectDetailsProps> = ({ project }) => {
  return (
    <Box sx={{ mt: 2, p: 2, overflowY: "auto", maxHeight: "50vh" }}>
      <Typography variant="h6" gutterBottom>
        Project Details
      </Typography>
      <Grid container spacing={2}>
        <Grid size={12}>
          <Typography variant="body2">
            <strong>Name:</strong> {project.project_name}
          </Typography>
        </Grid>
        <Grid size={12}>
          <Typography variant="body2">
            <strong>Promoter:</strong> {project.promoter_name}
          </Typography>
        </Grid>
        <Grid size={12}>
          <Typography variant="body2">
            <strong>Status:</strong> {project.project_status}
          </Typography>
        </Grid>
        <Grid size={12}>
          <Typography variant="body2">
            <strong>RERA Registration:</strong>{" "}
            {project.rera_registration_number}
          </Typography>
        </Grid>
        <Grid size={12}>
          <Typography variant="body2">
            <strong>Water Source:</strong> {project.source_of_water}
          </Typography>
        </Grid>
        <Grid size={12}>
          <Typography variant="body2">
            <strong>Approving Authority:</strong> {project.approving_authority}
          </Typography>
        </Grid>
        <Grid size={12}>
          <Typography variant="body2">
            <strong>Start Date:</strong> {project.project_start_date}
          </Typography>
        </Grid>
        <Grid size={12}>
          <Typography variant="body2">
            <strong>Completion Date:</strong> {project.proposed_completion_date}
          </Typography>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ProjectDetails;
