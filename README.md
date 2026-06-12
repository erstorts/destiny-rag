# 📚 Whitman Middle School Library Chat

**A conversational AI that helps students find books from their school library's real collection, just by asking for what they're in the mood for.**

🔗 **[Try the live app →](https://library-ai-chat.streamlit.app/)**

> Project repo: `destiny-rag`. A book-recommendation assistant built on top of a real school library's Follett Destiny catalog.

---

## The problem

Most school library catalogs only do keyword search. To find a book, a student already has to know the title, the author, or the exact subject heading. That is not how a middle schooler actually looks for something to read. They walk up to the librarian and say "do you have anything funny about a kid who keeps getting in trouble?" or "I liked Percy Jackson, what should I read next?"

A keyword catalog cannot answer questions like that. A good librarian can. But one librarian cannot be at the desk for every student at every moment, and a lot of kids will not ask in the first place.

This project puts that librarian conversation online. A student types what they want in their own words and gets back a short list of books that are actually sitting on the shelves of *their* school library, each one linked so they can go check it out.

## What it does

A student opens the chat and asks a question. Here is the kind of thing they get back:

> **You:** *something funny about a kid getting into trouble at school*
>
> **Assistant:** Here are a few you might like:
> 1. **Diary of a Wimpy Kid** by *Jeff Kinney* — Greg Heffley narrates the daily disasters of middle school, from cheese-touch panic to schemes that always backfire. [View in catalog →]
> 2. **Big Nate: In a Class by Himself** by *Lincoln Peirce* — A sixth-grader who is certain he is destined for greatness keeps finding new ways to land in detention. [View in catalog →]

Behind that simple chat box, three things are happening that matter:

- **It only recommends books the library actually owns.** No generic bestseller lists, and no made-up titles. Every suggestion comes from this library's own catalog.
- **It understands what the student *means*, not just the words they typed.** "Funny book about a kid in trouble" finds the right books even when none of those exact words appear in the description.
- **It hands the student a direct path to borrow.** Each recommendation links straight to that book's page in the live catalog.

## How it works, in plain English

The hard part of using AI for something like this is that language models sound confident even when they are wrong. Ask a normal chatbot for book recommendations and it will cheerfully invent titles that *sound* real but do not exist, or push popular books the library does not carry. For a tool students are supposed to trust, that is worse than useless.

The fix is a technique called **RAG** (Retrieval-Augmented Generation). The clearest way to picture it is the difference between a closed-book and an open-book exam.

A normal chatbot takes a **closed-book exam**. You ask a question, and it answers from memory alone. It might remember well, or it might confidently make something up. You have no way to tell which.

This app gives the AI an **open-book exam** instead. Before the AI is allowed to answer, the system looks up the most relevant books from the library's own records and places them on the desk in front of it, then says: "Answer the student's question using only these." The AI's job stops being "recall every book that exists" and becomes "pick and describe the best matches from this stack." That single change is what keeps the recommendations real, local, and honest.

So a question flows through the system like this. The student's question goes out and searches the library's catalog. The best-matching books come back. Those books, plus the original question, get handed to the AI. The AI writes up a friendly, formatted answer drawn only from those books. The student gets titles they can actually borrow today.

## Design decisions worth calling out

The interesting work in a project like this is in the choices, not the chat box. A few that shaped how well it performs:

**Grounding every answer in the real catalog.** This is the whole point and the reason it is trustworthy. Recommendations are pulled from the school's actual Follett Destiny records, so the tool never sends a student looking for a book that isn't there.

**Searching two different ways at the same time.** The app runs every question through two kinds of search and combines the results. The first is a *meaning-based* search, like a librarian who understands what you are getting at even if you use different words than the book's description does. The second is a *keyword* search, like the old card catalog that matches the exact words you typed. Each one has a blind spot. Meaning-search can drift toward the general "vibe" and miss a specific author name. Keyword-search nails the exact name but misses a book that happens to be described differently than you phrased it. Running both and merging the results covers both weaknesses.

**A second-pass sort before answering.** After the two searches hand back a combined shortlist, a separate step re-reads that list and reorders it strictly by how well each book answers the actual question. Think of it as a careful second reader who takes a rough pile of "close enough" results and puts the genuinely best matches on top before anyone sees them.

**Keeping the assistant on-topic.** The AI is given firm instructions to act as a middle school librarian's assistant and to politely decline anything that is not about the library, its books, or their authors. That guardrail matters a lot when the users are kids on a school device.

**Filling in missing descriptions automatically.** Library catalog records are often missing a plot summary, and a recommendation engine is only as good as the descriptions it can search. When a book's record has no synopsis, the pipeline looks one up from an external book database and fills the gap. To avoid paying for and waiting on the same lookups twice, it saves what it finds and reuses it on later runs.

**Measuring whether it actually helps.** Every question, every result, and every thumbs-up or thumbs-down is logged and routed to cloud storage for analysis. That means the tool can be studied and improved based on how real students use it, rather than on guesses. *(This is where real usage numbers can go once they're collected: questions asked, most common requests, satisfaction rate.)*

## The technology behind it

For readers who want to know what it is built on, in plain terms:

| Piece | What it is, and what it does here |
|---|---|
| **Follett Destiny + MARC records** | The school's existing library system. Its catalog is exported in the standard library-record format and used as the single source of truth for what's on the shelves. |
| **Python data pipeline** | Reads the catalog export, cleans up titles and author names, and prepares each book for search. |
| **ISBNdb (book database)** | An outside reference used to fill in plot summaries that the catalog is missing. |
| **Pinecone** | A search database that stores a "fingerprint" of every book's description so the app can find books by meaning, not just by matching words. |
| **OpenAI (gpt-4o-mini)** | The language model that turns a pile of matching books into a friendly, written set of recommendations. |
| **Streamlit** | The simple chat web app the student actually sees and types into. |
| **Segment + AWS S3** | The usage-tracking layer that records how the tool is being used so it can be measured and improved. |

The mix is deliberate. The project spans the full path from raw institutional data to a polished, AI-powered product: pulling and cleaning messy real-world records, enriching them from an outside source, building meaning-based search, wiring up a language model responsibly, shipping a usable interface, and instrumenting the whole thing so its impact can be measured.

## Status and what's next

This is a working MVP, deployed and usable today (link at the top). Natural next steps include filtering recommendations by reading level, showing whether a copy is currently available to check out, and expanding from one school's catalog to several.
