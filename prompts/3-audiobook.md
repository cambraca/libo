Create a version of the target book suitable for generating an audiobook, and put it in a new `audiobook/` directory.

This version should only have the text of the book (the part that was adapted), without anything extra like an
acknowledgements section, etc. Do include a structured table of contents, if the book has one. See the initialize prompt
to help identify what should be removed.

Make sure each chapter is in its own file, so that the .m4b generation does chapter detection properly.

Only create or modify files inside the `audiobook/` directory. Do not run `create-epub.sh`, Docker, Docker Compose,
`epub2tts`, or any other build or audiobook-generation command. Do not create `audiobook.epub`, `audiobook.txt`, or
`audiobook.m4b`; those steps will be run separately by the user.
