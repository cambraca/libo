# Quick start

1. Open this project in an IDE.
2. Set up the book you want to translate into a subdirectory of `/books`.
3. Run the initialization prompt (tested with Codex using GPT-5.5, with "medium" reasoning).

   ```shell
   codex exec "Run the initialize prompt for the book \"Le tour du monde\". Only inspect files under the current directory."
   ```

4. Check that `progress.md`, `sections.yaml`, and a `/target` dir were created.
5. Run the process prompt repeatedly until it finishes the book.

   ```shell
   codex exec "Run an iteration of the process prompt for the book \"Le tour du monde\". Only inspect files under the current directory."
   ```
