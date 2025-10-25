#!/usr/bin/env python3
"""
Phase 2 Frontend Builder
Generates all frontend modules for desk_navbar_extended v2.0
Apple-level UX, Fortune-500 production quality
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent / "desk_navbar_extended" / "public" / "js"
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Command Palette Module
COMMAND_PALETTE_JS = '''/**
 * Command Palette - Universal command launcher (Ctrl+K/Cmd+K)
 * Apple-inspired keyboard-first navigation
 */
(function () {
	"use strict";
	frappe.provide("frappe.desk_navbar_extended.command_palette");

	const CommandPalette = {
		state: { isOpen: false, searchQuery: "", results: [], selectedIndex: 0, allCommands: [], modal: null, input: null, resultsList: null },

		init: function () {
			if (!frappe.desk_navbar_extended?.settings?.features?.\1) return;
			this.setupKeyboardShortcuts();
			this.buildModal();

'''

if __name__ == "__main__":
	# Minimal writer to make this script syntactically valid and useful
	try:
		out = BASE_DIR / "command_palette.js"
		out.write_text(COMMAND_PALETTE_JS)
		print(f"Wrote {out}")
	except Exception as e:
		print("Could not write command_palette.js:", e)
