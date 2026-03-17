"""
Generador de Propuestas v2 — Lut Parra Leadership Mentoring
============================================================
Estilo: Propuesta FUNO 2026 (navy + rojo + azul accent)
Fuente: DejaVu Sans (soporta español completo)

Uso:
    python3 generar_propuesta_v2.py
    from generar_propuesta_v2 import generar_pdf, CATALOGO
"""

import textwrap
import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── FUENTES ──────────────────────────────────────────────────────────────────
pdfmetrics.registerFont(TTFont("DV",    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DV-B",  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DV-I",  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DV-BI", "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"))

# ── COLORES DE MARCA ─────────────────────────────────────────────────────────
NAVY        = HexColor('#1B2A4A')   # fondo azul oscuro
RED         = HexColor('#CC0000')   # rojo acento
BLUE_ACC    = HexColor('#2980B9')   # azul claro (nombres, links)
WHITE       = white
GRAY_BG     = HexColor('#F4F6FA')   # fondo gris suave
GRAY_LINE   = HexColor('#DDDDDD')   # líneas separadoras
GRAY_MED    = HexColor('#888888')   # texto secundario
GRAY_DARK   = HexColor('#333333')   # texto cuerpo
NAVY_HEADER = HexColor('#1B2A4A')   # header de tablas

PW, PH = letter   # 612 × 792 pts

# ── RUTAS DE LOGOS ────────────────────────────────────────────────────────────
try:
    from logo_loader import get_logo_paths as _get_logo_paths
    LOGO_BLANCO, LOGO_NEGRO = _get_logo_paths()
except ImportError:
    _BASE = os.path.dirname(os.path.abspath(__file__))
    LOGO_BLANCO = os.path.join(_BASE, "logo_blanco_final.png")
    LOGO_NEGRO  = os.path.join(_BASE, "logo_negro_final.png")

# Aspect ratios de los logos procesados
_LOGO_BLANCO_AR = 2877 / 845   # width / height
_LOGO_NEGRO_AR  = 2835 / 894

def logo(c, x, y, h=36, dark_bg=False):
    """
    Incrusta el logo real PNG.
    dark_bg=True  → versión blanca (fondo navy/oscuro)
    dark_bg=False → versión navy  (fondo blanco)
    h = altura deseada en puntos
    """
    if dark_bg:
        path = LOGO_BLANCO
        ar   = _LOGO_BLANCO_AR
    else:
        path = LOGO_NEGRO
        ar   = _LOGO_NEGRO_AR
    w = h * ar
    c.drawImage(path, x, y, width=w, height=h, mask='auto')


# ── HELPERS ───────────────────────────────────────────────────────────────────
def W(c, text, font, size):
    return c.stringWidth(text, font, size)

def wrap(text, cols):
    return textwrap.wrap(text, width=cols)

def section_header(c, x, y, text):
    c.setFillColor(NAVY_HEADER)
    c.setFont("DV-B", 11)
    c.drawString(x, y, text)
    line_end = x + W(c, text, "DV-B", 11) + 22
    c.setStrokeColor(RED)
    c.setLineWidth(1.6)
    c.line(x, y - 5, line_end, y - 5)
    return y - 20

def page_header_bar(c, breadcrumb_items, active=0):
    """Breadcrumb top bar + logo right + separator line — estilo interior FUNO."""
    # Thin red top stripe
    c.setFillColor(RED)
    c.rect(0, PH - 10, PW, 10, fill=1, stroke=0)

    # Logo top-right — height 28pt, positioned so top aligns near top stripe
    _lh = 28
    _lw = _lh * _LOGO_NEGRO_AR
    logo(c, PW - 40 - _lw, PH - 14 - _lh - 4, h=_lh, dark_bg=False)

    # Breadcrumb text
    x = 40
    y = PH - 34
    for i, part in enumerate(breadcrumb_items):
        if i == active:
            c.setFillColor(RED)
            c.setFont("DV-B", 8)
        else:
            c.setFillColor(GRAY_MED)
            c.setFont("DV", 8)
        c.drawString(x, y, part)
        x += W(c, part, "DV-B" if i == active else "DV", 8)
        if i < len(breadcrumb_items) - 1:
            sep = "  |  "
            c.setFillColor(GRAY_MED)
            c.setFont("DV", 8)
            c.drawString(x, y, sep)
            x += W(c, sep, "DV", 8)

    # Separator line
    c.setStrokeColor(GRAY_LINE)
    c.setLineWidth(0.7)
    c.line(40, PH - 56, PW - 40, PH - 56)

def page_footer_bar(c):
    """Footer simple — estilo FUNO."""
    c.setStrokeColor(GRAY_LINE)
    c.setLineWidth(0.5)
    c.line(40, 36, PW - 40, 36)
    c.setFillColor(GRAY_MED)
    c.setFont("DV", 7.5)
    c.drawCentredString(PW / 2, 22,
        "Lut Parra  |  Coach Transformacional & Facilitador  |  "
        "lut@lutparra.com  |  55.6674.0475  |  www.lutparra.com")

def red_bullet(c, x, y, text, cols=46, fsize=9.5):
    lines = wrap(text, cols)
    c.setFillColor(RED)
    c.setFont("DV-B", fsize - 0.5)
    c.drawString(x, y, "\u25a0")          # ■
    c.setFillColor(GRAY_DARK)
    c.setFont("DV", fsize)
    for i, ln in enumerate(lines):
        c.drawString(x + 14, y - i * (fsize + 1.5), ln)
    return y - len(lines) * (fsize + 1.5) - 4

def check_bullet(c, x, y, text, cols=46, fsize=9.5):
    lines = wrap(text, cols)
    c.setFillColor(RED)
    c.setFont("DV-B", fsize)
    c.drawString(x, y, "\u2713")          # ✓
    c.setFillColor(GRAY_DARK)
    c.setFont("DV", fsize)
    for i, ln in enumerate(lines):
        c.drawString(x + 15, y - i * (fsize + 1.5), ln)
    return y - len(lines) * (fsize + 1.5) - 4

def left_border_box(c, x, y, w, h, border_color=RED, bg_color=None):
    if bg_color:
        c.setFillColor(bg_color)
        c.rect(x + 4, y - h, w - 4, h, fill=1, stroke=0)
    c.setFillColor(border_color)
    c.rect(x, y - h, 4, h, fill=1, stroke=0)

def tag_pill(c, x, y, text, bg=RED, fg=WHITE, fsize=8):
    tw = W(c, text, "DV-B", fsize)
    c.setFillColor(bg)
    c.roundRect(x, y - 3, tw + 12, 14, 3, fill=1, stroke=0)
    c.setFillColor(fg)
    c.setFont("DV-B", fsize)
    c.drawString(x + 6, y + 1, text)
    return x + tw + 16


# ── CATÁLOGO DE PROGRAMAS (contenido real de fichas de programa) ──────────────
CATALOGO = {

    # ── TALLERES Y CURSOS ─────────────────────────────────────────────────────

    "speak_up": {
        "nombre": "Speak Up",
        "subtitulo": "Herramientas de inteligencia emocional aplicadas al modelo conversacional",
        "enfoque": "Liderazgo Interpersonal",
        "dirigido_a": "Toda la organización",
        "duraciones": [2, 4, 8], "unidad": "horas",
        "descripcion": (
            "Fortalecer competencias de comunicación que son clave para desarrollar y "
            "consolidar habilidades sociales e influir positivamente en los colaboradores "
            "a través de un diálogo saludable. Los participantes trabajan autoconciencia "
            "emocional, automotivación, empatía y habilidades sociales con herramientas "
            "prácticas aplicables de inmediato."
        ),
        "para_quien": [
            "Toda la organización",
            "Líderes que buscan mayor influencia en su equipo",
            "Equipos con retos de comunicación interna",
        ],
        "resultados": [
            "Logro de resultados con comunicación efectiva",
            "Fortalecimiento de relaciones interpersonales",
            "Mejor doma de decisiones",
            "Mayor influencia a través de un diálogo saludable",
        ],
    },

    "accountability_skills": {
        "nombre": "Accountability Skills",
        "subtitulo": "Herramientas para mejorar el desempeño, resolver expectativas insatisfechas, compromisos rotos y mala actitud",
        "enfoque": "Liderazgo Gerencial",
        "dirigido_a": "Personas con gente a su cargo",
        "duraciones": [4, 8], "unidad": "horas",
        "descripcion": (
            "Proveer al participante herramientas sencillas y prácticas que lo lleven "
            "a una elección personal para sobreponerse a las propias circunstancias y "
            "demostrar la apropiación necesaria para lograr los resultados deseados. "
            "Trabaja inteligencia emocional, diagnóstico de la brecha, conversaciones "
            "de rendición de cuentas y la metodología S.M.A. (Sencillo, Motivante, Accionable)."
        ),
        "para_quien": [
            "Personas con gente a su cargo",
            "Líderes que enfrentan incumplimiento de compromisos",
            "Equipos con brechas de rendimiento o mala actitud",
        ],
        "resultados": [
            "Logro de resultados con responsabilidad genuina",
            "Fortalecimiento de relaciones interpersonales",
            "Mejor doma de decisiones",
            "Cultura de accountability observable en el día a día",
        ],
    },

    "administracion_tiempo": {
        "nombre": "Administración del Tiempo",
        "subtitulo": "Herramientas para decidir de forma eficiente, mejorar el desempeño y traducirlas en acciones que llevan al logro de objetivos",
        "enfoque": "Liderazgo Personal",
        "dirigido_a": "Toda la organización",
        "duraciones": [4, 6], "unidad": "horas",
        "descripcion": (
            "Elevar la productividad, toda vez que los participantes adquirirán las "
            "técnicas y habilidades necesarias para administrar de una manera efectiva "
            "el tiempo. Cubre principios de administración del tiempo, la matriz de "
            "urgente/importante, técnicas anti-distractores, asignación de prioridades "
            "y construcción de un plan de acción personal de mejora."
        ),
        "para_quien": [
            "Toda la organización",
            "Líderes con agenda desbordada o baja productividad",
            "Profesionales que buscan mayor enfoque y resultados",
        ],
        "resultados": [
            "Definición clara y objetiva de prioridades",
            "Facilita la implementación de hábitos productivos",
            "Responsabilidad y puntualidad en compromisos",
            "Objetividad y estructura de planes personales",
        ],
    },

    "comportamientos_vitales": {
        "nombre": "Comportamientos Vitales del Líder",
        "subtitulo": "Paradigmas, procesos y comportamientos fundamentales para el líder",
        "enfoque": "Liderazgo Gerencial",
        "dirigido_a": "Personas con gente a su cargo",
        "duraciones": [4, 6, 8], "unidad": "horas",
        "descripcion": (
            "Proporcionar al participante las herramientas necesarias para establecer "
            "criterios de decisión, definir procesos claros y fomentar los "
            "comportamientos saludables como líder. Trabaja los roles gerenciales, "
            "establecimiento de objetivos, delegación y empoderamiento, retroalimentación "
            "efectiva, reconocimiento del equipo y plan de acción."
        ),
        "para_quien": [
            "Personas con gente a su cargo",
            "Líderes que buscan mayor efectividad en su gestión",
            "Gerentes en desarrollo o nuevos en el rol",
        ],
        "resultados": [
            "Habilitado para dirigir un equipo de trabajo",
            "Capacidad de definir y sostener el rumbo",
            "Empoderar al equipo de trabajo con método",
            "Retroalimentación efectiva y reconocimiento genuino",
        ],
    },

    "liderazgo_sentido_humano": {
        "nombre": "Liderazgo con Sentido Humano",
        "subtitulo": "Liderazgo que genera ambientes apropiados para trabajar y equipos de alto desempeño",
        "enfoque": "Liderazgo Gerencial",
        "dirigido_a": "Toda la organización",
        "duraciones": [4], "unidad": "horas",
        "descripcion": (
            "Conocer y entender la importancia de generar un ambiente apropiado para "
            "trabajar y fortalecer la gestión efectiva de Capital Humano. Promover un "
            "cambio de comportamiento y de cultura generando un impacto positivo en el "
            "ambiente de trabajo y el rendimiento de los equipos. Trabaja clima "
            "organizacional, liderazgo humano, control y confianza, y cultura como "
            "ventaja competitiva."
        ),
        "para_quien": [
            "Toda la organización",
            "Líderes que buscan mejorar el clima laboral",
            "Organizaciones con retos de rotación o desmotivación",
        ],
        "resultados": [
            "Fomentar relaciones basadas en confianza",
            "Estimular el apoyo voluntario y espontáneo",
            "Orientar el liderazgo asertivo",
            "Cultura como ventaja competitiva sostenible",
        ],
    },

    "disena_tus_habitos": {
        "nombre": "Diseña Tus Hábitos",
        "subtitulo": "Habilidades para identificar y crear los hábitos necesarios para alcanzar el éxito y la felicidad en lo profesional y personal",
        "enfoque": "Liderazgo Personal",
        "dirigido_a": "Toda la organización",
        "duraciones": [4], "unidad": "horas",
        "descripcion": (
            "Comprender cómo funcionan los hábitos e identificar aquellos que impactan "
            "de manera desproporcionada en el desempeño, el compromiso y la felicidad. "
            "Aprender a utilizar la habilidad en lugar de la fuerza de voluntad para "
            "reemplazar hábitos limitantes por hábitos efectivos. Metodología: "
            "Dejar atrás el rezago · Hágalo realizable · Hágalo deseable · Hágalo habitual."
        ),
        "para_quien": [
            "Toda la organización",
            "Profesionales que buscan mayor efectividad y bienestar",
            "Líderes que quieren instalar cambios duraderos",
        ],
        "resultados": [
            "Reconocer cuándo y qué comportamientos cambiar",
            "Instalar nuevos hábitos sin fuerza de voluntad",
            "Mantener los cambios en el tiempo",
            "Crear nuevas rutinas que produzcan los resultados deseados",
        ],
    },

    "influenciar": {
        "nombre": "Influenciar a los Otros",
        "subtitulo": "Herramientas para llevar a cabo cambios organizacionales. Influir sin ejercer el poder del organigrama",
        "enfoque": "Liderazgo Organizacional",
        "dirigido_a": "Agentes de cambio y personas que requieren alto nivel de influencia",
        "duraciones": [4, 6], "unidad": "horas",
        "descripcion": (
            "Ayudar a los líderes a influir positivamente en el comportamiento de toda "
            "la organización, motivar con eficacia y empoderar a otros. Trabaja: "
            "resultados claros y medibles, identificación de comportamientos necesarios, "
            "diagnóstico real de la situación y las 6 fuentes de influencia "
            "(motivación y habilidad personal, social y estructural)."
        ),
        "para_quien": [
            "Agentes de cambio organizacional",
            "Líderes que requieren influir sin autoridad formal",
            "Profesionales en estructuras matriciales",
        ],
        "resultados": [
            "Canalizar la autoridad formal e informal para motivar",
            "Impulsar comportamientos de alto apalancamiento",
            "Fomentar y manejar el cambio organizacional",
            "Liderazgo organizacional con influencia positiva",
        ],
    },

    "inteligencia_emocional": {
        "nombre": "Inteligencia Emocional",
        "subtitulo": "El manejo de las emociones en situaciones de adversidad",
        "enfoque": "Liderazgo Personal",
        "dirigido_a": "Toda la organización",
        "duraciones": [4], "unidad": "horas",
        "descripcion": (
            "Desarrollar en los participantes las habilidades para identificar y "
            "manejar adecuadamente las emociones en ellos mismos y en los demás, "
            "en beneficio de la organización. Abarca: introducción a la IE, "
            "identificación de propias emociones y de emociones en otros, y manejo "
            "apropiado de las emociones con un laboratorio práctico y plan de acción."
        ),
        "para_quien": [
            "Toda la organización",
            "Líderes en entornos de alta presión o adversidad",
            "Equipos que buscan mejor colaboración y clima",
        ],
        "resultados": [
            "Mejora el autoconocimiento y toma de decisiones",
            "Mejora el rendimiento laboral y relaciones interpersonales",
            "Otorga capacidad de influencia y liderazgo",
            "Desarrolla proactividad y motivación intrínseca",
        ],
    },

    "liderazgo_siglo_xxi": {
        "nombre": "Liderazgo del Siglo XXI",
        "subtitulo": "Comprensión clara de los fundamentos del liderazgo en el entorno empresarial actual",
        "enfoque": "Liderazgo Gerencial",
        "dirigido_a": "Toda la organización",
        "duraciones": [4], "unidad": "horas",
        "descripcion": (
            "Capacitar a los participantes para desempeñarse eficazmente en puestos "
            "de liderazgo, proporcionando una comprensión clara de los conceptos "
            "fundamentales del liderazgo y cómo se aplican en un entorno empresarial. "
            "Cubre: estilos de liderazgo, habilidades del líder, liderazgo y motivación, "
            "liderazgo y trabajo en equipo."
        ),
        "para_quien": [
            "Toda la organización",
            "Líderes nuevos o en transición al rol",
            "Organizaciones que buscan una cultura de liderazgo sólida",
        ],
        "resultados": [
            "Fomentar relaciones basadas en confianza",
            "Estimular el apoyo voluntario y espontáneo",
            "Comunicación y visión estratégica fortalecidas",
            "Motivación, trabajo en equipo y toma de decisiones",
        ],
    },

    "desarrollando_colaboradores": {
        "nombre": "Desarrollando, Reconociendo y Motivando a tus Colaboradores",
        "subtitulo": "Herramientas para maximizar la productividad, mejorar el clima laboral y reducir la rotación",
        "enfoque": "Liderazgo Gerencial",
        "dirigido_a": "Toda la organización",
        "duraciones": [4], "unidad": "horas",
        "descripcion": (
            "Brindar a los líderes de equipo las herramientas y técnicas necesarias "
            "para desarrollar, reconocer y motivar efectivamente a sus colaboradores. "
            "Abarca: desarrollo de colaboradores, reconocimiento y su impacto en la "
            "satisfacción laboral, y motivación intrínseca y extrínseca con técnicas "
            "para motivar individual y en equipo."
        ),
        "para_quien": [
            "Toda la organización",
            "Líderes con equipos a cargo",
            "Organizaciones con retos de retención y motivación",
        ],
        "resultados": [
            "Fomentar relaciones basadas en confianza",
            "Estimular el apoyo voluntario y espontáneo del equipo",
            "Orientar el liderazgo asertivo y empático",
            "Reducción de rotación y aumento del compromiso",
        ],
    },

    # ── CONFERENCIAS ──────────────────────────────────────────────────────────

    "conferencia_conversaciones": {
        "nombre": "Conferencia: Conversaciones Cruciales",
        "subtitulo": "Aprende a dirigir conversaciones difíciles e importantes de manera persuasiva",
        "enfoque": "Comunicación",
        "dirigido_a": "Toda la organización",
        "duraciones": [50], "unidad": "minutos",
        "descripcion": (
            "Que el participante cobre consciencia de la importancia de aprender "
            "a dirigir 'conversaciones difíciles e importantes' de una manera "
            "persuasiva; fortaleciendo relaciones y logrando mejores resultados. "
            "Temas: primero trabaja en ti, aprende a exponer tu camino, observar y "
            "crear seguridad, y pasar a la acción."
        ),
        "para_quien": [
            "Toda la organización",
            "Líderes que evitan conversaciones difíciles",
            "Equipos con tensiones no resueltas",
        ],
        "resultados": [
            "Logro de resultados en conversaciones clave",
            "Fortalecimiento de relaciones interpersonales",
            "Mejor doma de decisiones con claridad",
            "Mejora sustancial en la comunicación del equipo",
        ],
    },

    "conferencia_habitos": {
        "nombre": "Conferencia: El Poder de los Hábitos",
        "subtitulo": "Cómo los hábitos determinan los resultados en la vida personal y profesional",
        "enfoque": "Liderazgo Personal",
        "dirigido_a": "Toda la organización",
        "duraciones": [50], "unidad": "minutos",
        "descripcion": (
            "Al finalizar esta conferencia, el 100% de los presentes sabrá de qué "
            "manera los hábitos determinan los resultados que obtienen en la vida "
            "personal y profesional. Abarca: qué son los hábitos y cómo funcionan, "
            "casos de éxito (Alcoa, Starbucks, Google), cultura organizacional y "
            "hábitos, y el impacto en la organización."
        ),
        "para_quien": [
            "Toda la organización",
            "Equipos que buscan mejorar su desempeño colectivo",
            "Líderes que quieren transformar la cultura del equipo",
        ],
        "resultados": [
            "Identificar los hábitos que impactan el desempeño y la felicidad",
            "Adaptarse ante el cambio con mayor agilidad",
            "Crear nuevas rutinas que produzcan los resultados deseados",
            "Entender la cultura organizacional desde los hábitos",
        ],
    },

    # ── TEAMBUILDING ──────────────────────────────────────────────────────────

    "teambuilding": {
        "nombre": "Teambuilding con Points of You",
        "subtitulo": "Retiro experiencial de integración y liderazgo — Be the Captain of your Ship",
        "enfoque": "Integración de equipos",
        "dirigido_a": "Toda la organización",
        "duraciones": [6], "unidad": "horas",
        "descripcion": (
            "Fomentar la toma de conciencia sobre la importancia de ser un colaborador "
            "accountable, mejorar el entorno laboral incentivando comunicación abierta "
            "y sincera, e impulsar el espíritu de colaboración. Utiliza la metodología "
            "Points of You® (herramienta certificada internacionalmente) con fotografías "
            "y palabras que generan reflexión profunda y compromisos concretos. "
            "El desarrollo es completamente a la medida de cada equipo."
        ),
        "para_quien": [
            "Toda la organización",
            "Equipos que necesitan reconectarse o están en formación",
            "Líderes con sus equipos directos",
        ],
        "resultados": [
            "Mayor cohesión, confianza y comunicación en el equipo",
            "Compromisos concretos de mejora individual y grupal",
            "Impulso al espíritu de colaboración y accountability",
            "Energía renovada y sentido de propósito compartido",
        ],
    },

    # ── PROGRAMA 0-100 ────────────────────────────────────────────────────────

    "cero_a_cien": {
        "nombre": "Liderazgo 0-100",
        "subtitulo": "Formación para nuevos líderes y líderes en evolución · Base + Ejecución (2 niveles)",
        "enfoque": "Desarrollo integral de liderazgo",
        "dirigido_a": "Nuevos líderes y líderes en evolución",
        "duraciones": [3, 6], "unidad": "meses",
        "descripcion": (
            "Un programa práctico para acelerar habilidades de liderazgo, comunicación "
            "y accountability con resultados medibles. Nivel 1 (0→50): Liderazgo Personal "
            "+ Interpersonal — autogestión emocional, comunicación, delegación sin "
            "fricción, feedback y conversaciones difíciles. Entregable: Plan 90 días. "
            "Nivel 2 (50→100): Liderazgo Gerencial + Organizacional — accountability, "
            "influencia, coaching de desempeño, toma de decisiones y liderar el cambio. "
            "Entregable: Sistema de Rendición de Cuentas. Incluye diagnóstico pre/post "
            "y Reporte Ejecutivo para RRHH."
        ),
        "para_quien": [
            "Nuevos líderes que necesitan bases sólidas",
            "Líderes en evolución hacia roles de mayor responsabilidad",
            "Organizaciones que invierten en su pipeline de liderazgo",
        ],
        "resultados": [
            "Líderes que alinean, delegan y sostienen resultados",
            "Conversaciones difíciles manejadas con claridad y respeto",
            "Accountability sano. claridad + seguimiento + consecuencias",
            "Evidencia medible de avance (diagnóstico pre/post por competencia)",
        ],
    },
}


# ── PÁGINA 1: PORTADA ─────────────────────────────────────────────────────────
def pagina_portada(c, data):
    prog    = data["programa"]
    cliente = data["cliente"]
    fmt     = data.get("formato", "Presencial")
    unidad  = prog.get("unidad", "horas")
    dur     = data.get("duracion")
    fecha   = data.get("fecha", datetime.date.today().strftime("%-d de %B de %Y"))

    # ── Fondo navy completo
    c.setFillColor(NAVY)
    c.rect(0, 0, PW, PH, fill=1, stroke=0)

    # ── Franja roja superior (como en FUNO)
    c.setFillColor(RED)
    c.rect(0, PH - 12, PW, 12, fill=1, stroke=0)

    # ── Logo top-left (versión blanca sobre navy)
    # Logo portada: versión blanca sobre navy, altura 38pt
    logo(c, 40, PH - 14 - 38, h=38, dark_bg=True)

    # ── "PROPUESTA COMERCIAL" con subrayado rojo
    y_label = PH * 0.545
    c.setFillColor(RED)
    c.setFont("DV-B", 10)
    label = "PROPUESTA COMERCIAL"
    c.drawString(40, y_label, label)
    c.setStrokeColor(RED)
    c.setLineWidth(1.5)
    c.line(40, y_label - 5, 40 + W(c, label, "DV-B", 10) + 90, y_label - 5)

    # ── Nombre del programa (grande, blanco, bold — hasta 2 líneas)
    nombre = prog["nombre"].upper()
    words  = nombre.split()
    if len(words) == 1:
        lineas_prog = [nombre]
    elif len(words) == 2:
        lineas_prog = [words[0], words[1]]
    elif len(words) == 3:
        lineas_prog = [words[0], " ".join(words[1:])]
    else:
        mid = len(words) // 2
        lineas_prog = [" ".join(words[:mid]), " ".join(words[mid:])]

    max_l = max(len(l) for l in lineas_prog)
    fsz   = 52 if max_l <= 8 else 40 if max_l <= 12 else 30 if max_l <= 18 else 24

    c.setFillColor(WHITE)
    c.setFont("DV-B", fsz)
    y_title = y_label - 58
    for ln in lineas_prog:
        c.drawString(40, y_title, ln)
        y_title -= fsz + 10

    # ── Subtítulo
    if prog.get("subtitulo"):
        c.setFillColor(HexColor('#9AACCC'))
        c.setFont("DV-I", 12)
        c.drawString(40, y_title - 4, prog["subtitulo"])
        y_title -= 24

    # ── Tag duración · formato
    if dur:
        c.setFillColor(HexColor('#8899BB'))
        c.setFont("DV", 11)
        c.drawString(40, y_title - 8, f"{dur} {unidad}  ·  {fmt}")

    # ── Info cliente (zona inferior)
    y_cli = PH * 0.25
    c.setFillColor(BLUE_ACC)
    c.setFont("DV", 12)
    c.drawString(40, y_cli, f"Preparada para: {cliente.get('contacto', '')}")

    if cliente.get("area") or cliente.get("empresa"):
        partes = [p for p in [cliente.get("area"), cliente.get("empresa")] if p]
        c.setFillColor(WHITE)
        c.setFont("DV", 11)
        c.drawString(40, y_cli - 22, "  |  ".join(partes))

    c.setFillColor(HexColor('#8899BB'))
    c.setFont("DV", 11)
    c.drawString(40, y_cli - 44, fecha)

    # ── Footer
    c.setStrokeColor(HexColor('#2A3F6A'))
    c.setLineWidth(0.5)
    c.line(40, 52, PW - 40, 52)
    c.setFillColor(HexColor('#8899BB'))
    c.setFont("DV", 8)
    c.drawString(40, 36,
        "Preparada por: Lut Parra  |  Coach Transformacional & Facilitador  |  "
        "lut@lutparra.com  |  55.6674.0475  |  www.lutparra.com")


# ── PÁGINA 2: EL PROGRAMA ─────────────────────────────────────────────────────
def pagina_programa(c, data):
    c.showPage()
    prog    = data["programa"]
    cliente = data["cliente"]
    unidad  = prog.get("unidad", "horas")
    dur     = data.get("duracion")

    crumbs = [
        "El Programa",
        prog["nombre"],
        f"{dur} {unidad}" if dur else "",
        cliente.get("empresa", ""),
    ]
    crumbs = [x for x in crumbs if x]
    page_header_bar(c, crumbs, active=0)

    y = PH - 76

    # ── Párrafo introductorio (contexto)
    contexto = data.get("contexto_cliente", "")
    if contexto:
        c.setFillColor(GRAY_MED)
        c.setFont("DV-I", 10)
        for ln in wrap(contexto, 92):
            c.drawString(40, y, ln)
            y -= 14
        y -= 8

    # ── Descripción del programa (caja con borde rojo izquierdo)
    y = section_header(c, 40, y, "DESCRIPCIÓN DEL PROGRAMA")
    desc_lines = wrap(prog["descripcion"], 88)
    box_h      = len(desc_lines) * 13 + 18
    left_border_box(c, 40, y + 8, PW - 80, box_h, RED, GRAY_BG)
    c.setFillColor(GRAY_DARK)
    c.setFont("DV-I", 9.5)
    ty = y - 2
    for ln in desc_lines:
        c.drawString(56, ty, ln)
        ty -= 13
    y -= box_h + 16

    # ── Dos columnas: PARA QUIÉN + RESULTADOS ESPERADOS
    cx1 = 40
    cx2 = PW / 2 + 8
    cw  = PW / 2 - 52

    y_sec = y
    section_header(c, cx1, y_sec, "PARA QUIÉN ES")
    section_header(c, cx2, y_sec, "RESULTADOS ESPERADOS")
    y -= 4

    # Caja izquierda
    n_left  = len(prog.get("para_quien", []))
    box_h_l = n_left * 24 + 12
    left_border_box(c, cx1, y + 2, cw, box_h_l, BLUE_ACC, GRAY_BG)

    # Caja derecha
    n_right = len(prog.get("resultados", []))
    box_h_r = n_right * 24 + 12
    left_border_box(c, cx2, y + 2, cw, box_h_r, RED, GRAY_BG)

    yl = y - 8
    for item in prog.get("para_quien", []):
        yl = red_bullet(c, cx1 + 8, yl, item, cols=36)

    yr = y - 8
    for item in prog.get("resultados", []):
        yr = check_bullet(c, cx2 + 8, yr, item, cols=36)

    # ── Nota de formato (opcional)
    nota = data.get("nota_formato")
    if nota:
        yn = min(yl, yr) - 18
        c.setFillColor(GRAY_MED)
        c.setFont("DV-I", 8.5)
        for ln in wrap(f"* {nota}", 92):
            c.drawString(40, yn, ln)
            yn -= 12

    page_footer_bar(c)


# ── PÁGINA 3: INVERSIÓN ───────────────────────────────────────────────────────
def pagina_inversion(c, data):
    c.showPage()
    prog    = data["programa"]
    cliente = data["cliente"]
    inv     = data.get("inversion", {})
    unidad  = prog.get("unidad", "horas")
    dur     = data.get("duracion")
    fmt     = data.get("formato", "Presencial")

    crumbs = [
        "Propuesta Económica",
        "Inversión",
        "Condiciones",
        cliente.get("empresa", ""),
    ]
    crumbs = [x for x in crumbs if x]
    page_header_bar(c, crumbs, active=0)

    y = PH - 76

    # ── INVERSIÓN ────────────────────────────────────────────────────────────
    y = section_header(c, 40, y, "INVERSIÓN")

    # Columnas de tabla
    cx = [40, 250, 348, 442]   # x de: solución, sesiones, participantes, inversión
    cw_total = PW - 80         # ancho total tabla
    row_h    = 36

    # — Header de tabla (navy)
    c.setFillColor(NAVY_HEADER)
    c.rect(40, y - row_h + 10, cw_total, row_h, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("DV-B", 8.5)
    for txt, xi in zip(["SOLUCIÓN", "SESIONES", "PARTICIPANTES", "INVERSIÓN"], cx):
        c.drawString(xi + 8, y - 8, txt)
    y -= row_h

    # — Fila del programa
    c.setFillColor(GRAY_BG)
    c.rect(40, y - row_h + 10, cw_total, row_h, fill=1, stroke=0)
    c.setFillColor(RED)
    c.rect(40, y - row_h + 10, 4, row_h, fill=1, stroke=0)

    c.setFillColor(NAVY)
    c.setFont("DV-B", 9.5)
    c.drawString(cx[0] + 10, y - 8, prog["nombre"])
    if prog.get("subtitulo"):
        c.setFillColor(GRAY_MED)
        c.setFont("DV-I", 8)
        sub = prog["subtitulo"]
        if len(sub) > 32:
            sub = sub[:29] + "..."
        c.drawString(cx[0] + 10, y - 20, sub)

    sesiones = inv.get("sesiones", f"{dur} {unidad}" if dur else "—")
    c.setFillColor(GRAY_DARK)
    c.setFont("DV", 9.5)
    c.drawCentredString(cx[1] + 44, y - 12, str(sesiones))
    c.drawCentredString(cx[2] + 44, y - 12, inv.get("participantes", "—"))
    c.setFillColor(NAVY)
    c.setFont("DV-B", 10)
    c.drawCentredString(cx[3] + 55, y - 12, inv.get("total", "—"))
    y -= row_h

    # — Fila TOTAL
    c.setFillColor(NAVY_HEADER)
    c.rect(40, y - 26 + 10, cw_total, 26, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("DV-B", 10)
    c.drawString(52, y - 7, "TOTAL DEL PROGRAMA")
    total_iva = inv.get("total_iva", (inv.get("total", "—") + " + I.V.A."))
    c.setFont("DV-B", 13)
    c.drawRightString(PW - 48, y - 9, total_iva)
    y -= 26 + 14

    # ── CONDICIONES COMERCIALES ──────────────────────────────────────────────
    y = section_header(c, 40, y, "CONDICIONES COMERCIALES")

    condiciones = [
        ("Precios:",     "Expresados en pesos mexicanos. No incluyen IVA."),
        ("Pago:",        inv.get("modalidad_pago", "Pago de contado.")),
        ("Vigencia:",    "30 días naturales a partir de la fecha de emisión."),
        ("Modalidad:",   f"{fmt}. En caso necesario, sesiones virtuales por Zoom sin costo adicional."),
        ("Cancelaciones:", "Sesiones canceladas con menos de 24 hrs de anticipación se consideran impartidas."),
    ]
    if inv.get("notas"):
        condiciones.append(("Notas:", inv["notas"]))

    # Dividir en dos columnas
    mid      = (len(condiciones) + 1) // 2
    col_l    = condiciones[:mid]
    col_r    = condiciones[mid:]
    col2_x   = PW / 2 + 8
    label_w  = 94

    def draw_conditions(items, ox, oy):
        for lbl, val in items:
            c.setFillColor(RED)
            c.setFont("DV-B", 9)
            c.drawString(ox, oy, lbl)
            c.setFillColor(GRAY_DARK)
            c.setFont("DV", 9)
            vlines = wrap(val, 40)
            for i, vl in enumerate(vlines):
                c.drawString(ox + label_w, oy - i * 12, vl)
            oy -= len(vlines) * 12 + 10
        return oy

    yl = y
    yr = y
    yl = draw_conditions(col_l, 40,      yl)
    yr = draw_conditions(col_r, col2_x,  yr)

    y = min(yl, yr) - 14

    # ── SIGUIENTE PASO ───────────────────────────────────────────────────────
    if y > 110:
        y = section_header(c, 40, y, "SIGUIENTE PASO")
        pasos = data.get("siguiente_paso", [
            "Agendar una llamada para revisar los detalles",
            "Confirmar fechas de inicio",
            "Firmar carta de acuerdo",
        ])
        for paso in pasos:
            y = red_bullet(c, 40, y, paso, cols=80)

    page_footer_bar(c)


# ── FUNCIÓN PRINCIPAL ─────────────────────────────────────────────────────────
def generar_pdf(data: dict, ruta_salida: str = "propuesta.pdf") -> str:
    """
    Genera un PDF de propuesta de 3 páginas.

    Campos de 'data':
        programa_key      (str)  : clave del CATALOGO
        duracion          (int)  : duración elegida (4, 8…)
        formato           (str)  : "Presencial" | "Virtual" | "Presencial / Virtual"
        cliente           (dict) : {
                                     "contacto": "Nombre del contacto",
                                     "area":     "Área / Departamento",
                                     "empresa":  "Nombre de la empresa"
                                   }
        contexto_cliente  (str)  : 1-2 frases del reto del cliente
        inversion         (dict) : {
                                     "sesiones":       "4",
                                     "participantes":  "25 participantes",
                                     "total":          "$32,000",
                                     "total_iva":      "$32,000 + I.V.A.",
                                     "modalidad_pago": "Pago de contado",
                                     "notas":          "Incluye materiales"
                                   }
        siguiente_paso    (list) : pasos opcionales para el cierre
        nota_formato      (str)  : nota logística opcional
        fecha             (str)  : "17 de marzo de 2026"
    """
    prog_key = data.get("programa_key")
    if prog_key not in CATALOGO:
        raise ValueError(
            f"Programa '{prog_key}' no encontrado.\n"
            f"Disponibles: {', '.join(CATALOGO.keys())}"
        )
    data["programa"] = CATALOGO[prog_key]

    c = rl_canvas.Canvas(ruta_salida, pagesize=letter)
    c.setTitle(f"Propuesta – {data['programa']['nombre']} – "
               f"{data['cliente'].get('empresa', '')}")
    c.setAuthor("Lut Parra – Leadership Mentoring")
    c.setSubject("Propuesta Comercial")

    pagina_portada(c, data)
    pagina_programa(c, data)
    pagina_inversion(c, data)
    c.save()
    print(f"✓  {ruta_salida}")
    return ruta_salida


# ── EJEMPLO ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    datos = {
        "programa_key": "speak_up",
        "duracion":     4,
        "formato":      "Presencial",
        "cliente": {
            "contacto": "Lic. Patricia Morales",
            "area":     "Recursos Humanos",
            "empresa":  "Grupo Innovación MX",
        },
        "contexto_cliente": (
            "El equipo directivo de Grupo Innovación MX enfrenta retos de comunicación "
            "interna que generan fricciones en la toma de decisiones y reuniones "
            "poco efectivas. La organización busca que sus líderes comuniquen con "
            "mayor claridad, confianza e impacto."
        ),
        "inversion": {
            "sesiones":      "1 taller de 4 hrs",
            "participantes": "20 participantes",
            "total":         "$28,500",
            "total_iva":     "$28,500 + I.V.A.",
            "modalidad_pago":"Pago de contado al confirmar",
            "notas":         "Incluye materiales digitales y reporte de cierre.",
        },
        "siguiente_paso": [
            "Agendar llamada para afinar detalles",
            "Confirmar fecha de impartición",
            "Firmar carta de acuerdo",
        ],
        "fecha": "17 de marzo de 2026",
    }

    out = "/sessions/eager-clever-pasteur/mnt/outputs/Propuesta_SpeakUp_v2.pdf"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    generar_pdf(datos, out)
