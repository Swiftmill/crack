"""Programme de démonstration d'une attaque par dictionnaire avec interface visionOS.

Ce script propose une simulation locale (aucune connexion réseau) d'une attaque
par dictionnaire contre l'utilisateur "admin" avec le mot de passe cible
"1231232024". L'interface graphique est conçue avec CustomTkinter et s'inspire
littéralement des lignes directrices esthétiques de visionOS : glassmorphism,
profondeur, animations à 60 FPS et effets lumineux.
"""

import math
import time
import random
from pathlib import Path
from typing import List, Optional

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFilter


# ------------------------------- Constantes UI -------------------------------- #
USER = "admin"
PASSWORD = "1231232024"
DEFAULT_DICT_PATH = Path("dic/fakerockyou.txt")

WINDOW_SIZE = (1280, 720)
FPS = 60  # Cible d'animation
FRAME_INTERVAL = int(1000 / FPS)
FLOAT_AMPLITUDE = 8
FLOAT_PERIOD = 6.0  # secondes

GLASS_BG_COLOR = (18, 18, 24)
PANEL_COLOR = "#FFFFFF1A"
PANEL_HOVER_COLOR = "#1E90FF22"
ACCENT_COLOR = "#4FD1FF"
TEXT_PRIMARY = "#F5F6F7"
TEXT_SECONDARY = "#C7CCD6"
ERROR_COLOR = "#FF5F7B"
SUCCESS_GLOW_COLOR = "#74F9FF"

# --------------------------- Génération d'arrière-plan ------------------------ #

