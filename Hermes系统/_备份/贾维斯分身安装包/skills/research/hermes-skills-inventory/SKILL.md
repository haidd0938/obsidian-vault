---
name: hermes-skills-inventory
description: Fetch the complete inventory of Hermes Agent skills — both built-in and optional — from the Skills Hub website and GitHub repository. Useful for discovering what skills are available and getting their descriptions.
tags:
  - hermes
  - skills
  - inventory
  - discovery
---

# Hermes Skills Inventory

## When to Use

- You want to see all available Hermes skills (not just currently loaded ones)
- You need to find skills by category or feature
- You want the description of a specific optional skill before deciding to install it

## Sources

There are two sources for Hermes skills:

1. **Skills Hub Website**: `https://hermes-agent.nousresearch.com/docs/skills`
   - Shows built-in skills and optional skills in a nice visual grid
   - Has category filtering (Apple, AI Agents, Creative, Gaming)
   - Docusaurus SSG + client-side hydration (body is empty at first)

2. **GitHub Repository**: `https://github.com/NousResearch/hermes-agent`
   - Built-in skills: `skills/` directory (26 categories)
   - Optional skills: `optional-skills/` directory (15 categories, ~59 skills)

## How to Fetch the Full Inventory

### Optional Skills (Recommended approach)

Use the GitHub REST API + Raw Content API to avoid rate limits and get descriptions:

```javascript
// Step 1: List optional-skills categories and their skill names
const SKILL_DIRS = await fetch(
  'https://api.github.com/repos/NousResearch/hermes-agent/contents/optional-skills'
).then(r => r.json()).then(data => data.filter(d => d.type === 'dir').map(d => d.name));

// Step 2: Get skill names for each category
const categorySkills = await Promise.all(SKILL_DIRS.map(dir =>
  fetch(`https://api.github.com/repos/NousResearch/hermes-agent/contents/optional-skills/${dir}`)
    .then(r => r.json())
    .then(items => ({
      category: dir,
      skills: items.filter(i => i.type === 'dir').map(i => i.name)
    }))
));

// Step 3: Fetch SKILL.md for each skill to get description
const allSkills = [];
for (const cat of categorySkills) {
  for (const skill of cat.skills) {
    try {
      const text = await fetch(
        `https://raw.githubusercontent.com/NousResearch/hermes-agent/main/optional-skills/${cat.category}/${skill}/SKILL.md`
      ).then(r => r.text());
      const descMatch = text.match(/description:\s*"([^"]+)"/) ||
                        text.match(/^# (.+)/m) ||
                        text.match(/\n\n(.+?)\n/);
      allSkills.push({
        category: cat.category,
        name: skill,
        description: descMatch ? descMatch[1] : text.substring(0, 150).replace(/\n/g, ' ')
      });
    } catch(e) {
      allSkills.push({category: cat.category, name: skill, description: '(unavailable)'});
    }
  }
}
```

Run this in the browser console (browser_console tool with expression parameter).

### Built-in Skills (from website)

Use browser_navigate to `https://hermes-agent.nousresearch.com/docs/skills`, then:

```javascript
fetch('https://hermes-agent.nousresearch.com/docs/skills')
  .then(r => r.text()).then(t => {
    const doc = new DOMParser().parseFromString(t, 'text/html');
    const cards = [...doc.querySelectorAll('.card_ZJrH')];
    return cards.map(c => ({
      name: c.querySelector('.cardTitle_CL7f')?.textContent,
      desc: c.querySelector('.cardDesc_SVV6')?.textContent,
      type: c.querySelector('.sourcePill_HAdI')?.textContent?.trim(),
      category: c.querySelector('.catButton_ZmPX')?.textContent
    }));
  });
```

## Pitfalls

- **GitHub API rate limit**: Anonymous requests are limited to 60/hr. If you exceed this, use GitHub token or switch to raw.githubusercontent.com direct fetch.
- **Skills Hub website**: The body is hydrated client-side by Docusaurus JS bundle. `document.body.textContent` is empty. Always use `fetch()` + `DOMParser` to get the SSG HTML.
- **CSS class names**: Docusaurus class names like `.card_ZJrH`, `.cardTitle_CL7f` are hashed and may change between versions. If they don't match, inspect the page first.
- **Optional skills count**: As of April 2026, there are ~59 optional skills across 15 categories. This may grow over time.

## Current Optional Skills by Category (captured 2026-04-25)

- autonomous-ai-agents: blackbox, honcho
- blockchain: base, solana
- communication: one-three-one-rule
- creative: blender-mcp, concept-diagrams, meme-generation, touchdesigner-mcp
- devops: cli, docker-management
- dogfood: adversarial-ux-test
- email: agentmail
- health: fitness-nutrition, neuroskill-bci
- mcp: fastmcp, mcporter
- migration: openclaw-migration
- mlops: accelerate, chroma, clip, faiss, flash-attention, guidance, hermes-atropos-environments, huggingface-tokenizers, instructor, lambda-labs, llava, modal, nemo-curator, peft, pinecone, pytorch-fsdp, pytorch-lightning, qdrant, saelens, simpo, slime, stable-diffusion, tensorrt-llm, torchtitan, whisper
- productivity: canvas, memento-flashcards, siyuan, telephony
- research: bioinformatics, domain-intel, drug-discovery, duckduckgo-search, gitnexus-explorer, parallel-cli, qmd, scrapling
- security: 1password, oss-forensics, sherlock
- web-development: page-agent
