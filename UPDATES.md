# UPDATES

A log of project progress and specific lessons learned.

## Log

### 2025-09-17

Hokay finally think it makes sense to recap what I've done so far and jot down some thoughts on where this project can go.

First just a quick recap:

 1. This whole started out as a vibe-coding what-if exercise: My friends and I made a chatbot a long time ago while learning full stack web dev before ChatGPT was a thing and now whaddya know, what took us months to code now just takes about a day. Granted, what we made wasn't that sophisticated: A chatbot that asks a series of questions from a database and then recommends books by copy pasting the entire conversation history into a Google Books search bar.
 2. Once this thing was vibe-coded I saw this as an opportunity to learn LangChain/LangGraph and replace the "questions database back end" with an LLM

Most recently, I've been toying around with an `agent.py` coded using LangChain and then using a separate notebook `chat.ipynb` to simulate the front end.

My initial goals within this `agent<=>chat` sandbox were:
 - Control how the chatbot responds during the conversation with SystemMessages - sometimes the questions were general and broad, other times specific and mentioning a book title or author.
 - At the end of the conversation with at least 10 questions, have the chatbot summarize the user's tastes back to them.
 - Have the chatbot/LLM automatically generate a list of search terms to send to Google Books API.

This last goal was a bit tricky but achieved by adding a node to the LangGraph and inserting a fake `HumanMessage` to prompt the LLM. I feel like this way is a bit janky since this means not every `HumanMessage` in the chat history may be reflective of what a real user has said.

But a bigger problem became apparent even when the Google Books API returns results: **the search results really suck!**

I had hoped the search terms would represent the keywords/themes/features of what the user wanted. The LLM generated lists do reflect that quite well. The problem is that Google Books doesn't search books "thematically" or even by genre. If you search something like "surreal sci-fi" on Google Books, you'll get back textbooks and nonfiction books by critics on common sci-fi authors works and their social impact or something, instead of even one or two fiction books under that genre.

So, the next step could just be: ask the LLM for the book title and author recommendations!

Google Books API can still come in handy - AFTER the LLM comes up with a book title and author, use the Google Books API to look it up and, if it exists, get the book cover and description! This seems like what the Google Books API was meant to do anyway!

The LLM generated search term list could still be a thing to keep around - it's always fun to see how that list changes as the conversation moves forward. In a way the search term list are a kind of headspace/latent space of the chatbot as it is trying to figure out the user's specific tastes in books.