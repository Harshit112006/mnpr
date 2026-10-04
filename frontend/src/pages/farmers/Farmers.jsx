import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  AlertCircle,
  Edit3,
  LoaderCircle,
  MapPin,
  Phone,
  Plus,
  RefreshCw,
  Search,
  Trash2,
  UserRound,
  Users,
  X,
} from "lucide-react";

import {
  createFarmer,
  deleteFarmer,
  getFarmers,
  updateFarmer,
} from "../../services/phase9/farmerService";

import "../../styles/Farmers.css";


const EMPTY_FORM = {
  full_name: "",
  phone: "",
  email: "",
  village: "",
  district: "",
  state: "",
  postal_code: "",
  notes: "",
};


function Farmers() {

  const [
    farmers,
    setFarmers,
  ] = useState([]);


  const [
    form,
    setForm,
  ] = useState(
    EMPTY_FORM
  );


  const [
    search,
    setSearch,
  ] = useState("");


  const [
    loading,
    setLoading,
  ] = useState(true);


  const [
    saving,
    setSaving,
  ] = useState(false);


  const [
    error,
    setError,
  ] = useState("");


  const [
    editingId,
    setEditingId,
  ] = useState(null);


  const [
    showForm,
    setShowForm,
  ] = useState(false);


  const loadFarmers =
    useCallback(async () => {

      try {

        setLoading(true);

        setError("");


        const data =
          await getFarmers();


        setFarmers(
          data
        );

      }

      catch (
        loadError
      ) {

        console.error(
          "Farmer load error:",
          loadError
        );


        setError(
          loadError.message ||
          "Unable to load farmers."
        );

      }

      finally {

        setLoading(false);

      }

    }, []);


  useEffect(() => {

    loadFarmers();

  }, [
    loadFarmers,
  ]);


  const handleChange = (
    event
  ) => {

    const {
      name,
      value,
    } = event.target;


    setForm(
      (
        previous
      ) => ({
        ...previous,
        [name]:
          value,
      })
    );
  };


  const resetForm = () => {

    setForm(
      EMPTY_FORM
    );

    setEditingId(
      null
    );

    setShowForm(
      false
    );
  };


  const handleSubmit =
    async (
      event
    ) => {

      event.preventDefault();


      try {

        setSaving(true);

        setError("");


        if (
          editingId
        ) {

          const updated =
            await updateFarmer(
              editingId,
              form
            );


          setFarmers(
            (
              previous
            ) =>
              previous.map(
                (
                  farmer
                ) =>
                  farmer.id ===
                  editingId
                    ? updated
                    : farmer
              )
          );

        }

        else {

          const created =
            await createFarmer(
              form
            );


          setFarmers(
            (
              previous
            ) => [
              created,
              ...previous,
            ]
          );

        }


        resetForm();

      }

      catch (
        saveError
      ) {

        console.error(
          "Farmer save error:",
          saveError
        );


        setError(
          saveError.message ||
          "Unable to save farmer."
        );

      }

      finally {

        setSaving(false);

      }

    };


  const handleEdit = (
    farmer
  ) => {

    setEditingId(
      farmer.id
    );


    setForm({
      full_name:
        farmer.full_name ||
        "",

      phone:
        farmer.phone ||
        "",

      email:
        farmer.email ||
        "",

      village:
        farmer.village ||
        "",

      district:
        farmer.district ||
        "",

      state:
        farmer.state ||
        "",

      postal_code:
        farmer.postal_code ||
        "",

      notes:
        farmer.notes ||
        "",
    });


    setShowForm(
      true
    );


    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };


  const handleDelete =
    async (
      farmer
    ) => {

      const confirmed =
        window.confirm(
          `Delete farmer "${farmer.full_name}"? Linked animals and detections will remain but their farmer link may be cleared.`
        );


      if (!confirmed) {
        return;
      }


      try {

        setError("");


        await deleteFarmer(
          farmer.id
        );


        setFarmers(
          (
            previous
          ) =>
            previous.filter(
              (
                item
              ) =>
                item.id !==
                farmer.id
            )
        );

      }

      catch (
        deleteError
      ) {

        console.error(
          "Delete farmer error:",
          deleteError
        );


        setError(
          deleteError.message ||
          "Unable to delete farmer."
        );
      }
    };


  const filteredFarmers =
    useMemo(() => {

      const query =
        search
          .trim()
          .toLowerCase();


      if (!query) {
        return farmers;
      }


      return farmers.filter(
        (
          farmer
        ) => {

          const values = [
            farmer.full_name,
            farmer.phone,
            farmer.email,
            farmer.village,
            farmer.district,
            farmer.state,
          ];


          return values.some(
            (
              value
            ) =>
              value
                ?.toString()
                .toLowerCase()
                .includes(
                  query
                )
          );
        }
      );

    }, [
      farmers,
      search,
    ]);


  if (loading) {

    return (
      <div className="farmers-loading">

        <LoaderCircle
          size={32}
          className="farmers-spinner"
        />

        <h3>
          Loading farmers
        </h3>

        <p>
          Retrieving your farmer registry...
        </p>

      </div>
    );
  }


  return (
    <div className="farmers-page">

      <section className="farmers-header">

        <div>

          <span className="farmers-eyebrow">
            FIELD REGISTRY
          </span>

          <h1>
            Farmers
          </h1>

          <p>
            Manage farmer profiles and prepare
            animal-to-owner records for BreedVision.
          </p>

        </div>


        <div className="farmers-header-actions">

          <button
            type="button"
            className="farmers-secondary-button"
            onClick={
              loadFarmers
            }
          >

            <RefreshCw
              size={16}
            />

            Refresh

          </button>


          <button
            type="button"
            className="farmers-primary-button"
            onClick={() => {

              setEditingId(
                null
              );

              setForm(
                EMPTY_FORM
              );

              setShowForm(
                true
              );
            }}
          >

            <Plus
              size={17}
            />

            Add Farmer

          </button>

        </div>

      </section>


      <section className="farmers-summary-grid">

        <div className="farmers-summary-card">

          <Users
            size={21}
          />

          <div>

            <span>
              Total Farmers
            </span>

            <strong>
              {farmers.length}
            </strong>

          </div>

        </div>


        <div className="farmers-summary-card">

          <MapPin
            size={21}
          />

          <div>

            <span>
              Districts
            </span>

            <strong>
              {
                new Set(
                  farmers
                    .map(
                      (
                        farmer
                      ) =>
                        farmer.district
                    )
                    .filter(
                      Boolean
                    )
                ).size
              }
            </strong>

          </div>

        </div>


        <div className="farmers-summary-card">

          <Phone
            size={21}
          />

          <div>

            <span>
              With Contact
            </span>

            <strong>
              {
                farmers.filter(
                  (
                    farmer
                  ) =>
                    Boolean(
                      farmer.phone
                    )
                ).length
              }
            </strong>

          </div>

        </div>

      </section>


      {error && (

        <div className="farmers-error">

          <AlertCircle
            size={17}
          />

          <span>
            {error}
          </span>

        </div>

      )}


      {showForm && (

        <section className="farmers-form-card">

          <div className="farmers-form-header">

            <div>

              <span>
                {
                  editingId
                    ? "EDIT FARMER"
                    : "NEW FARMER"
                }
              </span>

              <h2>
                {
                  editingId
                    ? "Update farmer details"
                    : "Register a farmer"
                }
              </h2>

            </div>


            <button
              type="button"
              className="farmers-icon-button"
              onClick={
                resetForm
              }
            >

              <X
                size={18}
              />

            </button>

          </div>


          <form
            onSubmit={
              handleSubmit
            }
            className="farmers-form"
          >

            <div className="farmers-field">

              <label>
                Full Name *
              </label>

              <input
                name="full_name"
                value={
                  form.full_name
                }
                onChange={
                  handleChange
                }
                placeholder="Farmer name"
                required
              />

            </div>


            <div className="farmers-field">

              <label>
                Phone
              </label>

              <input
                name="phone"
                value={
                  form.phone
                }
                onChange={
                  handleChange
                }
                placeholder="Phone number"
              />

            </div>


            <div className="farmers-field">

              <label>
                Email
              </label>

              <input
                type="email"
                name="email"
                value={
                  form.email
                }
                onChange={
                  handleChange
                }
                placeholder="Email address"
              />

            </div>


            <div className="farmers-field">

              <label>
                Village
              </label>

              <input
                name="village"
                value={
                  form.village
                }
                onChange={
                  handleChange
                }
                placeholder="Village"
              />

            </div>


            <div className="farmers-field">

              <label>
                District
              </label>

              <input
                name="district"
                value={
                  form.district
                }
                onChange={
                  handleChange
                }
                placeholder="District"
              />

            </div>


            <div className="farmers-field">

              <label>
                State
              </label>

              <input
                name="state"
                value={
                  form.state
                }
                onChange={
                  handleChange
                }
                placeholder="State"
              />

            </div>


            <div className="farmers-field">

              <label>
                Postal Code
              </label>

              <input
                name="postal_code"
                value={
                  form.postal_code
                }
                onChange={
                  handleChange
                }
                placeholder="Postal code"
              />

            </div>


            <div className="farmers-field farmers-field-full">

              <label>
                Notes
              </label>

              <textarea
                name="notes"
                value={
                  form.notes
                }
                onChange={
                  handleChange
                }
                rows={3}
                placeholder="Optional notes..."
              />

            </div>


            <div className="farmers-form-actions">

              <button
                type="button"
                className="farmers-secondary-button"
                onClick={
                  resetForm
                }
              >
                Cancel
              </button>


              <button
                type="submit"
                className="farmers-primary-button"
                disabled={
                  saving
                }
              >

                {
                  saving ? (
                    <LoaderCircle
                      size={16}
                      className="farmers-spinner"
                    />
                  ) : (
                    editingId
                      ? <Edit3 size={16} />
                      : <Plus size={16} />
                  )
                }

                {
                  saving
                    ? "Saving..."
                    : editingId
                      ? "Update Farmer"
                      : "Create Farmer"
                }

              </button>

            </div>

          </form>

        </section>

      )}


      <section className="farmers-toolbar">

        <div className="farmers-search">

          <Search
            size={17}
          />

          <input
            value={
              search
            }
            onChange={
              (
                event
              ) =>
                setSearch(
                  event.target.value
                )
            }
            placeholder="Search name, phone, village, district..."
          />

        </div>


        <span>
          {filteredFarmers.length}
          {" "}
          farmer
          {
            filteredFarmers.length ===
            1
              ? ""
              : "s"
          }
        </span>

      </section>


      {
        filteredFarmers.length ===
        0 ? (

          <section className="farmers-empty">

            <UserRound
              size={34}
            />

            <h2>
              No farmers found
            </h2>

            <p>
              Register your first farmer to start
              building the animal registry.
            </p>

          </section>

        ) : (

          <section className="farmers-grid">

            {
              filteredFarmers.map(
                (
                  farmer
                ) => (

                  <article
                    className="farmer-card"
                    key={
                      farmer.id
                    }
                  >

                    <div className="farmer-card-top">

                      <div className="farmer-avatar">

                        <UserRound
                          size={22}
                        />

                      </div>


                      <div>

                        <span>
                          FARMER PROFILE
                        </span>

                        <h2>
                          {farmer.full_name}
                        </h2>

                      </div>

                    </div>


                    <div className="farmer-details">

                      <div>

                        <span>
                          Phone
                        </span>

                        <strong>
                          {farmer.phone || "—"}
                        </strong>

                      </div>


                      <div>

                        <span>
                          Village
                        </span>

                        <strong>
                          {farmer.village || "—"}
                        </strong>

                      </div>


                      <div>

                        <span>
                          District
                        </span>

                        <strong>
                          {farmer.district || "—"}
                        </strong>

                      </div>


                      <div>

                        <span>
                          State
                        </span>

                        <strong>
                          {farmer.state || "—"}
                        </strong>

                      </div>

                    </div>


                    {
                      farmer.notes && (

                        <p className="farmer-notes">
                          {farmer.notes}
                        </p>

                      )
                    }


                    <div className="farmer-card-actions">

                      <button
                        type="button"
                        onClick={() =>
                          handleEdit(
                            farmer
                          )
                        }
                      >

                        <Edit3
                          size={15}
                        />

                        Edit

                      </button>


                      <button
                        type="button"
                        className="danger"
                        onClick={() =>
                          handleDelete(
                            farmer
                          )
                        }
                      >

                        <Trash2
                          size={15}
                        />

                        Delete

                      </button>

                    </div>

                  </article>

                )
              )
            }

          </section>

        )
      }

    </div>
  );
}


export default Farmers;