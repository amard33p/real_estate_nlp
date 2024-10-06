import React, { useState, useEffect } from "react";
import {
  Box,
  TextField,
  Button,
  CircularProgress,
  Container,
} from "@mui/material";
import { TypeAnimation } from "react-type-animation";
import axios from "axios";
import { Project } from "../types";

interface SearchFormProps {
  setProjects: React.Dispatch<React.SetStateAction<Project[]>>;
}

const SearchForm: React.FC<SearchFormProps> = ({ setProjects }) => {
  const [query, setQuery] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isTyping, setIsTyping] = useState<boolean>(true);
  const [isFocused, setIsFocused] = useState<boolean>(false);

  useEffect(() => {
    axios.defaults.baseURL = "http://localhost:5000";
  }, []);

  const sampleQueries = [
    "Projects launched in 2022 near Electronic City",
    "Projects with bwssb water source near Marathahalli",
    "Projects by Prestige Group",
    "Projects launched after 2022 with land area greater than 8000",
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await axios.post<Project[]>("/api/projects", { query });
      setProjects(response.data);
    } catch (error) {
      console.error("Error fetching projects:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ my: 4 }}>
      <Box
        component="form"
        onSubmit={handleSubmit}
        sx={{ display: "flex", alignItems: "center", justifyContent: "center" }}
      >
        <Box sx={{ position: "relative", flexGrow: 1, mr: 2 }}>
          <TextField
            fullWidth
            required
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setIsTyping(false);
            }}
            onFocus={() => {
              setIsFocused(true);
              setIsTyping(false);
            }}
            onBlur={() => {
              setIsFocused(false);
              setIsTyping(query.length === 0);
            }}
            placeholder={isTyping ? "" : "Enter your search query"}
            variant="outlined"
            size="medium"
          />
          {isTyping && !isFocused && query.length === 0 && (
            <Box
              sx={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                display: "flex",
                alignItems: "center",
                pl: 2,
                pointerEvents: "none",
              }}
            >
              <TypeAnimation
                sequence={[
                  ...sampleQueries.flatMap((q) => [q, 1000]),
                  () => setIsTyping(true),
                ]}
                wrapper="span"
                cursor={true}
                repeat={Infinity}
                style={{ display: "inline-block" }}
                speed={75}
              />
            </Box>
          )}
        </Box>
        <Button
          type="submit"
          variant="contained"
          disabled={isLoading}
          size="large"
          sx={{ height: "56px", minWidth: "120px" }} // Match the height of the TextField
        >
          {isLoading ? <CircularProgress size={24} /> : "Search"}
        </Button>
      </Box>
    </Container>
  );
};

export default SearchForm;
