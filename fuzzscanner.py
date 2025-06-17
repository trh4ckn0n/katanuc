import os
import subprocess
import concurrent.futures
import re
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.text import Text

# === CONFIG ===
KATANA_OUT_DIR = "output/katana"
NUCLEI_OUT_DIR = "output/nuclei"
TEMPLATES_PATH = os.path.expanduser("~/nuclei-templates-fuzzing")

os.makedirs(KATANA_OUT_DIR, exist_ok=True)
os.makedirs(NUCLEI_OUT_DIR, exist_ok=True)

console = Console()

def banner():
    console.print(Panel.fit(
        "[bold magenta]trhacknon[/bold magenta] [green]FuzzScanner[/green]\n[cyan]Katana + Nuclei + Fuzzing Templates[/cyan]",
        border_style="bold green"
    ))

def has_query_param(url):
    return "?" in url and "=" in url

def run_katana(domain):
    out_file = os.path.join(KATANA_OUT_DIR, re.sub(r"https?://", "", domain).replace("/", "_") + ".txt")
    try:
        result = subprocess.run(
            ["katana", "-u", domain, "-silent"],
            capture_output=True, text=True, check=True
        )
        with open(out_file, "w") as f:
            f.write(result.stdout)
        return out_file
    except subprocess.CalledProcessError:
        return None

def colorize_line(line):
    severity_colors = {
        "info": "cyan",
        "low": "blue",
        "medium": "yellow",
        "high": "red",
        "critical": "bold red"
    }
    match = re.search(r"(info|low|medium|high|critical)", line, re.IGNORECASE)
    if match:
        severity = match.group(1).lower()
        color = severity_colors.get(severity, "white")
        return Text(line.strip(), style=color)
    return Text(line.strip())

def run_nuclei(input_urls_path):
    filtered_urls = []
    with open(input_urls_path, "r") as f:
        for line in f:
            url = line.strip()
            if has_query_param(url):
                filtered_urls.append(url)

    if not filtered_urls:
        return

    target_file = input_urls_path.replace("katana", "nuclei")
    with open(target_file, "w") as f:
        f.write("\n".join(filtered_urls))

    output_file = target_file.replace(".txt", "_fuzzing.txt")

    try:
        result = subprocess.run([
            "nuclei", "-l", target_file,
            "-t", TEMPLATES_PATH,
            "-o", output_file,
            "-severity", "info,low,medium,high,critical",
            "-silent"
        ], capture_output=True, text=True, check=True)

        for line in result.stdout.strip().split("\n"):
            if line.strip():
                console.print(colorize_line(line))

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Erreur Nuclei : {e}[/red]")

def process_domain(domain, progress, task_id):
    katana_out = run_katana(domain)
    progress.advance(task_id)
    if katana_out:
        run_nuclei(katana_out)

def main():
    banner()

    # Liste des fichiers .txt dans le dossier courant
    txt_files = [f for f in os.listdir() if f.endswith(".txt")]

    if not txt_files:
        console.print("[red]Aucun fichier .txt trouvé dans le dossier courant.[/red]")
        return

    domains_file = questionary.select("Choisir un fichier de domaines :", choices=txt_files).ask()

    with open(domains_file, "r") as f:
        domains = [line.strip() for line in f if line.strip()]

    if not domains:
        console.print("[yellow]Le fichier est vide ![/yellow]")
        return

    threads = questionary.select(
        "Choisir le nombre de threads à utiliser :",
        choices=["5", "10", "20", "40", "60", "80", "100"]
    ).ask()
    max_threads = int(threads)

    console.print(f"[bold cyan]Lancement avec {max_threads} threads...[/bold cyan]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:

        task_id = progress.add_task("[green]Scan en cours...", total=len(domains))

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(process_domain, d, progress, task_id) for d in domains]
            concurrent.futures.wait(futures)

    console.print("\n[bold green]✔ Scan terminé ![/bold green]")
    console.print(f"[blue]Résultats enregistrés dans : {NUCLEI_OUT_DIR}[/blue]")

if __name__ == "__main__":
    main()
