import React, { useRef, useEffect } from 'react';
import { useGoogleMap, Polyline as GoogleMapsPolyline } from '@react-google-maps/api';

const Polyline = ({ path, options }) => {
  const polylineRef = useRef(null);
  const map = useGoogleMap();

  useEffect(() => {
    if (path.length > 0 && map) {
      const polyline = new google.maps.Polyline({
        path: path.map((point) => ({
          lat: point.lat,
          lng: point.lng,
        })),
        ...options,
      });

      polyline.setMap(map);

      polylineRef.current = polyline;

      return () => {
        polylineRef.current.setMap(null);
      };
    }
  }, [path, options, map]);

  return path.length > 0 ? (
    <GoogleMapsPolyline
      path={path}
      options={options}
    />
  ) : null;
};

export default Polyline;