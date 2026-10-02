import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Bell,
  Search,
  ChevronDown,
  Menu,
  LogOut,
  UserRound,
  Settings,
  Mail,
} from "lucide-react";

import { useAuth } from "../../context/AuthContext";

import { signOutUser } from "../../services/authService";


function Topbar({
  sidebarCollapsed,
  setSidebarCollapsed,
}) {
  const navigate = useNavigate();

  const { user } = useAuth();

  const [profileOpen, setProfileOpen] =
    useState(false);

  const [logoutLoading, setLogoutLoading] =
    useState(false);


  const metadata =
    user?.user_metadata || {};


  const fullName =
    metadata.full_name ||
    user?.email?.split("@")[0] ||
    "BreedVision User";


  const role =
    metadata.role ||
    "user";


  const email =
    user?.email || "";


  const formattedRole =
    role
      .replaceAll("_", " ")
      .replace(/\b\w/g, (character) =>
        character.toUpperCase()
      );


  const initials = fullName
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();


  const handleLogout = async () => {
    try {
      setLogoutLoading(true);

      await signOutUser();

      setProfileOpen(false);

      navigate(
        "/login",
        {
          replace: true,
        }
      );

    } catch (logoutError) {
      console.error(
        "Logout error:",
        logoutError
      );

    } finally {
      setLogoutLoading(false);
    }
  };


  return (
    <header className="dashboard-topbar">

      <div className="topbar-left">

        <button
          type="button"
          className="mobile-menu-button"
          onClick={() =>
            setSidebarCollapsed(
              !sidebarCollapsed
            )
          }
        >
          <Menu size={21} />
        </button>


        <div className="topbar-search">

          <Search size={18} />

          <input
            type="text"
            placeholder="Search animals, detections, farmers..."
          />

          <span>
            ⌘ K
          </span>

        </div>

      </div>


      <div className="topbar-right">

        <button
          type="button"
          className="topbar-icon-button"
          title="Notifications"
        >
          <Bell size={20} />

          <span className="notification-indicator" />
        </button>


        <div className="topbar-divider" />


        <div className="profile-menu-wrapper">

          <button
            type="button"
            className="profile-button"
            onClick={() =>
              setProfileOpen(
                !profileOpen
              )
            }
          >

            <div className="profile-avatar">
              {initials}
            </div>


            <div className="profile-information">

              <span>
                {fullName}
              </span>

              <p>
                {formattedRole}
              </p>

            </div>


            <ChevronDown
              size={17}
              className={`profile-dropdown-icon ${
                profileOpen
                  ? "open"
                  : ""
              }`}
            />

          </button>


          {profileOpen && (

            <div className="profile-dropdown">

              <div className="profile-dropdown-header">

                <div className="profile-dropdown-avatar">
                  {initials}
                </div>


                <div>

                  <strong>
                    {fullName}
                  </strong>

                  <span>
                    {formattedRole}
                  </span>

                </div>

              </div>


              <div className="profile-dropdown-email">

                <Mail size={14} />

                <span>
                  {email}
                </span>

              </div>


              <div className="profile-dropdown-divider" />


              <button
                type="button"
                className="profile-dropdown-item"
              >
                <UserRound size={16} />

                My Profile
              </button>


              <button
                type="button"
                className="profile-dropdown-item"
                onClick={() =>
                  navigate("/settings")
                }
              >
                <Settings size={16} />

                Settings
              </button>


              <div className="profile-dropdown-divider" />


              <button
                type="button"
                className="profile-dropdown-item logout-item"
                onClick={handleLogout}
                disabled={logoutLoading}
              >
                <LogOut size={16} />

                {logoutLoading
                  ? "Signing out..."
                  : "Sign Out"}
              </button>

            </div>

          )}

        </div>

      </div>

    </header>
  );
}


export default Topbar;