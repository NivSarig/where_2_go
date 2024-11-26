import { styled } from "@mui/material";
import img from "./background.png";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

const Container = styled("div")({
  backgroundImage: `url(${img})`,
  backgroundSize: "100% 100%",
  height: "100vh",
  width: "100vw",
});

const BACKEND = process.env.BACKEND || "http://localhost:8000";

function LandingPage() {
  const [name, setName] = useState<string>("");
  const [code, setCode] = useState<string>("");

  const navigate = useNavigate();

  const onCreate = () => {
    fetch(
      `${BACKEND}/game?` +
        new URLSearchParams({
          location: "Tel Aviv",
        }),
      {
        method: "PUT",
      }
    ).then(async response => {
      const newGameState = await response.json();
      console.log("newly created game", newGameState);
      navigate("/map", { state: { name: name, code: newGameState.game_id } });
    });
  };

  return (
    <Container>
      <Select
        labelId='demo-simple-select-label'
        id='demo-simple-select'
        value={10}
        label='Age'
        // onChange={handleChange}
      >
        <MenuItem value={10}>Ten</MenuItem>
        <MenuItem value={20}>Twenty</MenuItem>
        <MenuItem value={30}>Thirty</MenuItem>
      </Select>

      <button disabled={!name} onClick={onCreate}>
        {" "}
        Create{" "}
      </button>
      <form
        onSubmit={() => {
          navigate("/map", { state: { name: name, code: code } });
        }}
      >
        <label>
          Name:
          <input
            type='text'
            value={name}
            onChange={e => {
              setName(e.target.value);
            }}
          />
        </label>
        <label>
          Code:
          <input
            type='text'
            value={code}
            onChange={e => {
              setCode(e.target.value);
            }}
          />
        </label>
        <input disabled={!name || !code} type='submit' value='Submit' />
      </form>
    </Container>
  );
}

export default LandingPage;
