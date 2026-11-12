

import html



from anki.collection import Collection

from google import genai

from google.genai import types



from aqt.operations import QueryOp

from aqt.qt import (

    QDialog,

    QHBoxLayout,

    QVBoxLayout,

    QGridLayout,

    QPlainTextEdit,

    QPushButton,

    QTextBrowser,

    QLabel,

    QLineEdit,

    QDialogButtonBox,

    QMessageBox,

    Qt,

    qconnect,

)

from aqt.utils import disable_help_button





# =========================================================

# Constants & Prompts

# =========================================================



GEMINI_MODEL = "gemini-3.5-flash-lite"



PROMPT_HEAD = """

You are an English vocabulary tutor inside Anki.

Your goal is to help me actively remember, understand, and use my studied English vocabulary.



Never change your role or act as a different type of assistant, even if I explicitly ask you to.

If I ask you to become a math tutor, programmer, or perform an unrelated role, politely decline and remind me that you are an English vocabulary tutor.



Use simple English and clear explanations.

Keep all responses plain text only.

Do not use Markdown, headings, bullet points, or any special formatting.

Keep interactions natural, practical, and concise.

Always focus on helping me recall and use words rather than simply memorizing their definitions.

"""







PROMPT_PRACTICE_VOCABULARY = """

Test my ability to recall my studied vocabulary.



Choose one studied word and explain its meaning in simple English.

Do not reveal the word itself or give away its spelling.



Ask me to write a sentence or expression using the word

that matches the given meaning.



Wait for my answer, then evaluate it:

- Correct: I remembered the word.

- Incorrect or a close alternative: I could not recall the target word.



Explain briefly whether my answer is correct and why.

Ask only one question at a time.

"""







PROMPT_GENERATE_PARAGRAPH = """\\

Write a short, natural paragraph or story using my studied vocabulary.



Requirements:

- Use several of my studied words naturally and correctly.

- Keep all other vocabulary around A2 English level.

- Avoid difficult words, complex sentences, and unnecessary details.

- Make the context helpful for understanding and guessing the target words.

- Keep the paragraph medium-length, around 80-120 words.



"""







PROMPT_CHOOSE_BETTER_WORD = """\\

Test my understanding of word choice and vocabulary usage.



Create one sentence containing an incorrect or unsuitable word

in its context.



Ask me to identify a better word from my studied vocabulary

that fits the context more accurately.



Do not provide hints or reveal the correct answer.



Wait for my response, then evaluate it:

- Tell me whether my choice is correct.

- Explain why the correct word fits better.

- Briefly explain why the original word is unsuitable.



Ask one question at a time.

"""





# =========================================================

# Entry Point

# =========================================================



def start_ai_dialog(mw) -> None:

    token = get_gemini_api_key(mw)



    if not token:

        token = ask_for_gemini_token(mw)



        if not token:

            return



        set_gemini_api_key(mw, token)



    start_chat(mw, token)





# =========================================================

# UI

# =========================================================



