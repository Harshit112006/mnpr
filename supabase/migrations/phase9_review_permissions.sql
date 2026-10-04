-- =========================================================
-- BREEDVISION AI
-- PHASE 9
-- REVIEW WORKFLOW + OWNERSHIP SECURITY PATCH
-- =========================================================


-- =========================================================
-- 1. DETECTIONS UPDATE POLICY
--
-- Required for:
-- review_status
-- farmer_id
-- animal_id
-- =========================================================


DROP POLICY IF EXISTS
"Users can update own detections"
ON public.detections;


CREATE POLICY
"Users can update own detections"
ON public.detections
FOR UPDATE
TO authenticated
USING (
    (SELECT auth.uid()) =
    user_id
)
WITH CHECK (

    (SELECT auth.uid()) =
    user_id

    AND

    (
        farmer_id IS NULL

        OR EXISTS (

            SELECT 1

            FROM public.farmers f

            WHERE
                f.id = farmer_id
                AND
                f.user_id =
                    (SELECT auth.uid())
        )
    )

    AND

    (
        animal_id IS NULL

        OR EXISTS (

            SELECT 1

            FROM public.animals a

            WHERE
                a.id = animal_id
                AND
                a.user_id =
                    (SELECT auth.uid())
        )
    )
);


-- Only Phase-9 operational fields may be updated
-- directly from authenticated frontend clients.

GRANT UPDATE (
    review_status,
    farmer_id,
    animal_id
)
ON public.detections
TO authenticated;



-- =========================================================
-- 2. HARDEN ANIMAL ↔ FARMER OWNERSHIP
-- =========================================================


DROP POLICY IF EXISTS
"Users can create own animals"
ON public.animals;


CREATE POLICY
"Users can create own animals"
ON public.animals
FOR INSERT
TO authenticated
WITH CHECK (

    (SELECT auth.uid()) =
    user_id

    AND

    (
        farmer_id IS NULL

        OR EXISTS (

            SELECT 1

            FROM public.farmers f

            WHERE
                f.id = farmer_id
                AND
                f.user_id =
                    (SELECT auth.uid())
        )
    )
);


DROP POLICY IF EXISTS
"Users can update own animals"
ON public.animals;


CREATE POLICY
"Users can update own animals"
ON public.animals
FOR UPDATE
TO authenticated
USING (
    (SELECT auth.uid()) =
    user_id
)
WITH CHECK (

    (SELECT auth.uid()) =
    user_id

    AND

    (
        farmer_id IS NULL

        OR EXISTS (

            SELECT 1

            FROM public.farmers f

            WHERE
                f.id = farmer_id
                AND
                f.user_id =
                    (SELECT auth.uid())
        )
    )
);



-- =========================================================
-- 3. HARDEN DETECTION REVIEW POLICIES
--
-- A user must:
-- - own the review
-- - own the referenced detection
-- =========================================================


DROP POLICY IF EXISTS
"Users can view own detection reviews"
ON public.detection_reviews;


CREATE POLICY
"Users can view own detection reviews"
ON public.detection_reviews
FOR SELECT
TO authenticated
USING (

    reviewer_user_id =
        (SELECT auth.uid())

    AND

    EXISTS (

        SELECT 1

        FROM public.detections d

        WHERE
            d.id = detection_id
            AND
            d.user_id =
                (SELECT auth.uid())
    )
);


DROP POLICY IF EXISTS
"Users can create own detection reviews"
ON public.detection_reviews;


CREATE POLICY
"Users can create own detection reviews"
ON public.detection_reviews
FOR INSERT
TO authenticated
WITH CHECK (

    reviewer_user_id =
        (SELECT auth.uid())

    AND

    EXISTS (

        SELECT 1

        FROM public.detections d

        WHERE
            d.id = detection_id
            AND
            d.user_id =
                (SELECT auth.uid())
    )
);


DROP POLICY IF EXISTS
"Users can update own detection reviews"
ON public.detection_reviews;


CREATE POLICY
"Users can update own detection reviews"
ON public.detection_reviews
FOR UPDATE
TO authenticated
USING (

    reviewer_user_id =
        (SELECT auth.uid())

    AND

    EXISTS (

        SELECT 1

        FROM public.detections d

        WHERE
            d.id = detection_id
            AND
            d.user_id =
                (SELECT auth.uid())
    )
)
WITH CHECK (

    reviewer_user_id =
        (SELECT auth.uid())

    AND

    EXISTS (

        SELECT 1

        FROM public.detections d

        WHERE
            d.id = detection_id
            AND
            d.user_id =
                (SELECT auth.uid())
    )
);



-- =========================================================
-- 4. ATOMIC HUMAN REVIEW FUNCTION
--
-- Important:
-- ML prediction is NEVER overwritten.
--
-- Original prediction remains in detections:
-- species
-- predicted_breed
-- confidence
--
-- Human decision is stored separately in:
-- detection_reviews
-- =========================================================


