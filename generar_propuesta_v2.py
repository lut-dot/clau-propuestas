"""
Generador de Propuestas v2 â Lut Parra Leadership Mentoring
============================================================
Estilo: Propuesta FUNO 2026 (navy + rojo + azul accent)
Fuente: DejaVu Sans (soporta espaÃ±ol completo)

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

# ââ FUENTES ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
pdfmetrics.registerFont(TTFont("DV",    os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DV-B",  os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DV-I",  os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFont(TTFont("DV-BI", os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans-BoldOblique.ttf")))

# ââ COLORES DE MARCA âââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
NAVY        = HexColor('#1B2A4A')   # fondo azul oscuro
RED         = HexColor('#CC0000')   # rojo acento
BLUE_ACC    = HexColor('#2980B9')   # azul claro (nombres, links)
WHITE       = white
GRAY_BG     = HexColor('#F4F6FA')   # fondo gris suave
GRAY_LINE   = HexColor('#DDDDDD')   # lÃ­neas separadoras
GRAY_MED    = HexColor('#888888')   # texto secundario
GRAY_DARK   = HexColor('#333333')   # texto cuerpo
NAVY_HEADER = HexColor('#1B2A4A')   # header de tablas

PW, PH = letter   # 612 Ã 792 pts

# ââ RUTAS DE LOGOS ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
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
    dark_bg=True  â versiÃ³n blanca (fondo navy/oscuro)
    dark_bg=False â versiÃ³n navy  (fondo blanco)
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


# ââ HELPERS âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
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
    """Breadcrumb top bar + logo right + separator line â estilo interior FUNO."""
    # Thin red top stripe
    c.setFillColor(RED)
    c.rect(0, PH - 10, PW, 10, fill=1, stroke=0)

    # Logo top-right â height 28pt, positioned so top aligns near top stripe
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
    """Footer simple â estilo FUNO."""
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
    c.drawString(x, y, "\u25a0")          # â 
    c.setFillColor(GRAY_DARK)
    c.setFont("DV", fsize)
    for i, ln in enumerate(lines):
        c.drawString(x + 14, y - i * (fsize + 1.5), ln)
    return y - len(lines) * (fsize + 1.5) - 4

def check_bullet(c, x, y, text, cols=46, fsize=9.5):
    lines = wrap(text, cols)
    c.setFillColor(RED)
    c.setFont("DV-B", fsize)
    c.drawString(x, y, "\u2713")          # â
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


# ââ CATÃLOGO DE PROGRAMAS (contenido real de fichas de programa) ââââââââââââââ
CATALOGO = {

    # ââ TALLERES Y CURSOS âââââââââââââââââââââââââââââââââââââââââââââââââââââ

    "speak_up": {
        "nombre": "Speak Up",
        "subtitulo": "Herramientas de inteligencia emocional aplicadas al modelo conversacional",
        "enfoque": "Liderazgo Interpersonal",
        "dirigido_a": "Toda la organizaciÃ³n",
        "duraciones": [2, 4, 8], "unidad": "horas",
        "descripcion": (
            "Fortalecer competencias de comunicaciÃ³n que son clave para desarrollar y "
            "consolidar habilidades sociales e influir positivamente en los colaboradores "
            "a travÃ©s de un diÃ¡logo saludable. Los participantes trabajan autoconciencia "
            "emocional, automotivaciÃ³n, empatÃ­a y habilidades sociales con herramientas "
            "prÃ¡cticas aplicables de inmediato."
        ),
        "para_quien": [
            "Toda la organizaciÃ³n",
            "LÃ­deres que buscan mayor influencia en su equipo",
            "Equipos con retos de comunicaciÃ³n interna",
        ],
        "resultados": [
            "Logro de resultados con comunicaciÃ³n efectiva",
            "Fortalecimiento de relaciones interpersonales",
            "Mejor doma de decisiones",
            "Mayor influencia a travÃ©s de un diÃ¡logo saludable",
        ],
    },

    "accountability_skills": {
        "nombre": "Accountability Skills",
        "subtitulo": "Herramientas para mejorar el desempeÃ±o, resolver expectativas insatisfechas, compromisos rotos y mala actitud",
        "enfoque": "Liderazgo Gerencial",
        "dirigido_a": "Personas con gente a su cargo",
        "duraciones": [4, 8], "unidad": "horas",
        "descripcion": (
            "Proveer al participante herramientas sencillas y prÃ¡cticas que lo lleven "
            "a una elecciÃ³n personal para sobreponerse a las propias circunstancias y "
            "demostrar la apropiaciÃ³n necesaria para lograr los resultados deseados. "
            "Trabaja inteligencia emocional, diagnÃ³stico de la brecha, conversaciones "
            "de rendiciÃ³n de cuentas y la metodologÃ­a S.M.A. (Sencillo, Motivante, Accionable)."
        ),
        "para_quien": [
            "Personas con gente a su cargo",
            "LÃ­deres que enfrentan incumplimiento de compromisos",
            "Equipos con brechas de rendimiento o mala actitud",
        ],
        "resultados": [
            "Logro de resultados con responsabilidad genuina",
            "Fortalecimiento de relaciones interpersonales",
            "Mejor doma de decisiones",
            "Cultura de accountability observable en el dÃ­a a dÃ­a",
        ],
    },

    "administracion_tiempo": {
        "nombre": "AdministraciÃ³n del Tiempo",
        "subtitulo": "Herramientas para decidir de forma eficiente, mejorar el desempeÃ±o y traducirlas en acciones que llevan al logro de objetivos",
        "enfoque": "Liderazgo Personal",
        "dirigido_a": "Toda la organizaciÃ³n",
        "duraciones": [4, 6], "unidad": "horas",
        "descripcion": (
            "Elevar la productividad, toda vez que los participantes adquirirÃ¡n las "
            "tÃ©cnicas y habilidades necesarias para administrar de una manera efectiva "
            "el tiempo. Cubre principios de administraciÃ³n del tiempo, la matriz de "
            "urgente/importante, tÃ©cnicas anti-distractores, asignaciÃ³n de prioridades "
            "y construcciÃ³n de un plan de acciÃ³n personal de mejora."
        ),
        "para_quien": [
            "Toda la organizaciÃ³n",
            "LÃ­deres con agenda desbordada o baja productividad",
            "Profesionales que buscan mayor enfoque y resultados",
        ],
        "resultados": [
            "DefiniciÃ³n clara y objetiva de prioridades",
            "Facilita la implementaciÃ³n de hÃ¡bitos productivos",
            "Responsabilidad y puntualidad en compromisos",
            "Objetividad y estructura de planes personales",
        ],
    },

    "comportamientos_vitales": {
        "nombre": "Comportamientos Vitales del LÃ­der",
        "subtitulo": "Paradigmas, procesos y comportamientos fundamentales para el lÃ­der",
        "enfoque": "Liderazgo Gerencial",
        "dirigido_a": "Personas con gente a su cargo",
        "duraciones": [4, 6, 8], "unidad": "horas",
        "descripcion": (
            "Proporcionar al participante las herramientas necesarias para establecer "
            "criterios de decisiÃ³n, definir procesos claros y fomentar los "
            "comportamientos saludables como lÃ­der. Trabaja los roles gerenciales, "
            "establecimiento de objetivos, delegaciÃ³n y empoderamiento, retroalimentaciÃ³n "
            "efectiva, reconocimiento del equipo y plan de acciÃ³n."
        ),
        "para_quien": [
            "Personas con gente a su cargo",
            "LÃ­deres que buscan mayor efectividad en su gestiÃ³n",
            "Gerentes en desarrollo o nuevos en el rol",
        ],
        "resultados": [
            "Habilitado para dirigir un equipo de trabajo",
            "Capacidad de definir y sostener el rumbo",
            "Empoderar al equipo de trabajo con mÃ©todo",
            "RetroalimentaciÃ³n efectiva y reconocimiento genuino",
        ],
    },

    "liderazgo_sentido_humano": {
        "nombre": "Liderazgo con Sentido Humano",
        "subtitulo": "Liderazgo que genera ambientes apropiados para trabajar y equipos de alto desempeÃ±o",
        "enfoque": "Liderazgo Gerencial",
        "dirigido_a": "Toda la organizaciÃ³n",
        "duraciones": [4], "unidad": "horas",
        "descripcion": (
            "Conocer y entender la importancia de generar un ambiente apropiado para "
            "trabajar y fortalecer la gestiÃ³n efectiva de Capital Humano. Promover un "
            "cambio de comportamiento y de cultura generando un impacto positivo en el "
            "ambiente de trabajo y el rendimiento de los equipos. Trabaja clima "
            "organizacional, liderazgo humano, control y confianza, y cultura como "
            "ventaja competitiva."
        ),
        "para_quien": [
            "Toda la organizaciÃ³n",
            "LÃ­deres que buscan mejorar el clima laboral",
            "Organizaciones con retos de rotaciÃ³n o desmotivaciÃ³n",
        ],
        "resultados": [
            "Fomentar relaciones basadas en confianza",
            "Estimular el apoyo voluntario y espontÃ¡neo",
            "Orientar el liderazgo asertivo",
            "Cultura como ventaja competitiva sostenible",
        ],
    },

    "disena_tus_habitos": {
        "nombre": "DiseÃ±a Tus HÃ¡bitos",
        "subtitulo": "Habilidades para identificar y crear los hÃ¡bitos necesarios para alcanzar el Ã©xito y la felicidad en lo profesional y personal",
        "enfoque": "Liderazgo Personal",
        "dirigido_a": "Toda la organizaciÃ³n",
        "duraciones": [4], "unidad": "horas",
        "descripcion": (
            "Comprender cÃ³mo funcionan los hÃ¡bitos e identificar aquellos que impactan "
            "de manera desproporcionada en el desempeÃ±o, el compromiso y la felicidad. "
            "Aprender a utilizar la habilidad en lugar de la fuerza de voluntad para "
            "reemplazar hÃ¡bitos limitantes por hÃ¡bitos efectivos. MetodologÃ­a: "
            "Dejar atrÃ¡s el rezago Â· HÃ¡galo realizable Â· HÃ¡galo deseable Â· HÃ¡galo habitual."
        ),
        "para_quien": [
            "Toda la organizaciÃ³n",
            "Profesionales que buscan mayor efectividad y bienestar",
            "LÃ­deres que quieren instalar cambios duraderos",
        ],
        "resultados": [
            "Reconocer cuÃ¡ndo y quÃ© comportamientos cambiar",
            "Instalar nuevos hÃ¡bitos sin fuerza de voluntad",
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
            "Ayudar a los lÃ­deres a influir positivamente en el comportamiento de toda "
            "la organizaciÃ³n, motivar con eficacia y empoderar a otros. Trabaja: "
            "resultados claros y medibles, identificaciÃ³n de comportamientos necesarios, "
            "diagnÃ³stico real de la situaciÃ³n y las 6 fuentes de influencia "
            "(motivaciÃ³n y habilidad personal, social y estructural)."
        ),
        "para_quien": [
            "Agentes de cambio organizacional",
            "LÃ­deres que requieren influir sin autoridad formal",
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
        "dirigido_a": "Toda la organizaciÃ³n",
        "duraciones": [4], "unidad": "horas",
        "descripcion": (
            "Desarrollar en los participantes las habilidades para identificar y "
            "manejar adecuadamente las emociones en ellos mismos y en los demÃ¡s, "
            "en beneficio de la organizaciÃ³n. Abarca: introducciÃ³n a la IE, "
            "identificaciÃ³n de propias emociones y de emociones en otros, y manejo "
            "apropiado de las emociones con un laboratorio prÃ¡ctico y plan de acciÃ³n."
        ),
        "para_quien": [
            "Toda la organizaciÃ³n",
            "LÃ­deres en entornos de alta presiÃ³n o adversidad",
            "Equipos que buscan mejor colaboraciÃ³n y clima",
        ],
        "resultados": [
            "Mejora el autoconocimiento y toma de decisiones",
            "Mejora el rendimiento laboral y relaciones interpersonales",
            "Otorga capacidad de influencia y liderazgo",
            "Desarrolla proactividad y motivaciÃ³n intrÃ­nseca",
        ],
    },

    "liderazgo_siglo_xxi": {
        "nombre": "Liderazgo del Siglo XXI",
        "subtitulo": "ComprensiÃ³n clara de los fundamentos del liderazgo en el entorno empresarial actual",
        "enfoque": "Liderazgo Gerencial",
        "dirigido_a": "Toda la organizaciÃ³n",
        "duraciones": [4], "unidad": "horas",
        "descripcion": (
            "Capacitar a los participantes para desempeÃ±arse eficazmente en puestos "
            "de liderazgo, proporcionando una comprensiÃ³n clara de los conceptos "
            "fundamentales del liderazgo y cÃ³mo se aplican en un entorno empresarial. "
            "Cubre: estilos de liderazgo, habilidades del lÃ­der, liderazgo y motivaciÃ³n, "
            "liderazgo y trabajo en equipo."
        ),
        "para_quien": [
            "Toda la organizaciÃ³n",
            "LÃ­deres nuevos o en transiciÃ³n al rol",
            "Organizaciones que buscan una cultura de liderazgo sÃ³lida",
        ],
        "resultados": [
            "Fomentar relaciones basadas en confianza",
            "Estimular el apoyo voluntario y espontÃ¡neo",
            "ComunicaciÃ³n y visiÃ³n estratÃ©gica fortalecidas",
            "MotivaciÃ³n, trabajo en equipo y toma de decisiones",
        ],
    },

    "desarrollando_colaboradores": {
        "nombre": "Desarrollando, Reconociendo y Motivando a tus Colaboradores",
        "subtitulo": "Herramientas para maximizar la productividad, mejorar el clima laboral y reducir la rotaciÃ³n",
        "enfoque": "Liderazgo Gerencial",
        "dirigido_a": "Toda la organizaciÃ³n",
        "duraciones": [4], "unidad": "horas",
        "descripcion": (
            "Brindar a los lÃ­deres de equipo las herramientas y tÃ©cnicas necesarias "
            "para desarrollar, reconocer y motivar efectivamente a sus colaboradores. "
            "Abarca: desarrollo de colaboradores, reconocimiento y su impacto en la "
            "satisfacciÃ³n laboral, y motivaciÃ³n intrÃ­nseca y extrÃ­nseca con tÃ©cnicas "
            "para motivar individual y en equipo."
        ),
        "para_quien": [
            "Toda la organizaciÃ³n",
            "LÃ­deres con equipos a cargo",
            "Organizaciones con retos de retenciÃ³n y motivaciÃ³n",
        ],
        "resultados": [
            "Fomentar relaciones basadas en confianza",
            "Estimular el apoyo voluntario y espontÃ¡neo del equipo",
            "Orientar el liderazgo asertivo y empÃ¡tico",
            "ReducciÃ³n de rotaciÃ³n y aumento del compromiso",
        ],
    },

    # ââ CONFERENCIAS ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

    "conferencia_conversaciones": {
        "nombre": "Conferencia: Conversaciones Cruciales",
        "subtitulo": "Aprende a dirigir conversaciones difÃ­ciles e importantes de manera persuasiva",
        "enfoque": "ComunicaciÃ³n",
        "dirigido_a": "Toda la organizaciÃ³n",
        "duraciones": [50], "unidad": "minutos",
        "descripcion": (
            "Que el participante cobre consciencia de la importancia de aprender "
            "a dirigir 'conversaciones difÃ­ciles e importantes' de una manera "
            "persuasiva; fortaleciendo relaciones y logrando mejores resultados. "
            "Temas: primero trabaja en ti, aprende a exponer tu camino, observar y "
            "crear seguridad, y pasar a la acciÃ³n."
        ),
        "para_quien": [
            "Toda la organizaciÃ³n",
            "LÃ­deres que evitan conversaciones difÃ­ciles",
            "Equipos con tensiones no resueltas",
        ],
        "resultados": [
            "Logro de resultados en conversaciones clave",
            "Fortalecimiento de relaciones interpersonales",
            "Mejor doma de decisiones con claridad",
            "Mejora sustancial en la comunicaciÃ³n del equipo",
        ],
    },

    "conferencia_habitos": {
        "nombre": "Conferencia: El Poder de los HÃ¡bitos",
        "subtitulo": "CÃ³mo los hÃ¡bitos determinan los resultados en la vida personal y profesional",
        "enfoque": "Liderazgo Personal",
        "dirigido_a": "Toda la organizaciÃ³n",
        "duraciones": [50], "unidad": "minutos",
        "descripcion": (
            "Al finalizar esta conferencia, el 100% de los presentes sabrÃ¡ de quÃ© "
            "manera los hÃ¡bitos determinan los resultados que obtienen en la vida "
            "personal y profesional. Abarca: quÃ© son los hÃ¡bitos y cÃ³mo funcionan, "
            "casos de Ã©xito (Alcoa, Starbucks, Google), cultura organizacional y "
            "hÃ¡bitos, y el impacto en la organizaciÃ³n."
        ),
        "para_quien": [
            "Toda la organizaciÃ³n",
            "Equipos que buscan mejorar su desempeÃ±o colectivo",
            "LÃ­deres que quieren transformar la cultura del equipo",
        ],
        "resultados": [
            "Identificar los hÃ¡bitos que impactan el desempeÃ±o y la felicidad",
            "Adaptarse ante el cambio con mayor agilidad",
            "Crear nuevas rutinas que produzcan los resultados deseados",
            "Entender la cultura organizacional desde los hÃ¡bitos",
        ],
    },

    # ââ TEAMBUILDING ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

    "teambuilding": {
        "nombre": "Teambuilding con Points of You",
        "subtitulo": "Retiro experiencial de integraciÃ³n y liderazgo â Be the Captain of your Ship",
        "enfoque": "IntegraciÃ³n de equipos",
        "dirigido_a": "Toda la organizaciÃ³n",
        "duraciones": [6], "unidad": "horas",
        "descripcion": (
            "Fomentar la toma de conciencia sobre la importancia de ser un colaborador "
            "accountable, mejorar el entorno laboral incentivando comunicaciÃ³n abierta "
            "y sincera, e impulsar el espÃ­ritu de colaboraciÃ³n. Utiliza la metodologÃ­a "
            "Points of YouÂ® (herramienta certificada internacionalmente) con fotografÃ­as "
            "y palabras que generan reflexiÃ³n profunda y compromisos concretos. "
            "El desarrollo es completamente a la medida de cada equipo."
        ),
        "para_quien": [
            "Toda la organizaciÃ³n",
            "Equipos que necesitan reconectarse o estÃ¡n en formaciÃ³n",
            "LÃ­deres con sus equipos directos",
        ],
        "resultados": [
            "Mayor cohesiÃ³n, confianza y comunicaciÃ³n en el equipo",
            "Compromisos concretos de mejora individual y grupal",
            "Impulso al espÃ­ritu de colaboraciÃ³n y accountability",
            "EnergÃ­a renovada y sentido de propÃ³sito compartido",
        ],
    },

    # ââ PROGRAMA 0-100 ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

    "cero_a_cien": {
        "nombre": "Liderazgo 0-100",
        "subtitulo": "FormaciÃ³n para nuevos lÃ­deres y lÃ­deres en evoluciÃ³n Â· Base + EjecuciÃ³n (2 niveles)",
        "enfoque": "Desarrollo integral de liderazgo",
        "dirigido_a": "Nuevos lÃ­deres y lÃ­deres en evoluciÃ³n",
        "duraciones": [3, 6], "unidad": "meses",
        "descripcion": (
            "Un programa prÃ¡ctico para acelerar habilidades de liderazgo, comunicaciÃ³n "
            "y accountability con resultados medibles. Nivel 1 (0â50): Liderazgo Personal "
            "+ Interpersonal â autogestiÃ³n emocional, comunicaciÃ³n, delegaciÃ³n sin "
            "fricciÃ³n, feedback y conversaciones difÃ­ciles. Entregable: Plan 90 dÃ­as. "
            "Nivel 2 (50â100): Liderazgo Gerencial + Organizacional â accountability, "
            "influencia, coaching de desempeÃ±o, toma de decisiones y liderar el cambio. "
            "Entregable: Sistema de RendiciÃ³n de Cuentas. Incluye diagnÃ³stico pre/post "
            "y Reporte Ejecutivo para RRHH."
        ),
        "para_quien": [
            "Nuevos lÃ­deres que necesitan bases sÃ³lidas",
            "LÃ­deres en evoluciÃ³n hacia roles de mayor responsabilidad",
            "Organizaciones que invierten en su pipeline de liderazgo",
        ],
        "resultados": [
            "LÃ­deres que alinean, delegan y sostienen resultados",
            "Conversaciones difÃ­ciles manejadas con claridad y respeto",
            "Accountability sano. claridad + seguimiento + consecuencias",
            "Evidencia medible de avance (diagnÃ³stico pre/post por competencia)",
        ],
    },
}


# ââ PÃGINA 1: PORTADA âââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
def pagina_portada(c, data):
    prog    = data["programa"]
    cliente = data["cliente"]
    fmt     = data.get("formato", "Presencial")
    unidad  = prog.get("unidad", "horas")
    dur     = data.get("duracion")
    fecha   = data.get("fecha", datetime.date.today().strftime("%-d de %B de %Y"))

    # ââ Fondo navy completo
    c.setFillColor(NAVY)
    c.rect(0, 0, PW, PH, fill=1, stroke=0)

    # ââ Franja roja superior (como en FUNO)
    c.setFillColor(RED)
    c.rect(0, PH - 12, PW, 12, fill=1, stroke=0)

    # ââ Logo top-left (versiÃ³n blanca sobre navy)
    # Logo portada: versiÃ³n blanca sobre navy, altura 38pt
    logo(c, 40, PH - 14 - 38, h=38, dark_bg=True)

    # ââ "PROPUESTA COMERCIAL" con subrayado rojo
    y_label = PH * 0.545
    c.setFillColor(RED)
    c.setFont("DV-B", 10)
    label = "PROPUESTA COMERCIAL"
    c.drawString(40, y_label, label)
    c.setStrokeColor(RED)
    c.setLineWidth(1.5)
    c.line(40, y_label - 5, 40 + W(c, label, "DV-B", 10) + 90, y_label - 5)

    # ââ Nombre del programa (grande, blanco, bold â hasta 2 lÃ­neas)
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

    # ââ SubtÃ­tulo
    if prog.get("subtitulo"):
        c.setFillColor(HexColor('#9AACCC'))
        c.setFont("DV-I", 12)
        c.drawString(40, y_title - 4, prog["subtitulo"])
        y_title -= 24

    # ââ Tag duraciÃ³n Â· formato
    if dur:
        c.setFillColor(HexColor('#8899BB'))
        c.setFont("DV", 11)
        c.drawString(40, y_title - 8, f"{dur} {unidad}  Â·  {fmt}")

    # ââ Info cliente (zona inferior)
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

    # ââ Footer
    c.setStrokeColor(HexColor('#2A3F6A'))
    c.setLineWidth(0.5)
    c.line(40, 52, PW - 40, 52)
    c.setFillColor(HexColor('#8899BB'))
    c.setFont("DV", 8)
    c.drawString(40, 36,
        "Preparada por: Lut Parra  |  Coach Transformacional & Facilitador  |  "
        "lut@lutparra.com  |  55.6674.0475  |  www.lutparra.com")


# ââ PÃGINA 2: EL PROGRAMA âââââââââââââââââââââââââââââââââââââââââââââââââââââ
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

    # ââ PÃ¡rrafo introductorio (contexto)
    contexto = data.get("contexto_cliente", "")
    if contexto:
        c.setFillColor(GRAY_MED)
        c.setFont("DV-I", 10)
        for ln in wrap(contexto, 92):
            c.drawString(40, y, ln)
            y -= 14
        y -= 8

    # ââ DescripciÃ³n del programa (caja con borde rojo izquierdo)
    y = section_header(c, 40, y, "DESCRIPCIÃN DEL PROGRAMA")
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

    # ââ Dos columnas: PARA QUIÃN + RESULTADOS ESPERADOS
    cx1 = 40
    cx2 = PW / 2 + 8
    cw  = PW / 2 - 52

    y_sec = y
    section_header(c, cx1, y_sec, "PARA QUIÃN ES")
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

    # ââ Nota de formato (opcional)
    nota = data.get("nota_formato")
    if nota:
        yn = min(yl, yr) - 18
        c.setFillColor(GRAY_MED)
        c.setFont("DV-I", 8.5)
        for ln in wrap(f"* {nota}", 92):
            c.drawString(40, yn, ln)
            yn -= 12

    page_footer_bar(c)


# ââ PÃGINA 3: INVERSIÃN âââââââââââââââââââââââââââââââââââââââââââââââââââââââ
def pagina_inversion(c, data):
    c.showPage()
    prog    = data["programa"]
    cliente = data["cliente"]
    inv     = data.get("inversion", {})
    unidad  = prog.get("unidad", "horas")
    dur     = data.get("duracion")
    fmt     = data.get("formato", "Presencial")

    crumbs = [
        "Propuesta EconÃ³mica",
        "InversiÃ³n",
        "Condiciones",
        cliente.get("empresa", ""),
    ]
    crumbs = [x for x in crumbs if x]
    page_header_bar(c, crumbs, active=0)

    y = PH - 76

    # ââ INVERSIÃN ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    y = section_header(c, 40, y, "INVERSIÃN")

    # Columnas de tabla
    cx = [40, 250, 348, 442]   # x de: soluciÃ³n, sesiones, participantes, inversiÃ³n
    cw_total = PW - 80         # ancho total tabla
    row_h    = 36

    # â Header de tabla (navy)
    c.setFillColor(NAVY_HEADER)
    c.rect(40, y - row_h + 10, cw_total, row_h, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("DV-B", 8.5)
    for txt, xi in zip(["SOLUCIÃN", "SESIONES", "PARTICIPANTES", "INVERSIÃN"], cx):
        c.drawString(xi + 8, y - 8, txt)
    y -= row_h

    # â Fila del programa
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

    sesiones = inv.get("sesiones", f"{dur} {unidad}" if dur else "â")
    c.setFillColor(GRAY_DARK)
    c.setFont("DV", 9.5)
    c.drawCentredString(cx[1] + 44, y - 12, str(sesiones))
    c.drawCentredString(cx[2] + 44, y - 12, inv.get("participantes", "â"))
    c.setFillColor(NAVY)
    c.setFont("DV-B", 10)
    c.drawCentredString(cx[3] + 55, y - 12, inv.get("total", "â"))
    y -= row_h

    # â Fila TOTAL
    c.setFillColor(NAVY_HEADER)
    c.rect(40, y - 26 + 10, cw_total, 26, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("DV-B", 10)
    c.drawString(52, y - 7, "TOTAL DEL PROGRAMA")
    total_iva = inv.get("total_iva", (inv.get("total", "â") + " + I.V.A."))
    c.setFont("DV-B", 13)
    c.drawRightString(PW - 48, y - 9, total_iva)
    y -= 26 + 14

    # ââ CONDICIONES COMERCIALES ââââââââââââââââââââââââââââââââââââââââââââââ
    y = section_header(c, 40, y, "CONDICIONES COMERCIALES")

    condiciones = [
        ("Precios:",     "Expresados en pesos mexicanos. No incluyen IVA."),
        ("Pago:",        inv.get("modalidad_pago", "Pago de contado.")),
        ("Vigencia:",    "30 dÃ­as naturales a partir de la fecha de emisiÃ³n."),
        ("Modalidad:",   f"{fmt}. En caso necesario, sesiones virtuales por Zoom sin costo adicional."),
        ("Cancelaciones:", "Sesiones canceladas con menos de 24 hrs de anticipaciÃ³n se consideran impartidas."),
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

    # ââ SIGUIENTE PASO âââââââââââââââââââââââââââââââââââââââââââââââââââââââ
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


# ââ FUNCIÃN PRINCIPAL âââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
def generar_pdf(data: dict, ruta_salida: str = "propuesta.pdf") -> str:
    """
    Genera un PDF de propuesta de 3 pÃ¡ginas.

    Campos de 'data':
        programa_key      (str)  : clave del CATALOGO
        duracion          (int)  : duraciÃ³n elegida (4, 8â¦)
        formato           (str)  : "Presencial" | "Virtual" | "Presencial / Virtual"
        cliente           (dict) : {
                                     "contacto": "Nombre del contacto",
                                     "area":     "Ãrea / Departamento",
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
        nota_formato      (str)  : nota logÃ­stica opcional
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
    c.setTitle(f"Propuesta â {data['programa']['nombre']} â "
               f"{data['cliente'].get('empresa', '')}")
    c.setAuthor("Lut Parra â Leadership Mentoring")
    c.setSubject("Propuesta Comercial")

    pagina_portada(c, data)
    pagina_programa(c, data)
    pagina_inversion(c, data)
    c.save()
    print(f"â  {ruta_salida}")
    return ruta_salida


# ââ EJEMPLO âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
if __name__ == "__main__":
    datos = {
        "programa_key": "speak_up",
        "duracion":     4,
        "formato":      "Presencial",
        "cliente": {
            "contacto": "Lic. Patricia Morales",
            "area":     "Recursos Humanos",
            "empresa":  "Grupo InnovaciÃ³n MX",
        },
        "contexto_cliente": (
            "El equipo directivo de Grupo InnovaciÃ³n MX enfrenta retos de comunicaciÃ³n "
            "interna que generan fricciones en la toma de decisiones y reuniones "
            "poco efectivas. La organizaciÃ³n busca que sus lÃ­deres comuniquen con "
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
            "Confirmar fecha de imparticiÃ³n",
            "Firmar carta de acuerdo",
        ],
        "fecha": "17 de marzo de 2026",
    }

    out = "/sessions/eager-clever-pasteur/mnt/outputs/Propuesta_SpeakUp_v2.pdf"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    generar_pdf(datos, out)
