-- =========================================================
-- BREEDVISION AI
-- PHASE 9 DATABASE VERIFICATION
-- READ-ONLY CHECKS
-- =========================================================


-- =========================================================
-- 1. REQUIRED TABLES
-- =========================================================

SELECT
    table_name
FROM
    information_schema.tables
WHERE
    table_schema = 'public'
    AND table_name IN (
        'farmers',
        'animals',
        'detections',
        'detection_reviews',
        'alerts'
    )
ORDER BY
    table_name;



-- =========================================================
-- 2. DETECTION LINK COLUMNS
-- =========================================================

SELECT
    column_name,
    data_type,
    is_nullable
FROM
    information_schema.columns
WHERE
    table_schema = 'public'
    AND table_name = 'detections'
    AND column_name IN (
        'farmer_id',
        'animal_id'
    )
ORDER BY
    column_name;



-- =========================================================
-- 3. RLS ENABLED
-- =========================================================

SELECT
    c.relname AS table_name,
    c.relrowsecurity AS rls_enabled
FROM
    pg_class c
JOIN
    pg_namespace n
ON
    n.oid = c.relnamespace
WHERE
    n.nspname = 'public'
    AND c.relname IN (
        'farmers',
        'animals',
        'detection_reviews',
        'alerts'
    )
ORDER BY
    c.relname;



-- =========================================================
-- 4. PHASE 9 RLS POLICIES
-- =========================================================

SELECT
    tablename,
    policyname,
    cmd
FROM
    pg_policies
WHERE
    schemaname = 'public'
    AND tablename IN (
        'farmers',
        'animals',
        'detection_reviews',
        'alerts'
    )
ORDER BY
    tablename,
    policyname;



-- =========================================================
-- 5. FOREIGN KEYS
-- =========================================================

SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column
FROM
    information_schema.table_constraints tc
JOIN
    information_schema.key_column_usage kcu
ON
    tc.constraint_name = kcu.constraint_name
    AND tc.constraint_schema = kcu.constraint_schema
JOIN
    information_schema.constraint_column_usage ccu
ON
    ccu.constraint_name = tc.constraint_name
    AND ccu.constraint_schema = tc.constraint_schema
WHERE
    tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
    AND (
        tc.table_name IN (
            'farmers',
            'animals',
            'detection_reviews',
            'alerts'
        )
        OR (
            tc.table_name = 'detections'
            AND kcu.column_name IN (
                'farmer_id',
                'animal_id'
            )
        )
    )
ORDER BY
    tc.table_name,
    kcu.column_name;



-- =========================================================
-- 6. UPDATED_AT TRIGGERS
-- =========================================================

SELECT
    event_object_table AS table_name,
    trigger_name
FROM
    information_schema.triggers
WHERE
    trigger_schema = 'public'
    AND event_object_table IN (
        'farmers',
        'animals',
        'detection_reviews'
    )
ORDER BY
    event_object_table,
    trigger_name;