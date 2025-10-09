# AI Nurse Florence Tutorials

**Complete Onboarding Path: Zero to First Contribution in 4 Hours**

---

## Welcome

This learning path takes you from setting up your development environment to making your first contribution to AI Nurse Florence. Each tutorial builds on the previous one, teaching you practical skills through hands-on exercises.

**Who This Is For**: New developers joining the AI Nurse Florence project, from students to experienced developers new to healthcare AI.

**What You'll Be Able to Do**: After completing this path, you'll be able to independently add features, write tests, and contribute pull requests following project standards.

**Total Time**: Approximately 4 hours

---

## Learning Path Overview

### Tutorial 1: Environment Setup (30 min)
**File**: [01-environment-setup.md](./01-environment-setup.md)

Get a working local development environment with automated setup scripts.

**You'll learn**:
- Clone and configure the repository
- Run the automated setup script
- Verify your installation works
- Troubleshoot common setup issues

**Prerequisites**: Basic terminal knowledge, Python 3.10+ installed

---

### Tutorial 2: Understanding the Codebase (30 min)
**File**: [02-understanding-codebase.md](./02-understanding-codebase.md)

Build a mental model of how AI Nurse Florence is organized.

**You'll learn**:
- Project structure (`src/`, `docs/`, `static/`, `tests/`)
- Key files and their roles
- Development philosophy quick reference
- Where to find what you need

**Prerequisites**: Completed Tutorial 1

---

### Tutorial 3: Your First Patient Lookup (45 min)
**File**: [03-first-patient-lookup.md](./03-first-patient-lookup.md)

Trace code through a real feature from API request to response.

**You'll learn**:
- How patient lookup workflows work
- Trace code path: router → service → integration
- Test features via Swagger UI
- Add console logging to see data flow
- Modify a response to add a custom field

**Prerequisites**: Completed Tutorials 1-2

---

### Tutorial 4: Adding a New Service Method (60 min)
**File**: [04-adding-service-method.md](./04-adding-service-method.md)

Extend functionality by adding a new service method following project patterns.

**You'll learn**:
- Choose a simple feature to implement
- Follow the Service Layer Pattern from PATTERNS.md
- Add type hints and docstrings
- Test your method manually
- Add a router endpoint
- Test via Swagger UI

**Prerequisites**: Completed Tutorials 1-3, basic Python OOP

---

### Tutorial 5: Writing Tests for Healthcare Code (45 min)
**File**: [05-writing-healthcare-tests.md](./05-writing-healthcare-tests.md)

Ensure your code works reliably with proper testing.

**You'll learn**:
- Why testing matters in healthcare
- Write unit tests for service methods
- Use mocks for external dependencies
- Add test fixtures
- Run tests locally with pytest
- Check test coverage

**Prerequisites**: Completed Tutorial 4, basic pytest knowledge

---

### Tutorial 6: Your First Pull Request (30 min)
**File**: [06-first-pull-request.md](./06-first-pull-request.md)

Contribute your changes back to the project following standards.

**You'll learn**:
- Create a feature branch
- Review your changes
- Follow commit message conventions
- Push to GitHub
- Create a clear pull request
- Respond to review feedback

**Prerequisites**: Completed Tutorials 1-5, Git basics

---

## How to Use These Tutorials

### Sequential Path (Recommended)
Work through tutorials 1-6 in order. Each builds on previous concepts.

### Just-in-Time Learning
If you're already familiar with some topics:
- **Know Python?** Start at Tutorial 2
- **Environment setup done?** Jump to Tutorial 3
- **Need testing help?** Go directly to Tutorial 5

### Learning Styles

**Hands-On Learners**: Follow step-by-step instructions exactly as written

**Explorers**: Use tutorials as guides but experiment with variations

**Reference Users**: Skim for key concepts, dive deep when needed

---

## Prerequisites for the Entire Path

**Required**:
- Python 3.10 or higher installed
- Git installed and configured
- Basic terminal/command line knowledge
- Text editor or IDE (VS Code recommended)
- GitHub account (for Tutorial 6)

**Helpful but Not Required**:
- Python programming basics (variables, functions, classes)
- FastAPI or web framework experience
- Understanding of REST APIs
- Healthcare or clinical knowledge

**Don't worry if you're missing some skills** - tutorials include explanations and links to learning resources.

---

## Sample Code and Examples

Working code examples are in the `examples/` directory:

- **examples/patient_age_service.py**: Complete service method from Tutorial 4
- **examples/test_patient_age.py**: Complete test from Tutorial 5

Use these as reference when following tutorials or adapting for your own features.

---

## What You'll Be Able to Do After Completion

**Technical Skills**:
- Set up and run AI Nurse Florence locally
- Navigate the codebase confidently
- Add new service methods following patterns
- Write unit tests with mocks and fixtures
- Create pull requests following project standards

**Project Knowledge**:
- Understand the Service Layer Pattern
- Know where to find documentation
- Follow coding standards and conventions
- Use Swagger UI for API testing
- Debug common issues

**Contribution Ready**:
- Pick up good first issues from GitHub
- Implement features independently
- Write tests that pass CI
- Respond to code review feedback
- Collaborate with maintainers

---

## Getting Help

**Stuck on a tutorial?**
1. Check the "Troubleshooting" section in each tutorial
2. Review related documentation in `docs/`
3. Search GitHub Issues for similar problems
4. Ask in GitHub Discussions

**Found an error in a tutorial?**
- Open a GitHub Issue with the tutorial name and problem description
- Or submit a PR with the fix (great practice!)

**Want to suggest improvements?**
- Open a GitHub Discussion with your ideas
- Contribute example code or screenshots

---

## Next Steps After Completing Tutorials

### Good First Issues
Browse GitHub Issues labeled `good-first-issue` to find beginner-friendly tasks.

### Related Documentation
- **[PATTERNS.md](../PATTERNS.md)**: Deep dive into code patterns
- **[CODING_STANDARDS.md](../CODING_STANDARDS.md)**: Complete coding standards
- **[CONTRIBUTING.md](../../CONTRIBUTING.md)**: Contribution guidelines

### Advanced Topics
- Add integration with external EHR systems
- Implement new clinical decision support features
- Contribute to internationalization (i18n)
- Improve test coverage

---

## Tutorial Maintenance

**Last Updated**: 2025-10-07

**Tutorial Authors**: AI Nurse Florence maintainers

**Feedback**: If you completed these tutorials, please share feedback in GitHub Discussions to help us improve them for future contributors.

---

**Ready to start?** Begin with [Tutorial 1: Environment Setup](./01-environment-setup.md)
