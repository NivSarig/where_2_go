import React from "react";
import { Marker as GoogleMapsMarker } from "@react-google-maps/api";

const Marker = ({
  position,
  text,
  onClick,
  // onMouseOver,
  color,
}) => {
  return (
    <GoogleMapsMarker
      onClick={onClick}
      // onMouseOver={onMouseOver}
      position={position}
      zIndex={999}
      icon={{
        path: google.maps.SymbolPath.CIRCLE,
        scale: 15,
        strokeColor: color,
        fillColor: color,
        fillOpacity: 1,
      }}
      label={{
        text: text || "",
        color: "#271076",
        fontSize: "30px",
      }}
    />
  );
};

export default Marker;
