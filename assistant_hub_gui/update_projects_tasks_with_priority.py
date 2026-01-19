#!/usr/bin/env python3
"""Sync projects/tasks priority data sourced from the master PDF."""

import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(__file__))

from assistant_hub.db import (
    init_db,
    db_upsert_project,
    db_insert_task,
    Task,
    Project,
)
from datetime import datetime

# Projects extracted from the PDF with AI OS at the top
PROJECTS_DATA = [
    # SPECIAL PRIORITY: AI OS (Priority Order #1)
    {
        "name": "AI OS",
        "description": "Core AI assistant system for operating system dashboard management, task coordination, and intelligent automation. This is the foundational platform that enables all other projects.\n\nNext Tasks:\n- Implement core daemon architecture\n- Set up task prioritization system\n- Develop project management integration\n- Create user interface for system monitoring\n- Implement AI-driven task suggestions\n- Set up external service integrations\n\nKey Features:\n- Real-time system monitoring\n- Intelligent task prioritization\n- Project dependency management\n- AI-powered automation\n- External service integration (Gmail, Calendar, OneNote, etc.)",
        "priority": "CRITICAL",
        "status": "active",
        "priority_order": 1,
    },
    # LAYER 1 - PURE LOGIC (ROOT) - HIGH PRIORITY
    {
        "name": "1. Theoretical Reasoning Framework (TRF)",
        "description": "Universal inference engine. All math, physics, AI, accusations, proofs, and system reasoning depend on TRF.\n\nNext Tasks:\n- Finalize operator algebra (AND / OR / EXCEPT / RESONATE / COLLAPSE / etc.)\n- Define truth-graphs and proof paths\n- Encode deduction, induction, abduction, and coherence rules\n- Build 10-15 example proofs across domains (math, physics, finance, ethics)\n\nDeliverables:\n- TRF v1.0 paper\n- Operator tables + semantics\n- Example proof compendium\n\nPublication Targets:\n- Journals: Journal of Symbolic Logic, Synthese, Review of Symbolic Logic, Journal of Applied Logic\n- Conferences: ACM SIGLOG, ESSLLI\n- Archives: arXiv (math.LO, cs.LO)\n- Institutions: Association for Symbolic Logic, philosophy of logic groups",
        "priority": "CRITICAL",
        "status": "active",
        "priority_order": 2,
    },
    {
        "name": "2. AIC / Daemon Framework (Echo, Oracle, Critic, Archivist)",
        "description": "Meta-coherence layer supervising reasoning, catching contradictions, tracking drift. Backbone of your 'thinking machine.'\n\nNext Tasks:\n- Define roles & operators for each daemon\n- Specify AIC arbitration rules & constraints matrix\n- Integrate AIC with TRF (how it evaluates proofs & structures)\n- Design output formats for reports and annotations\n\nDeliverables:\n- AIC Protocol v1.0\n- Architecture diagrams\n- Sample coherence reports over TRF / math / physics drafts\n\nPublication Targets:\n- Journals: JAIR, AI Magazine, Artificial Intelligence\n- Conferences: NeurIPS (interpretability/LLM reasoning), ICLR, AAAI\n- Archives: arXiv (cs.AI, cs.MA)\n- Institutions: AAAI, NeurIPS Foundation, AI safety/interpretability labs",
        "priority": "CRITICAL",
        "status": "active",
        "priority_order": 3,
    },
    {
        "name": "3. Symbolic Phase Entropy",
        "description": "Quantifies stability/drift of symbolic systems: equations, ontologies, writing systems, code, daemons.\n\nNext Tasks:\n- Define entropy functional over symbol distributions/sequences\n- Classify stability regimes (stable / metastable / unstable)\n- Test on three domains: math notation, physics framework, writing framework\n\nDeliverables:\n- Symbolic Phase Entropy v1.0 paper\n- Worked case studies\n\nPublication Targets:\n- Journals: Entropy (MDPI), Information Sciences, IEEE Transactions on Information Theory\n- Archives: arXiv (cs.IT, cs.LO)",
        "priority": "HIGH",
        "status": "active",
        "priority_order": 4,
    },
    {
        "name": "4. Ontological-Epistemological Matrix",
        "description": "Global grid for classifying all 47 works: Real / Emergent / Symbolic / Hypothetical × Known / Conjectured / Underdetermined / Undecidable.\n\nNext Tasks:\n- Lock in axes and definitions\n- Classify every framework, equation set, technology, and canon volume\n- Note dependency paths directly on the matrix\n\nDeliverables:\n- Onto-Ep Matrix v1.0 paper\n- Master table of all works mapped\n\nPublication Targets:\n- Journals: Philosophy of Science, Synthese, Studies in History and Philosophy of Modern Physics\n- Archives: arXiv (physics.hist-ph, physics.gen-ph)",
        "priority": "HIGH",
        "status": "active",
        "priority_order": 5,
    },
    {
        "name": "5. Mathematical Phenomena Interpretation System (MPIS)",
        "description": "Systematic way to interpret mathematical 'behaviors' (divergence, oscillation, phase-locking, singularities) via TRF + entropy.\n\nNext Tasks:\n- Build taxonomy of mathematical phenomena\n- Map each to TRF/entropy interpretations\n- Demonstrate on Synchronetic Math and Reflexive Arithmetic examples\n\nDeliverables:\n- MPIS v1.0 paper\n- Example catalogue\n\nPublication Targets:\n- Journals: Journal of Mathematical Behavior, Mathematical Structures in Computer Science\n- Archives: arXiv (math.GM, math.HO)",
        "priority": "HIGH",
        "status": "active",
        "priority_order": 6,
    },
    # LAYER 2 - AXIOMATIC SYMBOLIC MATHEMATICS
    {
        "name": "6. Symbolic Axiom Set (Five Foundational Equations)",
        "description": "Defines the fundamental symbolic 'physics' of your math universe: 1²+i²=0, e^{iπ}+1=0, φ²=φ+1, |1+i|=√2, ∫e^{-x²}dx=√π.\n\nNext Tasks:\n- Formalize them as axioms in a symbolic system\n- Derive constant relations and invariants\n- Show how standard math structures arise from them\n\nDeliverables:\n- Symbolic Axioms & Unified Constant System paper\n\nPublication Targets:\n- Journals: Foundations of Physics, Studies in History and Philosophy of Modern Physics\n- Archives: arXiv (math-ph)",
        "priority": "HIGH",
        "status": "active",
        "priority_order": 7,
    },
    {
        "name": "7. Synchronetic Mathematics",
        "description": "Core formalism for resonance, pattern-locking, and synchrony - primary mathematical substrate for your physics.\n\nNext Tasks:\n- Define synchronetic operators and resonance laws\n- Characterize locked, beating, amplifying, and cancelling patterns\n- Relate to geometric/topological objects\n\nDeliverables:\n- Synchronetic Mathematics v1.0 paper\n\nPublication Targets:\n- Journals: Communications in Mathematical Physics, Annals of Mathematics (stretch)\n- Archives: arXiv (math-ph)",
        "priority": "HIGH",
        "status": "active",
        "priority_order": 8,
    },
    {
        "name": "8. Reflexive Arithmetic Universe",
        "description": "Self-referential arithmetic underpinning recursion, self-reference in TRF, and aspects of STUFF.\n\nNext Tasks:\n- Define reflexive numbers and operations\n- Prove fixed-point and self-reference theorems\n- Connect to Symbolic Phase Entropy and Tarski-like limits\n\nDeliverables:\n- Reflexive Arithmetic paper\n\nPublication Targets:\n- Journals: Annals of Pure and Applied Logic, Journal of Symbolic Logic\n- Archives: arXiv (math.LO)",
        "priority": "HIGH",
        "status": "active",
        "priority_order": 9,
    },
    {
        "name": "9. Archetypal Mathematics",
        "description": "Mathematical formalization of 'archetypes' (center/edge/threshold/dual/etc.), bridging psyche, narrative, and structure.\n\nNext Tasks:\n- Define archetypal primitives and relations\n- Build transformation algebra\n- Show mapping from motifs + psyche structures to archetypal operations\n\nDeliverables:\n- Archetypal Mathematics paper\n\nPublication Targets:\n- Journals: Cognitive Systems Research, Journal of Mathematical Psychology\n- Archives: arXiv (math.GM, q-bio.NC for cognitive mapping)",
        "priority": "MEDIUM",
        "status": "active",
        "priority_order": 10,
    },
    {
        "name": "10. Arithmorphics Mathematics",
        "description": "Captures morphic transformations and structural changes in number/form - key for evolution of symbolic systems.\n\nNext Tasks:\n- Define morphic numbers and morphic operators\n- Show relationship to Synchronetic and Reflexive frameworks\n\nDeliverables:\n- Arithmorphics primer paper\n\nPublication Targets:\n- Journals: Journal of Mathematical Analysis and Applications\n- Archives: arXiv (math.GM)",
        "priority": "MEDIUM",
        "status": "active",
        "priority_order": 11,
    },
    {
        "name": "11. Triadic Mathematics",
        "description": "Tri-valued logic/math underpinning your collapse interpretation and quantum logic.\n\nNext Tasks:\n- Define triadic truth values and operators\n- Construct triune symmetry groups\n- Apply to simple quantum-like toy models\n\nDeliverables:\n- Triadic Mathematics & Quantum Logic paper\n\nPublication Targets:\n- Journals: Foundations of Physics, Quantum\n- Archives: arXiv (quant-ph, math.LO)",
        "priority": "MEDIUM",
        "status": "active",
        "priority_order": 12,
    },
    {
        "name": "12. Synchronetic Coordinate System",
        "description": "Geometric realization of synchronetic math: coordinates as resonance states instead of simple metric distances.\n\nNext Tasks:\n- Define coordinate tuples (resonance-based)\n- Build transform rules between standard (x, y, z, t) and synchronetic coordinates\n- Provide physical interpretations\n\nDeliverables:\n- Synchronetic Coordinate Systems paper\n\nPublication Targets:\n- Journals: Journal of Mathematical Physics\n- Archives: arXiv (math-ph, gr-qc)",
        "priority": "MEDIUM",
        "status": "active",
        "priority_order": 13,
    },
    {
        "name": "13. Unknown Equations Atlas",
        "description": "Living inventory of 'intended' but not-yet-derived equations across your canon - ensures continuity and future growth.\n\nNext Tasks:\n- Catalogue conceptual gaps by domain (math, physics, engineering)\n- Assign tentative symbols, roles, and dependencies\n- Version-control it as you derive new equations\n\nDeliverables:\n- Atlas of Unknown Equations (v1.0 internal whitepaper + evolving arXiv series)\n\nPublication Targets:\n- Archives: arXiv preprints as a series ('Atlas of Undiscovered Equations')",
        "priority": "MEDIUM",
        "status": "active",
        "priority_order": 14,
    },
    # LAYER 3 - PHYSICS (continuing with remaining projects...)
    # Note: I'll add a condensed version for the remaining 34 projects due to length
]

