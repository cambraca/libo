# Libo

Libo turns an EPUB book into a language-learning edition. Codex progressively
adapts the book from a configured starting proficiency level to an ending level,
adds vocabulary notes, verifies the completed text, and can optionally generate
an audiobook with Microsoft Edge cloud TTS.

Each book is an independent project stored directly under `books/`.

## Requirements

- [Codex CLI](https://developers.openai.com/codex/cli/) for running the prompts.
- `unzip` for extracting the source EPUB.
- `zip` for compiling EPUB directories with `scripts/create-epub.sh`.
- Docker with the Compose plugin for audiobook generation.
- An internet connection to build the audiobook image and use Edge cloud TTS.

Docker is only required for the audiobook workflow. The first audiobook build
downloads the container dependencies.

## Book Layout

Create one directory per book:

```text
books/
└── Author - Title - A1-B1/
    ├── source.epub
    ├── source/
    │   └── ...unzipped EPUB contents...
    └── config.yaml
```

The `source/` directory must contain the extracted, DRM-free EPUB, including its
`mimetype` file. `config.yaml` defines the languages and proficiency range:

```yaml
native_language: "es-419"
target_language: "fr-FR"
start_level: "A1"
end_level: "B1"
```

## Quick Start

Run all commands from the repository root, and replace `Author - Title - A1-B1` in each one.

1. Extract the original source EPUB into `source/`, and create `config.yaml` as shown above:

   ```shell
   mkdir -p "books/Author - Title - A1-B1/source"
   unzip "mybook.epub" -d "books/Author - Title - A1-B1/source"
   ```

2. Initialize the language-learning edition:

   ```shell
   codex exec "Run the initialize prompt for the book \"Author - Title - A1-B1\". Only inspect files under the current directory."
   ```

3. Confirm that Codex created `target/`, `sections.yaml`, and `progress.md`.

4. Run the processing prompt repeatedly until `progress.md` reports that every
   section is complete:

   ```shell
   codex exec "Run an iteration of the process prompt for the book \"Author - Title - A1-B1\". Only inspect files under the current directory."
   ```

5. Verify and correct the completed target book:

   ```shell
   codex exec "Run the verify prompt for the book \"Author - Title - A1-B1\". Only inspect files under the current directory."
   ```

6. Compile `target/` into `target.epub`:

   ```shell
   ./scripts/create-epub.sh "Author - Title - A1-B1"
   ```

   The default version is `target`; the equivalent explicit command is:

   ```shell
   ./scripts/create-epub.sh "Author - Title - A1-B1" target
   ```

## Audiobook

Run the audiobook prompt after the target book has been processed and verified:

```shell
codex exec "Run the audiobook prompt for the book \"Author - Title - A1-B1\". Only inspect files under the current directory."
```

The prompt only creates the audiobook-specific EPUB tree in `audiobook/`. It
does not compile the EPUB or run Docker.

After the prompt finishes, run these commands yourself from the repository root:

```shell
./scripts/create-epub.sh "Author - Title - A1-B1" audiobook
docker compose run --rm epub2tts "Author - Title - A1-B1"
```

The first command compiles `audiobook/` into `audiobook.epub`. The Compose
service then:

1. Scans `audiobook.epub`.
2. Exports its contents to `.audiobook-work/audiobook.txt`.
3. Uses Edge cloud TTS to generate `audiobook.m4b`.

Intermediate and resumable audio files are stored in the ignored
`books/Author - Title - A1-B1/.audiobook-work/` directory. Keep this directory to resume
an interrupted generation, or remove it to restart synthesis from scratch.

If the audiobook prompt creates `cover.png`, `cover.jpg`, or `cover.jpeg` in the
book directory, the Compose service embeds it in `audiobook.m4b`.

The default voice is `fr-FR-HenriNeural`. See https://tts.travisvn.com/ for a full list.

Override the voice or concurrency with environment variables:

```shell
TTS_SPEAKER=en-US-AndrewNeural TTS_THREADS=4 \
  docker compose run --rm epub2tts "Author - Title - A1-B1"
```

Microsoft Edge TTS does not require an API key, but it is an online,
unofficial service whose availability or limits may change.
