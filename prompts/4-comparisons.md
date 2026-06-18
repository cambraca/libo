For each paragraph in the target book, add these links as EPUB footnotes (assuming the target language is French and the
native language is Spanish):

1. "ES" - The Spanish translation of the simplified paragraph.
2. "FR+" - The corresponding original text from the source book.
3. "ES+" - The direct Spanish translation of the original text.

If there are multiple short paragraphs in a row, like a sequence of short dialogue lines, group them together.

Comparison text in the native language must use normal orthography. Preserve all required diacritics and characters. Do
not emit ASCII-only text.

Use real EPUB footnotes. Keep each comparison footnote `aside` directly after the paragraph it belongs to; do not put
comparison footnotes in a separate file. Each visible comparison link should point to a matching hidden footnote
`aside`. Add `epub:type="noteref"` and `role="doc-noteref"` to each visible comparison link. Add
`epub:type="footnote"`, `role="doc-footnote"`, and `hidden="until-found"` to each comparison footnote `aside`.

Do not add visible labels inside the footnote bodies, such as `.comparison-label` spans, and do not add "return" links.

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
    color: #888;
    text-decoration: none;
}
.comparison-refs a:focus,
.comparison-refs a:hover {
    color: #000;
    text-decoration: underline;
}

```

Do not try to use external tools for generating the translation. Do it in this session, one chapter at a time.