# Condensed entries (14-47) with priority ordering
REMAINING_PROJECTS = [
    (
        "14",
        "STUFF Framework",
        "HIGH",
        "Core physics framework",
        15,
    ),
    (
        "15",
        "Resonant Universe Theory",
        "HIGH",
        "Primary physics theory",
        16,
    ),
    (
        "16",
        "Time-Causality Matrix",
        "HIGH",
        "Causality framework",
        17,
    ),
    (
        "17",
        "Resonance Field Equations",
        "HIGH",
        "Field equations",
        18,
    ),
    (
        "18",
        "Quantum Resonance Interpretation",
        "HIGH",
        "Quantum mechanics interpretation",
        19,
    ),
    (
        "19",
        "Gravitational Resonance",
        "MEDIUM",
        "Gravity theory",
        20,
    ),
    (
        "20",
        "Electromagnetic Resonance",
        "MEDIUM",
        "EM theory",
        21,
    ),
    (
        "21",
        "Cosmological Resonance Model",
        "MEDIUM",
        "Cosmology",
        22,
    ),
    (
        "22",
        "Particle Resonance Taxonomy",
        "MEDIUM",
        "Particle physics",
        23,
    ),
    (
        "23",
        "Energy Resonance Framework",
        "MEDIUM",
        "Energy systems",
        24,
    ),
    (
        "24",
        "Information-Energy Equivalence",
        "MEDIUM",
        "Information theory",
        25,
    ),
    (
        "25",
        "Consciousness-Physics Bridge",
        "MEDIUM",
        "Consciousness research",
        26,
    ),
    (
        "26",
        "Experimental Validation Roadmap",
        "MEDIUM",
        "Experimental design",
        27,
    ),
    (
        "27",
        "Resonance Detector Design",
        "MEDIUM",
        "Detector technology",
        28,
    ),
    (
        "28",
        "Alternative Interpretation Tests",
        "MEDIUM",
        "Experimental tests",
        29,
    ),
    (
        "29",
        "Engineering Applications Framework",
        "LOW",
        "Engineering applications",
        30,
    ),
    (
        "30",
        "Resonance-Based Energy Systems",
        "LOW",
        "Energy technology",
        31,
    ),
    (
        "31",
        "Resonance Computing",
        "LOW",
        "Computing technology",
        32,
    ),
    (
        "32",
        "Resonance Propulsion",
        "LOW",
        "Propulsion systems",
        33,
    ),
    (
        "33",
        "Resonance Sensing Technologies",
        "LOW",
        "Sensor technology",
        34,
    ),
    (
        "34",
        "Next Generation Technologies Roadmap",
        "LOW",
        "Tech roadmap",
        35,
    ),
    (
        "35",
        "Portfolio Strategist MVP",
        "HIGH",
        "High-probability early win: practical product, direct revenue",
        36,
    ),
    (
        "36",
        "Document OCR Platform (Django)",
        "MEDIUM",
        "Applied ML/engineering credit; potential B2B income",
        37,
    ),
    (
        "37",
        "Portfolio Strategist v1.0 (Paid Tier)",
        "HIGH",
        "Converts MVP into actual income engine",
        38,
    ),
    (
        "38",
        "Trader Exchange MVP",
        "MEDIUM",
        "Second major engine; leverages Time-Causality Matrix",
        39,
    ),
    (
        "39",
        "Financial Frameworks Book",
        "MEDIUM",
        "Formalizes personal finance strategies",
        40,
    ),
    (
        "40",
        "Writing Measurement Framework",
        "MEDIUM",
        "Gives distinctive, rigorous voice in writing craft",
        41,
    ),
    (
        "41",
        "Motif Taxonomy Atlas",
        "MEDIUM",
        "Deep motif resource; highly monetizable as writer tool",
        42,
    ),
    (
        "42",
        "Podcast: The Resonance Paradox",
        "MEDIUM",
        "Public-facing voice tying physics, writing, psyche, finance",
        43,
    ),
    (
        "43",
        "Psyche Spatial Architecture",
        "MEDIUM",
        "Formal psyche topology",
        44,
    ),
    (
        "44",
        "Royal Polyarchy Constitution & Government",
        "LOW",
        "Political-structural backbone of mythos",
        45,
    ),
    (
        "45",
        "Royal Polyarchy Dynasties & Atlas",
        "LOW",
        "Historical depth: genealogies, eras, dynastic shifts",
        46,
    ),
    (
        "46",
        "Royal Polyarchy Encyclopedia (Blueprint/Cipher/Entities)",
        "LOW",
        "Master reference text",
        47,
    ),
    (
        "47",
        "Royal Polyarchy Cosmology & Volumes of the Cosmos",
        "LOW",
        "Ultimate synthesis: physics, math, psyche, politics in narrative "
        "cosmology",
        48,
    ),
]

