-- =========================================================
-- PHASE 9 REVIEW WORKFLOW VERIFICATION
-- READ ONLY
-- =========================================================


-- Review function exists

SELECT

    routine_name,

    routine_type

FROM
    information_schema.routines

WHERE
    routine_schema = 'public'

    AND

    routine_name =
        'review_detection';



-- Detection UPDATE policy exists

SELECT

    tablename,

    policyname,

    cmd

FROM
    pg_policies

WHERE
    schemaname = 'public'

    AND

    tablename IN (
        'detections',
        'detection_reviews',
        'animals'
    )

ORDER BY
    tablename,
    policyname;



-- Detection UPDATE privilege

SELECT

    grantee,

    table_name,

    privilege_type,

    column_name

FROM
    information_schema.column_privileges

WHERE
    table_schema = 'public'

    AND

    table_name = 'detections'

    AND

    grantee = 'authenticated'

ORDER BY
    column_name;