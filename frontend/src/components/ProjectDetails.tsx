import React from "react";
import { Card, CardContent, Typography, Grid } from "@mui/material";
import { ProjectDetails as ProjectDetailsType } from "../types";

interface ProjectDetailsProps {
  project: ProjectDetailsType;
}

const ProjectDetails: React.FC<ProjectDetailsProps> = ({ project }) => {
  return (
    <Card sx={{ mt: 2 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Project Details
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="body1">
              <strong>Name:</strong> {project.project_name}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body1">
              <strong>Promoter:</strong> {project.promoter_name}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body1">
              <strong>Status:</strong> {project.project_status}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body1">
              <strong>RERA Registration:</strong>{" "}
              {project.rera_registration_number}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body1">
              <strong>Water Source:</strong> {project.source_of_water}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body1">
              <strong>Approving Authority:</strong>{" "}
              {project.approving_authority}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body1">
              <strong>Start Date:</strong> {project.project_start_date}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body1">
              <strong>Completion Date:</strong>{" "}
              {project.proposed_completion_date}
            </Typography>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default ProjectDetails;
