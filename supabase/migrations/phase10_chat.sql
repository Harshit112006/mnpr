-- =========================================================
-- BREEDVISION AI
-- PHASE 10 AI ASSISTANT HISTORY
-- =========================================================


CREATE TABLE IF NOT EXISTS
public.chat_conversations (

    id UUID
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    user_id UUID
        NOT NULL
        REFERENCES auth.users(id)
        ON DELETE CASCADE,

    title TEXT
        NOT NULL
        DEFAULT 'New chat',

    created_at TIMESTAMPTZ
        NOT NULL
        DEFAULT NOW(),

    updated_at TIMESTAMPTZ
        NOT NULL
        DEFAULT NOW()
);


CREATE INDEX IF NOT EXISTS
chat_conversations_user_updated_idx
ON public.chat_conversations (
    user_id,
    updated_at DESC
);


CREATE TABLE IF NOT EXISTS
public.chat_messages (

    id UUID
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    conversation_id UUID
        NOT NULL
        REFERENCES public.chat_conversations(id)
        ON DELETE CASCADE,

    user_id UUID
        NOT NULL
        REFERENCES auth.users(id)
        ON DELETE CASCADE,

    role TEXT
        NOT NULL
        CHECK (
            role IN (
                'user',
                'assistant'
            )
        ),

    content TEXT
        NOT NULL
        CHECK (
            CHAR_LENGTH(content) > 0
        ),

    metadata JSONB
        NOT NULL
        DEFAULT '{}'::JSONB,

    created_at TIMESTAMPTZ
        NOT NULL
        DEFAULT NOW()
);


CREATE INDEX IF NOT EXISTS
chat_messages_conversation_created_idx
ON public.chat_messages (
    conversation_id,
    created_at ASC
);


ALTER TABLE
public.chat_conversations
ENABLE ROW LEVEL SECURITY;


ALTER TABLE
public.chat_messages
ENABLE ROW LEVEL SECURITY;


DROP POLICY IF EXISTS
"Users can view own chat conversations"
ON public.chat_conversations;


CREATE POLICY
"Users can view own chat conversations"
ON public.chat_conversations
FOR SELECT
TO authenticated
USING (
    user_id =
        (SELECT auth.uid())
);


DROP POLICY IF EXISTS
"Users can create own chat conversations"
ON public.chat_conversations;


CREATE POLICY
"Users can create own chat conversations"
ON public.chat_conversations
FOR INSERT
TO authenticated
WITH CHECK (
    user_id =
        (SELECT auth.uid())
);


DROP POLICY IF EXISTS
"Users can update own chat conversations"
ON public.chat_conversations;


CREATE POLICY
"Users can update own chat conversations"
ON public.chat_conversations
FOR UPDATE
TO authenticated
USING (
    user_id =
        (SELECT auth.uid())
)
WITH CHECK (
    user_id =
        (SELECT auth.uid())
);


DROP POLICY IF EXISTS
"Users can delete own chat conversations"
ON public.chat_conversations;


CREATE POLICY
"Users can delete own chat conversations"
ON public.chat_conversations
FOR DELETE
TO authenticated
USING (
    user_id =
        (SELECT auth.uid())
);


DROP POLICY IF EXISTS
"Users can view own chat messages"
ON public.chat_messages;


CREATE POLICY
"Users can view own chat messages"
ON public.chat_messages
FOR SELECT
TO authenticated
USING (

    user_id =
        (SELECT auth.uid())

    AND

    EXISTS (

        SELECT 1

        FROM
            public.chat_conversations c

        WHERE
            c.id =
                conversation_id

            AND

            c.user_id =
                (SELECT auth.uid())
    )
);


DROP POLICY IF EXISTS
"Users can create own chat messages"
ON public.chat_messages;


CREATE POLICY
"Users can create own chat messages"
ON public.chat_messages
FOR INSERT
TO authenticated
WITH CHECK (

    user_id =
        (SELECT auth.uid())

    AND

    EXISTS (

        SELECT 1

        FROM
            public.chat_conversations c

        WHERE
            c.id =
                conversation_id

            AND

            c.user_id =
                (SELECT auth.uid())
    )
);


DROP POLICY IF EXISTS
"Users can delete own chat messages"
ON public.chat_messages;


CREATE POLICY
"Users can delete own chat messages"
ON public.chat_messages
FOR DELETE
TO authenticated
USING (
    user_id =
        (SELECT auth.uid())
);


DROP TRIGGER IF EXISTS
chat_conversations_updated_at
ON public.chat_conversations;


CREATE TRIGGER
chat_conversations_updated_at

BEFORE UPDATE
ON public.chat_conversations

FOR EACH ROW

EXECUTE FUNCTION
public.set_updated_at();


GRANT
SELECT,
INSERT,
UPDATE,
DELETE
ON public.chat_conversations
TO authenticated;


GRANT
SELECT,
INSERT,
DELETE
ON public.chat_messages
TO authenticated;