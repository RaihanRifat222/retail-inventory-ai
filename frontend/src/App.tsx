import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Forecast from "./pages/Forecast";
import LossPrevention from "./pages/LossPrevention";
import Replenishment from "./pages/Replenishment";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/forecast" element={<Forecast />} />
          <Route path="/loss-prevention" element={<LossPrevention />} />
          <Route path="/replenishment" element={<Replenishment />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
