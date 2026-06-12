# Quick start

1. Set up the book you want to translate into a subdirectory of `/books`.

   - `/source` should contain the unzipped contents of the EPUB book.
   - `/config.yaml` should contain configuration about the target and native languages, and starting and ending levels.

2. Run the initialization prompt (tested with Codex using GPT-5.5, with "medium" reasoning).

   ```shell
   codex exec "Run the initialize prompt for the book \"Le tour du monde\". Only inspect files under the current directory."
   ```

3. Check that `progress.md`, `sections.yaml`, and a `/target` dir were created.
4. Run the process prompt repeatedly until it finishes the book.

   ```shell
   codex exec "Run an iteration of the process prompt for the book \"Le tour du monde\". Only inspect files under the current directory."
   ```
5. Run the verify prompt.

   ```shell
   codex exec "Run the verify prompt for the book \"Le tour du monde\". Only inspect files under the current directory."
   ```

6. Create the final .epub book.

   ```shell
   ./scripts/create-epub.sh "Jules Verne - Le tour du monde"
   ```