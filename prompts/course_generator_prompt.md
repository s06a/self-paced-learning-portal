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
- "title" (string): The module title.
- "theory" (string): Educational explanation of core concepts under a "### Core Concepts" heading.
- "commands" (string): Essential CLI commands wrapped inside a ```bash ... ``` block with clear inline comments.
- "examples" (string): Exactly 5 real-world technical scenarios. Define each using "#### Scenario 1: [Name]", "#### Scenario 2: [Name]" up to "#### Scenario 5: [Name]". Each scenario must contain realistic configuration code (YAML, Python, JSON, etc.) and must be fully written with ZERO placeholders (do not use comments like "# ... insert rest of code").
- "exercise" (string): Exactly 5 sequential, step-by-step local hands-on instructions under a "### Lab Assignment" heading. Label them "1. ...", "2. ...", up to "5. ...".
- "insight" (string): Exactly 5 high-quality certification/interview Q&As under a "### Certified Prep Queries" heading. Format each explicitly as bold:
  **Q1: [Technical Question]**
  **A1: [Detailed expert response]**
  ... up to **Q5:** and **A5:**.

### Strict Formatting and Quality Rules:
- COMPREHENSIVE COVERAGE: Generate as many distinct, sequential modules inside CURRICULUM_DATA as necessary to fully and comprehensively cover the user's requested subject. Do not artificially limit the course to a single module if the topic requires deeper coverage.
- NO PLACEHOLDERS: Do not use comments like "# ... add more logic here". Provide full, fully formed configurations.
- ESCAPING: Wrap all multi-line strings in Python triple-quotes (either """ or ''') safely so the file parses without syntax errors.

Following these rules, generate the complete curriculum module file for the subject described below:
[APPEND YOUR SUBJECT HERE, e.g. "Add a course covering Ansible Playbooks, Roles, and Vault with a focus on SRE web server configuration"]
```