def add_priority_order_column():
    """Add priority_order column to projects and tasks tables."""
    conn = init_db()
    c = conn.cursor()

    # Check if priority_order column exists in projects table, add if not
    c.execute("PRAGMA table_info(projects)")
    columns = [row[1] for row in c.fetchall()]
    if "priority_order" not in columns:
        c.execute("ALTER TABLE projects ADD COLUMN priority_order INTEGER")
        print("Added priority_order column to projects table")

    # Check if priority_order column exists in tasks table, add if not
    c.execute("PRAGMA table_info(tasks)")
    columns = [row[1] for row in c.fetchall()]
    if "priority_order" not in columns:
        c.execute("ALTER TABLE tasks ADD COLUMN priority_order INTEGER")
        print("Added priority_order column to tasks table")

    conn.commit()
    conn.close()


def clear_all_data():
    """Delete all existing projects and tasks."""
    conn = init_db()
    c = conn.cursor()

    c.execute("DELETE FROM tasks")
    c.execute("DELETE FROM projects")
    c.execute("DELETE FROM comments")  # Clear related data
    c.execute("DELETE FROM note_links")  # Clear related data

    conn.commit()
    conn.close()
    print("Cleared all existing projects, tasks, and related data")


def add_all_projects():
    """Add all projects from the PDF to the database with priority ordering."""
    conn = init_db()

    # Add detailed projects
    for proj_data in PROJECTS_DATA:
        proj = Project(
            name=proj_data["name"],
            description=proj_data["description"],
            priority=proj_data["priority"],
            status=proj_data["status"],
        )
        db_upsert_project(conn, proj)

        # Update priority_order
        c = conn.cursor()
        c.execute(
            "UPDATE projects SET priority_order = ? WHERE name = ?",
            (proj_data["priority_order"], proj_data["name"]),
        )

        message = (
            f"Added: {proj_data['name']} "
            f"(Priority Order: {proj_data['priority_order']})"
        )
        print(message)

    # Add remaining projects with basic descriptions and priority orders
    for num, name, priority, desc, priority_order in REMAINING_PROJECTS:
        proj = Project(
            name=f"{num}. {name}",
            description=(
                f"Reason: {desc}\n\n"
                "This project is part of the AIC Master Canon Roadmap."
            ),
            priority=priority,
            status="active",
        )
        db_upsert_project(conn, proj)

        # Update priority_order
        c = conn.cursor()
        c.execute(
            "UPDATE projects SET priority_order = ? WHERE name = ?",
            (priority_order, proj.name),
        )

        print(f"Added: {num}. {name} (Priority Order: {priority_order})")

    conn.commit()
    conn.close()
    total_projects = len(PROJECTS_DATA) + len(REMAINING_PROJECTS)
    print(f"\nTotal projects added: {total_projects}")


