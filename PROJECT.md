# Project Requirements Document (PRD)

---
Status: DRAFT
Owner: Dan
Designer: Dan
Developer: Dan
Target Release Date: 2025-08-03
---

## 1. Goals and Objectives

**Premise:**
Develop a web application that provides personalized book recommendations through a conversational chatbot interface. The chatbot will engage users in a structured dialogue to elicit nuanced reading preferences and recommend books accordingly.

**End Product:**
A web application for book enthusiasts, featuring a chatbot as the primary interface, which recommends books based on user input and conversation history.

**Objectives:**
- Enable users to discover books beyond their usual preferences through conversation.
- Provide recommendations supported by specific conversation points and, where possible, direct book quotations.
- Continuously refine recommendations based on ongoing user interaction.

## 2. Background and Strategic Fit

**Challenges:**
 - Google search can be a very efficient way to find books of interest, but still requires some time for the user to persue or skim the "top 10 books..." lists that come up.
 - Sometimes the books a user wants to find is not a simple matter of subject matter or genre - and this becomes harder for a Google search to satisfy because:
   - writing out everything in search feels too time consuming
   - Google search results are sorted more by a general popularity of sites without much attention to th user's nuanced particular interests.
- Traditional search engines and book lists do not capture nuanced user preferences.
- Users may lack the time or inclination to articulate detailed search queries.
- Popularity-based search results may not align with individual tastes.

**Opportunities:**
- Leverage large language models (LLMs) and retrieval-augmented generation (RAG) to provide context-aware recommendations.
- Utilize full-text book datasets to enable recommendations based on writing style, themes, and content.

## 3. Assumptions
- Users may have only general ideas about their reading preferences.
- Users are open to exploring new genres, authors, and styles.
- The application will initially run locally (no cloud deployment required).

## 4. User Stories

1. As a user, I want to interact with a chatbot that asks me at least 10 questions about my reading and storytelling interests, so that it can understand my preferences.
2. As a user, I want to receive book recommendations in the form of a grid of book cover images, so that I can visually browse options.
3. As a user, I want to click on a book cover to view its title, author, and synopsis, so that I can learn more about each recommendation.
4. As a user, I want the chatbot to explain why it recommended a particular book, referencing either my conversation or the book's text, so that I understand the rationale behind the recommendation.

## 5. Functional Requirements

### 5.1 Chatbot Interaction
- The chatbot shall initiate a conversation with the user upon arrival at the website.
- The chatbot shall ask a minimum of 10 questions per user session, covering:
  - General storytelling interests (books, film, TV, podcasts, etc.)
  - Past reading experiences
  - Current interests and disinterests
- The chatbot shall store the conversation log in browser local storage during the session.

### 5.2 Book Recommendation
- The system shall recommend at least 3 books at the end of each conversation session.
- Recommendations shall be displayed as a grid of book cover images on a bookshelf-like UI.
- Each book cover shall be clickable, revealing the book's title, author, and synopsis.
- The chatbot shall provide a concise explanation for each recommendation, referencing:
  - Specific user conversation points
  - (If available) Direct quotations from the book text

### 5.3 Data Handling
- The system shall use a PostgreSQL database (Phase 1) to store a list of questions and book metadata.
- The system shall transition to using an LLM with RAG and a full-text book dataset (Phase 2).
- After recommendations are presented, the full conversation log and recommendations shall be stored on the Flask backend.

### 5.4 Technical Stack
- Backend: Flask (Python)
- Frontend: Vue.js
- Database: PostgreSQL (initially for questions and book metadata)
- LLM and RAG: LangChain framework (Phase 2)

## 6. Non-Functional Requirements

- The application shall use a warm color scheme and a visual design reminiscent of a classic library or bookstore.
- The chatbot shall be the central UI element, not a peripheral widget.
- The application shall not use cloud-based server platforms for the prototype.
- The application shall not include e-commerce functionality.
- The application shall not use a "hi-tech" or robotic visual theme.

## 7. Acceptance Criteria

- [ ] The chatbot asks at least 10 questions per session.
- [ ] Book recommendations are displayed as a grid of cover images.
- [ ] Clicking a book cover reveals title, author, and synopsis.
- [ ] The chatbot provides a rationale for each recommendation.
- [ ] The application uses a warm, library-inspired design.
- [ ] All data is stored locally (browser and Flask backend).

## 8. Open Questions

- What full-text book datasets are available and suitable for local use?
- How can the recommendation engine be restricted to the available dataset?
- If full-text datasets are unavailable, what APIs can provide sufficient book data?
- How can the chatbot reliably quote book text in its explanations?

## 9. Out of Scope

- One-shot search functionality (i.e., no conversational context)
- E-commerce or book selling features
- High-tech or robotic UI themes 