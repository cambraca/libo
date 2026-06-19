# Libo

Libo turns an EPUB book into a language-learning edition. Codex progressively
adapts the book from a configured starting proficiency level to an ending level,
adds vocabulary notes, verifies the completed text, and can optionally generate
an audiobook with Microsoft Edge cloud TTS.

Each book is an independent project stored directly under `books/`.

## Requirements

- [Codex CLI](https://developers.openai.com/codex/cli/) for running the prompts.
- `sbx` for running Codex inside the Docker sandbox.
- `unzip` for extracting the source EPUB.
- `zip` for compiling EPUB directories with `scripts/create-epub.sh`.
- Docker with the Compose plugin for audiobook generation.
- An internet connection to build the audiobook image and use Edge cloud TTS.
- An internet connection to install the Codex sandbox kit dependencies the first time.

The Codex sandbox kit is configured in `spec.yaml`. It installs Python 3, Git,
ripgrep (`rg`), `jq`, `zip`, `unzip`, and other common command-line tools used
while inspecting and editing EPUB contents.

Install Docker Desktop or Docker Engine, then install `sbx`. Use
`scripts/codex.sh` to run Codex. The wrapper creates the `codex-libo` sandbox
with the project kit if it does not already exist.

Log in to Codex inside the sandbox once:

```shell
./scripts/codex.sh login
```

The sandbox stores Codex state in a Docker volume, so login state and resumable
sessions persist between runs. The wrapper reattaches to the `codex-libo`
sandbox for every prompt.

The audiobook workflow uses a separate Compose service in `compose.yaml`. Its
first build downloads the audiobook container dependencies.

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
   ./scripts/codex.sh "Run the initialize prompt for the book \"Author - Title - A1-B1\"."
   ```

3. Confirm that Codex created `target/`, `sections.yaml`, and `progress.md`.

4. Run the processing prompt repeatedly until `progress.md` reports that every
   section is complete:

   ```shell
   ./scripts/codex.sh resume --last "Run an iteration of the process prompt for the book \"Author - Title - A1-B1\"."
   ```

5. Verify and correct the completed target book:

   ```shell
   ./scripts/codex.sh resume --last "Run the verify prompt for the book \"Author - Title - A1-B1\"."
   ```

6. Add comparison footnotes for language study:

   ```shell
   ./scripts/codex.sh resume --last "Run the comparisons prompt for the book \"Author - Title - A1-B1\"."
   ```

   The prompt adds compact `FR+`, `ES-`, and `ES+` footnote links to the
   adapted text. `FR+` shows the corresponding original target-language text,
   `ES-` translates the simplified paragraph into the native language, and
   `ES+` translates the original paragraph into the native language.

7. Compile `target/` into `target.epub`:

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
./scripts/codex.sh resume --last "Run the audiobook prompt for the book \"Author - Title - A1-B1\"."
```

The prompt creates `audiobook.txt` in the book directory. It does not run Docker.

After the prompt finishes, run these commands yourself from the repository root:

```shell
docker compose run --rm epub2tts "Author - Title - A1-B1"
```

The Compose service reads `audiobook.txt` and uses Edge cloud TTS to generate
`audiobook.m4b`.

Intermediate and resumable audio files are stored in the ignored
`books/Author - Title - A1-B1/.audiobook-work/` directory. Keep this directory to resume
an interrupted generation, or remove it to restart synthesis from scratch.

The Edge TTS conversion script was downloaded from
[aedocw/epub2tts](https://github.com/aedocw/epub2tts) on June 13, 2026, then
adapted to support only Microsoft Edge TTS.

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
