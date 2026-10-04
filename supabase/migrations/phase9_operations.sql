-- =========================================================
-- BREEDVISION AI
-- PHASE 9
-- OPERATIONS PLATFORM
--
-- Farmer registry
-- Animal registry
-- Detection-to-animal linkage
-- Human review audit
-- User alerts
-- =========================================================


-- =========================================================
-- COMMON UPDATED_AT FUNCTION
-- =========================================================


CREATE OR REPLACE FUNCTION
public.set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    NEW.updated_at = NOW();

    RETURN NEW;

END;
$$;



-- =========================================================
-- FARMERS
-- =========================================================


CREATE TABLE IF NOT EXISTS
public.farmers (

    id UUID PRIMARY KEY
        DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL
        REFERENCES auth.users(id)
        ON DELETE CASCADE,

    full_name TEXT NOT NULL,

    phone TEXT,

    email TEXT,

    village TEXT,

    district TEXT,

    state TEXT,

    postal_code TEXT,

    notes TEXT,

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW()
);



CREATE INDEX IF NOT EXISTS
farmers_user_created_at_idx
ON public.farmers (
    user_id,
    created_at DESC
);



ALTER TABLE
public.farmers
ENABLE ROW LEVEL SECURITY;



DROP POLICY IF EXISTS
"Users can view own farmers"
ON public.farmers;



CREATE POLICY
"Users can view own farmers"
ON public.farmers
FOR SELECT
TO authenticated
USING (
    (SELECT auth.uid()) =
    user_id
);



DROP POLICY IF EXISTS
"Users can create own farmers"
ON public.farmers;



CREATE POLICY
"Users can create own farmers"
ON public.farmers
FOR INSERT
TO authenticated
WITH CHECK (
    (SELECT auth.uid()) =
    user_id
);



DROP POLICY IF EXISTS
"Users can update own farmers"
ON public.farmers;



CREATE POLICY
"Users can update own farmers"
ON public.farmers
FOR UPDATE
TO authenticated
USING (
    (SELECT auth.uid()) =
    user_id
)
WITH CHECK (
    (SELECT auth.uid()) =
    user_id
);



DROP POLICY IF EXISTS
"Users can delete own farmers"
ON public.farmers;



CREATE POLICY
"Users can delete own farmers"
ON public.farmers
FOR DELETE
TO authenticated
USING (
    (SELECT auth.uid()) =
    user_id
);



DROP TRIGGER IF EXISTS
set_farmers_updated_at
ON public.farmers;



CREATE TRIGGER
set_farmers_updated_at
BEFORE UPDATE
ON public.farmers
FOR EACH ROW
EXECUTE FUNCTION
public.set_updated_at();



GRANT
    SELECT,
    INSERT,
    UPDATE,
    DELETE
ON public.farmers
TO authenticated;



-- =========================================================
-- ANIMALS
-- =========================================================


CREATE TABLE IF NOT EXISTS
public.animals (

    id UUID PRIMARY KEY
        DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL
        REFERENCES auth.users(id)
        ON DELETE CASCADE,

    farmer_id UUID
        REFERENCES public.farmers(id)
        ON DELETE SET NULL,

    tag_number TEXT,

    name TEXT,

    species TEXT NOT NULL,

    verified_breed TEXT,

    sex TEXT,

    date_of_birth DATE,

    color_markings TEXT,

    notes TEXT,

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    CONSTRAINT animals_species_check
    CHECK (
        species IN (
            'cattle',
            'buffalo'
        )
    ),

    CONSTRAINT animals_sex_check
    CHECK (
        sex IS NULL
        OR
        sex IN (
            'male',
            'female',
            'unknown'
        )
    )
);



CREATE UNIQUE INDEX IF NOT EXISTS
animals_user_tag_unique_idx
ON public.animals (
    user_id,
    tag_number
)
WHERE tag_number IS NOT NULL;



CREATE INDEX IF NOT EXISTS
animals_user_created_at_idx
ON public.animals (
    user_id,
    created_at DESC
);



CREATE INDEX IF NOT EXISTS
animals_farmer_idx
ON public.animals (
    farmer_id
);



ALTER TABLE
public.animals
ENABLE ROW LEVEL SECURITY;



DROP POLICY IF EXISTS
"Users can view own animals"
ON public.animals;



CREATE POLICY
"Users can view own animals"
ON public.animals
FOR SELECT
TO authenticated
USING (
    (SELECT auth.uid()) =
    user_id
);



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
);



DROP POLICY IF EXISTS
"Users can delete own animals"
ON public.animals;



CREATE POLICY
"Users can delete own animals"
ON public.animals
FOR DELETE
TO authenticated
USING (
    (SELECT auth.uid()) =
    user_id
);



DROP TRIGGER IF EXISTS
set_animals_updated_at
ON public.animals;



CREATE TRIGGER
set_animals_updated_at
BEFORE UPDATE
ON public.animals
FOR EACH ROW
EXECUTE FUNCTION
public.set_updated_at();



GRANT
    SELECT,
    INSERT,
    UPDATE,
    DELETE
ON public.animals
TO authenticated;



-- =========================================================
-- EXTEND DETECTIONS
-- =========================================================


ALTER TABLE
public.detections

ADD COLUMN IF NOT EXISTS
farmer_id UUID
REFERENCES public.farmers(id)
ON DELETE SET NULL;



ALTER TABLE
public.detections

