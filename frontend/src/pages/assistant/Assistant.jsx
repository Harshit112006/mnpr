import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import ReactMarkdown
  from "react-markdown";

import remarkGfm
  from "remark-gfm";

import {
  Bot,
  Check,
  Copy,
  LoaderCircle,
  MessageSquare,
  Plus,
  Send,
  Sparkles,
  Trash2,
} from "lucide-react";

import {
  sendAssistantMessage,
} from "../../services/assistantService";

import {
  createConversation,
  deleteConversation,
  getConversationMessages,
  getConversations,
  saveChatMessage,
} from "../../services/assistantDataService";

import "../../styles/Assistant.css";


const STARTERS = [

  {
    title:
      "BreedVision",

    prompt:
      "Explain how BreedVision AI identifies cattle and buffalo breeds.",
  },

  {
    title:
      "Coding",

    prompt:
      "Explain REST APIs in simple Hinglish with an example.",
  },

  {
    title:
      "Hindi",

    prompt:
      "क्लाउड कंप्यूटिंग को आसान हिंदी में समझाओ।",
  },

  {
    title:
      "General",

    prompt:
      "Explain how the internet works in simple language.",
  },

];


const makeTitle = (
  text
) => {

  const cleaned =
    text
      .replace(
        /\s+/g,
        " "
      )
      .trim();


  return (
    cleaned.length <= 48

      ? cleaned

      : (
        cleaned.slice(
          0,
          48
        )
        +
        "..."
      )
  );
};


