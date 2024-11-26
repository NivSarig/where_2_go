import React from "react";
import "./App.css";
import MapWithPolyline from "./MapWithPolyline";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import LeadingBoard from "./LeadingBoard";
import CreateGamePage from "./CreateGamePage";

function App() {
  return (
    <div className="App">
      <Router>
        <Routes>
          <Route path="/map" element={<MapWithPolyline />}></Route>
          <Route path="/" element={<CreateGamePage />}></Route>
          <Route path="/LeadingBoard" element={<LeadingBoard />}></Route>
        </Routes>
      </Router>
    </div>
  );
}

export default App;
