# Project Requirements Document (PRD)

A project requirements document (PRD) for this project.

---
Status: DRAFT
Owner: Dan
Designer: Dan
Developer: Dan
Target Release Date: 2025-08-03
---

## Goals and Objectives

**Premise:** Finding a book you want to read isn’t always a quick Google search away. Sometimes a conversation with a friend can suss out the important nuances of the stories and ideas you’re interested in. But not all of your friends have a vast body of knowledge of all the books that are out there. This web app explores the possibilities of a chatbot that makes books recommendations after having a long-form conversation with you.

**End product:** A website for bibliophiles with the chatbot as the central UI element that helps users explore books beyond what they are used to reading.

**Ideally:** The chatbot is familiar with the full text of the book such that they can even quote specific passages in the books that led to a recommendation to the user and tie it to a specific parts of the conversation. And over time, the chatbot can further continously refine its knowledge of the user and improve on the quality of its recommendations.

## Background and Strategic Fit

**Challenges:**

 - Google search can be a very efficient way to find books of interest, but still requires some time for the user to persue or skim the "top 10 books..." lists that come up.
 - Sometimes the books a user wants to find is not a simple matter of subject matter or genre - and this becomes harder for a Google search to satisfy because
   - writing out everything in search feels too time consuming
   - Google search results are sorted more by a general popularity of sites without much attention to th user's nuanced particular interests.

**Opportunities:**

 - LLMs have been trained a large body of knowledge including stories of various data modalities: mixed media news, audio visual film and TV, audio-only podcasts
 - They can potentially utilize this knowledge to improve the quality of recommendations around the user's particular interests and preferences rather than high-level labels/categorizations like genre.

## Assumptions

 - The user has only vague ideas of what they want to read
    - The user may have preferences for authors or genres but ultimately wants to explore and go beyond their existing preferences. 

## User Stories

 1. The user arrives on a website and is approached by a chatbot in the center of the screen.
 2. The chatbot asks a series of questions about the user's tastes in stories in general, specific experiences with books in the past, what they're currently interested in, what are they not interested in.
 3. Based on the content of this conversation, the chatbot displays book recommendations as a grid of book cover images.
 4. Users can click on each book for title, author, and synopsis.
 5. Ideally, the chatbot provides a concise explanation as to why it recommends the user-clicked book and quotes either the book text or specific text from the initial conversation.

## User Interaction and Design

**Basic requirements:**

 - "10 question minimum" rule: The chatbot must ask at least 10 questions. More questions are OK.
 - The chatbot should really ask questions about the user's background interests in all forms of storytelling: news, film, TV, podcasts, etc.
 - A chatbot may bring up a book title and author during the conversation to briefly test if they understand the user's tastes.
 - Overall the conversation should have a natural flow yet revolve around stories of potential interest to the user.
 - Beyond that, there are no strict constraints to what the chatbot should ask.

**Look and Feel**

 - The website overall look and feel should remind users of an old yet beautifully preserved library.
 - Definitely uses a warm color scheme.
 - The book recommendations should be displayed as cover images on a bookshelf-like grid.

**Technical requirements**

 - Simple locally run prototype: No cloud based server platforms to be used if possible.
 - Flask local server for the backend
 - LangChain framework for chatbot
    - Specific hard-coding that enforces the "10 question minimum" rule.
 - Vue.js Front-end
 - Chatbot conversation log is stored first using the browser local storage.
 - After the chatbot conversation ends with the book recommendations, a full log of the conversation and final book recommendations is stored to the Flask local server.

## Questions

 - What full-text book datasets are readily available?
 - How can we restrict the chatbot's search and recommendation space to just that dataset?
 - If no good full-text datasets exist, what are good book-based APIs?
 - In either case, how do we get the the chatbot to quote book-related text in its explanations of its recommendations? Quotes can come from full-text or book synopsis/descriptions depending on the API.

## Not Doing

 - This is not a "one-shot" search tool. 
 - This is not meant to look like a "hi-tech website" - especially when it comes to the various colors of blue or images of anthropomorphic robots.
 - This is not an e-commerce site selling books. 