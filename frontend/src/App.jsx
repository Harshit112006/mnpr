import AppRoutes
  from "./routes/AppRoutes";

import PWAStatus
  from "./components/pwa/PWAStatus";

import "./App.css";


function App() {

  return (
    <>

      <AppRoutes />

      <PWAStatus />

    </>
  );
}


export default App;
