import {
  useEffect,
  useState,
} from "react";

import {
  useNavigate,
} from "react-router-dom";

import {
  Building2,
  CheckCircle2,
  LoaderCircle,
  User,
  BriefcaseBusiness,
  AlertCircle,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";

import {
  useAuth,
} from "../../context/AuthContext";

import {
  updateUserProfile,
} from "../../services/profileService";

import "../../styles/CompleteProfile.css";


function CompleteProfile() {
  const navigate =
    useNavigate();

  const {
    user,
    profile,
    refreshProfile,
  } = useAuth();


  const [formData, setFormData] =
    useState({
      full_name: "",
      organization: "",
      role: "",
    });


  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");


  /* =====================================================
     PREFILL EXISTING INFORMATION
     ===================================================== */

  useEffect(() => {
    const defaultName =
      profile?.full_name ||
      user?.user_metadata?.full_name ||
      user?.user_metadata?.name ||
      "";

    const defaultOrganization =
      profile?.organization ||
      "";

    const defaultRole =
      profile?.role &&
      profile.role !== "user"
        ? profile.role
        : "";


    setFormData({
      full_name:
        defaultName,

      organization:
        defaultOrganization,

      role:
        defaultRole,
    });

  }, [
    profile,
    user,
  ]);


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


    if (!formData.full_name.trim()) {
      setError(
        "Please enter your full name."
      );

      return;
    }


    if (!formData.role) {
      setError(
        "Please select your role."
      );

      return;
    }


    if (!user?.id) {
      setError(
        "Unable to identify the current user."
      );

      return;
    }


    try {
      setLoading(true);


      await updateUserProfile(
        user.id,
        {
          full_name:
            formData.full_name.trim(),

          organization:
            formData.organization.trim() ||
            null,

          role:
            formData.role,
        }
      );


      await refreshProfile();


      setSuccess(
        "Profile completed successfully."
      );


      setTimeout(() => {
        navigate(
          "/dashboard",
          {
            replace: true,
          }
        );
      }, 700);

    } catch (
      profileError
    ) {
      console.error(
        "Profile completion error:",
        profileError
      );


      setError(
        profileError.message ||
        "Unable to complete your profile."
      );

    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="complete-profile-page">

      <div className="complete-profile-background">

        <div className="profile-glow profile-glow-one" />

        <div className="profile-glow profile-glow-two" />

      </div>


      <div className="complete-profile-container">

        {/* LEFT INFORMATION */}

        <section className="complete-profile-intro">

          <div className="complete-profile-badge">

            <ShieldCheck
              size={16}
            />

            PROFILE SETUP

          </div>


          <h1>
            One final step before
            entering BreedVision.
          </h1>


          <p>
            Tell us how you use the platform so
            BreedVision can personalize your
            livestock intelligence workspace.
          </p>


          <div className="profile-feature-list">

            <div>

              <CheckCircle2
                size={17}
              />

              <span>
                Personalized dashboard
              </span>

            </div>


            <div>

              <CheckCircle2
                size={17}
              />

              <span>
                Role-aware livestock workflows
              </span>

            </div>


            <div>

              <CheckCircle2
                size={17}
              />

              <span>
                Secure profile linked with your account
              </span>

            </div>

          </div>

        </section>


        {/* FORM */}

        <section className="complete-profile-card">

          <div className="complete-profile-heading">

            <span>
              BREEDVISION AI
            </span>

            <h2>
              Complete your profile
            </h2>

            <p>
              These details can be updated later
              from your profile settings.
            </p>

          </div>


          <form
            onSubmit={
              handleSubmit
            }
          >

            {/* FULL NAME */}

            <div className="complete-input-group">

              <label>
                Full name
              </label>

              <div className="complete-input-wrapper">

                <User
                  size={18}
                />

                <input
                  type="text"
                  name="full_name"
                  placeholder="Enter your full name"
                  value={
                    formData.full_name
                  }
                  onChange={
                    handleChange
                  }
                  required
                />

              </div>

            </div>


            {/* EMAIL */}

            <div className="complete-input-group">

              <label>
                Account email
              </label>

              <div className="complete-input-wrapper disabled-input">

                <span className="complete-email-symbol">
                  @
                </span>

                <input
                  type="email"
                  value={
                    user?.email || ""
                  }
                  disabled
                />

              </div>

              <small>
                Your authentication email cannot
                be changed here.
              </small>

            </div>


            {/* ROLE */}

            <div className="complete-input-group">

              <label>
                Your role
              </label>

              <div className="complete-input-wrapper">

                <BriefcaseBusiness
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

                  <option value="">
                    Select how you use BreedVision
                  </option>

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

            <div className="complete-input-group">

              <label>
                Organization
                <span>
                  Optional
                </span>
              </label>

              <div className="complete-input-wrapper">

                <Building2
                  size={18}
                />

                <input
                  type="text"
                  name="organization"
                  placeholder="Farm, university or organization"
                  value={
                    formData.organization
                  }
                  onChange={
                    handleChange
                  }
                />

              </div>

            </div>


            {/* ERROR */}

            {error && (

              <div className="complete-profile-message error">

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

              <div className="complete-profile-message success">

                <CheckCircle2
                  size={17}
                />

                <span>
                  {success}
                </span>

              </div>

            )}


            {/* SUBMIT */}

            <button
              type="submit"
              className="complete-profile-submit"
              disabled={
                loading
              }
            >

              {loading ? (

                <>
                  <LoaderCircle
                    size={18}
                    className="complete-profile-spinner"
                  />

                  Saving Profile...
                </>

              ) : (

                <>
                  Complete Profile

                  <ArrowRight
                    size={18}
                  />
                </>

              )}

            </button>

          </form>

        </section>

      </div>

    </div>
  );
}


export default CompleteProfile;