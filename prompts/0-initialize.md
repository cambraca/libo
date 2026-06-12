Create a `target` dir with a copy of the epub book in `source`, but without any of the actual text of the book
(usually starting from a "Chapter 1").

The target book should still contain the same table of contents, metadata, CSS styles, and any text surrounding the
real book content (e.g. any sections like "acknowledgements", book covers, etc. should be copied now).

Add this to the CSS (check for naming collisions with the existing styles and adapt this snippet if necessary):

```css
/* Learning notes shown before each adapted section. */
.language-notes {
    margin: 2em 0;
    padding: 1em;
    border: 1px solid #777;
    background-color: #f3f3f3;
    color: #222;
}
.language-notes h3 {
    margin-top: 0;
    font-weight: bold;
}
.language-notes dl {
    margin-bottom: 0;
}
.language-notes dt {
    margin-top: 0.75em;
    font-weight: bold;
}
.language-notes dd {
    margin-left: 1.5em;
}
```

This will be used to later write an adaptation of the book meant to learn a new language. We will write it in a way
that starts easy and gets progressively harder.

The starting and ending levels, as well as the book language and the user's native language, are set in `config.yaml`.

Let's also initialize the `sections.yaml` file. Add a list of sections that we will use to split the book into an
appropriate number of chunks, each of which getting progressively harder than the one that came before. Usually, book
chapters are a good chunking strategy, unless they are unusually short or long, in which case this file will define
the chunks. You can use the table of contents, if the source book has it (e.g. a `toc.ncx` file).

Also, initialize the `progress.md` file, which will contain the appropriate context to keep going with the book
translation process. On each iteration, we will rewrite a section of the book, and this file will store information
about what we have accomplished so far, including what vocabulary and phrases we've already explained (the resulting
book, before each section, will introduce these things to the reader), and the current complexity level (not just
"A2" or "B1", but a more granular value, using percentages).
