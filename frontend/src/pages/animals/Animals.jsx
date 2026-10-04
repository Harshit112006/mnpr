import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  AlertCircle,
  Beef,
  Edit3,
  LoaderCircle,
  Plus,
  RefreshCw,
  Search,
  Tag,
  Trash2,
  UserRound,
  X,
} from "lucide-react";

import {
  createAnimal,
  deleteAnimal,
  getAnimals,
  updateAnimal,
} from "../../services/phase9/animalService";

import {
  getFarmers,
} from "../../services/phase9/farmerService";

import "../../styles/Phase9.css";


const EMPTY_FORM = {
  farmer_id: "",
  tag_number: "",
  name: "",
  species: "cattle",
  verified_breed: "",
  sex: "unknown",
  date_of_birth: "",
  color_markings: "",
  notes: "",
};


function Animals() {

  const [animals, setAnimals] =
    useState([]);

  const [farmers, setFarmers] =
    useState([]);

  const [form, setForm] =
    useState(EMPTY_FORM);

  const [search, setSearch] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");

  const [editingId, setEditingId] =
    useState(null);

  const [showForm, setShowForm] =
    useState(false);


  const loadData =
    useCallback(async () => {

      try {

        setLoading(true);
        setError("");


        const [
          animalData,
          farmerData,
        ] =
          await Promise.all([
            getAnimals(),
            getFarmers(),
          ]);


        setAnimals(
          animalData
        );

        setFarmers(
          farmerData
        );

      }

      catch (
        loadError
      ) {

        console.error(
          "Animal registry load error:",
          loadError
        );


        setError(
          loadError.message ||
          "Unable to load animal registry."
        );

      }

      finally {

        setLoading(false);

      }

    }, []);


  useEffect(() => {

    loadData();

  }, [
    loadData,
  ]);


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


  const handleSubmit =
    async (
      event
    ) => {

      event.preventDefault();


      try {

        setSaving(true);
        setError("");


        if (editingId) {

          const updated =
            await updateAnimal(
              editingId,
              form
            );


          setAnimals(
            (
              previous
            ) =>
              previous.map(
                (
                  animal
                ) =>
                  animal.id ===
                  editingId
                    ? updated
                    : animal
              )
          );

        }

        else {

          const created =
            await createAnimal(
              form
            );


          setAnimals(
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
          "Animal save error:",
          saveError
        );


        setError(
          saveError.message ||
          "Unable to save animal."
        );

      }

      finally {

        setSaving(false);

      }

    };


  const handleEdit = (
    animal
  ) => {

    setEditingId(
      animal.id
    );


    setForm({
      farmer_id:
        animal.farmer_id ||
        "",

      tag_number:
        animal.tag_number ||
        "",

      name:
        animal.name ||
        "",

      species:
        animal.species ||
        "cattle",

      verified_breed:
        animal.verified_breed ||
        "",

      sex:
        animal.sex ||
        "unknown",

      date_of_birth:
        animal.date_of_birth ||
        "",

      color_markings:
        animal.color_markings ||
        "",

      notes:
        animal.notes ||
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
      animal
    ) => {

      const label =
        animal.name ||
        animal.tag_number ||
        "this animal";


      if (
        !window.confirm(
          `Delete ${label}?`
        )
      ) {

        return;
      }


      try {

        setError("");


        await deleteAnimal(
          animal.id
        );


        setAnimals(
          (
            previous
          ) =>
            previous.filter(
              (
                item
              ) =>
                item.id !==
                animal.id
            )
        );

      }

      catch (
        deleteError
      ) {

        setError(
          deleteError.message ||
          "Unable to delete animal."
        );
      }
    };


  const filteredAnimals =
    useMemo(() => {

      const query =
        search
          .trim()
          .toLowerCase();


      if (!query) {
        return animals;
      }


      return animals.filter(
        (
          animal
        ) => {

          const values = [
            animal.name,
            animal.tag_number,
            animal.species,
            animal.verified_breed,
            animal.farmers
              ?.full_name,
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
      animals,
      search,
    ]);


  if (loading) {

    return (
      <div className="phase9-loading">

        <LoaderCircle
          className="phase9-spinner"
          size={32}
        />

        <h3>
          Loading animal registry
        </h3>

      </div>
    );
  }


  return (
    <div className="phase9-page">

      <section className="phase9-header">

        <div>

          <span className="phase9-eyebrow">
            LIVESTOCK REGISTRY
          </span>

          <h1>
            Animals
          </h1>

          <p>
            Register cattle and buffalo,
            link owners and maintain verified
            breed information.
          </p>

        </div>


        <div className="phase9-actions">

          <button
            className="phase9-secondary"
            type="button"
            onClick={
              loadData
            }
          >
            <RefreshCw size={16} />
            Refresh
          </button>


          <button
            className="phase9-primary"
            type="button"
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
            <Plus size={16} />
            Add Animal
          </button>

        </div>

      </section>


      <section className="phase9-summary-grid">

        <div className="phase9-summary-card">
          <Beef size={21} />
          <div>
            <span>Total Animals</span>
            <strong>
              {animals.length}
            </strong>
          </div>
        </div>


        <div className="phase9-summary-card">
          <Tag size={21} />
          <div>
            <span>Cattle</span>
            <strong>
              {
                animals.filter(
                  (
                    item
                  ) =>
                    item.species ===
                    "cattle"
                ).length
              }
            </strong>
          </div>
        </div>


        <div className="phase9-summary-card">
          <Beef size={21} />
          <div>
            <span>Buffalo</span>
            <strong>
              {
                animals.filter(
                  (
                    item
                  ) =>
                    item.species ===
                    "buffalo"
                ).length
              }
            </strong>
          </div>
        </div>


        <div className="phase9-summary-card">
          <UserRound size={21} />
          <div>
            <span>Linked Owners</span>
            <strong>
              {
                animals.filter(
                  (
                    item
                  ) =>
                    Boolean(
                      item.farmer_id
                    )
                ).length
              }
            </strong>
          </div>
        </div>

      </section>


      {error && (

        <div className="phase9-error">
          <AlertCircle size={17} />
          {error}
        </div>

      )}


      {showForm && (

        <section className="phase9-form-card">

          <div className="phase9-form-header">

            <div>
              <span>
                {
                  editingId
                    ? "EDIT ANIMAL"
                    : "NEW ANIMAL"
                }
              </span>

              <h2>
                {
                  editingId
                    ? "Update animal record"
                    : "Register an animal"
                }
              </h2>
            </div>


            <button
              className="phase9-icon-button"
              type="button"
              onClick={
                resetForm
              }
            >
              <X size={18} />
            </button>

          </div>


          <form
            className="phase9-form"
            onSubmit={
              handleSubmit
            }
          >

            <div className="phase9-field">
              <label>
                Farmer
              </label>

              <select
                name="farmer_id"
                value={
                  form.farmer_id
                }
                onChange={
                  handleChange
                }
              >
                <option value="">
                  No farmer assigned
                </option>

                {
                  farmers.map(
                    (
                      farmer
                    ) => (
                      <option
                        key={farmer.id}
                        value={farmer.id}
                      >
                        {farmer.full_name}
                      </option>
                    )
                  )
                }
              </select>
            </div>


            <div className="phase9-field">
              <label>
                Tag Number
              </label>

              <input
                name="tag_number"
                value={
                  form.tag_number
                }
                onChange={
                  handleChange
                }
                placeholder="Animal tag"
              />
            </div>


            <div className="phase9-field">
              <label>
                Name
              </label>

              <input
                name="name"
                value={
                  form.name
                }
                onChange={
                  handleChange
                }
                placeholder="Optional name"
              />
            </div>


            <div className="phase9-field">
              <label>
                Species *
              </label>

              <select
                name="species"
                value={
                  form.species
                }
                onChange={
                  handleChange
                }
                required
              >
                <option value="cattle">
                  Cattle
                </option>

                <option value="buffalo">
                  Buffalo
                </option>
              </select>
            </div>


            <div className="phase9-field">
              <label>
                Verified Breed
              </label>

              <input
                name="verified_breed"
                value={
                  form.verified_breed
                }
                onChange={
                  handleChange
                }
                placeholder="Human-verified breed"
              />
            </div>


            <div className="phase9-field">
              <label>
                Sex
              </label>

              <select
                name="sex"
                value={
                  form.sex
                }
                onChange={
                  handleChange
                }
              >
                <option value="unknown">
                  Unknown
                </option>

                <option value="female">
                  Female
                </option>

                <option value="male">
                  Male
                </option>
              </select>
            </div>


            <div className="phase9-field">
              <label>
                Date of Birth
              </label>

              <input
                type="date"
                name="date_of_birth"
                value={
                  form.date_of_birth
                }
                onChange={
                  handleChange
                }
              />
            </div>


            <div className="phase9-field">
              <label>
                Color / Markings
              </label>

              <input
                name="color_markings"
                value={
                  form.color_markings
                }
                onChange={
                  handleChange
                }
                placeholder="Identification markings"
              />
            </div>


            <div className="phase9-field phase9-field-full">
              <label>
                Notes
              </label>

              <textarea
                rows={3}
                name="notes"
                value={
                  form.notes
                }
                onChange={
                  handleChange
                }
                placeholder="Optional notes..."
              />
            </div>


            <div className="phase9-form-actions">

              <button
                type="button"
                className="phase9-secondary"
                onClick={
                  resetForm
                }
              >
                Cancel
              </button>


              <button
                type="submit"
                className="phase9-primary"
                disabled={
                  saving
                }
              >

                {
                  saving
                    ? (
                      <LoaderCircle
                        size={16}
                        className="phase9-spinner"
                      />
                    )
                    : (
                      editingId
                        ? <Edit3 size={16} />
                        : <Plus size={16} />
                    )
                }

                {
                  saving
                    ? "Saving..."
                    : editingId
                      ? "Update Animal"
                      : "Create Animal"
                }

              </button>

            </div>

          </form>

        </section>

      )}


      <section className="phase9-toolbar">

        <div className="phase9-search">
          <Search size={17} />

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
            placeholder="Search animal, tag, breed or farmer..."
          />
        </div>

        <span>
          {filteredAnimals.length}
          {" "}
          animal
          {
            filteredAnimals.length ===
            1
              ? ""
              : "s"
          }
        </span>

      </section>


      {
        filteredAnimals.length ===
        0 ? (

          <section className="phase9-empty">
            <Beef size={35} />
            <h2>
              No animals found
            </h2>
            <p>
              Register an animal to start
              building livestock records.
            </p>
          </section>

        ) : (

          <section className="phase9-card-grid">

            {
              filteredAnimals.map(
                (
                  animal
                ) => (

                  <article
                    key={animal.id}
                    className="phase9-record-card"
                  >

                    <div className="phase9-record-heading">

                      <div className="phase9-record-icon">
                        <Beef size={21} />
                      </div>

                      <div>
                        <span>
                          {
                            animal.species
                              ?.toUpperCase()
                          }
                        </span>

                        <h2>
                          {
                            animal.name ||
                            animal.tag_number ||
                            "Unnamed animal"
                          }
                        </h2>
                      </div>

                    </div>


                    <div className="phase9-detail-grid">

                      <div>
                        <span>
                          Tag
                        </span>
                        <strong>
                          {animal.tag_number || "—"}
                        </strong>
                      </div>


                      <div>
                        <span>
                          Verified Breed
                        </span>
                        <strong>
                          {animal.verified_breed || "—"}
                        </strong>
                      </div>


                      <div>
                        <span>
                          Sex
                        </span>
                        <strong>
                          {animal.sex || "—"}
                        </strong>
                      </div>


                      <div>
                        <span>
                          Farmer
                        </span>
                        <strong>
                          {
                            animal.farmers
                              ?.full_name ||
                            "Unassigned"
                          }
                        </strong>
                      </div>

                    </div>


                    <div className="phase9-card-actions">

                      <button
                        type="button"
                        onClick={() =>
                          handleEdit(
                            animal
                          )
                        }
                      >
                        <Edit3 size={15} />
                        Edit
                      </button>


                      <button
                        type="button"
                        className="danger"
                        onClick={() =>
                          handleDelete(
                            animal
                          )
                        }
                      >
                        <Trash2 size={15} />
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


export default Animals;