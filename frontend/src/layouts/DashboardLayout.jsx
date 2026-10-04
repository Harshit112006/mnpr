import {
  useState,
} from "react";

import {
  Outlet,
} from "react-router-dom";

import Sidebar
  from "../components/dashboard/Sidebar";

import Topbar
  from "../components/dashboard/Topbar";

import "../styles/Dashboard.css";
import "../styles/Mobile.css";


function DashboardLayout() {

  const [
    sidebarCollapsed,
    setSidebarCollapsed,
  ] = useState(
    () =>
      window.innerWidth <= 560
  );


  return (
    <div
      className={
        `dashboard-layout ${
          sidebarCollapsed
            ? "sidebar-collapsed"
            : ""
        }`
      }
    >

      <Sidebar
        collapsed={
          sidebarCollapsed
        }
        setCollapsed={
          setSidebarCollapsed
        }
      />


      {
        !sidebarCollapsed && (

          <button
            type="button"
            className="mobile-sidebar-backdrop"
            aria-label="Close navigation"
            onClick={() =>
              setSidebarCollapsed(
                true
              )
            }
          />

        )
      }


      <div className="dashboard-main">

        <Topbar
          sidebarCollapsed={
            sidebarCollapsed
          }
          setSidebarCollapsed={
            setSidebarCollapsed
          }
        />


        <main className="dashboard-content">

          <Outlet />

        </main>

      </div>

    </div>
  );
}


export default DashboardLayout;