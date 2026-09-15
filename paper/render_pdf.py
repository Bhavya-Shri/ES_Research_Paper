"""Render the IEEE draft to PDF without a TeX installation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "_pdfdeps"))

from fpdf import FPDF  # noqa: E402
from fpdf.enums import XPos, YPos  # noqa: E402

FIGS = ROOT / "figures"
OUT = ROOT / "Frequency_Adaptive_Audio_Limiting.pdf"
FONTS = Path(r"C:\Windows\Fonts")


class IEEEPaper(FPDF):
    def __init__(self) -> None:
        super().__init__(format="letter", unit="mm")
        self.set_auto_page_break(auto=True, margin=16)
        self.col = 0
        self.col_w = 90.5
        self.gutter = 5.0
        self.lm = 15.0
        self.y0 = 18.0
        self.in_cols = False
        self._add_fonts()

    def _add_fonts(self) -> None:
        self.add_font("TN", "", str(FONTS / "times.ttf"))
        self.add_font("TN", "B", str(FONTS / "timesbd.ttf"))
        self.add_font("TN", "I", str(FONTS / "timesi.ttf"))
        self.add_font("TN", "BI", str(FONTS / "timesbi.ttf"))

    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("TN", "I", 8)
        self.set_text_color(60, 60, 60)
        self.set_xy(15, 8)
        self.cell(0, 4, "IEEE Student Research Paper, VIT Chennai", align="L")
        self.set_xy(15, 12)
        self.cell(0, 4, "Murthy and Shri: Frequency-Adaptive Audio Limiting", align="R")
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.2)
        self.line(15, 16.5, 200.9, 16.5)
        self.set_text_color(0, 0, 0)
        if self.in_cols:
            self.set_col(self.col)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("TN", "", 8)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, str(self.page_no()), align="C")

    def set_col(self, col: int) -> None:
        self.col = col
        x = self.lm + col * (self.col_w + self.gutter)
        self.set_left_margin(x)
        self.set_right_margin(215.9 - x - self.col_w)
        self.set_x(x)

    def accept_page_break(self) -> bool:
        if not self.in_cols:
            return True
        if self.col == 0:
            self.set_col(1)
            self.set_y(self.y0)
            return False
        self.set_col(0)
        return True

    def start_columns(self, y: float | None = None) -> None:
        self.in_cols = True
        self.y0 = self.get_y() if y is None else y
        self.set_col(0)
        self.set_y(self.y0)

    def full_width(self) -> None:
        self.in_cols = False
        self.col = 0
        self.set_left_margin(self.lm)
        self.set_right_margin(self.lm)
        self.set_x(self.lm)

    def ensure(self, h: float) -> None:
        if self.get_y() + h < self.h - 16:
            return
        if self.in_cols and self.col == 0:
            self.set_col(1)
            self.set_y(self.y0)
        else:
            self.add_page()
            if self.in_cols:
                self.y0 = 20.0
                self.set_col(0)
                self.set_y(self.y0)

    def p(self, text: str, size: float = 9.5, style: str = "", first_indent: float = 4.0, leading: float = 3.9) -> None:
        self.set_font("TN", style, size)
        self.ensure(12)
        x = self.lm + self.col * (self.col_w + self.gutter) if self.in_cols else self.lm
        w = self.col_w if self.in_cols else 215.9 - 2 * self.lm
        self.set_x(x + first_indent)
        self.multi_cell(w - first_indent, leading, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="J")
        self.ln(0.6)

    def p_plain(self, text: str, size: float = 9.5, style: str = "", leading: float = 3.9, align: str = "J") -> None:
        self.set_font("TN", style, size)
        self.ensure(10)
        w = self.col_w if self.in_cols else 215.9 - 2 * self.lm
        self.multi_cell(w, leading, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align=align)
        self.ln(0.4)

    def h1(self, n: str, title: str) -> None:
        self.ln(2.2)
        self.ensure(10)
        self.set_font("TN", "B", 11)
        label = f"{n}. {title.upper()}" if n else title.upper()
        self.p_plain(label, size=11, style="B", leading=5, align="L")
        self.ln(0.5)

    def h2(self, title: str) -> None:
        self.ln(1.2)
        self.ensure(8)
        self.set_font("TN", "B", 10)
        self.p_plain(f"A. {title}" if False else title, size=10, style="B", leading=4.4, align="L")

    def equation(self, text: str, number: str) -> None:
        self.ensure(8)
        self.ln(1.2)
        self.set_font("TN", "I", 9.5)
        w = self.col_w if self.in_cols else 215.9 - 2 * self.lm
        self.cell(w - 12, 5, text, align="C")
        self.set_font("TN", "", 9)
        self.cell(12, 5, f"({number})", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1.2)

    def caption(self, text: str) -> None:
        self.set_font("TN", "", 8)
        w = self.col_w if self.in_cols else 215.9 - 2 * self.lm
        self.multi_cell(w, 3.3, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="J")
        self.ln(1.5)

    def figure(self, path: Path, cap: str, wide: bool = False, max_h: float = 62) -> None:
        if wide:
            was = self.in_cols
            col = self.col
            y_keep = self.get_y()
            self.full_width()
            if was and col == 1:
                self.add_page()
            elif self.get_y() > 200:
                self.add_page()
            self.ln(1)
            img_w = 185.9
            self.image(str(path), x=15, w=img_w)
            self.ln(1)
            self.caption(cap)
            self.start_columns(self.get_y() + 1 if was else None)
            if was:
                self.y0 = self.get_y()
                self.set_col(0)
                self.set_y(self.y0)
            return
        self.ensure(max_h + 14)
        w = self.col_w
        self.ln(1)
        self.image(str(path), w=w)
        self.ln(0.8)
        self.caption(cap)


def draw_block_diagram(path: Path) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    fig, ax = plt.subplots(figsize=(10.2, 2.35))
    ax.set_xlim(0, 20.4)
    ax.set_ylim(0, 4.7)
    ax.axis("off")

    def box(x, y, w, h, text):
        ax.add_patch(
            FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.08",
                           facecolor="white", edgecolor="black", linewidth=1.0)
        )
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=7.5)

    box(0.15, 1.75, 1.5, 1.15, "x[n]")
    box(2.05, 1.75, 2.7, 1.15, "LR4 3-way\n300 Hz / 4 kHz")
    box(5.55, 3.15, 3.7, 1.3, "Low: −12 dB shelf\n+ NLD harmonics\n80–400 Hz")
    box(5.55, 1.7, 3.7, 1.2, "Mid: A-weighted\ncompressor")
    box(5.55, 0.2, 3.7, 1.2, "High: envelope\ngain")
    box(10.1, 1.75, 1.6, 1.15, "Sum")
    box(12.15, 1.7, 2.2, 1.25, "Ceiling\n−1 dBFS")
    box(14.8, 1.75, 1.5, 1.15, "y[n]")
    ax.annotate("", xy=(2.05, 2.32), xytext=(1.65, 2.32), arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.annotate("", xy=(5.55, 3.8), xytext=(4.75, 2.7), arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.annotate("", xy=(5.55, 2.3), xytext=(4.75, 2.32), arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.annotate("", xy=(5.55, 0.8), xytext=(4.75, 1.9), arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.annotate("", xy=(10.1, 2.7), xytext=(9.25, 3.7), arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.annotate("", xy=(10.1, 2.32), xytext=(9.25, 2.3), arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.annotate("", xy=(10.1, 1.95), xytext=(9.25, 0.85), arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.annotate("", xy=(12.15, 2.32), xytext=(11.7, 2.32), arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.annotate("", xy=(14.8, 2.32), xytext=(14.35, 2.32), arrowprops=dict(arrowstyle="->", lw=1.1))
    fig.tight_layout(pad=0.15)
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def table_lines(pdf: IEEEPaper, headers: list[str], rows: list[list[str]], col_fracs: list[float]) -> None:
    pdf.ensure(8 + 3.3 * (len(rows) + 2))
    w = pdf.col_w if pdf.in_cols else 185.9
    widths = [f * w for f in col_fracs]
    pdf.set_font("TN", "B", 7.2)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.25)
    y = pdf.get_y()
    x0 = pdf.get_x()
    pdf.line(x0, y, x0 + w, y)
    pdf.ln(0.6)
    for h, cw in zip(headers, widths):
        pdf.cell(cw, 4.0, h, align="C")
    pdf.ln(4.0)
    pdf.line(x0, pdf.get_y(), x0 + w, pdf.get_y())
    pdf.set_font("TN", "", 7.0)
    for row in rows:
        pdf.ensure(4.2)
        x0 = pdf.get_x()
        for val, cw in zip(row, widths):
            pdf.cell(cw, 3.6, val, align="C" if val[:1] in "+-" or val.replace(".", "", 1).isdigit() else "L")
        pdf.ln(3.6)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + w, pdf.get_y())
    pdf.ln(1.6)


def build() -> Path:
    block = FIGS / "block_diagram.png"
    draw_block_diagram(block)

    pdf = IEEEPaper()
    pdf.set_title("Frequency-Adaptive Audio Limiting for Reduced Acoustic Exposure and Loudness Preservation")
    pdf.set_author("Yashwini Krishna Murthy and Bhavya Shri")
    pdf.add_page()

    # Title block
    pdf.set_left_margin(18)
    pdf.set_right_margin(18)
    pdf.set_x(18)
    pdf.set_font("TN", "B", 16)
    pdf.set_y(22)
    pdf.multi_cell(179.9, 7.0, "Frequency-Adaptive Audio Limiting for Reduced Acoustic Exposure and Loudness Preservation", align="C")
    pdf.ln(3)
    pdf.set_x(18)
    pdf.set_font("TN", "", 11)
    pdf.multi_cell(179.9, 5.2, "Yashwini Krishna Murthy and Bhavya Shri", align="C")
    pdf.set_x(18)
    pdf.set_font("TN", "I", 9.5)
    pdf.multi_cell(179.9, 4.6, "Department of Computer Science and Engineering", align="C")
    pdf.set_x(18)
    pdf.multi_cell(179.9, 4.6, "Vellore Institute of Technology, Chennai, India", align="C")
    pdf.set_x(18)
    pdf.set_font("TN", "", 8.5)
    pdf.multi_cell(179.9, 4.2, "yashwini.krishna2024@vitstudent.ac.in", align="C")
    pdf.ln(3)

    # Abstract
    pdf.set_left_margin(18)
    pdf.set_right_margin(18)
    pdf.set_x(18)
    pdf.set_font("TN", "BI", 9.5)
    pdf.cell(22, 5, "Abstract—", new_x=XPos.END, new_y=YPos.TOP)
    pdf.set_font("TN", "", 9)
    abstract = (
        "Conventional personal-audio limiters reduce listening level by applying one gain to every frequency. "
        "A-weighted exposure and programme loudness do not weight the spectrum in the same way, so it is reasonable "
        "to ask whether cutting some bands more than others can lower an exposure metric at the same loudness. This "
        "paper tests that question with a three-band digital processor: a complementary Linkwitz–Riley split at 300 Hz "
        "and 4 kHz, a low-band shelf of −12 dB with harmonic fill from 80 to 400 Hz, an A-weighted mid-band compressor, "
        "and a mild high-band envelope gain. On 20 clips (16 Freesound recordings and four synthetic signals) we compare "
        "the processor with frequency-flat gain under two matching rules. At matched BS.1770 loudness (LUFS), the proposed "
        "system’s digital A-weighted LAeq proxy is on average 1.17 dB higher than flat gain. The matched-loudness exposure "
        "hypothesis is therefore not supported. The gap is largest on bass-heavy material (about +1.6 to +2.7 dB on real "
        "bass loops). Vocals, speech, and short transients are essentially tied. The reason is straightforward: A-weighting "
        "already discards most energy near 40 Hz, so removing sub-bass lowers LUFS much more than LAeq, and flat gain must "
        "then cut the midrange to match loudness. At matched LAeq the proposed output is correspondingly quieter. All levels "
        "in this study are digital-domain proxies, not calibrated ear-level SPL."
    )
    pdf.multi_cell(157.9, 3.85, abstract, align="J")
    pdf.ln(2)
    pdf.set_x(18)
    pdf.set_font("TN", "BI", 9)
    pdf.cell(26, 4, "Index Terms—", new_x=XPos.END, new_y=YPos.TOP)
    pdf.set_font("TN", "I", 9)
    pdf.multi_cell(153.9, 3.85, "Audio signal processing, A-weighting, dynamic range compression, frequency-selective limiting, loudness, multiband processing, virtual bass.")
    pdf.ln(3)

    pdf.start_columns()

    pdf.h1("I", "Introduction")
    pdf.p(
        "Personal listening devices can deliver high playback levels for long periods. The World Health Organization "
        "and ITU-T Recommendation H.870 treat this as a cumulative A-weighted sound-dose problem and give device makers "
        "a framework for tracking exposure [1]–[4]. H.870 specifies how much dose to allow. It does not specify a "
        "signal-processing algorithm that should be used when the limit is reached."
    )
    pdf.p(
        "The usual engineering response is a broadband limiter or automatic gain control [5]: when an exposure estimate "
        "exceeds a threshold, apply one scalar G < 1 to the whole signal. That is easy to implement and it does reduce "
        "an A-weighted metric. It is also crude. Equal-loudness contours [6], [7] show that hearing sensitivity is strongly "
        "frequency-dependent, so a flat cut changes bass, midrange, and treble by different perceptual amounts. Multiband "
        "compression and virtual-bass methods already exist as separate tools. What is missing is a direct test: if those "
        "tools are combined into an exposure-oriented limiter, do they beat “turn everything down” when exposure or loudness is matched?"
    )
    pdf.p("That is the question of this paper. We ask:")
    pdf.set_font("TN", "I", 9.5)
    pdf.p_plain(
        "Can frequency-selective gain allocation reduce an A-weighted digital exposure proxy more than conventional "
        "broadband attenuation at matched loudness, and preserve quality better at matched exposure?",
        style="I",
        leading=4.0,
    )
    pdf.p(
        "We implement three systems on the same audio: the original clip, frequency-flat gain, and a three-band processor "
        "described in Section III. We then match either LUFS or the digital LAeq proxy and compare the other quantity. "
        "The ingredients are not new. The comparison is the contribution."
    )
    pdf.p(
        "The result is mixed, and on the main hypothesis it is negative. At matched LUFS the proposed processor has a "
        "higher digital LAeq proxy than flat gain, by 1.17 dB on average over 20 clips. Bass-heavy programme accounts for "
        "almost all of the difference. Speech, vocals, and short transients sit near a tie. Section VI shows why: the "
        "processor spends its budget on a band that A-weighting barely counts."
    )
    pdf.p(
        "The rest of the paper is organised as follows. Section II reviews related methods and states the gap. Section III "
        "describes the processor as a design heuristic, not as a numerical solver. Section IV records implementation and "
        "verification. Section V defines the experiment. Section VI reports the 20-clip comparison. Section VII collects "
        "limitations in one place. Section VIII concludes."
    )

    pdf.h1("II", "Related Work")
    pdf.h2("A. Exposure control")
    pdf.p(
        "H.870 defines an A-weighted sound-allowance model and discusses the difficulty of mapping a digital signal to "
        "ear-level pressure, which depends on transducer sensitivity and volume setting [1]. Device-side responses are "
        "typically volume caps, dose meters, or broadband automatic gain reduction [3], [8]. These systems manage level. "
        "They do not allocate that level across frequency in order to keep loudness."
    )
    pdf.h2("B. Dynamic range control")
    pdf.p(
        "Digital compressors and limiters are well understood [5], [9]. Multiband designs apply a separate envelope in "
        "each band and are usually tuned for tonal balance, broadcast loudness, or hearing-aid audibility—not for an "
        "exposure-versus-loudness comparison against a flat baseline. ITU-R BS.1770 is the standard programme-loudness "
        "meter used here as a loudness stand-in [10]."
    )
    pdf.h2("C. Loudness perception")
    pdf.p(
        "ISO 226 equal-loudness contours [7] and excitation-pattern models [11]–[14] explain why a flat gain change is "
        "not perceptually flat. This paper uses that fact as motivation. It does not implement a Zwicker or Moore–Glasberg "
        "loudness model. Integrated LUFS is the operational loudness measure."
    )
    pdf.h2("D. Virtual bass")
    pdf.p(
        "When a harmonic complex loses its fundamental, listeners can still hear a pitch at f0 [15]–[17]. Loudspeaker "
        "virtual-bass systems exploit that residue pitch by synthesising harmonics when the driver cannot reproduce "
        "sub-bass [18]–[20]. We use the same mechanism in the opposite direction: attenuate physical sub-bass and add "
        "harmonics in 80–400 Hz. Residue pitch is not the same thing as preserved bass loudness, and we do not treat it as such."
    )
    pdf.h2("E. Gap")
    pdf.p(
        "Table I summarises the pieces. Exposure managers, multiband compressors, and virtual-bass processors exist "
        "separately. There is little published evidence that combining them outperforms broadband attenuation when either "
        "an exposure proxy or loudness is held constant. That matched comparison is what this study provides."
    )
    pdf.set_font("TN", "B", 8)
    pdf.p_plain("TABLE I", size=8, style="B", align="C", leading=3.4)
    pdf.set_font("TN", "I", 7.5)
    pdf.p_plain("Related methods versus this study. “Matched test” means a comparison at equal exposure or equal loudness.", size=7.5, style="I", align="C", leading=3.2)
    table_lines(
        pdf,
        ["Approach", "Exp.", "Freq.", "Loud.", "Bass", "Match"],
        [
            ["H.870 dose limit [1]", "Yes", "No", "No", "No", "No"],
            ["Broadband limiter [5]", "Yes", "No", "Ind.", "No", "Base"],
            ["Multiband DRC [9]", "Part", "Yes", "Part", "Rare", "Rare"],
            ["Virtual bass [19]", "No", "Yes", "Bass", "Yes", "No"],
            ["This work", "Proxy", "Yes", "Yes", "Yes", "Yes"],
        ],
        [0.34, 0.13, 0.13, 0.13, 0.13, 0.14],
    )

    pdf.h1("III", "Proposed Method")
    pdf.h2("A. Design objective")
    pdf.p(
        "Let x[n] be the input. A conventional limiter applies one gain"
    )
    pdf.equation("y[n] = G  x[n],    G < 1.", "1")
    pdf.p(
        "We want a frequency-dependent alternative that, for a given loudness, yields a lower A-weighted digital exposure "
        "proxy than (1). Preferentially cutting energy that contributes more to A-weighting than to loudness is the intended "
        "trade-off. Preferentially cutting energy that A-weighting already ignores is the failure mode."
    )
    pdf.p(
        "This is a design objective, not a solved optimisation. We do not run a numerical solver for a constrained cost. "
        "The implementation is a fixed three-band heuristic built toward that trade-off."
    )
    pdf.h2("B. Architecture")
    pdf.p(
        "The signal is split at 300 Hz and 4 kHz, processed per band, summed, and passed through a fixed-ceiling peak limiter (Fig. 1):"
    )
    pdf.equation("y[n] = yL[n] + yM[n] + yH[n].", "2")
    pdf.p(
        "The low band carries sub-bass, the mid band most speech and musical energy, and the high band many transients. "
        "Those cutoffs were chosen for the prototype. They were not optimised by a listening-test search."
    )
    pdf.figure(
        block,
        "Fig. 1. Three-band processor. The crossover is complementary. Per-band processing is a fixed heuristic, not a numerical optimiser.",
        wide=True,
        max_h=40,
    )
    pdf.h2("C. Low band")
    pdf.p(
        "A low shelf of β = 10^(−12/20) ≈ 0.25 (−12 dB) is applied around 100 Hz. Harmonics are generated from the isolated "
        "sub-bass xsub by a memoryless nonlinearity"
    )
    pdf.equation("xNLD[n] = a2 xsub²[n] + a3 xsub³[n]", "3")
    pdf.p(
        "with a2 = 0.8 and a3 = 0.35, then band-pass filtered to 80–400 Hz and mixed back. An earlier 160–300 Hz harmonic "
        "window missed 2f0 and 3f0 for fundamentals near 40 Hz. The wider window is used so that a 40 Hz tone actually "
        "produces energy at 80 and 120 Hz (Fig. 3). Harmonic injection supports a residue pitch cue. It is not evidence that "
        "bass loudness is preserved."
    )
    pdf.h2("D. Mid band")
    pdf.p("The mid band is compressed from an A-weighted envelope. If e[n] is that envelope and")
    pdf.equation("L[n] = 20 log10(e[n]+ε) + Lref,", "4")
    pdf.p(
        "gain reduction of ratio R = 4 is applied only when L[n] exceeds a target of 78 (the same uncalibrated digital "
        "offset Lref = 94 used in the exposure proxy):"
    )
    pdf.equation("gM[n] = 10^[ −(1−1/R) max(L[n]−Ltgt, 0) / 20 ].", "5")
    pdf.p(
        "Attack and release are 5 ms and 50 ms. The A-weighting filter is the IEC 61672 analog prototype [21], bilinearly "
        "transformed at 48 kHz and normalised to 0 dB at 1 kHz. Inside 300 Hz–4 kHz, where this detector is used, the digital "
        "magnitude tracks the analytic curve to well under 0.2 dB. Above about 8 kHz the bilinear transform warps the "
        "response; that region is not used for mid-band detection (Fig. 4)."
    )
    pdf.h2("E. High band")
    pdf.p("Content above 4 kHz is scaled by a one-pole envelope E[n]:")
    pdf.equation("yH[n] = xH[n] / (1 + γ max(0, E[n] − TH)),", "6")
    pdf.p(
        "with γ = 0.5 and TH = −12 dBFS. This is transient-aware gain control. It is not a validated perceptual model."
    )
    pdf.h2("F. Crossover reconstruction")
    pdf.p(
        "Independent Butterworth low/band/high splits are not magnitude-complementary and can boost the sum near the cutoffs. "
        "The processor uses cascaded fourth-order Linkwitz–Riley sections [22], with allpass compensation of the low path at "
        "the upper split, so the three bands sum to an allpass. Fig. 2 compares reconstruction with the older independent-Butterworth "
        "bank: the Linkwitz–Riley sum sits at 0 dB, while the older bank peaked at the 300 Hz and 4 kHz boundaries and raised "
        "a quiet 440 Hz tone by 19.7%."
    )
    pdf.figure(
        FIGS / "crossover_reconstruction.png",
        "Fig. 2. Crossover reconstruction. Linkwitz–Riley 3-way sum (this work) versus independent Butterworth splits used in an earlier draft. Dashed lines mark ±0.5 dB.",
    )
    pdf.figure(
        FIGS / "harmonic_coverage.png",
        "Fig. 3. Low-band output spectra for 40, 50, 60, and 80 Hz tones after the −12 dB shelf and 80–400 Hz harmonic path. Second and third harmonics are present for a 40 Hz fundamental.",
    )
    pdf.figure(
        FIGS / "aweighting_response.png",
        "Fig. 4. Digital A-weighting IIR (normalised at 1 kHz) versus the IEC analytic curve. The mid-band detector uses 300 Hz–4 kHz. A-weighting at 40 Hz is about −35 dB, which is the mechanism behind the main result.",
    )

    pdf.h1("IV", "Implementation")
    pdf.p(
        "The reference system is offline Python (numpy/scipy) at fs = 48 kHz. All filters are causal: second-order sections "
        "with state carried across blocks. The processor is hop-based (256 samples) and streamable. Processing a 2 s test "
        "signal in 240-sample blocks versus in one call gave a maximum absolute sample difference of 0.0. The output stage "
        "is a peak ceiling at −1 dBFS; it never renormalises a quiet block back toward full scale."
    )
    pdf.p(
        "Default parameters are listed in Table II. Source code is the exposure_dsp package in the project repository. "
        "Listings are omitted from the paper."
    )
    pdf.set_font("TN", "B", 8)
    pdf.p_plain("TABLE II", size=8, style="B", align="C", leading=3.4)
    pdf.set_font("TN", "I", 7.5)
    pdf.p_plain("Default processor parameters.", size=7.5, style="I", align="C", leading=3.2)
    table_lines(
        pdf,
        ["Parameter", "Value"],
        [
            ["Sample rate", "48 kHz"],
            ["Crossover", "LR4, 300 Hz / 4 kHz"],
            ["Sub-bass shelf β", "−12 dB near 100 Hz"],
            ["Harmonic band", "80–400 Hz (a2=0.8, a3=0.35)"],
            ["Mid target / ratio", "78 / 4:1"],
            ["Mid attack / release", "5 ms / 50 ms"],
            ["High threshold / γ", "−12 dBFS / 0.5"],
            ["Output ceiling", "−1 dBFS"],
        ],
        [0.48, 0.52],
    )

    pdf.h1("V", "Experimental Setup")
    pdf.h2("A. Systems")
    pdf.p("Every clip is processed by three systems:")
    pdf.p("1) Original: no processing.", first_indent=0)
    pdf.p("2) Frequency-flat gain: one scalar G applied to the whole waveform. This is the baseline that answers “turn everything down.”", first_indent=0)
    pdf.p("3) Proposed: the three-band processor of Section III at the Table II defaults.", first_indent=0)
    pdf.p(
        "A secondary A-weighted broadband compressor was also matched by searching its threshold. On many clips it never "
        "engaged, because the uncalibrated proxy never crossed the default target. Idle compression is not a fair “turn it "
        "down” baseline, so the reported comparison uses static flat gain."
    )
    pdf.h2("B. Matching")
    pdf.p("Two matching rules are applied, each to within a few hundredths of a dB:")
    pdf.p("Matched exposure: G is chosen so the flat-gain output has the same digital LAeq proxy as the proposed output.", first_indent=0)
    pdf.p("Matched loudness: G is chosen so the flat-gain output has the same integrated LUFS [10] as the proposed output (pyloudnorm).", first_indent=0)
    pdf.p(
        "Because flat gain is frequency-independent, both meters move by approximately 20 log10 G. The two matching rules "
        "are therefore two views of one difference, not two independent experiments. The interesting content is the sign of "
        "that difference and which material produces it."
    )
    pdf.h2("C. Metrics")
    pdf.p("The digital exposure proxy is A-weighted RMS plus an arbitrary offset,")
    pdf.equation("LAeq^proxy = 20 log10 RMS{wA * x} + 94.", "7")
    pdf.p(
        "The offset 94 maps digital full scale to a convenient number for development. It is not a calibration to pascals "
        "or to an ear simulator. Loudness is integrated LUFS. Spectral change versus the original is log-spectral distance "
        "(LSD) over Welch power estimates; LSD is an objective distance, not a listening-test score."
    )
    pdf.h2("D. Material")
    pdf.p(
        "The corpus has n = 20 clips at 48 kHz mono: 16 Creative Commons Freesound recordings (bass loops, drum loops, choir, "
        "solo vocal, speech, cymbals) and four built-in synthetic programmes (bass-heavy, speech-like, transient, mixed). "
        "Freesound IDs: 165523, 179270, 189635, 269906, 380303, 431525, 479941, 529808, 541260, 627643, 628213, 629137, "
        "629139, 657761, 735157, 739037. Synthetics are included for completeness and labelled as such. The conclusions below "
        "are also stated for the 16 real recordings alone."
    )
    pdf.h2("E. Hypotheses")
    pdf.p("H2 (matched loudness): at equal LUFS, the proposed LAeq proxy is lower than flat gain.", first_indent=0)
    pdf.p("H1 (matched exposure): at equal LAeq proxy, the proposed output is louder (higher LUFS) and/or closer to the original in LSD.", first_indent=0)
    pdf.h2("F. Listening notes")
    pdf.p(
        "No formal MUSHRA or PEAQ test was run, and no listener scores are reported. Processed files are available as "
        "*_proposed.wav versus *_gain_matched_loudness.wav (equal LUFS) and *_gain_matched_exposure.wav (equal proxy). A later "
        "test should lock playback volume, randomise order, and collect ratings for overall quality, bass, clarity, and "
        "loudness. Until that is done, quality claims stay with LUFS and LSD."
    )

    pdf.h1("VI", "Results")
    pdf.h2("A. Matched loudness: exposure proxy")
    pdf.p(
        "Fig. 5 plots, for each clip, the proposed digital LAeq proxy minus the flat-gain proxy at matched LUFS. Positive "
        "bars mean the proposed system is worse on the quantity it was supposed to reduce."
    )
    pdf.figure(
        FIGS / "matched_loudness_delta.png",
        "Fig. 5. Digital LAeq proxy at matched LUFS: proposed minus frequency-flat gain. Positive values mean the proposed processor has the higher exposure proxy. Bass loops (red) drive the mean; speech, vocals, and short transients sit near zero.",
        wide=True,
        max_h=70,
    )
    pdf.p(
        "The mean over 20 clips is +1.17 dB (median +0.61 dB). On the 16 Freesound recordings alone the mean is +0.92 dB. "
        "Twelve clips are more than 0.05 dB worse for the proposed system, six are within 0.05 dB, and two are slightly better "
        "(a female vocal at −0.07 dB and mixed command speech at −0.12 dB). H2 is not supported."
    )
    pdf.p(
        "The failure is concentrated in bass. The six real bass and drum-loop clips sit between +1.59 and +2.67 dB (mean "
        "+1.98 dB). Speech, choir, solo vocal, and cymbal clips as a group average +0.28 dB. Synthetic bass and mixed "
        "programmes are more extreme (+4.91 and +3.87 dB) because they were built with strong 40–50 Hz components; they inflate "
        "the overall mean but they do not create the finding. Real bass loops already go the same way. Per-clip numbers are in Table III."
    )

    # Per-clip table full width
    pdf.full_width()
    pdf.ln(1)
    pdf.set_font("TN", "B", 8)
    pdf.p_plain("TABLE III", size=8, style="B", align="C", leading=3.4)
    pdf.set_font("TN", "I", 7.4)
    pdf.p_plain(
        "Per-clip comparison. ΔLAeq is proposed minus frequency-flat gain at matched LUFS (positive: proposed has higher exposure proxy). "
        "ΔLUFS is proposed minus flat gain at matched LAeq (negative: proposed is quieter). LSD is vs. the unprocessed clip at the matched-exposure condition.",
        size=7.4,
        style="I",
        align="C",
        leading=3.2,
    )
    rows = [
        ["Bass+drums 130", "Bass", "+2.30", "−2.30", "0.54", "0.74"],
        ["Drum and bass", "Bass", "+1.61", "−1.61", "0.70", "0.19"],
        ["Bass loop 120", "Bass", "+1.59", "−1.59", "0.58", "1.36"],
        ["Lofi drums", "Bass", "+1.63", "−1.63", "0.51", "0.63"],
        ["Boombap", "Bass", "+2.67", "−2.67", "0.74", "0.25"],
        ["Bass/keys/drums", "Bass", "+2.07", "−2.07", "0.73", "0.15"],
        ["Synth bass", "Synth", "+4.91", "−4.91", "0.76", "0.18"],
        ["Synth mixed", "Synth", "+3.87", "−3.87", "0.78", "0.11"],
        ["Spoken poem", "Speech", "+0.84", "−0.85", "0.49", "0.20"],
        ["Male commands", "Speech", "−0.12", "+0.12", "0.67", "1.69"],
        ["Monologue", "Speech", "+1.44", "−1.44", "0.47", "0.17"],
        ["Synth speech", "Synth", "+0.01", "−0.01", "0.22", "0.12"],
        ["Choir amen", "Vocal", "+0.03", "−0.03", "0.27", "0.45"],
        ["Men choir", "Vocal", "+0.04", "−0.04", "0.25", "0.01"],
        ["Female vocal", "Vocal", "−0.07", "+0.07", "0.57", "1.40"],
        ["Male choir", "Vocal", "+0.22", "−0.22", "0.37", "0.08"],
        ["Acoustic", "Vocal", "+0.38", "−0.38", "0.23", "0.12"],
        ["Snare/crash", "Drums", "+0.05", "−0.05", "0.28", "0.03"],
        ["Cymbals", "Drums", "−0.01", "+0.01", "0.32", "0.03"],
        ["Synth transients", "Synth", "+0.01", "−0.01", "0.25", "0.09"],
        ["Mean (n=20)", "", "+1.17", "−1.17", "0.49", "0.40"],
    ]
    table_lines(
        pdf,
        ["Clip", "Type", "ΔLAeq (dB)", "ΔLUFS (dB)", "LSD prop.", "LSD flat"],
        rows,
        [0.26, 0.12, 0.16, 0.16, 0.15, 0.15],
    )
    pdf.start_columns()

    pdf.h2("B. Why the proxy moves the wrong way")
    pdf.p(
        "Fig. 6 plots, for the proposed output versus the original, LUFS drop against LAeq drop. If the two meters agreed, "
        "points would lie on the dashed line. Bass clips lie far to the right: LUFS falls by 2–5 dB while the A-weighted "
        "proxy barely moves. Speech and cymbals lie near the origin."
    )
    pdf.figure(
        FIGS / "metric_mismatch.png",
        "Fig. 6. Proposed processor versus the original clip. Bass-heavy material loses loudness (LUFS) without a matching drop in the A-weighted proxy, because A-weighting already ignores energy near 40 Hz.",
        max_h=72,
    )
    pdf.p(
        "A-weighting at 40 Hz is approximately −35 dB (Fig. 4). BS.1770 K-weighting does not discount that region to the "
        "same degree. The low-band shelf therefore does what it was designed to do—remove sub-bass—and LUFS notices. The "
        "exposure proxy does not. To match LUFS, flat gain must apply that same loudness reduction to the whole spectrum, "
        "including the midrange that A-weighting does count. Flat LAeq therefore falls further. Frequency-selective allocation "
        "aimed at “cheap” bass cuts is the wrong allocation for an A-weighted objective."
    )
    pdf.p(
        "This is not a crossover bug. Reconstruction is flat (Fig. 2), harmonics are present at 40 Hz (Fig. 3), and block "
        "streaming matches whole-signal processing. The negative result is a metric mismatch, not an implementation failure."
    )
    pdf.h2("C. Matched exposure: loudness and spectral distance")
    pdf.p(
        "Fig. 7 is the dual view. At equal digital LAeq, the proposed output is quieter by 1.17 dB LUFS on average—exactly "
        "the opposite sign of Fig. 5, as expected for a frequency-flat baseline. H1 is not supported as a loudness-preservation "
        "claim. At the same A-weighted proxy, turning the whole signal down keeps more LUFS than cutting sub-bass."
    )
    pdf.figure(
        FIGS / "matched_exposure_quality.png",
        "Fig. 7. Left: LUFS at matched digital LAeq proxy. The proposed system is quieter on bass-heavy clips. Right: log-spectral distance versus the original at the same match. LSD is an objective distance, not a quality grade.",
        wide=True,
        max_h=68,
    )
    pdf.p(
        "Mean LSD is 0.49 dB for the proposed system and 0.40 dB for flat gain. On many bass clips flat gain barely moves, "
        "so its LSD is small. On clips where the mid-band compressor actually works (female vocal, command speech), flat gain "
        "of the same LAeq drop produces a larger spectral shift than the band-limited compressor (LSD 1.40 and 1.69 dB versus "
        "0.57 and 0.67 dB). Spectral distance is therefore mixed: the proposed system is not uniformly closer to the original, "
        "but it avoids the largest broadband shifts. Without a listening test that pattern should not be read as “better quality.”"
    )
    pdf.h2("D. Ablation")
    pdf.p(
        "Fig. 8 shows mean change versus the original when bands are enabled one at a time. Crossover-only reconstruction "
        "does not change level. Mid-only compression moves LAeq on speech and vocals and does little on bass. Adding the low "
        "band is what drops LUFS. Adding the high band changes almost nothing on this corpus; transients in the test set rarely "
        "exceeded the high-band threshold. The full system tracks the mid+low curve. The exposure/loudness disagreement is "
        "produced by the low shelf, which is also the block that was supposed to be the advantage."
    )
    pdf.figure(
        FIGS / "ablation_delta.png",
        "Fig. 8. Ablation, mean over 20 clips, relative to the unprocessed signal. “Default DRC” is a full-band A-weighted compressor at the default target, not the LUFS-matched flat gain of Fig. 5. The low band dominates the LUFS drop.",
        max_h=62,
    )
    pdf.h2("E. Mid-band operating point")
    pdf.p(
        "A target/ratio sweep on a six-tone-plus-noise debug signal (Table IV) shows the expected trade-off: a lower mid "
        "target reduces the proxy and raises LSD. That sweep characterises the compressor. It is not the main result and it "
        "is not a perceptual quality measurement."
    )
    pdf.set_font("TN", "B", 8)
    pdf.p_plain("TABLE IV", size=8, style="B", align="C", leading=3.4)
    pdf.set_font("TN", "I", 7.4)
    pdf.p_plain("Mid-band target/ratio sweep on a synthetic six-tone-plus-noise signal.", size=7.4, style="I", align="C", leading=3.2)
    table_lines(
        pdf,
        ["Target", "Ratio", "LAeq", "ΔLAeq", "LSD"],
        [
            ["82", "2:1", "77.77", "−0.10", "0.82"],
            ["80", "3:1", "77.77", "−0.10", "0.82"],
            ["78", "4:1", "77.04", "−0.83", "0.88"],
            ["76", "4:1", "75.92", "−1.96", "1.16"],
            ["74", "6:1", "74.57", "−3.30", "1.65"],
            ["72", "8:1", "73.34", "−4.53", "2.20"],
        ],
        [0.2, 0.2, 0.2, 0.2, 0.2],
    )

    pdf.h1("VII", "Limitations")
    pdf.p(
        "This study compares two digital processing rules. It does not show prevention of hearing loss, and it does not "
        "report ear-level SPL. The LAeq figures use an uncalibrated offset; a real mapping would require a specific earphone, "
        "volume setting, and an IEC 60318-4 occluded-ear simulator [23], which still is not an individual human ear."
    )
    pdf.p(
        "LUFS is a standard loudness meter, not a booth loudness match. Band edges, shelf depth, and compressor constants "
        "were not searched over listeners. No Zwicker or Moore–Glasberg model is in the loop. No PEAQ or MUSHRA scores were "
        "collected. The high band did little on this set, so the experiment mainly contrasts a low-shelf-plus-harmonics path "
        "with flat gain. Four synthetic clips are in the mean; removing them lowers the matched-loudness gap from 1.17 dB to "
        "0.92 dB and does not reverse the sign."
    )

    pdf.h1("VIII", "Conclusion")
    pdf.p(
        "We asked whether a three-band, perceptually motivated limiter could reduce a digital A-weighted exposure proxy more "
        "than turning the whole signal down, at the same LUFS. On 20 clips it did not: the proposed proxy was 1.17 dB higher "
        "on average, and 1.6 to 2.7 dB higher on real bass loops. Vocals, speech, and short transients were a tie. Cutting "
        "sub-bass spends loudness on a band that A-weighting already ignores, so a flat gain that matches LUFS wins on LAeq. "
        "The useful outcome is that comparison. If an A-weighted dose limit is the constraint, frequency-selective bass cuts "
        "are a poor allocation; any later design should spend attenuation where wA(f) is large, or replace A-weighting with a "
        "metric that actually tracks the intended risk. Calibrated ear-simulator measurements and a locked-volume listening "
        "test remain the next experimental step."
    )

    pdf.h1("", "References")
    refs = [
        "[1] ITU, “ITU-T Recommendation H.870: Guidelines for Safe Listening Devices/Systems,” ITU and WHO, Geneva, 2018 (v1.1, 2019).",
        "[2] World Health Organization, World Report on Hearing. Geneva, Switzerland: WHO, 2021.",
        "[3] S. Levey, T. Levey, and B. J. Fligor, “Noise exposure estimates of urban MP3 player users,” J. Speech Lang. Hear. Res., vol. 54, no. 1, pp. 263–277, 2011.",
        "[4] C. D. F. Portnuff, B. J. Fligor, and K. H. Arehart, “Teenage use of portable listening devices: A hazard to hearing?,” J. Am. Acad. Audiol., vol. 22, no. 10, pp. 663–677, 2011.",
        "[5] D. Giannoulis, M. Massberg, and J. D. Reiss, “Digital dynamic range compressor design—a tutorial and analysis,” J. Audio Eng. Soc., vol. 60, no. 6, pp. 399–408, 2012.",
        "[6] H. Fletcher and W. A. Munson, “Loudness, its definition, measurement and calculation,” J. Acoust. Soc. Am., vol. 5, no. 2, pp. 82–108, 1933.",
        "[7] ISO, “ISO 226:2023 Acoustics — Normal equal-loudness-level contours,” Geneva, 2023.",
        "[8] A. H. Sulaiman, K. Seluakumaran, and R. Husain, “Hearing risk associated with the usage of personal listening devices among urban high school students in Malaysia,” Public Health, vol. 127, no. 8, pp. 710–715, 2013.",
        "[9] J. M. Kates, “Principles of digital dynamic-range compression,” Trends Amplif., vol. 12, no. 2, pp. 112–128, 2008.",
        "[10] ITU, “Recommendation ITU-R BS.1770-4: Algorithms to measure audio programme loudness and true-peak audio level,” Geneva, 2015.",
        "[11] E. Zwicker, “Subdivision of the audible frequency range into critical bands,” J. Acoust. Soc. Am., vol. 33, no. 2, p. 248, 1961.",
        "[12] E. Zwicker and H. Fastl, Psychoacoustics: Facts and Models, 2nd ed. Berlin: Springer, 1999.",
        "[13] B. C. J. Moore, B. R. Glasberg, and T. Baer, “A model for the prediction of thresholds, loudness, and partial loudness,” J. Audio Eng. Soc., vol. 45, no. 4, pp. 224–240, 1997.",
        "[14] B. R. Glasberg and B. C. J. Moore, “A model of loudness applicable to time-varying sounds,” J. Audio Eng. Soc., vol. 50, no. 5, pp. 331–342, 2002.",
        "[15] J. F. Schouten, “The residue and the mechanism of hearing,” Proc. Koninklijke Nederlandse Akademie van Wetenschappen, vol. 43, pp. 991–999, 1940.",
        "[16] E. Terhardt, “Pitch, consonance, and harmony,” J. Acoust. Soc. Am., vol. 55, no. 5, pp. 1061–1069, 1974.",
        "[17] E. Terhardt, “Calculating virtual pitch,” Hearing Research, vol. 1, no. 2, pp. 155–182, 1979.",
        "[18] D. Ben-Tzur, M. Rosenblatt, and A. Vardi, “The effect of MaxxBass psychoacoustic bass enhancement on loudspeaker design,” in Proc. 106th AES Convention, Munich, 1999.",
        "[19] W. S. Gan, S. M. Kuo, and C. W. Toh, “Virtual bass for home entertainment, multimedia PC, game station and portable audio systems,” IEEE Trans. Consum. Electron., vol. 47, no. 4, pp. 787–794, 2001.",
        "[20] W. S. Gan and S. M. Kuo, “Integration of virtual bass reproduction in active noise control headsets,” in Proc. 7th Int. Conf. Signal Process. (ICSP), vol. 1, 2004, pp. 368–371.",
        "[21] IEC, “IEC 61672-1:2013 Electroacoustics — Sound level meters — Part 1: Specifications,” Geneva, 2013.",
        "[22] S. H. Linkwitz, “Active crossover networks for noncoincident drivers,” J. Audio Eng. Soc., vol. 24, no. 1, pp. 2–8, 1976.",
        "[23] IEC, “IEC 60318-4:2010 Electroacoustics — Simulators of human head and ear — Part 4: Occluded-ear simulator,” Geneva, 2010.",
    ]
    pdf.set_font("TN", "", 8)
    for r in refs:
        pdf.ensure(10)
        pdf.p_plain(r, size=8, leading=3.35, align="J")

    pdf.output(str(OUT))
    return OUT


if __name__ == "__main__":
    path = build()
    print(path)
    print("bytes", path.stat().st_size)