def generate_blurred_gradient(size: tuple[int, int]) -> Image.Image:
    """Crée une image dégradée floue pour simuler un fond visionOS."""
    width, height = size
    base = Image.new("RGB", size, GLASS_BG_COLOR)
    draw = ImageDraw.Draw(base)

    # Dégradé radial cyan -> violet sombre
    center = (width // 2, height // 2)
    max_radius = math.hypot(width, height)
    for i in range(12):
        radius = max_radius * (i / 12)
        color_ratio = i / 11 if i else 0
        r = int(10 + 40 * (1 - color_ratio))
        g = int(40 + 120 * (1 - color_ratio))
        b = int(70 + 180 * color_ratio)
        draw.ellipse([
            center[0] - radius,
            center[1] - radius,
            center[0] + radius,
            center[1] + radius,
        ], fill=(r, g, b))

    # Ajout d'un reflet diagonal
    overlay = Image.new("RGB", size, (255, 255, 255))
    mask = Image.new("L", size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon([
        (0, height * 0.1),
        (width * 0.6, 0),
        (width, height * 0.4),
        (width * 0.2, height)
    ], fill=60)
    base = Image.composite(overlay, base, mask)

    # Blur puissant
    base = base.filter(ImageFilter.GaussianBlur(radius=30))
    return base


# ----------------------------- Composants Custom ------------------------------ #

class CircularProgress(ctk.CTkCanvas):
    """Barre de progression circulaire stylisée."""

    def __init__(self, master, size: int = 220, **kwargs):
        super().__init__(master, width=size, height=size, bg="transparent", **kwargs)
        self.size = size
        self.center = size / 2
        self.radius = size * 0.42
        self.start_angle = -90
        self.create_oval(
            self.center - self.radius,
            self.center - self.radius,
            self.center + self.radius,
            self.center + self.radius,
            outline="#FFFFFF22",
            width=6,
            tags="track",
        )
        self.arc = self.create_arc(
            self.center - self.radius,
            self.center - self.radius,
            self.center + self.radius,
            self.center + self.radius,
            start=self.start_angle,
            extent=0,
            style="arc",
            width=8,
            outline=ACCENT_COLOR,
            capstyle="round",
            tags="progress",
        )
        self.label = self.create_text(
            self.center,
            self.center,
            text="0%",
            fill=TEXT_PRIMARY,
            font=("Segoe UI", 28, "bold"),
        )

    def set_progress(self, progress: float) -> None:
        progress = max(0.0, min(1.0, progress))
        extent = 360 * progress
        self.itemconfigure(self.arc, extent=extent)
        self.itemconfigure(self.label, text=f"{int(progress * 100):02d}%")


class GlassFrame(ctk.CTkFrame):
    """Cadre translucide avec effet de verre."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            corner_radius=36,
            fg_color=(
                PANEL_COLOR,
                PANEL_COLOR,
            ),
            border_width=1,
            border_color="#FFFFFF33",
            **kwargs,
        )


class Particle:
    """Particule lumineuse pour l'effet de succès."""

    def __init__(self, canvas: ctk.CTkCanvas, x: float, y: float):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.life = random.uniform(0.8, 1.8)
        self.birth = time.time()
        self.radius = random.uniform(6, 14)
        self.dx = random.uniform(-80, 80)
        self.dy = random.uniform(-120, -30)
        self.id = canvas.create_oval(
            x - self.radius,
            y - self.radius,
            x + self.radius,
            y + self.radius,
            fill=SUCCESS_GLOW_COLOR,
            outline="",
            state="hidden",
        )

    def animate(self) -> bool:
        elapsed = time.time() - self.birth
        if elapsed > self.life:
            self.canvas.delete(self.id)
            return False
        progress = elapsed / self.life
        easing = 1 - (1 - progress) ** 3
        nx = self.x + self.dx * easing
        ny = self.y + self.dy * easing + 20 * math.sin(progress * math.pi)
        alpha = int(255 * (1 - progress))
        color = f"#{alpha:02x}ffff"
        self.canvas.itemconfigure(self.id, fill=color, state="normal")
        self.canvas.coords(
            self.id,
            nx - self.radius * (1 - progress * 0.4),
            ny - self.radius * (1 - progress * 0.4),
            nx + self.radius * (1 - progress * 0.4),
            ny + self.radius * (1 - progress * 0.4),
        )
        return True


# ----------------------------- Application principale ------------------------- #

class VisionAttackApp(ctk.CTk):
    """Application principale simulant l'attaque par dictionnaire."""

    def __init__(self):
        super().__init__()
        self.title("VisionOS Dictionary Attack - Démo")
        self.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self._background_image = generate_blurred_gradient(WINDOW_SIZE)
        self._background_photo = ctk.CTkImage(self._background_image, size=WINDOW_SIZE)

        # Canvas de fond
        self.background_label = ctk.CTkLabel(self, text="", image=self._background_photo)
        self.background_label.place(relwidth=1, relheight=1)

        # Superposition pour les particules
        self.particle_canvas = ctk.CTkCanvas(self, width=WINDOW_SIZE[0], height=WINDOW_SIZE[1], bg="transparent", highlightthickness=0)
        self.particle_canvas.place(relx=0, rely=0)

        # Cadre principal flottant
        self.main_frame = GlassFrame(self)
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.7, relheight=0.68)

        self.progress_ring = CircularProgress(self.main_frame)
        self.progress_ring.grid(row=0, column=0, rowspan=3, padx=(40, 20), pady=40, sticky="nsw")

        self.info_frame = GlassFrame(self.main_frame)
        self.info_frame.grid(row=0, column=1, padx=(10, 40), pady=(40, 10), sticky="new")

        self.status_frame = GlassFrame(self.main_frame)
        self.status_frame.grid(row=1, column=1, padx=(10, 40), pady=(10, 40), sticky="sew")

        for frame in (self.info_frame, self.status_frame):
            frame.grid_columnconfigure(0, weight=1)

        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # Titres
        self.title_label = ctk.CTkLabel(
            self.info_frame,
            text="Simulation d'attaque par dictionnaire",
            font=("Segoe UI", 28, "bold"),
            text_color=TEXT_PRIMARY,
        )
        self.title_label.grid(row=0, column=0, pady=(20, 10), padx=30, sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            self.info_frame,
            text=f"Cible : {USER} | Source dictionnaire : {DEFAULT_DICT_PATH}",
            font=("Segoe UI", 16),
            text_color=TEXT_SECONDARY,
        )
        self.subtitle_label.grid(row=1, column=0, pady=(0, 20), padx=30, sticky="w")

        # Zone d'état dynamique
        self.attempt_label = ctk.CTkLabel(
            self.status_frame,
            text="Essai en cours : -",
            font=("Segoe UI", 20, "bold"),
            text_color=TEXT_PRIMARY,
        )
        self.attempt_label.grid(row=0, column=0, pady=(30, 10), padx=30, sticky="w")

        self.counter_label = ctk.CTkLabel(
            self.status_frame,
            text="Essais totaux : 0",
            font=("Segoe UI", 18),
            text_color=TEXT_SECONDARY,
        )
        self.counter_label.grid(row=1, column=0, pady=5, padx=30, sticky="w")

        self.speed_label = ctk.CTkLabel(
            self.status_frame,
            text="Vitesse : 0 essais/s",
            font=("Segoe UI", 18),
            text_color=TEXT_SECONDARY,
        )
        self.speed_label.grid(row=2, column=0, pady=5, padx=30, sticky="w")

        self.elapsed_label = ctk.CTkLabel(
            self.status_frame,
            text="Temps écoulé : 0.00 s",
            font=("Segoe UI", 18),
            text_color=TEXT_SECONDARY,
        )
        self.elapsed_label.grid(row=3, column=0, pady=(5, 30), padx=30, sticky="w")

        # Bouton d'action
        self.action_button = ctk.CTkButton(
            self.main_frame,
            text="LANCER L'ATTAQUE",
            font=("Segoe UI", 24, "bold"),
            height=70,
            corner_radius=40,
            fg_color=ACCENT_COLOR,
            hover_color="#4FD1FFAA",
            command=self.toggle_attack,
        )
        self.action_button.grid(row=2, column=0, columnspan=2, padx=40, pady=(0, 40), sticky="ew")

        # Overlay de succès
        self.success_overlay = ctk.CTkLabel(
            self,
            text="ACCESS GRANTED",
            font=("Segoe UI", 72, "bold"),
            text_color=SUCCESS_GLOW_COLOR,
        )
        self.success_overlay.place_forget()

        # Variables de simulation
        self.passwords: List[str] = []
        self.total_attempts = 0
        self.start_time: Optional[float] = None
        self.last_update_time = time.time()
        self.attack_running = False
        self.float_phase = random.uniform(0, 1)
        self.particles: List[Particle] = []
        self.success_animation_progress = 0.0

        self.load_dictionary(DEFAULT_DICT_PATH)
        self.after(FRAME_INTERVAL, self.animation_loop)

    # ----------------------------- Gestion dictionnaire ---------------------- #

    def load_dictionary(self, path: Path) -> None:
        if path.exists():
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                self.passwords = [line.strip() for line in f if line.strip()]
        else:
            # Fichier introuvable : on propose quelques valeurs par défaut
            self.passwords = [
                "password",
                "admin",
                "letmein",
                "123456",
                "azerty",
                PASSWORD,
            ]
        if PASSWORD not in self.passwords:
            self.passwords.append(PASSWORD)
        self.subtitle_label.configure(text=f"Cible : {USER} | Source dictionnaire : {path}")

    # ----------------------------- Animation principale ---------------------- #

    def animation_loop(self) -> None:
        now = time.time()
        self.last_update_time = now

        # Animation de flottement du cadre principal
        phase = (now + self.float_phase) % FLOAT_PERIOD
        offset = FLOAT_AMPLITUDE * math.sin(2 * math.pi * phase / FLOAT_PERIOD)
        self.main_frame.place_configure(rely=0.5 + offset / WINDOW_SIZE[1])

        # Mise à jour du progrès si l'attaque est active
        if self.attack_running:
            self.process_attempts()

        # Animation des particules
        if self.particles:
            alive_particles = []
            for particle in self.particles:
                if particle.animate():
                    alive_particles.append(particle)
            self.particles = alive_particles

        # Animation du message de succès
        if self.success_animation_progress > 0:
            self.update_success_overlay()

        self.after(FRAME_INTERVAL, self.animation_loop)

    # ----------------------------- Simulation attaque ------------------------ #

    def toggle_attack(self) -> None:
        if not self.attack_running:
            self.start_attack()
        else:
            self.reset_attack()

    def start_attack(self) -> None:
        self.attack_running = True
        self.action_button.configure(text="STOP", fg_color=ERROR_COLOR, hover_color="#FF5F7B99")
        self.total_attempts = 0
        self.start_time = time.time()
        self.success_animation_progress = 0.0
        self.success_overlay.place_forget()
        self.particle_canvas.delete("all")
        self.particles.clear()
        random.shuffle(self.passwords)
        # on garantit que le mot de passe apparait
        if PASSWORD in self.passwords:
            self.passwords.remove(PASSWORD)
        self.passwords.insert(random.randint(len(self.passwords)//3, len(self.passwords)-1), PASSWORD)
        self.remaining_passwords = iter(self.passwords)

    def reset_attack(self) -> None:
        self.attack_running = False
        self.action_button.configure(text="LANCER L'ATTAQUE", fg_color=ACCENT_COLOR, hover_color="#4FD1FFAA")
        self.progress_ring.set_progress(0)
        self.attempt_label.configure(text="Essai en cours : -")
        self.counter_label.configure(text="Essais totaux : 0")
        self.speed_label.configure(text="Vitesse : 0 essais/s")
        self.elapsed_label.configure(text="Temps écoulé : 0.00 s")
        self.start_time = None

    def process_attempts(self) -> None:
        if not self.start_time:
            self.start_time = time.time()
        chunk_size = 250  # nombre d'essais par frame

        try:
            for _ in range(chunk_size):
                candidate = next(self.remaining_passwords)
                self.total_attempts += 1
                if candidate == PASSWORD:
                    self.on_password_found(candidate)
                    break
        except StopIteration:
            self.on_attack_exhausted()
            return

        if self.attack_running:
            elapsed = max(time.time() - self.start_time, 1e-3)
            speed = self.total_attempts / elapsed
            progress = self.total_attempts / len(self.passwords)
            self.attempt_label.configure(text=f"Essai en cours : {candidate}")
            self.counter_label.configure(text=f"Essais totaux : {self.total_attempts}")
            self.speed_label.configure(text=f"Vitesse : {speed:,.0f} essais/s".replace(",", " "))
            self.elapsed_label.configure(text=f"Temps écoulé : {elapsed:.2f} s")
            self.progress_ring.set_progress(progress)

    def on_attack_exhausted(self) -> None:
        self.attack_running = False
        self.action_button.configure(text="RELANCER", fg_color=ACCENT_COLOR)
        self.attempt_label.configure(text="Mot de passe introuvable")
        self.counter_label.configure(text=f"Essais totaux : {self.total_attempts}")
        self.speed_label.configure(text="Vitesse : -")
        self.elapsed_label.configure(text="Temps écoulé : -")

    def on_password_found(self, candidate: str) -> None:
        self.attack_running = False
        elapsed = time.time() - (self.start_time or time.time())
        self.attempt_label.configure(text=f"Mot de passe trouvé : {candidate}")
        self.counter_label.configure(text=f"Essais totaux : {self.total_attempts}")
        self.speed_label.configure(text=f"Temps total : {elapsed:.2f} s")
        self.elapsed_label.configure(text="Statut : accès autorisé")
        self.progress_ring.set_progress(1.0)
        self.action_button.configure(text="RELANCER", fg_color=ACCENT_COLOR, hover_color="#4FD1FFAA")
        self.trigger_success_animation()

    # ----------------------------- Animations de succès ----------------------- #

    def trigger_success_animation(self) -> None:
        self.success_animation_progress = 0.01
        self.success_overlay.configure(text_color=SUCCESS_GLOW_COLOR, text="ACCESS GRANTED")
        self.success_overlay.place(relx=0.5, rely=0.2, anchor="center")
        # Génération d'une explosion de particules
        for _ in range(36):
            x = WINDOW_SIZE[0] * 0.5 + random.uniform(-140, 140)
            y = WINDOW_SIZE[1] * 0.2 + random.uniform(-40, 40)
            particle = Particle(self.particle_canvas, x, y)
            self.particles.append(particle)

    def update_success_overlay(self) -> None:
        self.success_animation_progress = min(1.0, self.success_animation_progress + 0.02)
        progress = self.success_animation_progress
        scale = 1.0 + 0.2 * math.sin(progress * math.pi)
        opacity = int(255 * min(1.0, progress * 1.5))
        glow = int(150 + 105 * math.sin(progress * math.pi))
        color = f"#{opacity:02x}{glow:02x}ffff"
        self.success_overlay.configure(text_color=color)
        self.success_overlay.place_configure(relx=0.5, rely=0.2 + 0.02 * math.sin(progress * math.pi))
        self.success_overlay.configure(font=("Segoe UI", int(72 * scale), "bold"))
        if progress >= 1.0:
            # Maintient l'état final lumineux
            self.success_animation_progress = 0.0
            self.success_overlay.configure(text_color=SUCCESS_GLOW_COLOR)


def main() -> None:
    """Point d'entrée principal du programme."""
    app = VisionAttackApp()
    app.mainloop()


if __name__ == "__main__":
    main()
