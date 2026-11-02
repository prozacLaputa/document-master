# Document Master

[简体中文](README.md) | English

A portable document editing and review skill for AI agents. It preserves meaning, evidence and qualifications while improving structure, consistency and natural expression.

## Usage

Download `document-master-0.5.0.zip` from GitHub Releases and import it into a compatible host, or place its `document-master/` folder in the host's skill directory and reload. Start at [SKILL.md](document-master/SKILL.md).

Example: “Review this proposal with Document Master. Preserve its meaning and provide the revised draft, key changes and items requiring verification.”

AgentBuddy version: `skills:skills.byted.org/default/public/document-master:0.5.0`.

## Scope and limitations

Supports light editing, structural review, drafting, meeting notes, knowledge explanations and learning from authorized references. Formats depend on the reader's task.

Text review requires no external dependencies. Online access, writeback, file generation and rendering require host tools and permission. Original documents are preserved unless the relevant changes are explicitly authorized.

This is a trial release. Structural checks do not demonstrate cross-platform behavior. The sample HTML has not passed visual review. No real internal documents, credentials or personal corpus are included.

## Maintenance

Both distribution channels use the same `document-master/` directory. See [RELEASING.md](RELEASING.md) and [CHANGELOG.md](CHANGELOG.md).

No open-source license has been selected. Public visibility does not grant additional permissions.