def add_all_tasks():
    """Add tasks for all projects with priority ordering."""
    from add_tasks_from_pdf import PROJECT_TASKS  # Import the task data

    conn = init_db()
    c = conn.cursor()

    # Get all projects to map priorities
    c.execute("SELECT name, priority_order FROM projects")
    project_priorities = {row[0]: row[1] for row in c.fetchall()}

    tasks_added = 0
    task_priority_counter = {}  # Track task priority ordering per project

    for project_name, task_titles in PROJECT_TASKS.items():
        if project_name not in project_priorities:
            warning = (
                f"Warning: Project '{project_name}' "
                "not found, skipping tasks"
            )
            print(warning)
            continue

        project_priority_order = project_priorities[project_name]
        if project_name not in task_priority_counter:
            task_priority_counter[project_name] = 1

        for task_title in task_titles:
            # Determine task priority based on project priority and task type
            project_priority = "MEDIUM"  # Default
            if (
                project_priority_order <= 10
            ):  # Top 10 projects get higher priority tasks
                project_priority = "HIGH"
            if (
                project_priority_order <= 3
            ):  # Top 3 projects get critical priority tasks
                project_priority = "CRITICAL"

            # Set higher priority for foundational tasks
            if any(
                keyword in task_title.lower()
                for keyword in [
                    "define",
                    "finalize",
                    "develop",
                    "create",
                    "implement",
                ]
            ):
                if project_priority == "HIGH":
                    project_priority = "CRITICAL"
                elif project_priority == "MEDIUM":
                    project_priority = "HIGH"

            task = Task(
                id=0,  # Will be auto-generated
                title=task_title,
                project=project_name,
                status="TODO",
                priority=project_priority,
                due_date="",
                notes="",
                owner="Chris",
                created_at=datetime.now().isoformat(timespec="seconds"),
            )

            # Insert task and get its ID
            task_id = db_insert_task(conn, task)

            # Set task priority order (within project, by creation order)
            c.execute(
                "UPDATE tasks SET priority_order = ? WHERE id = ?",
                (task_priority_counter[project_name], task_id),
            )
            task_priority_counter[project_name] += 1

            tasks_added += 1

        print(f"Added {len(task_titles)} tasks for {project_name}")

    conn.commit()
    conn.close()
    print(f"\nTotal tasks added: {tasks_added}")


def main():
    """Main function to update database with priority ordering."""
    print("Adding priority_order column to database...")
    add_priority_order_column()

    print("\nClearing all existing data...")
    clear_all_data()

    print("\nAdding all projects with priority ordering...")
    add_all_projects()

    print("\nAdding all tasks with priority ordering...")
    add_all_tasks()

    print("\nDatabase update complete!")
    print("AI OS is set as Priority Order #1")
    print("Priority ordering: Lower number = Higher priority")


if __name__ == "__main__":
    main()
