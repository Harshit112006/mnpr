import {
  Bell,
  Search,
  ChevronDown,
  Menu,
} from "lucide-react";

function Topbar({ sidebarCollapsed, setSidebarCollapsed }) {
  return (
    <header className="dashboard-topbar">
      <div className="topbar-left">
        <button
          type="button"
          className="mobile-menu-button"
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        >
          <Menu size={21} />
        </button>

        <div className="topbar-search">
          <Search size={18} />

          <input
            type="text"
            placeholder="Search animals, detections, farmers..."
          />

          <span>⌘ K</span>
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

        <button
          type="button"
          className="profile-button"
        >
          <div className="profile-avatar">
            H
          </div>

          <div className="profile-information">
            <span>Harshit</span>
            <p>Project Admin</p>
          </div>

          <ChevronDown
            size={17}
            className="profile-dropdown-icon"
          />
        </button>
      </div>
    </header>
  );
}

export default Topbar;