CREATE OR REPLACE FUNCTION
public.review_detection(

    p_detection_id UUID,

    p_decision TEXT,

    p_reviewed_species TEXT
        DEFAULT NULL,

    p_reviewed_breed TEXT
        DEFAULT NULL,

    p_notes TEXT
        DEFAULT NULL

)
RETURNS public.detection_reviews

LANGUAGE plpgsql

SECURITY INVOKER

SET search_path = public

AS $$

DECLARE

    v_user_id UUID;

    v_detection
        public.detections%ROWTYPE;

    v_review
        public.detection_reviews%ROWTYPE;

    v_review_status TEXT;

    v_reviewed_species TEXT;

    v_reviewed_breed TEXT;

BEGIN

    v_user_id :=
        auth.uid();


    IF v_user_id IS NULL THEN

        RAISE EXCEPTION
            'Authentication required';

    END IF;


    IF p_decision NOT IN (
        'verified',
        'corrected',
        'rejected'
    ) THEN

        RAISE EXCEPTION
            'Invalid review decision';

    END IF;


    SELECT
        *
    INTO
        v_detection

    FROM
        public.detections

    WHERE
        id = p_detection_id

        AND

        user_id = v_user_id;


    IF NOT FOUND THEN

        RAISE EXCEPTION
            'Detection not found or access denied';

    END IF;


    -- =====================================================
    -- VERIFIED
    --
    -- Human confirms the ML prediction.
    -- =====================================================

    IF p_decision = 'verified' THEN

        IF
            v_detection.species IS NULL
            OR
            v_detection.predicted_breed IS NULL
        THEN

            RAISE EXCEPTION
                'Cannot verify a detection without an ML breed prediction';

        END IF;


        v_reviewed_species :=
            v_detection.species;

        v_reviewed_breed :=
            v_detection.predicted_breed;

        v_review_status :=
            'verified';


    -- =====================================================
    -- CORRECTED
    --
    -- Human supplies corrected species/breed.
    -- Original ML output remains unchanged.
    -- =====================================================

    ELSIF p_decision = 'corrected' THEN

        IF
            p_reviewed_species IS NULL
            OR
            BTRIM(
                p_reviewed_species
            ) = ''
        THEN

            RAISE EXCEPTION
                'Corrected species is required';

        END IF;


        IF
            p_reviewed_species NOT IN (
                'cattle',
                'buffalo'
            )
        THEN

            RAISE EXCEPTION
                'Corrected species must be cattle or buffalo';

        END IF;


        IF
            p_reviewed_breed IS NULL
            OR
            BTRIM(
                p_reviewed_breed
            ) = ''
        THEN

            RAISE EXCEPTION
                'Corrected breed is required';

        END IF;


        v_reviewed_species :=
            BTRIM(
                p_reviewed_species
            );

        v_reviewed_breed :=
            BTRIM(
                p_reviewed_breed
            );

        -- Corrected means human review is complete.
        v_review_status :=
            'verified';


    -- =====================================================
    -- REJECTED
    -- =====================================================

    ELSE

        v_reviewed_species :=
            NULL;

        v_reviewed_breed :=
            NULL;

        v_review_status :=
            'rejected';

    END IF;


    -- =====================================================
    -- UPSERT REVIEW
    -- =====================================================

    INSERT INTO
        public.detection_reviews (

            detection_id,

            reviewer_user_id,

            decision,

            original_species,

            original_breed,

            original_confidence,

            reviewed_species,

            reviewed_breed,

            notes

        )

    VALUES (

        v_detection.id,

        v_user_id,

        p_decision,

        v_detection.species,

        v_detection.predicted_breed,

        v_detection.confidence,

        v_reviewed_species,

        v_reviewed_breed,

        NULLIF(
            BTRIM(
                COALESCE(
                    p_notes,
                    ''
                )
            ),
            ''
        )

    )

    ON CONFLICT (
        detection_id
    )

    DO UPDATE SET

        reviewer_user_id =
            EXCLUDED.reviewer_user_id,

        decision =
            EXCLUDED.decision,

        original_species =
            EXCLUDED.original_species,

        original_breed =
            EXCLUDED.original_breed,

        original_confidence =
            EXCLUDED.original_confidence,

        reviewed_species =
            EXCLUDED.reviewed_species,

        reviewed_breed =
            EXCLUDED.reviewed_breed,

        notes =
            EXCLUDED.notes,

        updated_at =
            NOW()

    RETURNING
        *
    INTO
        v_review;


    -- =====================================================
    -- UPDATE OPERATIONAL STATUS ONLY
    --
    -- ML prediction fields stay untouched.
    -- =====================================================

    UPDATE
        public.detections

    SET
        review_status =
            v_review_status

    WHERE
        id =
            v_detection.id

        AND

        user_id =
            v_user_id;


    RETURN
        v_review;

END;

$$;



GRANT EXECUTE
ON FUNCTION
public.review_detection(
    UUID,
    TEXT,
    TEXT,
    TEXT,
    TEXT
)
TO authenticated;