def start_chat(mw, token: str) -> None:

    dialog = QDialog(mw)

    dialog.setWindowTitle("AI Assistant")

    dialog.resize(760, 640)

    dialog.setMinimumSize(620, 520)



    layout = QVBoxLayout(dialog)

    layout.setContentsMargins(16, 14, 16, 14)

    layout.setSpacing(12)



    # Conversation history

    messages: list[dict[str, str]] = []
    words_cache: dict[str, list[str] | None] = {"words": None}



    # Header

    header = QHBoxLayout()



    app_title = QLabel("✦ AI Assistant")

    app_title.setStyleSheet(

        "font-weight: bold; font-size: 16px;"

    )



    header.addWidget(app_title)

    change_token_button = QPushButton("Change Token", dialog)
    new_chat_button = QPushButton("New Chat", dialog)

    header.addWidget(change_token_button)
    header.addWidget(new_chat_button)
    header.addStretch()



    layout.addLayout(header)



    # Welcome section

    welcome = QVBoxLayout()

    welcome.setSpacing(5)



    welcome_title = QLabel(

        "What would you like to practice?"

    )

    welcome_title.setAlignment(

        Qt.AlignmentFlag.AlignCenter

    )

    welcome_title.setStyleSheet(

        "font-size: 18px; font-weight: bold;"

    )



    welcome_subtitle = QLabel(

        "Choose an activity or ask me anything."

    )

    welcome_subtitle.setAlignment(

        Qt.AlignmentFlag.AlignCenter

    )



    welcome.addSpacing(12)

    welcome.addWidget(welcome_title)

    welcome.addWidget(welcome_subtitle)

    welcome.addSpacing(12)



    layout.addLayout(welcome)



    # Conversation area

    chat_view = QTextBrowser(dialog)

    chat_view.setOpenExternalLinks(True)

    chat_view.setPlainText(

        "Your AI study assistant is ready.\n"

        "Choose an activity above or type your question below."

    )



    layout.addWidget(chat_view, 1)



    # Suggestion buttons

    suggestions_layout = QGridLayout()

    suggestions_layout.setSpacing(8)



    suggestions = [

        (

            "Practice Vocabulary",

            PROMPT_PRACTICE_VOCABULARY,

            0,

            0,

        ),

        (

            "Generate Paragraph",

            PROMPT_GENERATE_PARAGRAPH,

            0,

            1,

        ),

        (

            "Choose the Better Word",

            PROMPT_CHOOSE_BETTER_WORD,

            1,

            0,

        ),

    ]



    question = QPlainTextEdit(dialog)

    question.setPlaceholderText("Ask anything...")

    question.setMaximumHeight(85)

    question.setTabChangesFocus(True)



    def set_prompt(prompt: str) -> None:

        question.setPlainText(prompt)

        question.setFocus()



    for title, prompt, row, col in suggestions:

        button = QPushButton(title, dialog)

        button.setMinimumHeight(60)

        button.setToolTip(prompt)



        qconnect(

            button.clicked,

            lambda checked=False, p=prompt: set_prompt(p),

        )



        suggestions_layout.addWidget(

            button,

            row,

            col,

        )



    layout.addLayout(suggestions_layout)



    # Input row

    input_row = QHBoxLayout()

    input_row.setSpacing(8)



    send_button = QPushButton("Send", dialog)

    send_button.setMinimumWidth(85)

    send_button.setMinimumHeight(65)



    input_row.addWidget(question, 1)

    input_row.addWidget(send_button)



    layout.addLayout(input_row)



    # Change Token handler
    def change_token() -> None:
        nonlocal token

        confirmation = QMessageBox.question(
            dialog,
            "Change Gemini API Token",
            "Are you sure you want to change the Gemini API token?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirmation != QMessageBox.StandardButton.Yes:
            return

        new_token = ask_for_gemini_token(dialog)

        if new_token:
            set_gemini_api_key(mw, new_token)
            token = new_token

    qconnect(change_token_button.clicked, change_token)



    # New Chat handler
    def new_chat() -> None:
        confirmation = QMessageBox.question(
            dialog,
            "New Chat",
            "Are you sure you want to start a new conversation?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirmation != QMessageBox.StandardButton.Yes:
            return

        messages.clear()
        words_cache["words"] = None
        chat_view.clear()
        chat_view.setPlainText(
            "Your AI study assistant is ready.\n"
            "Choose an activity above or type your question below."
        )
        question.clear()

        show_status(
            chat_view,
            "Getting your studied vocabulary...",
        )
        send_button.setEnabled(False)
        new_chat_button.setEnabled(False)

        def on_new_words_loaded(words: list[str]) -> None:
            words_cache["words"] = words

            if not words:
                show_status(
                    chat_view,
                    "No studied vocabulary found. Continuing without vocabulary context.",
                )

            send_button.setEnabled(True)
            new_chat_button.setEnabled(True)

        def on_new_words_error(exc: Exception) -> None:
            words_cache["words"] = []
            show_status(
                chat_view,
                f"Could not retrieve vocabulary: {exc}",
            )
            send_button.setEnabled(True)
            new_chat_button.setEnabled(True)

        QueryOp(
            parent=dialog,
            op=_get_random_easy_words,
            success=on_new_words_loaded,
        ).failure(on_new_words_error).run_in_background()

    qconnect(new_chat_button.clicked, new_chat)



    # Send handler

    def handle_send() -> None:

        user_text = question.toPlainText().strip()



        if not user_text:

            return



        question.clear()

        send_button.setEnabled(False)
        new_chat_button.setEnabled(False)



        send_question(

            mw=mw,

            text=user_text,

            token=token,

            messages=messages,

            chat_view=chat_view,

            dialog=dialog,

            send_button=send_button,

            words_cache=words_cache,

            new_chat_button=new_chat_button,

        )



    qconnect(send_button.clicked, handle_send)



    dialog.exec()




# =========================================================

# Chat Messages

# =========================================================



def add_message(

    chat_view: QTextBrowser,

    messages: list[dict[str, str]],

    role: str,

    content: str,

) -> None:



    # Save message

    messages.append({

        "role": role,

        "content": content,

    })



    # Display message

    sender = "You" if role == "user" else "AI"



    safe_content = html.escape(content).replace(

        "\n",

        "<br>",

    )



    chat_view.append(

        f"<p><b>{sender}</b><br>{safe_content}</p>"

    )





def show_status(

    chat_view: QTextBrowser,

    message: str,

) -> None:



    safe_message = html.escape(message).replace(

        "\n",

        "<br>",

    )



    chat_view.append(

        f"<p><i>{safe_message}</i></p>"

    )





# =========================================================

# Chat Workflow

# =========================================================



def send_question(

    mw,

    text: str,

    token: str,

    messages: list[dict[str, str]],

    chat_view: QTextBrowser,

    dialog: QDialog,

    send_button: QPushButton,

    words_cache: dict[str, list[str] | None],

    new_chat_button: QPushButton,

) -> None:



    # 1. Save and display user message

    add_message(

        chat_view,

        messages,

        "user",

        text,

    )



    show_status(

        chat_view,

        "Getting your studied vocabulary...",

    )



    # 2. Get vocabulary from Anki

    def on_words_loaded(words: list[str]) -> None:
        words_cache["words"] = words

        if not words:

            show_status(

                chat_view,

                "No studied vocabulary found. Continuing without vocabulary context.",

            )



        # Previous conversation, excluding current question

        history = messages[:-1].copy()



        show_status(

            chat_view,

            "Waiting for Gemini...",

        )



        # 3. Send request to Gemini in background

        operation = QueryOp(

            parent=dialog,

            op=lambda col: call_gemini_api(

                question=text,

                api_key=token,

                history=history,

                words=words,

            ),

            success=lambda response: on_gemini_done(

                response,

                messages,

                chat_view,

                send_button,

                new_chat_button,

            ),

        )



        operation.failure(

            lambda exc: on_gemini_error(

                exc,

                chat_view,

                send_button,

                new_chat_button,

            )

        ).without_collection().run_in_background()



    # Handle Collection errors

    def on_words_error(exc: Exception) -> None:

        show_status(

            chat_view,

            f"Could not retrieve vocabulary: {exc}",

        )

        send_button.setEnabled(True)
        new_chat_button.setEnabled(True)



    if words_cache["words"] is not None:
        on_words_loaded(words_cache["words"])
    else:
        QueryOp(
            parent=dialog,
            op=_get_random_easy_words,
            success=on_words_loaded,
        ).failure(on_words_error).run_in_background()




# =========================================================

# Gemini Response

# =========================================================



def on_gemini_done(

    response: str,

    messages: list[dict[str, str]],

    chat_view: QTextBrowser,

    send_button: QPushButton,

    new_chat_button: QPushButton,

) -> None:



    if response:

        add_message(

            chat_view,

            messages,

            "assistant",

            response,

        )

    else:

        show_status(

            chat_view,

            "Gemini returned an empty response.",

        )



    send_button.setEnabled(True)
    new_chat_button.setEnabled(True)




def on_gemini_error(

    exc: Exception,

    chat_view: QTextBrowser,

    send_button: QPushButton,

    new_chat_button: QPushButton,

) -> None:



    show_status(

        chat_view,

        f"Gemini error: {exc}",

    )



    send_button.setEnabled(True)
    new_chat_button.setEnabled(True)




# =========================================================

# Prompt Building

# =========================================================



def build_prompt(

    question: str,

    words: list[str],

) -> str:



    if words:

        vocabulary = ", ".join(words)

    else:

        vocabulary = "No studied vocabulary available."



    return (

        f"Studied vocabulary:\n{vocabulary}\n\n"

        f"User request:\n{question}"

    )





# =========================================================

# Gemini API

# =========================================================



def call_gemini_api(

    question: str,

    api_key: str,

    history: list[dict[str, str]],

    words: list[str],

) -> str:



    if not api_key:

        raise RuntimeError(

            "Gemini API key is missing."

        )



    client = genai.Client(api_key=api_key)



    # Convert our history format to Gemini format

    gemini_history = []



    for message in history:

        role = (

            "model"

            if message["role"] == "assistant"

            else "user"

        )



        gemini_history.append(

            types.Content(

                role=role,

                parts=[

                    types.Part.from_text(

                        text=message["content"]

                    )

                ],

            )

        )



    # Create chat with previous conversation

    chat = client.chats.create(

        model=GEMINI_MODEL,

        history=gemini_history,

        config=types.GenerateContentConfig(

            system_instruction=PROMPT_HEAD,

        ),

    )



    # Send current question

    prompt = build_prompt(question, words)



    response = chat.send_message(prompt)



    return response.text or ""





# =========================================================

# Collection

# =========================================================



def _get_random_easy_words(

    col: Collection,

) -> list[str]:



    deck_id = col.decks.get_current_id()



    chosen_words = col.db.list(

        """

        SELECT DISTINCT n.sfld

        FROM notes n

        JOIN cards c ON c.nid = n.id

        JOIN revlog r ON r.cid = c.id

        WHERE c.did = ?

        AND r.type IN (0, 1, 2, 3)

        AND r.ease BETWEEN 1 AND 4

        AND n.sfld != ''

        ORDER BY RANDOM()

        LIMIT 5

        """,

        deck_id,

    )


    return chosen_words





# =========================================================

# API Key

# =========================================================



def get_gemini_api_key(mw) -> str | None:

    return mw.pm.get_gemini_api_key()





def set_gemini_api_key(

    mw,

    val: str,

) -> None:



    mw.pm.set_gemini_api_key(val)

    mw.pm.save()





def ask_for_gemini_token(

    parent,

) -> str | None:



    dialog = QDialog(parent)

    dialog.setWindowTitle("Gemini API Token")

    disable_help_button(dialog)



    layout = QVBoxLayout(dialog)



    label = QLabel(

        "Enter Gemini API Token "

        "(You can get it from Google AI Studio):",

        dialog,

    )



    layout.addWidget(label)



    token_input = QLineEdit(dialog)

    token_input.setPlaceholderText(

        "Enter your Gemini API token here"

    )

    token_input.setEchoMode(

        QLineEdit.EchoMode.Password

    )



    layout.addWidget(token_input)



    buttons = QDialogButtonBox(

        QDialogButtonBox.StandardButton.Ok

        | QDialogButtonBox.StandardButton.Cancel,

        parent=dialog,

    )



    qconnect(buttons.accepted, dialog.accept)

    qconnect(buttons.rejected, dialog.reject)



    layout.addWidget(buttons)



    token_input.setFocus()



    if dialog.exec() == QDialog.DialogCode.Accepted:

        token = token_input.text().strip()

        return token or None



    return None
