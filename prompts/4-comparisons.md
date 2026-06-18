For each paragraph in the target book (or, if there are multiple paragraphs that can be grouped together, like a
sequence of short dialogue lines), add these links as EPUB footnotes (assuming the target language is French and the
native language is Spanish):

1. "FR+" - The corresponding original text from the source book.
2. "ES-" - The Spanish translation of the simplified paragraph.
3. "ES+" - The direct Spanish translation of the original text.

Use real EPUB footnotes: each visible comparison link should point to a matching footnote `aside`, and each footnote
should link back to the paragraph.

Add this to the CSS (check for naming collisions with the existing styles and adapt this snippet if necessary):

```css
/* Compact comparison footnote links shown after adapted paragraphs. */
.comparison-refs {
    white-space: nowrap;
    font-size: 0.75em;
    vertical-align: super;
}
.comparison-refs a {
    margin-left: 0.25em;
    color: #555;
    text-decoration: none;
}
.comparison-refs a:focus,
.comparison-refs a:hover {
    color: #000;
    text-decoration: underline;
}

/* Hidden by most EPUB readers until opened from a noteref link. */
.comparison-footnote {
    margin: 1em 0;
    padding: 0.75em;
    border-left: 0.2em solid #777;
    background-color: #f3f3f3;
    color: #222;
    font-size: 0.9em;
}
.comparison-footnote p {
    margin-top: 0;
    text-indent: 0;
}
.comparison-footnote .comparison-label {
    font-weight: bold;
}
```

Do not try to use external tools for generating the translation. Do it in this session, one chapter at a time.
