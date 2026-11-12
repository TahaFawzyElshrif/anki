---
title: "Anki AI Integration"
---

Anki AI Integration adds an AI-powered English vocabulary tutor to **Anki Desktop**. It uses words the user has already studied to create practice activities and conversations.

The assistant supports Anki's normal review system; it does not replace it.

(Important - The feature is only available on Windows (x86 architecture))

## AI Assistant

The assistant opens directly from Anki Desktop and allows users to:

- Chat naturally with the AI.
- Ask their own questions.
- Practice previously studied English vocabulary.
- Continue a conversation using its existing context.

The assistant is designed primarily for English vocabulary learning.

## Learning Activities

Three predefined activities are available.

### Practice Vocabulary

Tests the user's ability to recall and use a studied word.

1. The AI selects one studied word.
2. Explains its meaning in simple English without revealing the word.
3. Asks the user to write a sentence or expression using it.
4. Evaluates the answer and briefly explains whether it is correct.

Only one question is presented at a time. The goal is to recall the target word, not just provide a similar alternative.

### Generate Paragraph

Creates a short paragraph or story using several studied words.

- Uses the selected vocabulary naturally and correctly.
- Keeps the surrounding language around **A2 level**.
- Provides context to help users understand the target words.
- Targets approximately **80–120 words**.

### Choose the Better Word

Tests vocabulary choice and understanding of context.

1. The AI creates a sentence with an incorrect or unsuitable word.
2. Asks the user to choose a better word from their studied vocabulary.
3. Waits for the answer without revealing the solution or giving hints.
4. Evaluates the answer and explains why the replacement fits better.

Only one question is presented at a time.

## Vocabulary Selection

The assistant retrieves vocabulary from the **currently selected deck** in the user's Anki Collection.

The `_get_random_easy_words()` function:

1. Gets the current deck ID.
2. Queries the `notes`, `cards`, and `revlog` tables.
3. Selects distinct note field values using `n.sfld`.
4. Filters review log types (`r.type IN (0, 1, 2, 3)`) and ease values (`r.ease BETWEEN 1 AND 4`).
5. Excludes empty values and randomly selects up to **5 words**.

### Vocabulary Cache

The selected words are stored in `words_cache` for the current conversation.

- The same vocabulary is reused for subsequent messages.
- The list is refreshed when the user starts **New Chat**.
- Caching prevents the vocabulary from changing during an ongoing conversation.

If no matching studied words are found, the assistant displays a status message and continues without vocabulary context. Users can still chat with the assistant.

## AI Integration

The integration uses **Google Gemini** through the `google-genai` Python SDK.

**Configured model:** `gemini-3.5-flash-lite`

The Gemini client is initialized with the user's API key. The system instruction tells the model to:

- Act as an English vocabulary tutor.
- Help users recall, understand, and use studied words.
- Use simple English and concise explanations.
- Keep the conversation focused on vocabulary learning.
- Return plain text without Markdown or special formatting.

Each request combines the selected vocabulary with the user's message. Previous messages are converted to Gemini conversation history (`assistant` → `model`, `user` → `user`).

## Conversation

Messages are kept in memory as a `list[dict[str, str]]`. Each message contains a `role` and `content`.

When a user sends a message, the integration:

1. Adds and displays the message.
2. Retrieves the vocabulary or reuses the cached list.
3. Converts previous messages into Gemini history.
4. Sends the request to Gemini.
5. Displays and stores the response.

### New Chat

Selecting **New Chat** asks for confirmation, then:

- Clears the conversation and chat view.
- Resets the vocabulary cache.
- Clears the input field.
- Retrieves studied vocabulary again.

Conversation history is kept only during the active chat session. It is not persistently stored.

## Interface

The assistant opens in a Qt dialog integrated into Anki Desktop.

| Setting | Value |
|---|---|
| Window title | AI Assistant |
| Initial size | 760 × 640 |
| Minimum size | 620 × 520 |

The interface includes:

- **Change Token** — replaces the Gemini API key.
- **New Chat** — starts a fresh conversation.
- **Chat View** — displays messages and status updates.
- **Practice Vocabulary** — prepares a recall exercise.
- **Generate Paragraph** — prepares a paragraph request.
- **Choose the Better Word** — prepares a word-choice exercise.
- **Text Input / Send** — sends custom requests.

Send and New Chat are disabled while a request is processing. The interface displays loading and error states, and users can resend a request manually after an error. There is no dedicated Retry button.

## API Key

The Gemini API key is stored using Python `keyring` in the operating system's credential storage, rather than ordinary profile configuration data.

When the assistant opens:

1. It checks for a saved API key.
2. If none is found, it asks the user to enter one.
3. The key is entered in a password field and saved to the OS Keyring.

To replace the key, select **Change Token**, confirm the action, and enter the new key. The current session uses the updated key for subsequent requests.

## Anki Integration

The assistant is launched through `start_ai_dialog()`.

An action named `studyByAI()` was added to the Anki Overview interface. It calls `start_ai_dialog(self.mw)` through the `study_by_ai` URL handler.

Main Anki components used:

- **Collection** — accesses the Anki collection and database.
- **QueryOp** — runs collection-related work in the background.
- **Profile Manager (`mw.pm`)** — accesses profile-related information.
- **Qt (`aqt.qt`)** — builds the interface and handles interactions.

## Background Operations

Time-consuming work runs through Anki's `QueryOp` so the main interface remains responsive.

- Vocabulary retrieval runs `_get_random_easy_words()` in the background.
- Gemini requests use `QueryOp.without_collection()`.
- Success and failure callbacks update the interface.
- Send and New Chat are re-enabled when processing finishes.

## Dependencies

The documented additional packages are:

- `google-genai` — Gemini API integration.
- `keyring` — operating system credential storage.

The exact dependency versions and other build changes are not specified in the current documentation.

## Testing

The recorded tests passed for:

- Practice Vocabulary.
- Generate Paragraph.
- Choose the Better Word.
- Topic-based chat.
- Working while another dictionary is open.
- Changing the API token.
- Keeping vocabulary stable during a conversation.
- Interface resizing at 1366 × 768, 800 × 600, and 1280 × 720.

Unrelated Arabic, mathematics, and other-skill requests were redirected toward the tutor's intended role.

Prompt-injection resistance was **partially verified**. Crash isolation was observed during use, but was not formally tested.

## Limitations

- Conversation history is not saved after the active session.
- Requests require an internet connection and a valid Gemini API key.
- The interface is currently supported only on English.
- The feature is only available on Windows (x86 architecture).

## Build

The Windows installer was successfully built using **MSVC Platform Toolset v143 (Visual Studio 2022)**. Toolset v145 was not used or tested.
