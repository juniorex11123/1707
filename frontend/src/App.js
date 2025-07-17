import React, { Suspense } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";

// Lazy loading komponentów dla lepszej wydajności
const HomePage = React.lazy(() => import("./components/HomePage"));
const PanelApp = React.lazy(() => import("./components/PanelApp"));

// Loading component
const LoadingSpinner = () => (
  <div className="min-h-screen flex items-center justify-center">
    <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
  </div>
);

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/panel/*" element={<PanelApp />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </div>
  );
}

export default App;