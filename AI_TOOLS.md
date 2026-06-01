# AI Tools Used

This project used several AI-assisted development tools:

- **_Claude_** – Primary AI assistant used for architecture design, planning, implementation, and technical decision-making.
- **_GitHub Copilot_** – Used as a secondary assistant, primarily for inline code suggestions and as a fallback when Claude was not available.
- **_Windsurf_** – Primarily used for code autocomplete. While capable of more advanced assistance, it was not used as a primary development tool in this project.

# How those tools ware used?

The project includes a `.claude` directory that contains reusable AI guidance and project-specific instructions.

### Skills

- **python-patterns** - Provides guidance on modern Python development practices

### Rules

- **coding-style** - Defines coding standards and best practices, ensuring that implementations follow established software engineering principles.

### Agents

- **Planner** - when working with AI, it is mandatory to first plan feature implementation, before giving AI permission to code. It will make task generation predictable and reduce implementation mistakes. Once the plan is generated, Claude uses the defined rules and skills to implement the feature according to the agreed approach.

# Copilot Integration

One advantage of Github Copilot is ability to read and utelize the `.claude` folder. This eliminates the need to create separate folder with duplicated skills.

# Prompt Engineering

### General rules for writing good prompts:

- Giving the AI a persona narrows its focus and expertise, forcing it to draw from specific knowledge bases
- Provide complete and relevant context. This project uses Context7 through MCP to retrieve up-to-date documentation and references when needed
- Reduce “fluffy” and imprecise descriptions
- When zero-shot prompting does not produce the desired results, provide examples to guide the model toward the expected output.

---

The ultimate skill in AI prompting is **Clarity of Thought**. If you cannot clearly explain the task, logic, or desired outcome yourself, the AI cannot execute it effectively. Treat every bad output as a personal skill issue: Analyze where your instructions were vague or lacked context.
