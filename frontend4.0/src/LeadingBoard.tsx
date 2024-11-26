import { Box, styled, Typography } from "@mui/material";
import img from "./scoreBoardBackground.png";
import QRCode from "./QRCode.png";
import { ReactComponent as AvatarIcon } from "./algo_avatar.svg";
import { ReactComponent as PlayerAvatar } from "./playerAvatar.svg";
import { useEffect, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from "@mui/material";
import { useLocation } from "react-router-dom";
import { BACKEND } from "./backend";

interface Data {
  rank: number;
  name: string;
  time: string; // duration
  distance: string;
  link: string;
}

type Contestant = {
  name: string;
  distance: number;
  duration: string;
  coordinates: [number[]];
};

const coordinatesToLink = (coordinates: [number[]]) => {
  return (
    "https://www.google.com/maps/dir/" +
    coordinates.map((c) => c.join(",")).join("/") +
    "/data=!3m1!4b1!4m2!4m1!3e2"
  );
};

const createData = (
  rank: number,
  name: string,
  duration: string,
  distance: string,
  coordinates: [number[]]
): Data => {
  const link = coordinatesToLink(coordinates);

  return {
    rank,
    name,
    time: `${duration.split(":")[0]} Hours, ${duration.split(":")[1]} Minutes`,
    distance,
    link,
  };
};

const Container = styled("div")({
  backgroundImage: `url(${img})`,
  backgroundSize: "100% 100%",
  height: "100vh",
  width: "100vw",
  display: "flex",
  justifyContent: "center",
  alignItems: "flex-start",
});
const QRCodeSection = styled("img")(() => ({
  marginTop: "10px",
  width: "768px",
}));

const HeaderTableCell = styled(TableCell)({
  fontWeight: "bold",
  backgroundColor: "transparent",
  color: "white",
  textTransform: "uppercase",
  borderBottom: "none",
});

const PinkTableCell = styled(TableCell)({
  fontWeight: "bold",
  color: "#f300b1",
  fontSize: "26px",
  borderBottom: "none",
});
const WhiteTableCell = styled(TableCell)({
  fontWeight: "bold",
  color: "white",
  fontSize: "26px",
  borderBottom: "none",
});

function LeadingBoard() {
  let location = useLocation();
  const [gameState, setGameState] = useState({} as any);
  const [leaderBoard, setLeaderBoard] = useState<Data[]>([]);
  useEffect(() => {
    const poll = () => {
      fetch(`${BACKEND}/game/${location.state.code}`, {
        method: "GET",
      })
        .then(async (response) => {
          const newGameState = await response.json();
          console.log("game state", newGameState);
          setGameState(newGameState);
          const sorted = Object.values(newGameState.contestants).sort(
            (a: Contestant, b: Contestant) => {
              return a.distance - b.distance;
            }
          );
          if (sorted.length !== leaderBoard.length) {
            setLeaderBoard(
              sorted
                .filter((c: Contestant) => c.distance !== undefined)
                .map((c: Contestant, i) => {
                  return createData(
                    i + 1,
                    c.name,
                    c.duration,
                    c.distance?.toString(),
                    c.coordinates
                  );
                })
            );
          }
        })
        .catch((error) => {
          console.log("failed to get response", error);
          alert("Lost connection with the server");
        });
    };
    poll();
    setInterval(poll, 3000);
  }, [leaderBoard.length, location.state.code]);

  const algoTime = `${gameState?.solution?.duration.split(":")[0]} Hours, ${
    gameState?.solution?.duration.split(":")[1]
  } Minutes`;
  const algoDistance = gameState?.solution?.distance;
  const algoLink = coordinatesToLink(gameState?.solution?.coordinates || []);

  return (
    <Container>
      <Box marginTop="25vh">
        <Typography
          textTransform={"uppercase"}
          fontWeight={800}
          fontSize={36}
          sx={{ color: "white", textAlign: "center" }}
          whiteSpace={"pre-wrap"}
          lineHeight={1.1}
        >
          {"Did you beat the algorithm?"}
        </Typography>
        <TableContainer sx={{ marginTop: "16px" }}>
          <Table
            stickyHeader
            aria-label="simple table"
            sx={{ borderCollapse: "separate", borderSpacing: "0px 10px" }}
          >
            <TableHead>
              <TableRow
                component={Paper}
                sx={{ backgroundColor: "transparent", boxShadow: "none" }}
              >
                <HeaderTableCell></HeaderTableCell>
                <HeaderTableCell></HeaderTableCell>
                <HeaderTableCell>Route Time</HeaderTableCell>
                <HeaderTableCell>Route Distance</HeaderTableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow
                sx={{
                  backgroundColor: "#1e0742",
                  borderRadius: "50px",
                }}
              >
                <TableCell
                  sx={{
                    borderRadius: "50px 0px 0px 50px",
                    borderBottom: "none",
                  }}
                >
                  <AvatarIcon
                    style={{
                      height: "50px",
                      float: "left",
                    }}
                  />
                </TableCell>
                <WhiteTableCell>Optibus Algorithm</WhiteTableCell>
                <PinkTableCell>{algoTime}</PinkTableCell>
                <PinkTableCell
                  sx={{
                    borderRadius: "0px 50px 50px 0px",
                  }}
                >
                  <a href={algoLink} style={{ color: "inherit" }}>
                    {`${algoDistance} KM`}
                  </a>
                </PinkTableCell>
              </TableRow>
              {leaderBoard.map((row, index) => (
                <TableRow
                  key={row.name}
                  sx={{
                    backgroundColor: "#1e0742",
                    borderRadius: "50px",
                  }}
                >
                  <TableCell
                    component="th"
                    scope="row"
                    sx={{
                      borderRadius: "50px 0px 0px 50px",
                      borderBottom: "none",
                    }}
                  >
                    <PlayerAvatar
                      color="white"
                      style={{
                        height: "50px",
                        width: "50px",
                        float: "left",
                      }}
                    ></PlayerAvatar>
                  </TableCell>
                  <WhiteTableCell>{row.name}</WhiteTableCell>
                  <PinkTableCell>{row.time}</PinkTableCell>
                  <PinkTableCell
                    sx={{
                      borderRadius: "0px 50px 50px 0px",
                      paddingRight: "30px",
                    }}
                  >
                    <a
                      href={row.link}
                      style={{ color: "inherit" }}
                    >{`${row.distance} KM`}</a>
                  </PinkTableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <QRCodeSection src={QRCode}></QRCodeSection>
      </Box>
    </Container>
  );
}

export default LeadingBoard;
