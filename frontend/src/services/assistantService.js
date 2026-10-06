import api
  from "./api";


export const sendAssistantMessage =
  async ({
    message,
    history = [],
    useProjectContext = true,
  }) => {

    try {

      const response =
        await api.post(
          "/api/assistant/chat",
          {
            message,

            history,

            use_project_context:
              useProjectContext,
          }
        );


      return response.data;

    }

    catch (error) {

      if (
        error?.code ===
        "ERR_NETWORK"
      ) {

        throw new Error(
          "BreedVision AI Assistant backend is unreachable. Check that the backend server is running."
        );
      }


      const detail =
        error
          ?.response
          ?.data
          ?.detail;


      throw new Error(
        detail ||
        "The AI Assistant could not complete the request."
      );
    }
  };