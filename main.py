import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from organizer.scanner import scan_directory
from organizer.rules import load_config, classify_by_type, classify_by_size, classify_by_date
from organizer.mover import move_file, undo_last

app = typer.Typer(
    help="📁 File Organizer — Sort files by type, size, or date.",
    add_completion=False,
)
console = Console()


def get_classifier(sort_by: str, rules: dict):
    """Returns the correct classify function based on sort_by flag."""
    classifiers = {
        "type": lambda f: classify_by_type(f, rules),
        "size": lambda f: classify_by_size(f, rules),
        "date": lambda f: classify_by_date(f, rules),
    }
    if sort_by not in classifiers:
        console.print(f"[red]Invalid --sort-by value: '{sort_by}'. Choose from: type, size, date[/red]")
        raise typer.Exit(code=1)
    return classifiers[sort_by]


@app.command()
def organize(
    directory: str = typer.Argument(..., help="Path to the directory to organize."),
    sort_by: str = typer.Option("type", "--sort-by", "-s", help="Sort by: type | size | date"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Include subdirectories."),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Preview moves without actually moving files."),
    undo: bool = typer.Option(False, "--undo", "-u", help="Undo the last organize run."),
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to config YAML file."),
):
    # ── UNDO MODE ──────────────────────────────────────────────────────────────
    if undo:
        console.print(Panel("[bold yellow]Undoing last organize run...[/bold yellow]", expand=False))
        results = undo_last(dry_run=dry_run)

        if not results:
            console.print("[yellow]Nothing to undo. Log is empty.[/yellow]")
            raise typer.Exit()

        table = Table(title="Undo Results", box=box.ROUNDED)
        table.add_column("Restored To", style="cyan")
        table.add_column("From", style="dim")
        table.add_column("Status", style="green")

        for r in results:
            status_color = "green" if r["status"] == "ok" else "red"
            table.add_row(r["src"], r["dest"], f"[{status_color}]{r['status']}[/{status_color}]")

        console.print(table)

        if dry_run:
            console.print("[dim italic]Dry run — no files were moved.[/dim italic]")

        raise typer.Exit()

    # ── ORGANIZE MODE ──────────────────────────────────────────────────────────
    try:
        cfg = load_config(config)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    try:
        files = scan_directory(directory, recursive=recursive)
    except (FileNotFoundError, NotADirectoryError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    if not files:
        console.print("[yellow]No files found in the given directory.[/yellow]")
        raise typer.Exit()

    classify = get_classifier(sort_by, cfg["rules"])

    # Build preview table
    table = Table(
        title=f"{'[DRY RUN] ' if dry_run else ''}Organizing by [bold]{sort_by}[/bold] → {directory}",
        box=box.ROUNDED,
    )
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("→ Destination Folder", style="green")

    moved = 0
    skipped = 0

    for file in files:
        folder_name = classify(file)
        destination = Path(directory) / folder_name

        # Skip files already in the right folder
        if file.parent.resolve() == destination.resolve():
            skipped += 1
            continue

        table.add_row(file.name, str(destination))
        move_file(file, destination, dry_run=dry_run)
        moved += 1

    console.print(table)

    # Summary
    action = "Would move" if dry_run else "Moved"
    console.print(f"\n[bold green]✓ {action} {moved} file(s).[/bold green]", end="  ")
    if skipped:
        console.print(f"[dim]{skipped} already in correct folder, skipped.[/dim]")
    else:
        console.print()

    if dry_run:
        console.print("[dim italic]Dry run — no files were actually moved. Remove --dry-run to apply.[/dim italic]")
    else:
        console.print("[dim]Run with [bold]--undo[/bold] to reverse this.[/dim]")


if __name__ == "__main__":
    app()