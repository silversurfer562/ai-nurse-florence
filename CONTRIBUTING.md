# Contributing to AI Nurse Florence

Welcome to the AI Nurse Florence project! We're excited that you're interested in contributing to our public benefit healthcare technology initiative.

## 🏥 Our Public Benefit Mission

Deep Study AI, LLC is committed to advancing healthcare accessibility and quality through responsible AI technology. All contributions should align with our mission of empowering healthcare professionals with evidence-based information tools while prioritizing patient safety, data privacy, and equitable access to medical knowledge.

## 🤝 How to Contribute

### Types of Contributions We Welcome

1. **Medical Information Accuracy**
   - Fact-checking medical content and references
   - Improving clinical terminology and descriptions
   - Enhancing evidence-based information sources

2. **Healthcare Accessibility Features**
   - Improving readability and user experience for healthcare professionals
   - Adding support for multiple languages
   - Enhancing accessibility for users with disabilities

3. **Technical Improvements**
   - Bug fixes and performance optimizations
   - Security enhancements
   - Documentation improvements

4. **Community Health Impact**
   - Features that support underserved healthcare communities
   - Tools that improve healthcare information equity
   - Educational content for healthcare professionals

### Contribution Guidelines

#### Before You Start
1. **Check our Mission Alignment**: Ensure your contribution supports our public benefit mission
2. **Review Existing Issues**: Look for existing issues or discussions related to your idea
3. **Create an Issue**: For new features, create an issue to discuss the proposal first

#### Development Process

1. **Fork the Repository**
   ```bash
   git fork https://github.com/silversurfer562/ai-nurse-florence.git
   cd ai-nurse-florence
   ```

2. **Set Up Development Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Your Changes**
   - Follow our coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed

5. **Test Your Changes**
   ```bash
   pytest
   flake8 .
   mypy --ignore-missing-imports services routers utils
   ```

6. **Commit Your Changes**
   ```bash
   git commit -m "feat: add feature supporting healthcare accessibility"
   ```

7. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

#### Code Standards

All contributors must follow our established development standards:

- **Development Philosophy**: Read [DEVELOPMENT_PHILOSOPHY.md](./docs/DEVELOPMENT_PHILOSOPHY.md) for core principles
- **Coding Standards**: Follow [CODING_STANDARDS.md](./docs/CODING_STANDARDS.md) for Python, FastAPI, and healthcare-specific standards
- **Code Patterns**: Use patterns from [PATTERNS.md](./docs/PATTERNS.md) for consistency
- **Documentation Policy**: Follow [DOCUMENTATION_POLICY.md](./docs/DOCUMENTATION_POLICY.md) for writing clear, audience-focused docs
- **Architectural Decisions**: Review [ADRs](./docs/adr/) to understand key technical choices
- **Medical Accuracy**: Ensure all medical information is accurate and properly sourced

#### Documentation Standards

> **This book uses plain language and role-based navigation. New readers get simple explanations of purpose and reasoning; practitioners find just-in-time how-tos and reference; deep dives live in explanations. This structure keeps learning efficient and filters out unrelated detail.**

When contributing documentation:
- **Identify the category**: Is this a tutorial, how-to, reference, or explanation?
- **State your audience**: First paragraph must say who this is for
- **Use plain language**: Define technical terms, explain the "why"
- **Include examples**: Show working code from the actual codebase
- **Add signposts**: "If you're new, start here. If experienced, skip to..."

See [DOCUMENTATION_POLICY.md](./docs/DOCUMENTATION_POLICY.md) for complete guidelines and templates.

#### Pull Request Guidelines

- **Clear Description**: Explain how your changes support our public benefit mission
- **Medical Safety**: Confirm that changes maintain patient safety standards
- **Privacy Compliance**: Ensure no PHI handling or storage is introduced
- **Evidence-Based**: Provide sources for any medical information added

## 🛡️ Medical Information Standards

### Required Standards
- All medical information must include appropriate disclaimers
- Sources must be from reputable medical literature or organizations
- Content must include educational context for healthcare professionals
- No diagnostic or treatment recommendations for specific patients

### Prohibited Content
- Personal health information (PHI) handling or storage
- Diagnostic recommendations for individual patients
- Treatment advice without proper clinical context
- Medical information without evidence-based sources

## 🔐 Security & Privacy

- Never commit API keys, passwords, or sensitive configuration
- Ensure all external service integrations maintain privacy standards
- Report security vulnerabilities privately before creating public issues
- Follow HIPAA-aligned principles even when PHI is not directly handled

## 📋 Issue Templates

### Bug Reports
- **Impact on Healthcare Professionals**: How does this affect users?
- **Steps to Reproduce**: Clear reproduction steps
- **Expected vs. Actual Behavior**: What should happen vs. what does happen
- **Medical Safety Impact**: Any potential safety implications

### Feature Requests
- **Public Benefit Alignment**: How does this support our healthcare mission?
- **Healthcare Professional Benefit**: Who will this help and how?
- **Evidence-Based Rationale**: Why is this feature needed?
- **Implementation Approach**: Suggested technical approach

## 🌍 Community Guidelines

### Respectful Communication
- Use inclusive, professional language
- Respect diverse healthcare perspectives and experiences
- Focus on patient safety and healthcare accessibility in discussions

### Collaboration Principles
- Prioritize public benefit and healthcare outcomes
- Share knowledge to benefit the healthcare community
- Provide constructive feedback to improve healthcare tools

## 📞 Getting Help

- **Documentation**: Check our [Developer Guide](docs/developer_guide.md)
- **Discussions**: Use GitHub Discussions for questions
- **Healthcare Context**: Ask healthcare professionals in our community for clinical guidance
- **Technical Issues**: Create issues with detailed reproduction steps

## 🏆 Recognition

Contributors who make significant contributions to our public benefit mission will be recognized in our:
- Annual public benefit impact reports
- Healthcare community acknowledgments
- Project documentation and credits

## 📜 Code of Conduct

This project follows a healthcare-focused code of conduct prioritizing:
- Patient safety and privacy
- Evidence-based information sharing
- Respectful professional communication
- Commitment to healthcare accessibility and equity

## 📈 Measuring Impact

We track our public benefit impact through:
- Healthcare professional usage and feedback
- Medical information accuracy improvements
- Accessibility feature adoption
- Community health outcomes

Thank you for contributing to healthcare accessibility through responsible AI technology!

---

**Questions?** Contact us at patrickroebuck@pm.me or create a discussion in our GitHub repository.