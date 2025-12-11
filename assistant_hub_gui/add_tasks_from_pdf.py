#!/usr/bin/env python3
"""Script to add tasks for each project from the PDF deliverables."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from assistant_hub.db import (
    init_db,
    db_insert_task,
    db_upsert_project,
    Task,
    Project,
    load_state,
)
from datetime import datetime

# Map of project names to their tasks from the PDF
PROJECT_TASKS = {
    "1. Theoretical Reasoning Framework (TRF)": [
        "Finalize operator algebra (AND / OR / EXCEPT / RESONATE / COLLAPSE / etc.)",
        "Define truth-graphs and proof paths",
        "Encode deduction, induction, abduction, and coherence rules",
        "Build 10-15 example proofs across domains (math, physics, finance, ethics)",
        "Write TRF v1.0 paper",
        "Create operator tables + semantics documentation",
        "Compile example proof compendium",
        "Prepare submission to Journal of Symbolic Logic",
        "Prepare submission to Synthese",
        "Prepare submission to Review of Symbolic Logic",
        "Prepare arXiv submission (math.LO, cs.LO)",
    ],
    "2. AIC / Daemon Framework (Echo, Oracle, Critic, Archivist)": [
        "Define roles & operators for each daemon",
        "Specify AIC arbitration rules & constraints matrix",
        "Integrate AIC with TRF (how it evaluates proofs & structures)",
        "Design output formats for reports and annotations",
        "Write AIC Protocol v1.0 document",
        "Create architecture diagrams",
        "Generate sample coherence reports over TRF / math / physics drafts",
        "Prepare submission to JAIR",
        "Prepare submission to AI Magazine",
        "Prepare submission to Artificial Intelligence journal",
        "Prepare NeurIPS submission (interpretability/LLM reasoning track)",
    ],
    "3. Symbolic Phase Entropy": [
        "Define entropy functional over symbol distributions/sequences",
        "Classify stability regimes (stable / metastable / unstable)",
        "Test on math notation domain",
        "Test on physics framework domain",
        "Test on writing framework domain",
        "Write Symbolic Phase Entropy v1.0 paper",
        "Create worked case studies",
        "Prepare submission to Entropy (MDPI)",
        "Prepare submission to Information Sciences",
        "Prepare submission to IEEE Transactions on Information Theory",
        "Prepare arXiv submission (cs.IT, cs.LO)",
    ],
    "4. Ontological-Epistemological Matrix": [
        "Lock in axes and definitions",
        "Classify every framework in the matrix",
        "Classify every equation set in the matrix",
        "Classify every technology in the matrix",
        "Classify every canon volume in the matrix",
        "Note dependency paths directly on the matrix",
        "Write Onto-Ep Matrix v1.0 paper",
        "Create master table of all works mapped",
        "Prepare submission to Philosophy of Science",
        "Prepare submission to Synthese",
        "Prepare submission to Studies in History and Philosophy of Modern Physics",
        "Prepare arXiv submission (physics.hist-ph, physics.gen-ph)",
    ],
    "5. Mathematical Phenomena Interpretation System (MPIS)": [
        "Build taxonomy of mathematical phenomena",
        "Map each phenomenon to TRF/entropy interpretations",
        "Demonstrate on Synchronetic Math examples",
        "Demonstrate on Reflexive Arithmetic examples",
        "Write MPIS v1.0 paper",
        "Create example catalogue",
        "Prepare submission to Journal of Mathematical Behavior",
        "Prepare submission to Mathematical Structures in Computer Science",
        "Prepare arXiv submission (math.GM, math.HO)",
    ],
    "6. Symbolic Axiom Set (Five Foundational Equations)": [
        "Formalize five foundational equations as axioms in a symbolic system",
        "Derive constant relations and invariants",
        "Show how standard math structures arise from them",
        "Write Symbolic Axioms & Unified Constant System paper",
        "Prepare submission to Foundations of Physics",
        "Prepare submission to Studies in History and Philosophy of Modern Physics",
        "Prepare arXiv submission (math-ph)",
    ],
    "7. Synchronetic Mathematics": [
        "Define synchronetic operators and resonance laws",
        "Characterize locked patterns",
        "Characterize beating patterns",
        "Characterize amplifying patterns",
        "Characterize cancelling patterns",
        "Relate to geometric/topological objects",
        "Write Synchronetic Mathematics v1.0 paper",
        "Prepare submission to Communications in Mathematical Physics",
        "Prepare submission to Annals of Mathematics (stretch goal)",
        "Prepare arXiv submission (math-ph)",
    ],
    "8. Reflexive Arithmetic Universe": [
        "Define reflexive numbers and operations",
        "Prove fixed-point theorems",
        "Prove self-reference theorems",
        "Connect to Symbolic Phase Entropy",
        "Connect to Tarski-like limits",
        "Write Reflexive Arithmetic paper",
        "Prepare submission to Annals of Pure and Applied Logic",
        "Prepare submission to Journal of Symbolic Logic",
        "Prepare arXiv submission (math.LO)",
    ],
    "9. Archetypal Mathematics": [
        "Define archetypal primitives and relations",
        "Build transformation algebra",
        "Show mapping from motifs to archetypal operations",
        "Show mapping from psyche structures to archetypal operations",
        "Write Archetypal Mathematics paper",
        "Prepare submission to Cognitive Systems Research",
        "Prepare submission to Journal of Mathematical Psychology",
        "Prepare arXiv submission (math.GM, q-bio.NC for cognitive mapping)",
    ],
    "10. Arithmorphics Mathematics": [
        "Define morphic numbers and morphic operators",
        "Show relationship to Synchronetic framework",
        "Show relationship to Reflexive framework",
        "Write Arithmorphics primer paper",
        "Prepare submission to Journal of Mathematical Analysis and Applications",
        "Prepare arXiv submission (math.GM)",
    ],
    "11. Triadic Mathematics": [
        "Define triadic truth values and operators",
        "Construct triune symmetry groups",
        "Apply to simple quantum-like toy models",
        "Write Triadic Mathematics & Quantum Logic paper",
        "Prepare submission to Foundations of Physics",
        "Prepare submission to Quantum journal",
        "Prepare arXiv submission (quant-ph, math.LO)",
    ],
    "12. Synchronetic Coordinate System": [
        "Define coordinate tuples (resonance-based)",
        "Build transform rules between standard (x, y, z, t) and synchronetic coordinates",
        "Provide physical interpretations",
        "Write Synchronetic Coordinate Systems paper",
        "Prepare submission to Journal of Mathematical Physics",
        "Prepare arXiv submission (math-ph, gr-qc)",
    ],
    "13. Unknown Equations Atlas": [
        "Catalogue conceptual gaps in math domain",
        "Catalogue conceptual gaps in physics domain",
        "Catalogue conceptual gaps in engineering domain",
        "Assign tentative symbols, roles, and dependencies",
        "Set up version-control system for the atlas",
        "Create Atlas of Unknown Equations v1.0 internal whitepaper",
        "Prepare first arXiv preprint in series",
    ],
    "14. STUFF Framework": [
        "Define STUFF core principles and axioms",
        "Establish relationship to TRF and Symbolic Phase Entropy",
        "Develop STUFF mathematical formalism",
        "Create STUFF framework documentation",
        "Write STUFF Framework paper",
        "Prepare publication submissions",
    ],
    "15. Resonant Universe Theory": [
        "Develop core resonant universe principles",
        "Integrate with Synchronetic Mathematics",
        "Formulate resonance-based physical laws",
        "Write Resonant Universe Theory paper",
        "Prepare publication submissions",
    ],
    "16. Time-Causality Matrix": [
        "Define time-causality relationships",
        "Create matrix structure and operators",
        "Apply to physical systems",
        "Apply to financial systems (for Trader Exchange)",
        "Write Time-Causality Matrix paper",
        "Prepare publication submissions",
    ],
    "17. Resonance Field Equations": [
        "Derive resonance field equations from Resonant Universe Theory",
        "Solve field equations for key scenarios",
        "Compare with standard field equations",
        "Write Resonance Field Equations paper",
        "Prepare publication submissions",
    ],
    "18. Quantum Resonance Interpretation": [
        "Develop quantum resonance interpretation framework",
        "Reinterpret standard quantum experiments",
        "Connect to Triadic Mathematics",
        "Write Quantum Resonance Interpretation paper",
        "Prepare publication submissions",
    ],
    "19. Gravitational Resonance": [
        "Develop gravitational resonance theory",
        "Derive gravitational field equations",
        "Compare predictions with general relativity",
        "Write Gravitational Resonance paper",
        "Prepare publication submissions",
    ],
    "20. Electromagnetic Resonance": [
        "Develop electromagnetic resonance theory",
        "Derive EM field equations",
        "Compare with Maxwell's equations",
        "Write Electromagnetic Resonance paper",
        "Prepare publication submissions",
    ],
    "21. Cosmological Resonance Model": [
        "Develop cosmological resonance model",
        "Apply to Big Bang and expansion",
        "Apply to dark matter and dark energy",
        "Write Cosmological Resonance Model paper",
        "Prepare publication submissions",
    ],
    "22. Particle Resonance Taxonomy": [
        "Classify particles by resonance properties",
        "Map standard model particles to resonance framework",
        "Identify new resonance-based particle categories",
        "Write Particle Resonance Taxonomy paper",
        "Prepare publication submissions",
    ],
    "23. Energy Resonance Framework": [
        "Develop energy resonance framework",
        "Define resonance energy states",
        "Connect to Information-Energy Equivalence",
        "Write Energy Resonance Framework paper",
        "Prepare publication submissions",
    ],
    "24. Information-Energy Equivalence": [
        "Formalize information-energy equivalence principle",
        "Derive quantitative relationships",
        "Apply to physical and computational systems",
        "Write Information-Energy Equivalence paper",
        "Prepare publication submissions",
    ],
    "25. Consciousness-Physics Bridge": [
        "Develop consciousness-physics bridge framework",
        "Connect to Psyche Spatial Architecture",
        "Formalize consciousness-resonance relationships",
        "Write Consciousness-Physics Bridge paper",
        "Prepare publication submissions",
    ],
    "26. Experimental Validation Roadmap": [
        "Design experimental validation strategy",
        "Identify key experiments to test resonance theory",
        "Prioritize experiments by feasibility and impact",
        "Create experimental validation roadmap document",
        "Prepare for collaboration with experimental groups",
    ],
    "27. Resonance Detector Design": [
        "Design resonance detector specifications",
        "Create detector architecture",
        "Identify required technologies",
        "Write Resonance Detector Design paper",
        "Prepare for engineering collaboration",
    ],
    "28. Alternative Interpretation Tests": [
        "Design tests for alternative interpretations",
        "Identify revisitable historical experiments",
        "Plan new experimental protocols",
        "Write Alternative Interpretation Tests paper",
        "Prepare for experimental collaboration",
    ],
    "29. Engineering Applications Framework": [
        "Develop engineering applications framework",
        "Map physics principles to engineering domains",
        "Create application guidelines",
        "Write Engineering Applications Framework document",
    ],
    "30. Resonance-Based Energy Systems": [
        "Design resonance-based energy generation systems",
        "Design resonance-based energy storage systems",
        "Create energy system prototypes",
        "Write Resonance-Based Energy Systems paper",
        "Prepare for engineering development",
    ],
    "31. Resonance Computing": [
        "Develop resonance computing architecture",
        "Design resonance-based processors",
        "Create computing system prototypes",
        "Write Resonance Computing paper",
        "Prepare for technology development",
    ],
    "32. Resonance Propulsion": [
        "Develop resonance propulsion principles",
        "Design propulsion system architecture",
        "Create propulsion system prototypes",
        "Write Resonance Propulsion paper",
        "Prepare for aerospace engineering collaboration",
    ],
    "33. Resonance Sensing Technologies": [
        "Develop resonance sensing principles",
        "Design sensor architectures",
        "Create sensor prototypes",
        "Write Resonance Sensing Technologies paper",
        "Prepare for technology development",
    ],
    "34. Next Generation Technologies Roadmap": [
        "Catalogue main tech categories (energy, computation, transport, sensing, etc.)",
        "Map each category to supporting physics/engineering layers",
        "Create technology roadmap document",
        "Prepare whitepapers for DARPA, NASA, research consortia",
        "Plan 'Resonant Technologies: A Future Engineering Manifesto' book",
    ],
    "35. Portfolio Strategist MVP": [
        "Implement core budgeting logic (bills/debt/needs/wants, savings, remains)",
        "Set up basic graphs and visualizations",
        "Implement simple rules engine",
        "Create user interface",
        "Set up deployment infrastructure",
        "Deploy MVP web app",
        "Create initial documentation",
        "Prepare GitHub release",
        "Prepare Product Hunt launch",
        "Prepare Journal of Financial Data Science architecture article",
    ],
    "36. Document OCR Platform (Django)": [
        "Set up Django project structure",
        "Implement upload pipeline",
        "Integrate OCR engine",
        "Implement field extraction",
        "Set up storage system",
        "Implement basic validation rules using TRF-style consistency checks",
        "Create API endpoints",
        "Deploy OCR micro-SaaS",
        "Create API & technical documentation",
        "Prepare IEEE Access submission",
        "Prepare Pattern Recognition Letters submission",
        "Prepare arXiv submission (cs.CV)",
        "Prepare GitHub release",
    ],
    "37. Portfolio Strategist v1.0 (Paid Tier)": [
        "Implement advanced analytics and reports",
        "Develop premium features (AI financial fellow)",
        "Develop equation library feature",
        "Implement advanced scenarios",
        "Integrate payment system",
        "Set up access tiers",
        "Create marketing site",
        "Design onboarding funnels",
        "Launch paid SaaS release",
        "Prepare app directory listings",
        "Prepare fintech blog features",
        "Prepare Product Hunt v1 relaunch",
        "Prepare CFA Institute fintech showcase",
    ],
    "38. Trader Exchange MVP": [
        "Design architecture for order-matching",
        "Design architecture for event streaming",
        "Implement risk engine based on TC Matrix",
        "Implement position engine based on TC Matrix",
        "Create prototype UI for strategy testing",
        "Deploy Trader Exchange MVP (sim or testnet)",
        "Write Trader Exchange whitepaper",
    ],
    "39. Financial Frameworks Book": [
        "Structure book outline (career ladders, savings, real estate ladders, case studies)",
        "Write career ladders section",
        "Write savings strategies section",
        "Write real estate ladders section",
        "Write case studies",
        "Integrate Portfolio Strategist workflows in narrative examples",
        "Create worksheets & calculators",
        "Complete book manuscript: The Resonant Wealth Framework",
        "Prepare Amazon Kindle publication",
        "Prepare Audible audiobook",
        "Prepare pitches to Penguin Random House / HarperCollins",
        "Plan podcast and YouTube/IG collaborations",
    ],
    "40. Writing Measurement Framework": [
        "Finalize definition of Form dimension",
        "Finalize definition of Pace dimension",
        "Finalize definition of Patterns dimension",
        "Finalize definition of Expression dimension",
        "Finalize definition of Interpretation dimension",
        "Annotate sample texts from multiple genres",
        "Write WMF v1.0 guide",
        "Create example library",
        "Prepare Journal of Writing Research submission",
        "Prepare Computers & Composition submission",
        "Plan Medium/Substack series",
        "Plan eventual craft book",
    ],
    "41. Motif Taxonomy Atlas": [
        "Finalize all 50× motif sets with definitions + examples",
        "Cross-link motifs with WMF dimensions (e.g., which motifs amplify Pace/Pattern)",
        "Create Motif Atlas v1.0 (tables + commentary)",
        "Set up Gumroad store",
        "Set up Patreon premium resource",
        "Create personal store",
        "Plan integration into future writing software",
    ],
    "42. Podcast: The Resonance Paradox": [
        "Plan Season 1 topics (logic, resonance, time, writing, wealth, mythos)",
        "Record pilot episode",
        "Edit pilot episode",
        "Create intro/outro branding",
        "Set up podcast hosting",
        "Create Season 1 outline (10-12 episodes)",
        "Launch on Spotify",
        "Launch on Apple Podcasts",
        "Launch on YouTube",
        "Create Substack transcripts",
        "Plan Twitter/X thread recaps",
        "Plan guest appearances on bigger shows",
    ],
    "43. Psyche Spatial Architecture": [
        "Define mental spaces and realms",
        "Define transitions and boundaries",
        "Tie to archetypal transforms",
        "Tie to symbolic entropy",
        "Create diagrams of psyche geometry",
        "Write Psyche Spatial Architecture manuscript",
        "Prepare Journal of Consciousness Studies submission",
        "Prepare Cognitive Systems Research submission",
        "Prepare book pitch to Routledge, Springer",
        "Plan essays for psychology-and-philosophy outlets",
    ],
    "44. Royal Polyarchy Constitution & Government": [
        "Finalize ministries structure",
        "Finalize houses structure",
        "Finalize law categories",
        "Finalize succession rules",
        "Model time-evolution with Time-Causality Matrix",
        "Write Royal Polyarchy Constitution Volume",
        "Create institutional charts",
        "Set up lore book / worldbuilding site",
        "Set up World Anvil",
        "Plan physical artbook/collector editions via Kickstarter",
    ],
    "45. Royal Polyarchy Dynasties & Atlas": [
        "Construct family trees",
        "Create timelines",
        "Map dynastic arcs to cosmic/physics epochs",
        "Create Dynastic Atlas (maps + timelines)",
        "Design illustrated print + digital atlas",
        "Prepare reference bible for adaptations (anime, novels, games)",
    ],
    "46. Royal Polyarchy Encyclopedia (Blueprint/Cipher/Entities)": [
        "Define all entity classes and items",
        "Encode cipher systems and symbol sets",
        "Tie entries back to physics & math layers (where appropriate)",
        "Write Encyclopedia vol. 1: Blueprint & Entities",
        "Create cipher appendix",
        "Design large-format hardcover",
        "Create digital compendium",
        "Set up lore wiki",
        "Set up custom site",
        "Plan NFT/collectible tie-ins",
    ],
    "47. Royal Polyarchy Cosmology & Volumes of the Cosmos": [
        "Map Nova Gaia → Omniverse with STUFF + Resonant Universe baked in",
        "Divide into major book cycles/volumes",
        "Define key arcs",
        "Define anchor characters/dynasties",
        "Create Volumes of the Cosmos series outline",
        "Write first volume manuscript",
        "Create canon cosmology map",
        "Prepare pitches to sci-fi/fantasy imprints (Tor, Orbit, Gollancz)",
        "Prepare Amazon KDP publication",
        "Prepare Audible audiobook",
        "Prepare pitches for anime/animated series",
        "Prepare pitches for games",
        "Prepare pitches for visual novels",
    ],
}


def add_tasks_for_all_projects():
    """Add tasks for all projects in the database."""
    conn = init_db()
    state = load_state(conn)

    # Get all projects from database
    existing_projects = {p.name: p for p in state.projects}

    tasks_added = 0
    projects_processed = 0

    # Process each project that has tasks defined
    for project_name, task_titles in PROJECT_TASKS.items():
        # Check if project exists, if not create it
        if project_name not in existing_projects:
            # Try to find project with similar name (might have different numbering)
            found = False
            for existing_name in existing_projects.keys():
                # Check if the core name matches (ignoring number prefix)
                core_name = (
                    project_name.split(". ", 1)[-1]
                    if ". " in project_name
                    else project_name
                )
                existing_core = (
                    existing_name.split(". ", 1)[-1]
                    if ". " in existing_name
                    else existing_name
                )
                if core_name == existing_core:
                    project_name = existing_name
                    found = True
                    break

            if not found:
                # Create the project
                proj = Project(
                    name=project_name,
                    description=f"Project from AIC Master Canon Roadmap",
                    priority="MEDIUM",
                    status="active",
                )
                db_upsert_project(conn, proj)
                existing_projects[project_name] = proj
                print(f"Created project: {project_name}")

        # Check if tasks already exist for this project
        existing_tasks = [t for t in state.tasks if t.project == project_name]
        existing_task_titles = {t.title for t in existing_tasks}

        # Add tasks that don't already exist
        for task_title in task_titles:
            if task_title not in existing_task_titles:
                # Determine priority based on project priority
                project = existing_projects[project_name]
                task_priority = (
                    project.priority
                    if project.priority in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
                    else "MEDIUM"
                )

                # Set higher priority for critical projects' foundational tasks
                if project.priority == "CRITICAL" and any(
                    keyword in task_title.lower()
                    for keyword in ["define", "finalize", "develop", "create"]
                ):
                    task_priority = "HIGH"

                task = Task(
                    id=0,  # Will be auto-generated
                    title=task_title,
                    project=project_name,
                    status="TODO",
                    priority=task_priority,
                    due_date="",
                    notes="",
                    owner="Chris",
                    created_at=datetime.now().isoformat(timespec="seconds"),
                )
                db_insert_task(conn, task)
                tasks_added += 1

        projects_processed += 1
        print(
            f"Processed {project_name}: {len([t for t in task_titles if t not in existing_task_titles])} new tasks added"
        )

    conn.close()
    print(f"\nTotal: {tasks_added} tasks added across {projects_processed} projects")


if __name__ == "__main__":
    add_tasks_for_all_projects()
