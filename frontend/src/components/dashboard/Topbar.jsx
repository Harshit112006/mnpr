import { useState } from "react";
import {
  useNavigate,
} from "react-router-dom";

import {
  Bell,
  Search,
  ChevronDown,
  Menu,
  LogOut,
  UserRound,
  Settings,
  Mail,
  Building2,
} from "lucide-react";

import {
  useAuth,
} from "../../context/AuthContext";

import {
  signOutUser,
} from "../../services/authService";


function Topbar({
  sidebarCollapsed,
  setSidebarCollapsed,
}) {
  const navigate =
    useNavigate();

  const {
    user,
    profile,
    profileLoading,
  } = useAuth();


  const [
    profileOpen,
    setProfileOpen,
  ] = useState(false);

  const [
    logoutLoading,
    setLogoutLoading,
  ] = useState(false);


  /* =====================================================
     USER INFORMATION
     ===================================================== */

  const fullName =
    profile?.full_name ||
    user?.user_metadata
      ?.full_name ||
    user?.user_metadata
      ?.name ||
    user?.email
      ?.split("@")[0] ||
    "BreedVision User";


  const email =
    profile?.email ||
    user?.email ||
    "";


  const role =
    profile?.role ||
    "user";


  const organization =
    profile?.organization ||
    "";


  const formattedRole =
    role
      .replaceAll(
        "_",
        " "
      )
      .replace(
        /\b\w/g,
        (character) =>
          character.toUpperCase()
      );


  const initials =
    fullName
      .split(" ")
      .filter(Boolean)
      .map(
        (part) =>
          part[0]
      )
      .join("")
      .slice(0, 2)
      .toUpperCase() ||
    "BV";


  /* =====================================================
     LOGOUT
     ===================================================== */

  const handleLogout =
    async () => {
      try {
        setLogoutLoading(
          true
        );

        await signOutUser();

        setProfileOpen(
          false
        );

        navigate(
          "/login",
          {
            replace: true,
          }
        );

      } catch (
        logoutError
      ) {
        console.error(
          "Logout error:",
          logoutError
        );

      } finally {
        setLogoutLoading(
          false
        );
      }
    };


  return (
    <header className="dashboard-topbar">

      {/* LEFT */}

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


      {/* RIGHT */}

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


        {/* PROFILE */}

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
                {profileLoading
                  ? "Loading..."
                  : fullName}
              </span>

              <p>
                {formattedRole}
              </p>

            </div>


            <ChevronDown
              size={17}
              className={
                `profile-dropdown-icon ${
                  profileOpen
                    ? "open"
                    : ""
                }`
              }
            />

          </button>


          {/* DROPDOWN */}

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


              {/* EMAIL */}

              <div className="profile-dropdown-email">

                <Mail size={14} />

                <span>
                  {email}
                </span>

              </div>


              {/* ORGANIZATION */}

              {organization && (
                <div className="profile-dropdown-email">

                  <Building2
                    size={14}
                  />

                  <span>
                    {organization}
                  </span>

                </div>
              )}


              <div className="profile-dropdown-divider" />


              {/* PROFILE */}

              <button
                type="button"
                className="profile-dropdown-item"
                onClick={() =>
                  navigate(
                    "/settings"
                  )
                }
              >
                <UserRound
                  size={16}
                />

                My Profile
              </button>


              {/* SETTINGS */}

              <button
                type="button"
                className="profile-dropdown-item"
                onClick={() =>
                  navigate(
                    "/settings"
                  )
                }
              >
                <Settings
                  size={16}
                />

                Settings
              </button>


              <div className="profile-dropdown-divider" />


              {/* LOGOUT */}

              <button
                type="button"
                className="profile-dropdown-item logout-item"
                onClick={
                  handleLogout
                }
                disabled={
                  logoutLoading
                }
              >
                <LogOut
                  size={16}
                />

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