# Module 2: Plan a Skill Before Writing It

Before writing `SKILL.md`, answer three questions. The examples below use a **code review skill**.

## 1. What domain should this skill cover?

Give the skill one clear job, and decide what is in and out of scope.

**Code review example**

| In scope | Out of scope |
| --- | --- |
| Reviewing a diff for correctness bugs | Fixing the code |
| Spotting security issues | Running the test suite |
| Commenting on readability | Writing commits or pull requests |
| Reporting findings by severity | |

The out-of-scope tasks belong to other skills. A focused skill triggers more reliably and is easier to maintain.

The domain also shapes the `description` field, because it tells you which trigger phrases to include:

```yaml
---
name: code-review
description: Reviews code changes for bugs, security issues and readability, and reports findings by severity. Use when the user asks to review a PR, check a diff, or look over their changes.
---
```

## 2. What degree of freedom is appropriate?

Match how prescriptive the instructions are to how fragile the task is. The more damage a wrong step can do, the less freedom Claude should have.

| Freedom | Instruction style | Use when |
| --- | --- | --- |
| High | Text guidance | It is a judgement call with many valid approaches |
| Medium | Templates or pseudocode | A preferred pattern exists, but some variation is fine |
| Low | Exact scripts or commands | The steps are fragile and must be consistent |

A single skill can mix these levels.

**Code review example**

- **High freedom:** judging the code. What counts as a problem depends on the context, so give guidance rather than rigid rules.
- **Low freedom:** the output format and severity labels. Every review should look the same, so specify them exactly.

## 3. Which patterns will the body use?

Choose the patterns that suit the job. Most skills need only a few of them.

| Pattern | Use it when | Code review example |
| --- | --- | --- |
| Template | The output needs a fixed structure | The format of the findings report |
| Examples | Quality is easier to show than describe | A good finding next to a vague one |
| Workflow / checklist | The steps must happen in order | Read the diff, gather context, check, report |
| Conditional | The approach depends on the situation | Small diff or large PR, security-sensitive files |
| Progressive disclosure | The detail is only needed sometimes | A language-specific checklist in `references/` |

## Planning checklist

Copy this before starting a new skill:

- [ ] **Domain:** What is the one job, and what is out of scope?
- [ ] **Freedom:** Which parts need judgement, and which must be exact?
- [ ] **Patterns:** Which patterns will the body use?