function Assistant() {

  const [
    conversations,
    setConversations,
  ] = useState([]);


  const [
    activeConversationId,
    setActiveConversationId,
  ] = useState(null);


  const [
    messages,
    setMessages,
  ] = useState([]);


  const [
    input,
    setInput,
  ] = useState("");


  const [
    loading,
    setLoading,
  ] = useState(false);


  const [
    historyLoading,
    setHistoryLoading,
  ] = useState(true);


  const [
    error,
    setError,
  ] = useState("");


  const [
    copiedId,
    setCopiedId,
  ] = useState(null);


  const messagesEndRef =
    useRef(null);


  const loadConversations =
    useCallback(
      async () => {

        try {

          setHistoryLoading(
            true
          );


          const rows =
            await getConversations();


          setConversations(
            rows
          );


          return rows;

        }

        finally {

          setHistoryLoading(
            false
          );
        }
      },
      []
    );


  const openConversation =
    useCallback(
      async (
        id
      ) => {

        try {

          setError("");

          setActiveConversationId(
            id
          );


          const rows =
            await getConversationMessages(
              id
            );


          setMessages(
            rows
          );

        }

        catch (
          loadError
        ) {

          setError(
            loadError.message ||
            "Unable to load conversation."
          );
        }
      },
      []
    );


  useEffect(() => {

    const initialize =
      async () => {

        try {

          const rows =
            await loadConversations();


          if (
            rows.length > 0
          ) {

            await openConversation(
              rows[0].id
            );
          }

        }

        catch (
          initError
        ) {

          setError(
            initError.message ||
            "Unable to initialize AI Assistant."
          );
        }
      };


    initialize();

  }, [
    loadConversations,
    openConversation,
  ]);


  useEffect(() => {

    messagesEndRef
      .current
      ?.scrollIntoView({
        behavior:
          "smooth",
      });

  }, [
    messages,
    loading,
  ]);


  const newChat =
    () => {

      setActiveConversationId(
        null
      );

      setMessages([]);

      setInput("");

      setError("");
    };


  const copyMessage =
    async (
      message
    ) => {

      try {

        await navigator
          .clipboard
          .writeText(
            message.content
          );


        setCopiedId(
          message.id
        );


        setTimeout(
          () =>
            setCopiedId(
              null
            ),
          1400
        );

      }

      catch {

        setError(
          "Could not copy response."
        );
      }
    };


  const removeConversation =
    async (
      conversation
    ) => {

      const confirmed =
        window.confirm(
          `Delete "${conversation.title}"?`
        );


      if (!confirmed) {

        return;
      }


      try {

        await deleteConversation(
          conversation.id
        );


        const remaining =
          conversations.filter(
            (
              item
            ) =>
              item.id !==
              conversation.id
          );


        setConversations(
          remaining
        );


        if (
          activeConversationId ===
          conversation.id
        ) {

          if (
            remaining.length > 0
          ) {

            await openConversation(
              remaining[0].id
            );

          }

          else {

            newChat();

          }
        }

      }

      catch (
        deleteError
      ) {

        setError(
          deleteError.message ||
          "Unable to delete conversation."
        );
      }
    };


  const sendMessage =
    async (
      rawMessage
    ) => {

      const message =
        String(
          rawMessage
        )
        .trim();


      if (
        !message
        ||
        loading
      ) {

        return;
      }


      setLoading(
        true
      );

      setError("");

      setInput("");


      try {

        let conversationId =
          activeConversationId;


        if (!conversationId) {

          const conversation =
            await createConversation(
              makeTitle(
                message
              )
            );


          conversationId =
            conversation.id;


          setActiveConversationId(
            conversationId
          );


          setConversations(
            (
              previous
            ) => [
              conversation,
              ...previous,
            ]
          );
        }


        const oldMessages =
          messages;


        const userRecord =
          await saveChatMessage({
            conversationId,

            role:
              "user",

            content:
              message,
          });


        setMessages(
          (
            previous
          ) => [
            ...previous,
            userRecord,
          ]
        );


        const history =
          oldMessages
            .slice(
              -16
            )
            .map(
              (
                item
              ) => ({
                role:
                  item.role,

                content:
                  item.content,
              })
            );


        const result =
          await sendAssistantMessage({
            message,

            history,

            useProjectContext:
              true,
          });


        const assistantRecord =
          await saveChatMessage({
            conversationId,

            role:
              "assistant",

            content:
              result.answer,

            metadata: {
              provider:
                result.provider,

              configured_model:
                result.configured_model,

              actual_model:
                result.actual_model,

              response_id:
                result.response_id,

              project_context_used:
                result.project_context_used,

              context_sources:
                result.context_sources,
            },
          });


        setMessages(
          (
            previous
          ) => [
            ...previous,
            assistantRecord,
          ]
        );


        await loadConversations();

      }

      catch (
        sendError
      ) {

        console.error(
          sendError
        );


        setError(
          sendError.message ||
          "Unable to generate response."
        );

      }

      finally {

        setLoading(
          false
        );
      }
    };


  const handleSubmit =
    async (
      event
    ) => {

      event.preventDefault();

      await sendMessage(
        input
      );
    };


  const handleKeyDown =
    (
      event
    ) => {

      if (
        event.key ===
        "Enter"
        &&
        !event.shiftKey
      ) {

        event.preventDefault();

        sendMessage(
          input
        );
      }
    };


  const activeConversation =
    useMemo(
      () =>
        conversations.find(
          (
            item
          ) =>
            item.id ===
            activeConversationId
        ),
      [
        conversations,
        activeConversationId,
      ]
    );


  return (
    <div className="assistant-page">

      <aside className="assistant-history">

        <div className="assistant-history-header">

          <div>

            <span>
              BREEDVISION AI
            </span>

            <h2>
              Assistant
            </h2>

          </div>


          <button
            type="button"
            onClick={
              newChat
            }
            title="New chat"
          >
            <Plus size={18} />
          </button>

        </div>


        <button
          type="button"
          className="assistant-new-chat"
          onClick={
            newChat
          }
        >
          <Plus size={16} />
          New chat
        </button>


        <div className="assistant-conversations">

          {
            historyLoading
              ? (

                <div className="assistant-history-empty">

                  <LoaderCircle
                    size={18}
                    className="assistant-spinner"
                  />

                  Loading...

                </div>

              )
              : conversations.length ===
                0
                ? (

                  <div className="assistant-history-empty">

                    <MessageSquare
                      size={23}
                    />

                    No conversations yet

                  </div>

                )
                : conversations.map(
                  (
                    conversation
                  ) => (

                    <div
                      key={
                        conversation.id
                      }
                      className={
                        `assistant-conversation ${
                          conversation.id ===
                          activeConversationId
                            ? "active"
                            : ""
                        }`
                      }
                    >

                      <button
                        type="button"
                        className="assistant-conversation-open"
                        onClick={() =>
                          openConversation(
                            conversation.id
                          )
                        }
                      >
                        <MessageSquare size={15} />

                        <span>
                          {conversation.title}
                        </span>
                      </button>


                      <button
                        type="button"
                        className="assistant-delete-chat"
                        onClick={() =>
                          removeConversation(
                            conversation
                          )
                        }
                        title="Delete chat"
                      >
                        <Trash2 size={14} />
                      </button>

                    </div>

                  )
                )
          }

        </div>

      </aside>


      <section className="assistant-main">

        <header className="assistant-header">

          <div>

            <span className="assistant-eyebrow">
              GENERAL + BREEDVISION AI
            </span>

            <h1>
              {
                activeConversation
                  ?.title ||
                "How can I help?"
              }
            </h1>

          </div>


          <span className="assistant-free-badge">
            Free AI
          </span>

        </header>


        <div className="assistant-messages">

          {
            messages.length === 0
              ? (

                <div className="assistant-welcome">

                  <div className="assistant-welcome-icon">
                    <Sparkles size={30} />
                  </div>

                  <h2>
                    Ask me anything
                  </h2>

                  <p>
                    BreedVision, coding,
                    engineering, mathematics,
                    writing, Hindi, Hinglish,
                    general knowledge and more.
                  </p>


                  <div className="assistant-starter-grid">

                    {
                      STARTERS.map(
                        (
                          starter
                        ) => (

                          <button
                            key={
                              starter.title
                            }
                            type="button"
                            onClick={() =>
                              sendMessage(
                                starter.prompt
                              )
                            }
                          >
                            <strong>
                              {starter.title}
                            </strong>

                            <span>
                              {starter.prompt}
                            </span>
                          </button>

                        )
                      )
                    }

                  </div>

                </div>

              )
              : messages.map(
                (
                  message
                ) => (

                  <article
                    key={
                      message.id
                    }
                    className={
                      `assistant-message ${
                        message.role
                      }`
                    }
                  >

                    <div className="assistant-avatar">

                      {
                        message.role ===
                        "assistant"
                          ? (
                            <Bot size={18} />
                          )
                          : "You"
                      }

                    </div>


                    <div className="assistant-message-content">

                      <div className="assistant-message-heading">

                        <strong>
                          {
                            message.role ===
                            "assistant"
                              ? "BreedVision AI"
                              : "You"
                          }
                        </strong>


                        {
                          message.role ===
                          "assistant"
                          && (

                            <button
                              type="button"
                              onClick={() =>
                                copyMessage(
                                  message
                                )
                              }
                            >
                              {
                                copiedId ===
                                message.id
                                  ? (
                                    <Check size={15} />
                                  )
                                  : (
                                    <Copy size={15} />
                                  )
                              }
                            </button>

                          )
                        }

                      </div>


                      {
                        message.role ===
                        "assistant"
                          ? (

                            <div className="assistant-markdown">

                              <ReactMarkdown
                                remarkPlugins={[
                                  remarkGfm,
                                ]}
                              >
                                {message.content}
                              </ReactMarkdown>

                            </div>

                          )
                          : (

                            <p className="assistant-user-message">
                              {message.content}
                            </p>

                          )
                      }


                      {
                        message.role ===
                        "assistant"
                        &&
                        message.metadata
                          ?.actual_model
                        && (

                          <span className="assistant-model-label">

                            {
                              message.metadata
                                .actual_model
                            }

                          </span>

                        )
                      }

                    </div>

                  </article>

                )
              )
          }


          {loading && (

            <article className="assistant-message assistant">

              <div className="assistant-avatar">
                <Bot size={18} />
              </div>

              <div className="assistant-thinking">
                <span />
                <span />
                <span />
              </div>

            </article>

          )}


          <div
            ref={
              messagesEndRef
            }
          />

        </div>


        {error && (

          <div className="assistant-error">
            {error}
          </div>

        )}


        <div className="assistant-composer-wrap">

          <form
            className="assistant-composer"
            onSubmit={
              handleSubmit
            }
          >

            <textarea
              value={
                input
              }
              onChange={
                (
                  event
                ) =>
                  setInput(
                    event.target.value
                  )
              }
              onKeyDown={
                handleKeyDown
              }
              placeholder="Message BreedVision AI..."
              rows={1}
              maxLength={12000}
              disabled={
                loading
              }
            />


            <button
              type="submit"
              className="assistant-send"
              disabled={
                loading ||
                !input.trim()
              }
            >
              {
                loading
                  ? (
                    <LoaderCircle
                      size={18}
                      className="assistant-spinner"
                    />
                  )
                  : (
                    <Send size={18} />
                  )
              }
            </button>

          </form>


          <p className="assistant-disclaimer">
            AI responses may contain mistakes.
            Verify important information.
            Live web search is not enabled.
          </p>

        </div>

      </section>

    </div>
  );
}


export default Assistant;