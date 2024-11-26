import React, { useState, useCallback, useEffect, useMemo } from "react";
import { GoogleMap, LoadScript } from "@react-google-maps/api";
import Marker from "./Marker";
import Polyline from "./Polyline";
import { useLocation } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import { Box, Typography, Button } from "@mui/material";
import { styled } from "@mui/system";
import mapHeader from "./mapHeader.png";

import { BACKEND } from "./backend";
const Header = styled("img")(() => ({
  height: "148px",
  width: "100vw",
  position: "absolute",
  top: 0,
  left: 0,
}));
const StyledBox = styled(Box)`
  position: absolute;
  bottom: 0px;
  width: 180px;
  box-sizing: border-box;
  left: 50%;
  transform: translateX(-50%);
  background-color: #fff;
  padding: 16px;
  border-radius: 8px 8px 0px 0px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const SubmitButton = styled(Button)`
  position: absolute;
  bottom: 20px;
  right: 20px;
  padding: 10px 20px;
  background: #f300b1;
  text-transform: none;
  color: white;
  border: none;
  border-radius: 50px;
  font-size: 24px;
  height: 75px;
  width: 153px;
  cursor: pointer;
  z-index: 999;
  @keyframes pulse {
    0% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.15);
    }
    100% {
      transform: scale(1);
    }
  }
  animation: pulse 1.6s infinite;
  :hover {
    background: #d60a9f;
  }
  &.Mui-disabled {
    color: rgba(0, 0, 0, 0.3);
    box-shadow: none;
    background-color: #8a8a8a;
    animation: none;
  }
`;

const ResetButton = styled(Button)`
  position: absolute;
  bottom: 20px;
  left: 20px;
  padding: 10px 20px;
  background-color: #271066;
  text-transform: none;
  color: white;
  border: none;
  border-radius: 50px;
  font-size: 24px;
  height: 75px;
  width: 153px;
  cursor: pointer;
  z-index: 999;