ADD COLUMN IF NOT EXISTS
animal_id UUID
REFERENCES public.animals(id)
ON DELETE SET NULL;



CREATE INDEX IF NOT EXISTS
detections_farmer_idx
ON public.detections (
    farmer_id
);



CREATE INDEX IF NOT EXISTS
detections_animal_idx
ON public.detections (
    animal_id
);



-- =========================================================
-- DETECTION REVIEWS
-- =========================================================


CREATE TABLE IF NOT EXISTS
public.detection_reviews (

    id UUID PRIMARY KEY
        DEFAULT gen_random_uuid(),

    detection_id UUID NOT NULL
        REFERENCES public.detections(id)
        ON DELETE CASCADE,

    reviewer_user_id UUID NOT NULL
        REFERENCES auth.users(id)
        ON DELETE CASCADE,

    decision TEXT NOT NULL,

    original_species TEXT,

    original_breed TEXT,

    original_confidence NUMERIC(6, 5),

    reviewed_species TEXT,

    reviewed_breed TEXT,

    notes TEXT,

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    CONSTRAINT detection_reviews_decision_check
    CHECK (
        decision IN (
            'verified',
            'corrected',
            'rejected'
        )
    ),

    CONSTRAINT detection_reviews_species_check
    CHECK (
        reviewed_species IS NULL
        OR
        reviewed_species IN (
            'cattle',
            'buffalo'
        )
    ),

    CONSTRAINT detection_reviews_confidence_check
    CHECK (
        original_confidence IS NULL
        OR (
            original_confidence >= 0
            AND
            original_confidence <= 1
        )
    )
);



CREATE UNIQUE INDEX IF NOT EXISTS
detection_reviews_detection_unique_idx
ON public.detection_reviews (
    detection_id
);



CREATE INDEX IF NOT EXISTS
detection_reviews_reviewer_idx
ON public.detection_reviews (
    reviewer_user_id,
    created_at DESC
);



ALTER TABLE
public.detection_reviews
ENABLE ROW LEVEL SECURITY;



DROP POLICY IF EXISTS
"Users can view own detection reviews"
ON public.detection_reviews;



CREATE POLICY
"Users can view own detection reviews"
ON public.detection_reviews
FOR SELECT
TO authenticated
USING (
    (SELECT auth.uid()) =
    reviewer_user_id
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
    (SELECT auth.uid()) =
    reviewer_user_id
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
    (SELECT auth.uid()) =
    reviewer_user_id
)
WITH CHECK (
    (SELECT auth.uid()) =
    reviewer_user_id
);



DROP TRIGGER IF EXISTS
set_detection_reviews_updated_at
ON public.detection_reviews;



CREATE TRIGGER
set_detection_reviews_updated_at
BEFORE UPDATE
ON public.detection_reviews
FOR EACH ROW
EXECUTE FUNCTION
public.set_updated_at();



GRANT
    SELECT,
    INSERT,
    UPDATE
ON public.detection_reviews
TO authenticated;



-- =========================================================
-- ALERTS
-- =========================================================


CREATE TABLE IF NOT EXISTS
public.alerts (

    id UUID PRIMARY KEY
        DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL
        REFERENCES auth.users(id)
        ON DELETE CASCADE,

    detection_id UUID
        REFERENCES public.detections(id)
        ON DELETE CASCADE,

    animal_id UUID
        REFERENCES public.animals(id)
        ON DELETE CASCADE,

    alert_type TEXT NOT NULL,

    severity TEXT NOT NULL
        DEFAULT 'info',

    title TEXT NOT NULL,

    message TEXT NOT NULL,

    status TEXT NOT NULL
        DEFAULT 'unread',

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    read_at TIMESTAMPTZ,

    CONSTRAINT alerts_severity_check
    CHECK (
        severity IN (
            'info',
            'warning',
            'critical'
        )
    ),

    CONSTRAINT alerts_status_check
    CHECK (
        status IN (
            'unread',
            'read',
            'dismissed'
        )
    )
);



CREATE INDEX IF NOT EXISTS
alerts_user_status_created_idx
ON public.alerts (
    user_id,
    status,
    created_at DESC
);



ALTER TABLE
public.alerts
ENABLE ROW LEVEL SECURITY;



DROP POLICY IF EXISTS
"Users can view own alerts"
ON public.alerts;



CREATE POLICY
"Users can view own alerts"
ON public.alerts
FOR SELECT
TO authenticated
USING (
    (SELECT auth.uid()) =
    user_id
);



DROP POLICY IF EXISTS
"Users can create own alerts"
ON public.alerts;



CREATE POLICY
"Users can create own alerts"
ON public.alerts
FOR INSERT
TO authenticated
WITH CHECK (
    (SELECT auth.uid()) =
    user_id
);



DROP POLICY IF EXISTS
"Users can update own alerts"
ON public.alerts;



CREATE POLICY
"Users can update own alerts"
ON public.alerts
FOR UPDATE
TO authenticated
USING (
    (SELECT auth.uid()) =
    user_id
)
WITH CHECK (
    (SELECT auth.uid()) =
    user_id
);



DROP POLICY IF EXISTS
"Users can delete own alerts"
ON public.alerts;



CREATE POLICY
"Users can delete own alerts"
ON public.alerts
FOR DELETE
TO authenticated
USING (
    (SELECT auth.uid()) =
    user_id
);



GRANT
    SELECT,
    INSERT,
    UPDATE,
    DELETE
ON public.alerts
TO authenticated;