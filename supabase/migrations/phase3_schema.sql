-- =========================================================
-- BREEDVISION AI
-- PHASE 3 DATABASE FOUNDATION
-- =========================================================


-- =========================================================
-- PROFILES
-- =========================================================

CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY
        REFERENCES auth.users(id)
        ON DELETE CASCADE,

    email TEXT,

    full_name TEXT,

    role TEXT NOT NULL
        DEFAULT 'user',

    organization TEXT,

    avatar_url TEXT,

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    CONSTRAINT profiles_role_check
    CHECK (
        role IN (
            'user',
            'field_worker',
            'farmer',
            'veterinarian',
            'researcher',
            'student'
        )
    )
);


ALTER TABLE public.profiles
ENABLE ROW LEVEL SECURITY;


DROP POLICY IF EXISTS
"Users can view own profile"
ON public.profiles;


CREATE POLICY
"Users can view own profile"
ON public.profiles
FOR SELECT
TO authenticated
USING (
    (SELECT auth.uid()) = id
);


DROP POLICY IF EXISTS
"Users can update own profile"
ON public.profiles;


CREATE POLICY
"Users can update own profile"
ON public.profiles
FOR UPDATE
TO authenticated
USING (
    (SELECT auth.uid()) = id
)
WITH CHECK (
    (SELECT auth.uid()) = id
);


CREATE OR REPLACE FUNCTION
public.update_profile_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    NEW.updated_at = NOW();

    RETURN NEW;

END;
$$;


DROP TRIGGER IF EXISTS
set_profiles_updated_at
ON public.profiles;


CREATE TRIGGER
set_profiles_updated_at
BEFORE UPDATE
ON public.profiles
FOR EACH ROW
EXECUTE FUNCTION
public.update_profile_updated_at();


CREATE OR REPLACE FUNCTION
public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN

    INSERT INTO public.profiles (
        id,
        email,
        full_name,
        role,
        organization,
        avatar_url
    )

    VALUES (
        NEW.id,

        NEW.email,

        COALESCE(
            NEW.raw_user_meta_data ->> 'full_name',
            NEW.raw_user_meta_data ->> 'name',
            SPLIT_PART(
                COALESCE(
                    NEW.email,
                    'BreedVision User'
                ),
                '@',
                1
            )
        ),

        COALESCE(
            NULLIF(
                NEW.raw_user_meta_data ->> 'role',
                ''
            ),
            'user'
        ),

        NULLIF(
            NEW.raw_user_meta_data ->> 'organization',
            ''
        ),

        COALESCE(
            NEW.raw_user_meta_data ->> 'avatar_url',
            NEW.raw_user_meta_data ->> 'picture'
        )
    )

    ON CONFLICT (id)
    DO NOTHING;


    RETURN NEW;

END;
$$;


DROP TRIGGER IF EXISTS
on_auth_user_created
ON auth.users;


CREATE TRIGGER
on_auth_user_created
AFTER INSERT
ON auth.users
FOR EACH ROW
EXECUTE FUNCTION
public.handle_new_user();


GRANT SELECT, UPDATE
ON public.profiles
TO authenticated;


-- =========================================================
-- DETECTIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS public.detections (

    id UUID PRIMARY KEY
        DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL
        REFERENCES auth.users(id)
        ON DELETE CASCADE,

    image_path TEXT NOT NULL,

    original_filename TEXT,

    mime_type TEXT,

    file_size_bytes BIGINT,

    image_width INTEGER,

    image_height INTEGER,

    image_format TEXT,

    quality_score NUMERIC(5, 2),

    quality_status TEXT,

    source TEXT NOT NULL
        DEFAULT 'upload',

    species TEXT,

    predicted_breed TEXT,

    confidence NUMERIC(6, 5),

    top_predictions JSONB,

    model_version TEXT,

    review_status TEXT NOT NULL
        DEFAULT 'pending',

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    CONSTRAINT detections_quality_score_check
    CHECK (
        quality_score IS NULL
        OR (
            quality_score >= 0
            AND quality_score <= 100
        )
    ),

    CONSTRAINT detections_confidence_check
    CHECK (
        confidence IS NULL
        OR (
            confidence >= 0
            AND confidence <= 1
        )
    ),

    CONSTRAINT detections_source_check
    CHECK (
        source IN (
            'upload',
            'camera'
        )
    ),

    CONSTRAINT detections_review_status_check
    CHECK (
        review_status IN (
            'pending',
            'verified',
            'rejected',
            'needs_review'
        )
    )
);


ALTER TABLE public.detections
ENABLE ROW LEVEL SECURITY;


DROP POLICY IF EXISTS
"Users can view own detections"
ON public.detections;


CREATE POLICY
"Users can view own detections"
ON public.detections
FOR SELECT
TO authenticated
USING (
    (SELECT auth.uid()) =
    user_id
);


DROP POLICY IF EXISTS
"Users can create own detections"
ON public.detections;


CREATE POLICY
"Users can create own detections"
ON public.detections
FOR INSERT
TO authenticated
WITH CHECK (
    (SELECT auth.uid()) =
    user_id
);


DROP POLICY IF EXISTS
"Users can delete own detections"
ON public.detections;


CREATE POLICY
"Users can delete own detections"
ON public.detections
FOR DELETE
TO authenticated
USING (
    (SELECT auth.uid()) =
    user_id
);


CREATE INDEX IF NOT EXISTS
detections_user_created_at_idx
ON public.detections (
    user_id,
    created_at DESC
);


GRANT
    SELECT,
    INSERT,
    DELETE
ON public.detections
TO authenticated;


-- =========================================================
-- PRIVATE STORAGE POLICIES
--
-- Required bucket:
-- detection-images
--
-- Bucket must remain PRIVATE.
-- =========================================================

DROP POLICY IF EXISTS
"Users can upload own detection images"
ON storage.objects;


CREATE POLICY
"Users can upload own detection images"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id =
        'detection-images'

    AND

    SPLIT_PART(
        name,
        '/',
        1
    ) = (
        SELECT auth.uid()::text
    )
);


DROP POLICY IF EXISTS
"Users can view own detection images"
ON storage.objects;


CREATE POLICY
"Users can view own detection images"
ON storage.objects
FOR SELECT
TO authenticated
USING (
    bucket_id =
        'detection-images'

    AND

    SPLIT_PART(
        name,
        '/',
        1
    ) = (
        SELECT auth.uid()::text
    )
);


DROP POLICY IF EXISTS
"Users can delete own detection images"
ON storage.objects;


CREATE POLICY
"Users can delete own detection images"
ON storage.objects
FOR DELETE
TO authenticated
USING (
    bucket_id =
        'detection-images'

    AND

    SPLIT_PART(
        name,
        '/',
        1
    ) = (
        SELECT auth.uid()::text
    )
);