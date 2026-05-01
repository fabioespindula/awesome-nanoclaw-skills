# NanoSkills

`nanoskills` is the package-level catalog and help system for Awesome NanoClaw Skills.

It lists the available skills, separates user-facing skills from admin/package skills, explains what each skill does, and provides examples in the language of the current conversation.

## Use It

Primary command:

```txt
/nanoskills
```

Help examples:

```txt
/nanoskills help board
/nanoskills help think-big
/nanoskills updates
```

Aliases and trigger phrases:

```txt
skills
lista skills
help skills
catalog
```

## Behavior

- Reads the generated local catalog from `references/catalog.md`.
- Generates a read-only fallback from local `SKILL.md` files only when the catalog is missing.
- Does not require network access for normal catalog or help output.
- Routes lifecycle questions to `awesome-updater` without running update tooling unless the user clearly asks.

## Output

The default catalog output groups skills into:

- user-facing skills
- admin/package skills

Skill help includes what the skill does, when to use it, commands, expected output, examples, and boundaries.

## Requirements

NanoClaw runtime with skill loading and local access to this package's generated catalog.

## Install

```bash
rsync -a skills/nanoskills/ /path/to/nanoclaw/container/skills/nanoskills/
```

Or install it through `awesome-updater`:

```bash
python3 skills/awesome-updater/scripts/awesome_skills.py install nanoskills \
  --source-dir "$PWD" \
  --skills-dir /path/to/nanoclaw/container/skills
```

## Validate

```bash
skills/nanoskills/scripts/validate-nanoskills.sh
```
