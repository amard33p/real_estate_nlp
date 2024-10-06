export interface Project {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
}

export interface ProjectDetails {
  project_name: string;
  promoter_name: string;
  project_status: string;
  rera_registration_number: string;
  source_of_water: string;
  approving_authority: string;
  project_start_date: string;
  proposed_completion_date: string;
}
