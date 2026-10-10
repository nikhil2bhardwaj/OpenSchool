# Project Master Brief \& Architectural Non-Negotiables



## 1.1 Core Mission

OpenSchool is an open-source, zero-dependency, static virtual laboratory platform mapped to the NCERT / CBSE Class 9–12 Science Practical Curriculum. It enables experiential laboratory learning for underfunded or remote schools without physical apparatus.


## 1.2 Non-Negotiable Technical Constraints



Any code generated for this project must strictly comply with the following architectural
boundaries:
● Zero-Build, Pure Static Architecture: No bundlers (npm, vite, webpack), no frameworks (React, Vue), and no transpilers. Every file must run directly when opened via file:/// or served statically via GitHub Pages.
● One Self-Contained HTML File Per Experiment: Each experiment is an autonomous sandbox (labs/class12/physics/meter\_bridge.html) containing its own simulation engine, UI, observation table, error calculation, and viva-voce tester.
● Separation of Deterministic Math and LLM Logic:
○ Simulation Math: Computed exclusively via deterministic JavaScript algorithms (Runge-Kutta numerical integration, Thevenin equivalent bridge analysis, chemical equilibrium curves). The LLM is strictly prohibited from generating raw physical simulation numbers.
○ LLM Role: Acts strictly as the Socratic tutor, Viva-Voce examiner, and pedagogicaltier adapter.
● Local-First Persistence: Observation tables, recorded constants, and Viva-Voce defense scores are saved to browser-native IndexedDB with zero external dependencies.
● Dual Operation Mode:
○ 100% Offline / Zero-AI Mode: Pre-baked NCERT viva questions, automated numerical validation, and manual error checks.
○ AI-Connected Mode: Connects via local Ollama (http://localhost:11434) or user-supplied API keys (OpenAI / Anthropic / OpenRouter) for dynamic
examination.

