import {
  supabase,
} from "../lib/supabaseClient";


const getCurrentUser =
  async () => {

    const {
      data: {
        user,
      },
      error,
    } =
      await supabase.auth
        .getUser();


    if (error) {
      throw error;
    }


    if (!user) {

      throw new Error(
        "You must be signed in to use the AI Assistant."
      );
    }


    return user;
  };


export const getConversations =
  async () => {

    await getCurrentUser();


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "chat_conversations"
        )
        .select("*")
        .order(
          "updated_at",
          {
            ascending:
              false,
          }
        );


    if (error) {
      throw error;
    }


    return data || [];
  };


export const createConversation =
  async (
    title = "New chat"
  ) => {

    const user =
      await getCurrentUser();


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "chat_conversations"
        )
        .insert({
          user_id:
            user.id,

          title:
            title.trim() ||
            "New chat",
        })
        .select()
        .single();


    if (error) {
      throw error;
    }


    return data;
  };


export const deleteConversation =
  async (
    conversationId
  ) => {

    await getCurrentUser();


    const {
      error,
    } =
      await supabase
        .from(
          "chat_conversations"
        )
        .delete()
        .eq(
          "id",
          conversationId
        );


    if (error) {
      throw error;
    }


    return {
      success:
        true,
    };
  };


export const getConversationMessages =
  async (
    conversationId
  ) => {

    if (!conversationId) {

      return [];
    }


    await getCurrentUser();


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "chat_messages"
        )
        .select("*")
        .eq(
          "conversation_id",
          conversationId
        )
        .order(
          "created_at",
          {
            ascending:
              true,
          }
        );


    if (error) {
      throw error;
    }


    return data || [];
  };


export const saveChatMessage =
  async ({
    conversationId,
    role,
    content,
    metadata = {},
  }) => {

    const user =
      await getCurrentUser();


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "chat_messages"
        )
        .insert({
          conversation_id:
            conversationId,

          user_id:
            user.id,

          role,

          content,

          metadata,
        })
        .select()
        .single();


    if (error) {
      throw error;
    }


    const {
      error:
        updateError,
    } =
      await supabase
        .from(
          "chat_conversations"
        )
        .update({
          updated_at:
            new Date()
              .toISOString(),
        })
        .eq(
          "id",
          conversationId
        );


    if (updateError) {

      console.warn(
        "Conversation timestamp update failed:",
        updateError
      );
    }


    return data;
  };