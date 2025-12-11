#!/usr/bin/env python3
"""Script to update project priorities according to the hierarchy:
TOP: Abstract/Ontological/Epistemological (CRITICAL/HIGH)
TOP-MID: Writers Frameworks, Software (Portfolio Strategist), Royal Polyarchy (HIGH)
MIDDLE: Philosophical, Psychological, Financial, Mathematics (Foundational) (MEDIUM)
MIDDLE/LOW: Physics (independently by testable experiments) (MEDIUM/LOW)
BOTTOM: Engineering/Future Technologies (LOW)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from assistant_hub.db import init_db, db_upsert_project, load_state, Project

# Priority mapping: project number -> new priority
PRIORITY_UPDATES = {
    # LAYER 1 - PURE LOGIC (TOP - Abstract/Ontological/Epistemological)
    # Keep as CRITICAL/HIGH - already correct
    "1": "CRITICAL",  # Theoretical Reasoning Framework
    "2": "CRITICAL",  # AIC / Daemon Framework
    "3": "HIGH",  # Symbolic Phase Entropy
    "4": "HIGH",  # Ontological-Epistemological Matrix
    "5": "HIGH",  # Mathematical Phenomena Interpretation System
    # LAYER 2 - AXIOMATIC SYMBOLIC MATHEMATICS (MIDDLE - Foundational Mathematics)
    "6": "MEDIUM",  # Symbolic Axiom Set
    "7": "MEDIUM",  # Synchronetic Mathematics
    "8": "MEDIUM",  # Reflexive Arithmetic Universe
    "9": "MEDIUM",  # Archetypal Mathematics
    "10": "MEDIUM",  # Arithmorphics Mathematics
    "11": "MEDIUM",  # Triadic Mathematics
    "12": "MEDIUM",  # Synchronetic Coordinate System
    "13": "MEDIUM",  # Unknown Equations Atlas
    # LAYER 3-4 - PHYSICS (MIDDLE/LOW - independently by testable experiments)
    "14": "MEDIUM",  # STUFF Framework (core)
    "15": "MEDIUM",  # Resonant Universe Theory (core)
    "16": "MEDIUM",  # Time-Causality Matrix (core)
    "17": "MEDIUM",  # Resonance Field Equations (core)
    "18": "MEDIUM",  # Quantum Resonance Interpretation (core)
    "19": "LOW",  # Gravitational Resonance
    "20": "LOW",  # Electromagnetic Resonance
    "21": "LOW",  # Cosmological Resonance Model
    "22": "LOW",  # Particle Resonance Taxonomy
    "23": "LOW",  # Energy Resonance Framework
    "24": "LOW",  # Information-Energy Equivalence
    "25": "LOW",  # Consciousness-Physics Bridge
    "26": "LOW",  # Experimental Validation Roadmap
    "27": "LOW",  # Resonance Detector Design
    "28": "LOW",  # Alternative Interpretation Tests
    # LAYER 5 - ENGINEERING/FUTURE TECHNOLOGIES (BOTTOM)
    "29": "LOW",  # Engineering Applications Framework
    "30": "LOW",  # Resonance-Based Energy Systems
    "31": "LOW",  # Resonance Computing
    "32": "LOW",  # Resonance Propulsion
    "33": "LOW",  # Resonance Sensing Technologies
    "34": "LOW",  # Next Generation Technologies Roadmap
    # LAYER 5 - FINTECH/SOFTWARE (TOP-MID - Software/Portfolio Strategist)
    "35": "HIGH",  # Portfolio Strategist MVP
    "36": "MEDIUM",  # Document OCR Platform (not Portfolio Strategist)
    "37": "HIGH",  # Portfolio Strategist v1.0 (Paid Tier)
    "38": "MEDIUM",  # Trader Exchange MVP
    "39": "MEDIUM",  # Financial Frameworks Book (Financial - MIDDLE)
    # LAYER 6 - WRITING/PSYCHE (TOP-MID for Writing, MIDDLE for Psychological)
    "40": "HIGH",  # Writing Measurement Framework (Writers Frameworks - TOP-MID)
    "41": "HIGH",  # Motif Taxonomy Atlas (Writers Frameworks - TOP-MID)
    "42": "MEDIUM",  # Podcast: The Resonance Paradox
    "43": "MEDIUM",  # Psyche Spatial Architecture (Psychological - MIDDLE)
    # LAYER 7 - ROYAL POLYARCHY (TOP-MID)
    "44": "HIGH",  # Royal Polyarchy Constitution & Government
    "45": "HIGH",  # Royal Polyarchy Dynasties & Atlas
    "46": "HIGH",  # Royal Polyarchy Encyclopedia
    "47": "HIGH",  # Royal Polyarchy Cosmology & Volumes of the Cosmos
}


def update_priorities():
    """Update all project priorities according to the hierarchy."""
    conn = init_db()
    state = load_state(conn)

    updated_count = 0
    for proj in state.projects:
        # Extract project number from name (e.g., "1. Theoretical Reasoning Framework" -> "1")
        name_parts = proj.name.split(".", 1)
        if len(name_parts) > 0 and name_parts[0].strip().isdigit():
            proj_num = name_parts[0].strip()
            if proj_num in PRIORITY_UPDATES:
                new_priority = PRIORITY_UPDATES[proj_num]
                if proj.priority != new_priority:
                    proj.priority = new_priority
                    db_upsert_project(conn, proj)
                    print(f"Updated: {proj.name} -> {new_priority}")
                    updated_count += 1
                else:
                    print(f"No change: {proj.name} (already {new_priority})")
            else:
                print(f"Warning: No priority mapping for project: {proj.name}")
        else:
            print(f"Warning: Could not extract project number from: {proj.name}")

    conn.close()
    print(f"\nTotal projects updated: {updated_count}")


if __name__ == "__main__":
    update_priorities()
