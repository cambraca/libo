Create a plain-text version of the target book suitable for audiobook generation and save it as `audiobook.txt` in the
book directory.

Include only the adapted text of the book. Omit front matter, acknowledgements, vocabulary notes, exercises, and other
material that is not part of the adapted narrative.

Use this format:

```text
Title: Le tour du monde en quatre-vingts jours
Author: Jules Verne

# Chapitre I. Dans lequel Phileas Fogg et Passepartout s'acceptent réciproquement, l'un comme maître, l'autre comme domestique.

En 1872, Phileas Fogg habite au numéro 7 de Saville-row, à Londres. C'est une maison célèbre.
On ne sait presque rien sur Phileas Fogg. C'est un homme poli et élégant.

# Chapitre II. Où Passepartout est convaincu qu'il a enfin trouvé son idéal

Passepartout est convaincu qu'il a enfin trouvé une vie tranquille.
```

The first two lines must contain `Title:` and `Author:`. Each chapter must begin with `# ` followed by its proper chapter
name or title. Do not use generic names such as `Part 1`, `Part 2`, or `Chapter 3` when the target book provides real
chapter names.

Ideally, put one paragraph on each non-heading line. If a paragraph is unusually long, split it at natural sentence or
clause boundaries into shorter lines. Keep each line comfortably below 1,000 characters so requests to Microsoft Edge
TTS do not fail. Do not split in the middle of a sentence unless necessary.

Preserve the reading order and punctuation. Do not include Markdown other than the `# ` chapter headings.

If the target book has a cover image, copy it to the book directory as `cover.png`, `cover.jpg`, or `cover.jpeg`, using
the appropriate extension.

Only create or modify `audiobook.txt` and the optional cover image in the book directory. Do not create an `audiobook/`
directory or `audiobook.epub`. Do not run Docker, Docker Compose, `epub2tts`, or any audiobook-generation command. Do not
create `audiobook.m4b`; that step will be run separately by the user.
