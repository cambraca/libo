Rewrite the next section of the book.

Take into account the exact level of where we are, given the total number of sections (see sections.yaml), the
current progress that we've recorded (progress.md), and the configuration of which levels we're aiming to start and end
on. Also look at the `0-initialize.md` instructions, which were already completed.

Write it in a way that does not summarize the source material. In general, try to preserve the structure (paragraphs,
etc.) as much as possible. We want to produce essentially the same text, only at a level that a language learner
can read.

Do not read much more than what's relevant (e.g. the entire source book), although it's fine to read, for context, the
previous section, so that the text flows naturally.

Before writing the content, identify vocabulary and phrases that may be hard for the reader, and add a block with those
things. You can use definition lists (dd, dt, dl tags in HTML) inside an `aside` tag, for which we added styles in the
initialization stage.

After the section text is written, record the progress (progress.md) so that the next iteration knows where to continue.
Clearly specify when the book is all done, so that if we run this again, it doesn't do anything.

Do not build the target.epub file. Only modify the text in the `target/` directory, and the `progress.md`. Only touch
`sections.yaml` if absolutely necessary.
