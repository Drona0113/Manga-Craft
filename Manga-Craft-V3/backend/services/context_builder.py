"""
Context Builder
Collects a project's information into a single text briefing
that we give the AI so it "knows" the project.
"""

from models import Project, ProjectMemory, Panel

async def build_project_context(project_id: str) -> str:
    """Return a text briefing describing the project, its memory and panels."""
    project = await Project.get(project_id)
    if not project:
        return ""

    lines = ["=== PROJECT CONTEXT ==="]
    lines.append(f"Project name: {project.name}")
    if project.description:
        lines.append(f"Description: {project.description}")

    # Group memory entries by their type (character, story, location, ...)
    memories = await ProjectMemory.find({"project_id": project_id}).to_list()
    if memories:
        lines.append("")
        lines.append("-- Project Memory --")
        for memory in memories:
            lines.append(f"[{memory.type}] {memory.title}: {memory.content}")

    # Panels: we can't "see" images yet, but the AI can know they exist
    panels = await Panel.find({"project_id": project_id}).to_list()
    if panels:
        lines.append("")
        lines.append(f"-- Panels ({len(panels)}) --")
        for index, panel in enumerate(panels, start=1):
            size = ""
            if panel.width and panel.height:
                size = f" ({panel.width}x{panel.height})"
            note = f" — notes: {panel.notes}" if panel.notes else ""
            lines.append(f"{index}. {panel.file_name}{size}{note}")

    return "\n".join(lines)
