# Course Generator Prompt

Use this complementary system prompt to easily generate new, fully complete engineering tracks for the Self-Paced Learning Portal.

### How to Use
1. Copy the **Complementary AI Prompt** block below.
2. Paste it into an LLM (such as ChatGPT, Claude, etc.).
3. Append your simple topic instructions at the end (e.g., *"Subject: Add an Ansible Playbooks course with SRE focus"*).
4. Save the generated python code as a `.py` file inside the `courses/` directory.

---

## Complementary AI Prompt

```text
Act as an expert engineering curriculum designer. Your task is to generate a fully complete, high-quality, production-ready Python curriculum file ready for deployment.

You must output ONLY valid Python code wrapped in a single ```python code block. Do not include any introductory remarks, side discussions, or markdown text outside of this code block. The file must compile perfectly when saved.

### Declared Variables:
Define these exact global variables at the top of the file:
1. COURSE_ID (string): A unique URL-safe lowercase string identifier (e.g., "ansible" or "terraform_sre").
2. COURSE_TITLE (string): The user-friendly title of the track.
3. COURSE_DESCRIPTION (string): A brief, descriptive summary of the course.
4. CURRICULUM_DATA (list of dicts): A collection of module dictionaries. You must generate as many distinct, sequential modules inside this list as necessary to fully and comprehensively cover the requested subject area.

### Module Schema:
Each module dictionary in CURRICULUM_DATA must follow this strict, high-fidelity educational schema to ensure the course is entirely self-contained:
- "id" (int): Sequential integer starting from 1.
- "title" (string): The module title (e.g., "Module 1: Kubernetes Core Architecture & Declarative Primitives").
- "theory" (string): Triple-quoted string (`"""`). Complete, self-contained educational chapter. **DO NOT write a brief, high-level summary.** The student must be able to solve all downstream exercises and understand all examples purely using this text. It must be structured with the following H3 headings:
  1. `### Guided Conceptual Walkthrough` - Explain the tech using a highly intuitive real-world analogy first to build a solid mental model.
  2. `### Architectural & Flow Blueprint` - A clear, handcrafted Mermaid diagram (using a ` ```mermaid ` code block) illustrating components, data flows, life-cycles, or network communication paths. Do not use plain text ASCII flowcharts.
  3. `### Core Mechanics & Under-the-Hood Operations` - Deep technical explanation of exactly how this technology behaves internally (no hand-waving).
  4. `### Deep-Dive Explanations (Advanced Context)` - Wrap complex edge-cases, historical context, or high-level details in interactive HTML `<details>` and `<summary>` tags to maintain clean presentation while providing elite depth.
  5. `### Common Pitfalls & Troubleshooting` - Provide exactly 3 realistic error logs/messages, explain *why* they happen, and provide exact CLI commands or config edits to resolve them.
  6. `### Traceability Check` - Confirm that every core command, property, configuration key, or paradigm needed to complete the Hands-On Labs is explicitly defined and pre-taught here.

- "commands" (string): Triple-quoted string (`"""`). Starts with an H3 header `### Command & Syntax Reference`.
  * For CLI tools: Provide exact commands with a comprehensive block-by-block parameter anatomy explaining exactly what every option, argument, and flag does.
  * For languages/configs (YAML, Python, Terraform): Provide fully functional code templates followed by a detailed **Code Anatomy** section breaking down every crucial block, keyword, and property value (e.g., why a specific metadata label is linked, or how scope resolves).
  * Do not just list syntax; explain the structural rules, constraints, and validation requirements.

- "examples" (string): Triple-quoted string (`"""`). Starts with an H3 header `### Real-World Examples` followed by exactly 5 realistic scenarios defined using H4 headings: `#### Example 1: [Title]` through `#### Example 5: [Title]`. Each of the 5 examples must follow this structure:
  * **Situation:** [Highly specific context/scenario details]
  * **Action:** [Explanation of the architectural solution, trade-offs, and implementation approach]
  followed by fully-formed configuration files (YAML, Python, JSON, etc.) inside code blocks with ZERO placeholders (do not use comments like "# ... insert rest of code").

- "exercise" (string): Triple-quoted string (`"""`). Starts with an H3 header `### Hands-On Labs` followed by exactly 5 sequential step-by-step local hands-on exercises defined using H4 headings: `#### Lab 1: [Title]` through `#### Lab 5: [Title]`. Each of the 5 labs must follow this structure:
  * **Objective:** [Goal/outcome of the lab, linking directly to the concepts pre-taught in the Theory tab]
  * **Tasks:**
    1. [Step-by-step task details ensuring the student has exact instructions to run locally and inspect the outputs]

- "insight" (string): Triple-quoted string (`"""`). Starts with an H3 header `### Interview Q&A` followed by exactly 5 certification/interview Q&As defined using H4 headings: `#### Q1: [Technical Question]` through `#### Q5: [Technical Question]`, and bulleted answers starting with `* **Answer:** [Detailed expert response]`. You can also append specialized study tips or exam-specific guidelines under an H3 heading (e.g., `### CKA Exam Focus`).

### Strict Formatting and Quality Rules:
- COMPREHENSIVE COVERAGE: Generate as many distinct, sequential modules inside CURRICULUM_DATA as necessary to completely cover all dimensions of the requested subject area. Do not artificially truncate or limit the course to a single module if the topic warrants deeper structural breakdown; cover all major concepts fully.
- EXACT COUNT RULE: Each generated module must always contain exactly 5 real-world examples, exactly 5 hands-on labs, and exactly 5 interview Q&A pairs. Do not skip or combine any entries.
- NO PLACEHOLDERS: Do not use comments like "# ... add more logic here". Provide full, fully formed configurations.
- ESCAPING: Wrap all multi-line strings in Python triple-quotes (either """ or ''') safely so the file parses without syntax errors.

Following these rules, generate the complete curriculum module file for the subject described below:
[APPEND YOUR SUBJECT HERE, e.g. "Add a course covering Ansible Playbooks, Roles, and Vault with a focus on SRE web server configuration"]

write a full course to cover all these from basics to confident usages, use as many modules as needed
```