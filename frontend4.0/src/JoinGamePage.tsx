import { styled } from "@mui/material";
import img from "./background.png";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import InputLabel from "@mui/material/InputLabel";
import { TextField, Button } from "@mui/material";
import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import disabledButton from "./joinDisabled.png";
import createButton from "./joinButton.png";

const Container = styled("div")({
  backgroundImage: `url(${img})`,
  backgroundSize: "100% 100%",
  height: "100vh",
  width: "100vw",
  display: "flex",
  justifyContent: "center",
  // alignItems: "center",
  // flexDirection: "column",
});
const ContentContainer = styled("div")({
  display: "flex",
  flexDirection: "column",
  marginTop: "400px",
  alignItems: "center",
});

const StyledButton = styled(Button)(({ disabled }) => ({
  background: `url(${disabled ? disabledButton : createButton})`,
  backgroundSize: "100%",
  border: "none",
  height: disabled ? "100px" : "140px",
  width: disabled ? "100px" : "140px",
  marginTop: disabled ? "70px" : "50px",
}));
function JoinGamePage() {
  const [URLSearchParams] = useSearchParams();
  const [name, setName] = useState<string>("");
  const [code, setCode] = useState<string>(URLSearchParams.get("code") || "");

  const handleCodeChange = (event) => {
    setCode(event.target.value);
  };
  const handleNameChange = (event) => {
    setName(event.target.value);
  };

  const navigate = useNavigate();

  const onCreate = () => {
    navigate("/map", { state: { name, code: code.toUpperCase() } });
  };
  return (
    <Container>
      <ContentContainer>
        <TextField
          sx={{
            backgroundColor: "white",
            borderRadius: "40px",
          }}
          autoComplete="off"
          label="Name"
          variant="filled"
          value={name}
          onChange={handleNameChange}
        />
        <TextField
          sx={{
            backgroundColor: "white",
            marginTop: "15px",
            borderRadius: "40px",
          }}
          autoComplete="off"
          label="Code"
          variant="filled"
          value={code}
          onChange={handleCodeChange}
        />

        <StyledButton
          disabled={!name || !code}
          onClick={onCreate}
        ></StyledButton>
      </ContentContainer>
    </Container>
  );
}

export default JoinGamePage;
