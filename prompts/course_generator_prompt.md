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
Each module dictionary in CURRICULUM_DATA must follow this schema:
- "id" (int): Sequential integer starting from 1.
- "title" (string): The module title (e.g., "Module 1: Kubernetes Core Architecture & Declarative Primitives").
- "theory" (string): Triple-quoted string (`"""`). Educational explanation of core concepts structured under relevant H3 headings (e.g., `### The Kubernetes Paradigm`, `### Control Plane vs. Worker Nodes`). Do not use a single generic heading.
- "commands" (string): Triple-quoted string (`"""`). Starts with an H3 header `### Command & Syntax Reference` followed by standard markdown listing essential commands, operators, keywords, or syntax rules (either as bullet points with descriptions or as formatted code blocks with clear inline comments). If the target course is about a programming language or a tool with specific structural syntax, focus heavily on the syntax, constructs, grammar, and keywords the student needs to master.
- "examples" (string): Triple-quoted string (`"""`). Starts with an H3 header `### Real-World Examples` followed by multiple realistic scenarios defined using H4 headings: `#### Example 1: [Title]`. Each example must follow this structure:
  * **Situation:** [Context/scenario details]
  * **Action:** [Explanation of solution]
  followed by fully-formed configuration files (YAML, Python, JSON, etc.) inside code blocks with ZERO placeholders (do not use comments like "# ... insert rest of code").
- "exercise" (string): Triple-quoted string (`"""`). Starts with an H3 header `### Hands-On Labs` followed by multiple sequential step-by-step local hands-on exercises defined using H4 headings: `#### Lab 1: [Title]`. Each lab must follow this structure:
  * **Objective:** [Goal/outcome of the lab]
  * **Tasks:**
    1. [Step-by-step task details]
- "insight" (string): Triple-quoted string (`"""`). Starts with an H3 header `### Interview Q&A` followed by multiple certification/interview Q&As defined using H4 headings: `#### Q1: [Technical Question]`, and bulleted answers starting with `* **Answer:** [Detailed expert response]`. You can also append specialized study tips or exam-specific guidelines under an H3 heading (e.g., `### CKA Exam Focus`).

### Strict Formatting and Quality Rules:
- COMPREHENSIVE COVERAGE: Generate as many distinct, sequential modules inside CURRICULUM_DATA as necessary to fully and comprehensively cover the user's requested subject. Do not artificially limit the course to a single module if the topic requires deeper coverage.
- NO PLACEHOLDERS: Do not use comments like "# ... add more logic here". Provide full, fully formed configurations.
- ESCAPING: Wrap all multi-line strings in Python triple-quotes (either """ or ''') safely so the file parses without syntax errors.

Following these rules, generate the complete curriculum module file for the subject described below:
[APPEND YOUR SUBJECT HERE, e.g. "Add a course covering Ansible Playbooks, Roles, and Vault with a focus on SRE web server configuration"]
```