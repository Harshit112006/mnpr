import {
  LayoutDashboard,
  ScanSearch,
  Beef,
  Users,
  History,
  ClipboardCheck,
  ChartNoAxesCombined,
  FileText,
  Bell,
  Settings,
  PanelLeftClose,
  PanelLeftOpen,
  Bot,
} from "lucide-react";

import {
  NavLink,
} from "react-router-dom";


const navigationItems = [

  {
    name: "Dashboard",
    icon: LayoutDashboard,
    path: "/dashboard",
  },

  {
    name: "AI Detection",
    icon: ScanSearch,
    path: "/detection",
  },

  {
    name: "Animals",
    icon: Beef,
    path: "/animals",
  },

  {
    name: "Farmers",
    icon: Users,
    path: "/farmers",
  },

  {
    name: "History",
    icon: History,
    path: "/history",
  },

  {
    name: "Review Center",
    icon: ClipboardCheck,
    path: "/review",
  },

  {
    name: "Analytics",
    icon: ChartNoAxesCombined,
    path: "/analytics",
  },

  {
    name: "Reports",
    icon: FileText,
    path: "/reports",
  },

];


const bottomItems = [

  {
    name: "AI Assistant",
    icon: Bot,
    path: "/assistant",
  },

  {
    name: "Alerts",
    icon: Bell,
    path: "/alerts",
  },

  {
    name: "Settings",
    icon: Settings,
    path: "/settings",
  },

];


function Sidebar({
  collapsed,
  setCollapsed,
}) {

  const handleNavigation =
    () => {

      if (
        window.innerWidth <=
        560
      ) {

        setCollapsed(
          true
        );
      }
    };


  const renderNavigationItem =
    (
      item
    ) => {

      const Icon =
        item.icon;


      return (
        <NavLink
          key={
            item.name
          }
          to={
            item.path
          }
          onClick={
            handleNavigation
          }
          className={({
            isActive,
          }) =>
            `sidebar-nav-item ${
              isActive
                ? "active"
                : ""
            }`
          }
          title={
            collapsed
              ? item.name
              : ""
          }
        >

          <Icon
            size={20}
          />

          {
            !collapsed && (
              <span>
                {item.name}
              </span>
            )
          }

        </NavLink>
      );
    };


  return (
    <aside
      className={
        `dashboard-sidebar ${
          collapsed
            ? "collapsed"
            : ""
        }`
      }
    >

      <div className="sidebar-header">

        <div className="sidebar-brand">

          <div className="sidebar-logo">

            <ScanSearch
              size={23}
            />

          </div>


          {
            !collapsed && (

              <div className="sidebar-brand-text">

                <h2>
                  BreedVision
                </h2>

                <span>
                  AI Platform
                </span>

              </div>

            )
          }

        </div>


        <button
          type="button"
          className="sidebar-collapse-button"
          onClick={() =>
            setCollapsed(
              !collapsed
            )
          }
          title={
            collapsed
              ? "Expand sidebar"
              : "Collapse sidebar"
          }
        >

          {
            collapsed
              ? (
                <PanelLeftOpen
                  size={19}
                />
              )
              : (
                <PanelLeftClose
                  size={19}
                />
              )
          }

        </button>

      </div>


      <div className="sidebar-label">

        {
          !collapsed && (
            <span>
              WORKSPACE
            </span>
          )
        }

      </div>


      <nav className="sidebar-navigation">

        {
          navigationItems.map(
            renderNavigationItem
          )
        }

      </nav>


      <div className="sidebar-spacer" />


      <div className="sidebar-label">

        {
          !collapsed && (
            <span>
              SYSTEM
            </span>
          )
        }

      </div>


      <nav className="sidebar-navigation sidebar-bottom-navigation">

        {
          bottomItems.map(
            renderNavigationItem
          )
        }

      </nav>


      <div className="sidebar-status">

        <div className="status-dot" />


        {
          !collapsed && (

            <div>

              <span>
                System Status
              </span>

              <p>
                All services operational
              </p>

            </div>

          )
        }

      </div>

    </aside>
  );
}


export default Sidebar;