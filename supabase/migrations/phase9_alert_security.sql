-- =========================================================
-- BREEDVISION AI
-- PHASE 9
-- ALERT OWNERSHIP SECURITY
-- =========================================================


DROP POLICY IF EXISTS
"Users can create own alerts"
ON public.alerts;


CREATE POLICY
"Users can create own alerts"
ON public.alerts
FOR INSERT
TO authenticated
WITH CHECK (

    user_id =
        (SELECT auth.uid())

    AND

    (
        detection_id IS NULL

        OR EXISTS (

            SELECT 1

            FROM public.detections d

            WHERE
                d.id = detection_id
                AND
                d.user_id =
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



DROP POLICY IF EXISTS
"Users can update own alerts"
ON public.alerts;


CREATE POLICY
"Users can update own alerts"
ON public.alerts
FOR UPDATE
TO authenticated
USING (
    user_id =
        (SELECT auth.uid())
)
WITH CHECK (

    user_id =
        (SELECT auth.uid())

    AND

    (
        detection_id IS NULL

        OR EXISTS (

            SELECT 1

            FROM public.detections d

            WHERE
                d.id = detection_id
                AND
                d.user_id =
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