`;

// Define the bounding box coordinates for London
const londonBounds = {
  north: 51.5287718,
  south: 51.5073509,
  west: -0.1277583,
  east: -0.064657,
};
const someRandomMarkers: { lat: number; lng: number }[] = [];
for (let i = 0; i < 10; i++) {
  const lat =
    londonBounds.south +
    Math.random() * (londonBounds.north - londonBounds.south);
  const lng =
    londonBounds.west + Math.random() * (londonBounds.east - londonBounds.west);
  someRandomMarkers.push({ lat, lng });
}
const MapWithPolyline = () => {
  // const [markers, setMarkers] = useState<{ lat: number; lng: number }[]>([]);
  const navigate = useNavigate();
  const [polyline, setPolyline] = useState<{ lat: number; lng: number }[]>([]);
  const [pointsOrder, setPointsOrder] = useState<number[]>([]);
  const [isDrawing, setIsDrawing] = useState(false);
  const [isReady, setIsReady] = useState(false);
  const [totalDistance, setTotalDistance] = useState(0);
  const [totalMinutes, setTotalMinutes] = useState(0);
  const [markers, setMarkers] = useState([]);

  let location = useLocation();
  const [gameState, setGameState] = useState({} as any);
  useEffect(() => {
    console.log("joining", location.state);
    fetch(
      `${BACKEND}/game/${location.state.code}/contestant?name=${location.state.name}`,
      {
        method: "PUT",
      }
    ).then(async (response) => {
      if (!response.ok) {
        navigate("/");
        return;
      }
      const newGameState = await response.json();
      console.log("game state", newGameState);
      setGameState(newGameState);
      setMarkers(
        newGameState.location.coordinates.map((coord: [number, number]) => ({
          lat: coord[0],
          lng: coord[1],
        }))
      );

      // fetch(`${BACKEND}/game/${location.state.code}`, {
      //   method: "GET",
      // }).then(async response => {
      //   const newGameState = await response.json();
      //   console.log("game state", newGameState);
      //   setGameState(newGameState);
      // });
    });
  }, [location.state, location.state.code, navigate]);

  const onSubmit = () => {
    fetch(
      `${BACKEND}/game/${gameState.game_id}/submit?name=${location.state.name}`,
      {
        method: "PUT",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(pointsOrder),
      }
    ).then(() => {
      navigate("/LeadingBoard", { state: { code: gameState.game_id } });
    });
  };

  // // Starting the user path drawing
  // const onMarkerClick = useCallback(
  //   index => {
  //     setIsDrawing(true);
  //     setPointsOrder([index]);
  //     setPolyline([markers[index]]);
  //     setTotalDistance(0);
  //     setTotalMinutes(0);
  //   },
  //   [markers]
  // );

  const resetDrawing = useCallback((index) => {
    setIsDrawing(false);
    setPointsOrder([]);
    setPolyline([]);
    setTotalDistance(0);
    setTotalMinutes(0);
  }, []);

  const [directionsService, setDirectionsService] = useState(null);

  const getPointColor = useCallback(
    (index: number) => {
      if (pointsOrder.includes(index)) {
        return "#FF2C95";
      } else {
        return "grey";
      }
    },
    [pointsOrder]
  );

  const boundingBox = useMemo(() => {
    let north = -Infinity;
    let south = Infinity;
    let west = Infinity;
    let east = -Infinity;
    markers.forEach((marker) => {
      if (marker.lat > north) north = marker.lat;
      if (marker.lat < south) south = marker.lat;
      if (marker.lng < west) west = marker.lng;
      if (marker.lng > east) east = marker.lng;
    });
    return { north, south, west, east };
  }, [markers]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDirectionsService(new google.maps.DirectionsService());
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  const getRouteDistance = useCallback(
    async (originPoint, destinationPoint) => {
      try {
        const route = await new Promise((resolve, reject) => {
          directionsService.route(
            {
              origin: `${originPoint.lat},${originPoint.lng}`,
              destination: `${destinationPoint.lat},${destinationPoint.lng}`,
              travelMode: google.maps.TravelMode.WALKING,
            },
            (response, status) => {
              if (status === google.maps.DirectionsStatus.OK) {
                resolve(response.routes[0]);
              } else {
                reject(
                  new Error(`Directions request failed. Status: ${status}`)
                );
              }
            }
          );
        });

        //@ts-ignore
        const distance = route.legs[0].distance.value;
        //@ts-ignore
        const polyline = route.legs[0].steps
          .map((step) => {
            return step.lat_lngs;
          })
          .flat();

        //@ts-ignore
        const minutes = route.legs[0].duration.value / 60;

        return { distance, polyline, minutes };
      } catch (error) {
        console.error("Error:", error);
        return { distance: 0, polyline: [], minutes: 0 };
      }
    },
    [directionsService]
  );

  // const onMarkerHover = useCallback(
  //   async (index) => {
  //     console.log("index", index);
  //     console.log("marker", markers[index]);
  //     if (isDrawing && !pointsOrder.includes(index)) {
  //       const route = await getRouteDistance(
  //         markers[pointsOrder[pointsOrder.length - 1]],
  //         markers[index]
  //       );
  //       setPointsOrder((prevOrder) => [...prevOrder, index]);
  //       setTotalDistance((prevDistance) => prevDistance + route?.distance);
  //       setTotalMinutes((prevMinutes) => prevMinutes + route?.minutes);
  //       setPolyline((prevPath) => [...prevPath, ...route?.polyline]);
  //     }
  //   },
  //   [getRouteDistance, isDrawing, pointsOrder, markers]
  // );
  const onMarkerClick = useCallback(
    async (index) => {
      console.log("index", index);
      console.log("marker", markers[index]);
      if (pointsOrder.length === 0) {
        setIsDrawing(true);
        setPointsOrder([index]);
        setPolyline([markers[index]]);
      } else if (isDrawing && !pointsOrder.includes(index)) {
        setPointsOrder((prevOrder) => [...prevOrder, index]);
        const route = await getRouteDistance(
          markers[pointsOrder[pointsOrder.length - 1]],
          markers[index]
        );
        setTotalDistance((prevDistance) => prevDistance + route?.distance);
        setTotalMinutes((prevMinutes) => prevMinutes + route?.minutes);
        setPolyline((prevPath) => [...prevPath, ...route?.polyline]);
      }
    },
    [getRouteDistance, isDrawing, markers, pointsOrder]
  );

  const allPointsCovered = useCallback(() => {
    return pointsOrder.length === markers.length;
  }, [pointsOrder.length, markers]);

  const formatTime = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours} Hours, ${remainingMinutes} Minutes`;
  };

  const formatDistance = (distance: number): string => {
    const km = Math.floor(distance / 1000);
    const m = distance % 1000;
    return `${km} KM, ${m} M`;
  };

  const apiKey = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;
  return (
    <LoadScript googleMapsApiKey={apiKey}>
      <Header src={mapHeader} alt="Map Header" />
      <SubmitButton
        variant="contained"
        disabled={!allPointsCovered()}
        onClick={onSubmit}
        sx={{ marginRight: 1 }}
      >
        Submit
      </SubmitButton>
      <ResetButton
        variant="contained"
        color="primary"
        onClick={resetDrawing}
        sx={{ marginRight: 1 }}
      >
        Reset
      </ResetButton>
      <GoogleMap
        onLoad={() => setIsReady(true)}
        mapContainerStyle={{
          height: "calc(100vh - 148px)",
          width: "100%",
          marginTop: "148px",
        }}
        center={markers[0]} // Center on London
        zoom={12}
        options={{
          restriction: {
            latLngBounds: {
              north: boundingBox.north,
              south: boundingBox.south,
              west: boundingBox.west,
              east: boundingBox.east,
            },
          },
        }}
      >
        {
          // isReady &&
          markers.map((marker, index) => (
            <Marker
              onClick={() => onMarkerClick(index)}
              // onMouseOver={() => onMarkerHover(index)}
              key={index}
              position={marker}
              text={`${index + 1}`}
              color={getPointColor(index)}
            />
          ))
        }
        <Polyline
          path={polyline}
          options={{ strokeColor: "#FF2C95", strokeWeight: 8 }}
        />
        <StyledBox>
          <Typography variant="h6" gutterBottom>
            {formatDistance(totalDistance)}
          </Typography>
          <Typography variant="body1" gutterBottom>
            {formatTime(Math.round(totalMinutes))}
          </Typography>
          {allPointsCovered() && (
            <Typography variant="body1" color="error" gutterBottom>
              Game Over!
            </Typography>
          )}
        </StyledBox>
      </GoogleMap>
    </LoadScript>
  );
};

export default MapWithPolyline;
