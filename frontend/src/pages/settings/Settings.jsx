import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  AlertCircle,
  Building2,
  CalendarDays,
  CheckCircle2,
  LoaderCircle,
  Mail,
  Save,
  ShieldCheck,
  User,
  UserRoundCog,
} from "lucide-react";

import {
  useAuth,
} from "../../context/AuthContext";

import {
  updateUserProfile,
} from "../../services/profileService";

import "../../styles/Settings.css";


function Settings() {
  const {
    user,
    profile,
    profileLoading,
    refreshProfile,
  } = useAuth();


  const [formData, setFormData] =
    useState({
      full_name: "",
      role: "",
      organization: "",
    });


  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");


  /* =====================================================
     LOAD CURRENT PROFILE VALUES
     ===================================================== */

  useEffect(() => {
    if (!profile) {
      return;
    }

    setFormData({
      full_name:
        profile.full_name || "",

      role:
        profile.role || "user",

      organization:
        profile.organization || "",
    });

  }, [profile]);


  /* =====================================================
     FORMATTED VALUES
     ===================================================== */

  const formattedRole = useMemo(() => {
    const role =
      profile?.role || "user";

    return role
      .replaceAll("_", " ")
      .replace(
        /\b\w/g,
        (character) =>
          character.toUpperCase()
      );
  }, [profile]);


  const displayName =
    profile?.full_name ||
    user?.user_metadata?.full_name ||
    user?.user_metadata?.name ||
    user?.email?.split("@")[0] ||
    "BreedVision User";


  const initials =
    displayName
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


  const avatarUrl =
    profile?.avatar_url ||
    user?.user_metadata?.avatar_url ||
    user?.user_metadata?.picture ||
    "";


  const formattedCreatedAt =
    profile?.created_at
      ? new Date(
          profile.created_at
        ).toLocaleDateString(
          "en-IN",
          {
            day: "2-digit",
            month: "short",
            year: "numeric",
          }
        )
      : "—";


  /* =====================================================
     INPUT CHANGE
     ===================================================== */

  const handleChange = (
    event
  ) => {
    const {
      name,
      value,
    } = event.target;


    setFormData(
      (previous) => ({
        ...previous,

        [name]:
          value,
      })
    );


    setError("");
    setSuccess("");
  };


  /* =====================================================
     SAVE PROFILE
     ===================================================== */

  const handleSubmit = async (
    event
  ) => {
    event.preventDefault();

    setError("");
    setSuccess("");


    if (!user?.id) {
      setError(
        "Unable to identify the current user."
      );

      return;
    }


    if (
      !formData.full_name.trim()
    ) {
      setError(
        "Full name cannot be empty."
      );

      return;
    }


    if (!formData.role) {
      setError(
        "Please select your role."
      );

      return;
    }


    try {
      setSaving(true);


      await updateUserProfile(
        user.id,
        {
          full_name:
            formData.full_name.trim(),

          role:
            formData.role,

          organization:
            formData.organization.trim() ||
            null,
        }
      );


      await refreshProfile();


      setSuccess(
        "Your BreedVision profile has been updated successfully."
      );

    } catch (
      profileError
    ) {
      console.error(
        "Profile update error:",
        profileError
      );


      setError(
        profileError.message ||
        "Unable to update your profile."
      );

    } finally {
      setSaving(false);
    }
  };


  /* =====================================================
     LOADING
     ===================================================== */

  if (
    profileLoading &&
    !profile
  ) {
    return (
      <div className="settings-loading">

        <LoaderCircle
          size={30}
          className="settings-spinner"
        />

        <span>
          Loading your profile...
        </span>

      </div>
    );
  }


  return (
    <div className="settings-page">

      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <div className="settings-page-header">

        <div>

          <span className="settings-eyebrow">
            ACCOUNT MANAGEMENT
          </span>

          <h1>
            Profile Settings
          </h1>

          <p>
            Manage your personal information and
            BreedVision account preferences.
          </p>

        </div>


        <div className="settings-secure-badge">

          <ShieldCheck
            size={17}
          />

          Secure Profile

        </div>

      </div>


      {/* =====================================================
          CONTENT
      ===================================================== */}

      <div className="settings-grid">

        {/* ===================================================
            PROFILE SUMMARY
        =================================================== */}

        <aside className="settings-profile-card">

          <div className="settings-profile-avatar-wrapper">

            {avatarUrl ? (

              <img
                src={avatarUrl}
                alt={displayName}
                className="settings-profile-image"
              />

            ) : (

              <div className="settings-profile-avatar">
                {initials}
              </div>

            )}

          </div>


          <h2>
            {displayName}
          </h2>


          <span className="settings-role-badge">
            {formattedRole}
          </span>


          <div className="settings-profile-divider" />


          <div className="settings-profile-detail">

            <Mail
              size={16}
            />

            <div>

              <span>
                Email
              </span>

              <strong>
                {user?.email || "—"}
              </strong>

            </div>

          </div>


          <div className="settings-profile-detail">

            <Building2
              size={16}
            />

            <div>

              <span>
                Organization
              </span>

              <strong>
                {profile?.organization ||
                  "Not specified"}
              </strong>

            </div>

          </div>


          <div className="settings-profile-detail">

            <CalendarDays
              size={16}
            />

            <div>

              <span>
                Member since
              </span>

              <strong>
                {formattedCreatedAt}
              </strong>

            </div>

          </div>


          <div className="settings-profile-note">

            <ShieldCheck
              size={16}
            />

            <p>
              Your profile is protected using
              Supabase authentication and
              row-level security.
            </p>

          </div>

        </aside>


        {/* ===================================================
            EDIT PROFILE
        =================================================== */}

        <section className="settings-form-card">

          <div className="settings-section-heading">

            <div className="settings-section-icon">

              <UserRoundCog
                size={20}
              />

            </div>


            <div>

              <h2>
                Personal Information
              </h2>

              <p>
                Update the details associated with
                your BreedVision profile.
              </p>

            </div>

          </div>


          <form
            onSubmit={
              handleSubmit
            }
          >

            {/* FULL NAME */}

            <div className="settings-input-group">

              <label>
                Full Name
              </label>

              <div className="settings-input-wrapper">

                <User
                  size={18}
                />

                <input
                  type="text"
                  name="full_name"
                  value={
                    formData.full_name
                  }
                  onChange={
                    handleChange
                  }
                  placeholder="Enter your full name"
                  required
                />

              </div>

            </div>


            {/* EMAIL */}

            <div className="settings-input-group">

              <label>
                Email Address
              </label>

              <div className="settings-input-wrapper settings-disabled-input">

                <Mail
                  size={18}
                />

                <input
                  type="email"
                  value={
                    user?.email || ""
                  }
                  disabled
                />

              </div>

              <small>
                Email changes are disabled here
                because this address is linked to
                your authentication account.
              </small>

            </div>


            {/* ROLE */}

            <div className="settings-input-group">

              <label>
                Role
              </label>

              <div className="settings-input-wrapper">

                <UserRoundCog
                  size={18}
                />

                <select
                  name="role"
                  value={
                    formData.role
                  }
                  onChange={
                    handleChange
                  }
                  required
                >

                  <option value="field_worker">
                    Field Worker
                  </option>

                  <option value="farmer">
                    Farmer
                  </option>

                  <option value="veterinarian">
                    Veterinarian
                  </option>

                  <option value="researcher">
                    Researcher
                  </option>

                  <option value="student">
                    Student / Research Team
                  </option>

                </select>

              </div>

            </div>


            {/* ORGANIZATION */}

            <div className="settings-input-group">

              <label>
                Organization

                <span>
                  Optional
                </span>
              </label>

              <div className="settings-input-wrapper">

                <Building2
                  size={18}
                />

                <input
                  type="text"
                  name="organization"
                  value={
                    formData.organization
                  }
                  onChange={
                    handleChange
                  }
                  placeholder="Farm, university or organization"
                />

              </div>

            </div>


            {/* ERROR */}

            {error && (

              <div className="settings-message settings-error">

                <AlertCircle
                  size={17}
                />

                <span>
                  {error}
                </span>

              </div>

            )}


            {/* SUCCESS */}

            {success && (

              <div className="settings-message settings-success">

                <CheckCircle2
                  size={17}
                />

                <span>
                  {success}
                </span>

              </div>

            )}


            {/* SAVE */}

            <div className="settings-form-actions">

              <button
                type="submit"
                className="settings-save-button"
                disabled={
                  saving
                }
              >

                {saving ? (

                  <>
                    <LoaderCircle
                      size={18}
                      className="settings-spinner"
                    />

                    Saving Changes...
                  </>

                ) : (

                  <>
                    <Save
                      size={18}
                    />

                    Save Changes
                  </>

                )}

              </button>

            </div>

          </form>

        </section>

      </div>

    </div>
  );
}


export default Settings;