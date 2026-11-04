# Claude Code Skills

## 1. Understand the Skill Structure

A skill is a folder containing a required `SKILL.md` file and optional supporting resources.

```text
my-skill-name/
├── SKILL.md       # Required: YAML frontmatter + instructions
├── scripts/       # Optional: executable code (Python, Bash, ...)
├── references/    # Optional: documentation loaded when needed
└── assets/        # Optional: templates, fonts, icons used in the output
```

**Naming rules**

- The file must be named exactly `SKILL.md` (case-sensitive). `skill.md` and `SKILL.MD` are wrong.
- The folder name uses kebab-case: `my-skill-name`, not `My Skill Name` or `my_skill_name`.
- Do not put a `README.md` inside the skill folder. Documentation goes in `SKILL.md` or `references/`.

**How a skill loads (progressive disclosure)**

| Level | Content | When it loads |
| --- | --- | --- |
| 1 | YAML frontmatter | Always, so Claude knows the skill exists |
| 2 | `SKILL.md` body | When Claude decides the skill is relevant |
| 3 | Linked files (`scripts/`, `references/`, `assets/`) | Only when needed |

## 2. YAML Frontmatter Rules

The frontmatter sits at the very top of `SKILL.md`, between two `---` lines.

```yaml
---
name: my-skill-name
description: Extracts action items from meeting notes. Use when the user asks to summarize a meeting or list follow-ups.
---
```

**Required fields**

| Field | Rules |
| --- | --- |
| `name` | Kebab-case only (lowercase, digits, hyphens). Max 64 characters. Should match the folder name. Must not contain `claude` or `anthropic`. |
| `description` | Says **what** the skill does and **when** to use it, including trigger phrases. Max 1024 characters. No XML tags. |

**Optional fields**

| Field | Purpose |
| --- | --- |
| `license` | License for the skill, such as `MIT` |
| `compatibility` | Environment requirements (max 500 characters) |
| `allowed-tools` | Tools the skill may use without asking for permission |
| `metadata` | Custom key-value pairs, such as `author` or `version` |

**Formatting and security**

- Use `---` on the first line and to close the block. A missing delimiter means the skill will not load.
- Do not use XML angle brackets (`<` or `>`) anywhere in the frontmatter, because it appears in Claude's system prompt.

**Claude Code note:** Claude Code is more lenient and adds its own fields. `name` is optional there and defaults to the folder name, and `description` is recommended. Following the rules above keeps a skill portable across Claude products.
