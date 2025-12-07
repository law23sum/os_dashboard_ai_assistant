"""Lightweight GUI for locating installed software.

The interface answers "where is git?" or similar questions using the
``SoftwareLocator`` helper that also powers the CLI. This keeps the GUI simple
while providing parity with the terminal commands.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from assistant_hub.integrations.software_locator import SoftwareLocator, SoftwareLocation


def _format_result(result: SoftwareLocation) -> str:
    if result.found:
        return f"{result.name} found at {result.path}"
    return f"{result.name} not found. Tried: {result.tried}"


def launch() -> None:
    locator = SoftwareLocator()

    root = tk.Tk()
    root.title("OSDash Software Locator")

    main_frame = ttk.Frame(root, padding=16)
    main_frame.grid(row=0, column=0, sticky="nsew")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    title = ttk.Label(main_frame, text="Locate software (git, Word, Excel, PDF, or custom)", font=("Arial", 12, "bold"))
    title.grid(row=0, column=0, columnspan=2, pady=(0, 10))

    results_var = tk.StringVar(value="Select a tool below or enter your own.")
    results_label = ttk.Label(main_frame, textvariable=results_var, wraplength=420, justify="left")
    results_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 12))

    def run_lookup(target: str) -> None:
        result = locator.locate_default(target)
        results_var.set(_format_result(result))

    quick_frame = ttk.LabelFrame(main_frame, text="Quick lookups")
    quick_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 12))
    for idx, target in enumerate(locator.default_targets):
        ttk.Button(quick_frame, text=target.capitalize(), command=lambda t=target: run_lookup(t)).grid(
            row=0, column=idx, padx=6, pady=6
        )

    custom_label = ttk.Label(main_frame, text="Custom software name")
    custom_label.grid(row=3, column=0, sticky="w")
    custom_entry = ttk.Entry(main_frame, width=30)
    custom_entry.grid(row=3, column=1, sticky="ew", pady=4)
    main_frame.columnconfigure(1, weight=1)

    alias_label = ttk.Label(main_frame, text="Optional aliases (comma separated)")
    alias_label.grid(row=4, column=0, sticky="w")
    alias_entry = ttk.Entry(main_frame, width=30)
    alias_entry.grid(row=4, column=1, sticky="ew", pady=4)

    def run_custom_lookup() -> None:
        name = custom_entry.get().strip()
        aliases = [alias.strip() for alias in alias_entry.get().split(",") if alias.strip()]
        if not name:
            results_var.set("Enter a software name to search for.")
            return
        result = locator.locate(name, aliases=aliases)
        results_var.set(_format_result(result))

    ttk.Button(main_frame, text="Find custom software", command=run_custom_lookup).grid(
        row=5, column=0, columnspan=2, pady=(8, 0)
    )

    root.mainloop()
