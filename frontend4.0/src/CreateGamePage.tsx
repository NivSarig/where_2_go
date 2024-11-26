import { Box, styled, Typography } from "@mui/material";
import startGameButton from "./startGameButton.png";
import landingStageBackground from "./background.png";
import selectCityStageBackground from "./selectCityBackground.png";
import selectArrow from "./selectArrow.png";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import { Button } from "@mui/material";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { BACKEND } from "./backend";

const Container = styled("div")<{ backgroundImg: string }>(
  ({ backgroundImg }) => ({
    backgroundImage: `url(${backgroundImg})`,
    backgroundSize: "100% 100%",
    height: "100vh",
    width: "100vw",
    display: "flex",
    justifyContent: "center",
  })
);
const StyledSelect = styled(Select)({
  color: "white",
  backgroundColor: "#05aaff",
  borderStyle: "none",
  borderRadius: "45px",
  width: "315px",
  height: "75px",
  fontSize: "28px",
  fontWeight: 800,
  textTransform: "uppercase",
  boxShadow: "5px 5px 8px rgba(0, 0, 0, 0.3)",
  // transition: "transform 1s",
  "@-webkit-keyframes floatBubble": {
    "0%": {
      marginTop: "300px",
    },
    "100%": {
      marginTop: "0px",
    },
  },
  ":hover": {
    borderStyle: "none",
  },
  animation: "floatBubble 1.1s",
});
const StyledButton = styled(Button)(() => ({
  background: `url(${startGameButton})`,
  backgroundSize: "100%",
  border: "none",
  height: "140px",
  width: "140px",
  marginTop: "20px",
  "@keyframes pulse": {
    "0%": {
      transform: "scale(1)",
    },
    "50%": {
      transform: "scale(1.15)",
    },
    "100%": {
      transform: "scale(1)",
    },
  },
  animation: "pulse 1.6s infinite",
}));
const StyledContinueButton = styled(Button)(() => ({
  backgroundColor: "#05aaff",
  borderRadius: "45px",
  width: "315px",
  height: "75px",
  fontSize: "28px",
  fontWeight: 800,
  marginTop: "50px",
  boxShadow: "5px 5px 8px rgba(0, 0, 0, 0.3)",
  ":hover": {
    backgroundColor: "#05aaff",
  },
  "&:not(:hover)": {
    "@keyframes pulse": {
      "0%": {
        transform: "scale(1)",
      },
      "50%": {
        transform: "scale(1.15)",
      },
      "100%": {
        transform: "scale(1)",
      },
    },
    animation: "pulse 1.6s infinite",
  },
}));
const cities = ["London", "Tel Aviv", "New York", "San Francisco", "Paris"];

function CreateGamePage() {
  const [city, setCity] = useState<string>("");
  const [isLandingStage, setIsLandingStage] = useState<boolean>(true);
  const handleChange = (event: SelectChangeEvent) => {
    setCity(event.target.value);
  };

  const navigate = useNavigate();

  const onCreate = () => {
    fetch(
      `${BACKEND}/game?` +
        new URLSearchParams({
          location: city,
          random: "false",
        }),
      {
        method: "PUT",
      }
    ).then(async (response) => {
      const newGameState = await response.json();
      console.log("newly created game", newGameState);
      navigate("/map", {
        state: { name: "Human Player", code: newGameState.game_id },
      });
    });
  };
  return (
    <Container
      backgroundImg={
        isLandingStage ? landingStageBackground : selectCityStageBackground
      }
    >
      {isLandingStage ? (
        <Box width={"1000px"} marginTop={"58vh"}>
          <Typography
            textTransform={"uppercase"}
            fontWeight={800}
            fontSize={40}
            sx={{ color: "white", textAlign: "center" }}
            whiteSpace={"pre-wrap"}
            lineHeight={1.1}
          >
            {"Can you plan public transportation\nbetter than an algorithm?"}
          </Typography>
          <Typography
            fontWeight={500}
            fontSize={30}
            sx={{ color: "white", textAlign: "center" }}
            whiteSpace={"pre-wrap"}
            lineHeight={1.1}
            marginTop={3.5}
          >
            {
              "Play against the Optibus algorithm to plan\nthe best bus route between all the stops."
            }
          </Typography>
          <StyledContinueButton
            onClick={() => setIsLandingStage(false)}
            variant="contained"
          >
            START PLAYING
          </StyledContinueButton>
        </Box>
      ) : (
        <Box height={"91px"} width={"1000px"} marginTop={"48vh"}>
          <StyledSelect
            value={city}
            displayEmpty
            onChange={handleChange}
            IconComponent={() => (
              <img alt="arrow" src={selectArrow} style={{ width: "55px" }} />
              // <></>
            )}
          >
            <MenuItem value={""}>
              <em>Select city</em>
            </MenuItem>
            {cities.map((city) => (
              <MenuItem value={city}>{city}</MenuItem>
            ))}
          </StyledSelect>
          {city && (
            <>
              <Typography
                fontWeight={400}
                fontSize={30}
                sx={{ color: "white", textAlign: "center" }}
                whiteSpace={"pre-wrap"}
                lineHeight={1.1}
                marginTop={3.5}
              >
                {
                  "Click the bus stops in the order that creates the shortest route."
                }
              </Typography>
              <Typography
                fontWeight={400}
                fontSize={30}
                sx={{ color: "white", textAlign: "center" }}
                whiteSpace={"pre-wrap"}
                lineHeight={1.1}
                marginTop={3.5}
              >
                {
                  "When you finish, click “Submit” & compare your route\nwith the algorithm’s solution."
                }
              </Typography>
              <StyledButton onClick={onCreate}></StyledButton>
            </>
          )}
        </Box>
      )}
    </Container>
  );
}

export default CreateGamePage;
