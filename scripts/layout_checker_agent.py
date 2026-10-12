#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — Agente Auditor de Layout, Identidade Visual e Design System v2
Audita arquivos HTML de painéis contra o PADRAO_DESIGN_PAINEIS.md com
14 verificações ponderadas por severidade, suporte a multi-arquivo e
relatório por severidade (CRITICAL / ERROR / WARNING / INFO).
"""

import sys
import os
import re
import glob
from typing import List, Dict, Tuple

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Pontuação descontada por severidade
SEVERITY_WEIGHTS = {"CRITICAL": 20, "ERROR": 10, "WARNING": 5, "INFO": 0}

ANALYTICAL_PANELS = [
    os.path.join(WORKSPACE_DIR, "public", "churn", "index.html"),
    os.path.join(WORKSPACE_DIR, "public", "churn-bl-total", "index.html"),
    os.path.join(WORKSPACE_DIR, "public", "churn-bl-pme", "index.html"),
    os.path.join(WORKSPACE_DIR, "public", "fpd", "index.html"),
    os.path.join(WORKSPACE_DIR, "public", "fpd-residencial", "index.html"),
    os.path.join(WORKSPACE_DIR, "public", "evolucao-carteira", "index.html"),
]

# CDNs externos proibidos (regra Zero Dependências Externas)
FORBIDDEN_CDN_PATTERN = re.compile(
    r'<(?:script|link)[^>]+(?:src|href)=["\'](?:https?:)?//(?:'
    r'cdn\.jsdelivr\.net|unpkg\.com|cdnjs\.cloudflare\.com|'
    r'fonts\.googleapis\.com|use\.fontawesome\.com|'
    r'maxcdn\.bootstrapcdn\.com|stackpath\.bootstrapcdn\.com|'
    r'ajax\.googleapis\.com|code\.jquery\.com'
    r')[^"\']*["\']',
    re.IGNORECASE
)

# Emojis informais (exclui símbolos técnicos ▲ ▼ ▶ ⟳ ⤢ ✎)
INFORMAL_EMOJI_RE = re.compile(
    r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|'
    r'[\U0001F680-\U0001F6FF]|[\U0001F900-\U0001F9FF]|'
    r'[\U0001FA70-\U0001FAFF]'
)


class LayoutAuditorAgent:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.rel_path = os.path.relpath(filepath, WORKSPACE_DIR)
        self.issues: List[Dict] = []
        self.checks_passed = 0
        self.checks_total = 0
        self.score = 100

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Arquivo nao encontrado: {filepath}")

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            self.content = f.read()

        self.line_count = self.content.count('\n') + 1

    def report(self, check_name: str, passed: bool, severity: str = "ERROR", details: str = ""):
        self.checks_total += 1
        if passed:
            self.checks_passed += 1
        else:
            self.score -= SEVERITY_WEIGHTS.get(severity, 5)
            self.issues.append({
                "check": check_name,
                "severity": severity,
                "details": details
            })

    # ─────────────────────────────────────────────────────────────────
    # 1. CSS DESIGN SYSTEM (PALETA COMPLETA)
    # ─────────────────────────────────────────────────────────────────
    def audit_css_variables(self):
        """Verifica todas as 13 variáveis CSS semânticas do Claro Design System"""
        required = {
            "--bg": "Fundo principal",
            "--panel": "Cartoes e paineis",
            "--ink": "Texto primario",
            "--ink2": "Texto secundario",
            "--ink3": "Texto terciario",
            "--line": "Bordas externas",
            "--line2": "Divisorias sutis",
            "--nav": "Barra de contexto",
            "--nav2": "Hover elementos escuros",
            "--red": "Churn/cancelamento",
            "--green": "Retencao/sucesso",
            "--amber": "Atencao/parcial",
            "--blue": "Links/ativo",
            "--purple": "Inadimplencia NP",
        }
        missing = [v for v, label in required.items() if v not in self.content]
        if missing:
            self.report(
                "Paleta CSS Completa (:root)",
                False,
                severity="CRITICAL" if len(missing) > 3 else "ERROR",
                details=f"Variaveis ausentes: {', '.join(missing)}"
            )
        else:
            self.report("Paleta CSS Completa (:root)", True)

    # ─────────────────────────────────────────────────────────────────
    # 2. IDENTIDADE DO CABEÇALHO
    # ─────────────────────────────────────────────────────────────────
    def audit_header_branding(self):
        """Gradiente corporativo Claro e subtitulo Regional Norte"""
        has_gradient = (
            "linear-gradient(90deg" in self.content
            and ("#8a0f18" in self.content or "#c0191f" in self.content)
        )
        self.report(
            "Gradiente Institucional Claro (cabecalho)",
            has_gradient,
            severity="CRITICAL",
            details="OK" if has_gradient else "Gradiente corporativo vermelho/laranja ausente ou incorreto."
        )

        has_regional = "Regional Norte" in self.content
        self.report(
            "Subtitulo Institucional 'Regional Norte'",
            has_regional,
            severity="WARNING",
            details="OK" if has_regional else "Texto 'Regional Norte' nao localizado no arquivo."
        )

        has_hd_sub = ".hd-sub" in self.content or "hd-sub" in self.content
        self.report(
            "Barra de Contexto Escura (.hd-sub)",
            has_hd_sub,
            severity="WARNING",
            details="OK" if has_hd_sub else "Classe .hd-sub ausente — barra de versao/data nao padronizada."
        )

    # ─────────────────────────────────────────────────────────────────
    # 3. TIPOGRAFIA E HIERARQUIA
    # ─────────────────────────────────────────────────────────────────
    def audit_typography(self):
        """Familia tipografica corporativa e metricas de KPI"""
        has_font = "Segoe UI" in self.content or "Roboto" in self.content
        self.report(
            "Tipografia Corporativa (Segoe UI / Roboto)",
            has_font,
            severity="WARNING",
            details="OK" if has_font else "Familia tipografica corporativa nao declarada."
        )

        # KPI value size 22px
        has_kpi_size = "22px" in self.content and (".kpi" in self.content or ".kpis" in self.content)
        self.report(
            "Metricas de KPI (22px / .kpi / .kpis)",
            has_kpi_size,
            severity="WARNING",
            details="OK" if has_kpi_size else "Estrutura de KPI com tamanho 22px nao identificada (.kpi/.kpis)."
        )

        # Numeração Sequencial de Indicadores
        has_numbered_kpis = bool(re.search(r'(?:card\(|class=["\']k["\']>)\s*[\'"]?1\.\s+', self.content))
        self.report(
            "Numeração Sequencial de Indicadores (1., 2., 3...)",
            has_numbered_kpis,
            severity="WARNING",
            details="OK" if has_numbered_kpis else "Indicadores de KPI sem prefixo numérico sequencial (ex: '1. ...')."
        )

    # ─────────────────────────────────────────────────────────────────
    # 4. EMOJIS INFORMAIS
    # ─────────────────────────────────────────────────────────────────
    def audit_no_emojis(self):
        """Emojis informais proibidos — apenas icones vetoriais SVG ou simbolos tecnicos"""
        matches = []
        for m in INFORMAL_EMOJI_RE.finditer(self.content):
            start = max(0, m.start() - 30)
            end = min(len(self.content), m.end() + 30)
            ctx = self.content[start:end]
            # Ignorar chunks base64
            if not re.search(r'[A-Za-z0-9+/=]{40,}', ctx):
                matches.append(m.group(0))
        self.report(
            "Ausencia de Emojis Informais",
            len(matches) == 0,
            severity="ERROR",
            details="OK" if not matches else f"{len(matches)} emoji(s) informal(is) detectado(s). Use simbolos vetoriais SVG."
        )

    # ─────────────────────────────────────────────────────────────────
    # 5. ZERO CDNs EXTERNOS
    # ─────────────────────────────────────────────────────────────────
    def audit_no_external_cdn(self):
        """Nenhum script ou folha de estilo deve ser carregado de CDN externo"""
        found = FORBIDDEN_CDN_PATTERN.findall(self.content)
        self.report(
            "Zero CDNs Externos (self-contained)",
            len(found) == 0,
            severity="CRITICAL",
            details="OK" if not found else f"{len(found)} referencia(s) a CDN externo detectada(s): {found[:3]}"
        )

    # ─────────────────────────────────────────────────────────────────
    # 6. HELPERS CONTEXTUAIS (.hlp) — DICIONÁRIO HELP
    # ─────────────────────────────────────────────────────────────────
    def audit_help_dictionary(self):
        """Todo botao ? com data-h deve ter verbete no objeto HELP do JS"""
        help_keys = set()
        help_block = re.search(
            r'(?:const|let|var)\s+HELP\s*=\s*\{([^}]+(?:\{[^}]+\}[^}]+)*)\}',
            self.content, re.DOTALL
        )
        if help_block:
            raw = re.findall(r'(\b[a-zA-Z0-9_]+\b)\s*:', help_block.group(1))
            help_keys = set(raw)

        hlp_buttons = re.findall(
            r'<button[^>]*class=["\'][^"\']*hlp[^"\']*["\'][^>]*data-h=["\']([^"\']+)["\']'
            r'|<button[^>]*data-h=["\']([^"\']+)["\'][^>]*class=["\'][^"\']*hlp[^"\']*["\']',
            self.content
        )
        hlp_keys = [h[0] or h[1] for h in hlp_buttons]
        unregistered = [h for h in hlp_keys if h not in help_keys]

        self.report(
            "Registro de Helpers Contextuais (dicionario HELP)",
            len(unregistered) == 0,
            severity="ERROR",
            details="OK" if not unregistered else f"Helpers sem verbete no HELP: {unregistered}"
        )

    # ─────────────────────────────────────────────────────────────────
    # 7. SVG NATIVO — HALO DE ROTULOS E VIEWBOX
    # ─────────────────────────────────────────────────────────────────
    def audit_svg_standards(self):
        """Graficos SVG devem usar viewBox e halo branco em rotulos"""
        has_svg = "<svg" in self.content
        if not has_svg:
            self.report("SVG Nativo com viewBox", True, details="Nenhum SVG no arquivo (pode ser intencional).")
            return

        has_viewbox = bool(re.search(r'viewBox\s*=', self.content, re.IGNORECASE))
        self.report(
            "SVG com viewBox Responsivo",
            has_viewbox,
            severity="ERROR",
            details="OK" if has_viewbox else "SVG(s) detectados sem atributo viewBox — graficos nao responsivos."
        )

        has_halo = "paint-order" in self.content or "stroke-width" in self.content
        self.report(
            "Halo Branco em Rotulos SVG (paint-order / stroke-width)",
            has_halo,
            severity="WARNING",
            details="OK" if has_halo else "Rotulos SVG sem halo branco — legibilidade comprometida sobre barras."
        )

    # ─────────────────────────────────────────────────────────────────
    # 8. TOOLTIPS .gtip
    # ─────────────────────────────────────────────────────────────────
    def audit_tooltips(self):
        """Tooltips flutuantes devem usar o padrao .gtip (elemento unico dinamico)"""
        has_svg_charts = bool(re.search(r'drawBars|drawLine|drawScatter|drawMap', self.content))
        if not has_svg_charts:
            return  # Painel sem graficos nao requer .gtip
        has_gtip = ".gtip" in self.content or "gtip" in self.content
        self.report(
            "Tooltips Flutuantes .gtip",
            has_gtip,
            severity="WARNING",
            details="OK" if has_gtip else "Painel com graficos sem tooltip padrao .gtip — UX de exploracao prejudicada."
        )

    # ─────────────────────────────────────────────────────────────────
    # 9. GAVETA DE FILTROS (.drawer-btn)
    # ─────────────────────────────────────────────────────────────────
    def audit_filter_drawer(self):
        """Gaveta de filtros retrátil obrigatoria em paineis analiticos"""
        is_analytical = any(
            term in self.content for term in ["churn", "fpd", "safra", "FPD", "Churn"]
        )
        if not is_analytical:
            return
        has_drawer = "drawer-btn" in self.content or "drawer" in self.content.lower()
        self.report(
            "Gaveta de Filtros Retrátil (.drawer-btn)",
            has_drawer,
            severity="WARNING",
            details="OK" if has_drawer else "Painel analitico sem gaveta de filtros retrátil (.drawer-btn)."
        )

    # ─────────────────────────────────────────────────────────────────
    # 10. EXPORTAÇÃO CSV NO CLIENTE
    # ─────────────────────────────────────────────────────────────────
    def audit_csv_export(self):
        """Tabelas analiticas devem oferecer exportacao CSV via Blob no cliente"""
        is_analytical = "table" in self.content.lower() and any(
            k in self.content for k in ["churn", "fpd", "safra"]
        )
        if not is_analytical:
            return
        has_export = "createObjectURL" in self.content or "Blob" in self.content
        self.report(
            "Exportacao CSV no Cliente (Blob / createObjectURL)",
            has_export,
            severity="INFO",
            details="OK" if has_export else "Tabela sem exportacao CSV no cliente — considere adicionar."
        )

    # ─────────────────────────────────────────────────────────────────
    # ─────────────────────────────────────────────────────────────────
    # 11. PADRONIZAÇÃO DAS VISÕES CRÍTICAS (PAINÉIS DE CHURN/SAFRA)
    # ─────────────────────────────────────────────────────────────────
    def audit_critical_views(self):
        """Verifica seções analíticas obrigatórias apenas se forem painéis de safra detalhada"""
        checks = [
            ("DISPERSÃO", "scatter", "Visao de Dispersao MoM & YoY"),
            ("RISCO",     "risco",   "Visao de Risco e Score"),
            ("MATRIZ DE SAFRA", "matriz", "Matriz de Safra com Marco FPD 60"),
        ]
        for term, helper_key, label in checks:
            # Verifica se o termo aparece como cabeçalho ou seção estrutural
            has_panel = bool(re.search(r'<h[23][^>]*>[^<]*\b' + re.escape(term) + r'\b', self.content, re.IGNORECASE))
            if not has_panel:
                has_panel = f'id="{helper_key}"' in self.content.lower() or f'class="view-{helper_key}"' in self.content.lower()
            if has_panel:
                has_helper = f'data-h="{helper_key}"' in self.content
                self.report(
                    f"Padronizacao: {label}",
                    has_helper,
                    severity="ERROR",
                    details=f"OK" if has_helper else f"Secao '{term}' presente mas sem helper data-h='{helper_key}'."
                )

    # ─────────────────────────────────────────────────────────────────
    # 12. ABAS (.tabs) COM CLASSE .on
    # ─────────────────────────────────────────────────────────────────
    def audit_tabs(self):
        """Componentes de abas devem usar .tabs e .on para estado ativo"""
        tabs_count = len(re.findall(r'class=["\'][^"\']*\btabs\b[^"\']*["\']', self.content))
        if tabs_count > 0:
            has_on_class = bool(re.search(r'class=["\'][^"\']*\bon\b[^"\']*["\']', self.content))
            self.report(
                "Abas (.tabs) com Estado Ativo (.on)",
                has_on_class,
                severity="WARNING",
                details=f"OK — {tabs_count} bloco(s) de abas com classe .on." if has_on_class
                        else f"{tabs_count} bloco(s) .tabs sem classe .on para estado ativo."
            )

    # ─────────────────────────────────────────────────────────────────
    # 13. FILTROS: CHIPS VISUAIS DE FILTROS ATIVOS
    # ─────────────────────────────────────────────────────────────────
    def audit_active_filter_chips(self):
        """Chips de filtros ativos devem ser exibidos no topo da gaveta"""
        is_analytical = "drawer" in self.content.lower()
        if not is_analytical:
            return
        has_chips = re.search(r'chips?|filter.?chip|active.?filter', self.content, re.IGNORECASE)
        self.report(
            "Chips Visuais de Filtros Ativos",
            bool(has_chips),
            severity="INFO",
            details="OK" if has_chips else "Gaveta de filtros sem chips visuais de filtros ativos — UX incompleto."
        )

    # ─────────────────────────────────────────────────────────────────
    # 14. TAMANHO DO ARQUIVO
    # ─────────────────────────────────────────────────────────────────
    def audit_file_size(self):
        """Arquivos acima de 3000 linhas requerem plano de decomposicao"""
        threshold_warn = 3000
        threshold_crit = 4000
        severity = (
            "CRITICAL" if self.line_count > threshold_crit
            else "WARNING" if self.line_count > threshold_warn
            else None
        )
        if severity:
            self.report(
                f"Tamanho do Arquivo ({self.line_count} linhas)",
                False,
                severity=severity,
                details=f"Arquivo com {self.line_count} linhas — acima do limite recomendado de {threshold_warn}. Planejar decomposicao."
            )

    # ─────────────────────────────────────────────────────────────────
    # 15. REGRAS DO PADRÃO OURO CHURN SAFRA (DESIGN SYSTEM COESIVO)
    # ─────────────────────────────────────────────────────────────────
    def audit_churn_safra_golden_rules(self):
        """Audita conformidade com o Padrão Ouro do Churn Safra:
        - Estrutura de cartões .panel com cabeçalho h2 limpo
        - Gaveta de filtros retrátil (.drawer-btn)
        - Destaque corporativo de Mês Foco (.th-foco / .td-foco)
        - Separador vertical da série histórica (.th-hist-start / .td-hist-start)
        """
        is_analytical = any(k in self.content.lower() for k in ["churn", "fpd", "safra", "market share"])
        if not is_analytical:
            return

        has_panel = ".panel" in self.content
        self.report(
            "Padrão Ouro: Estrutura de Painéis (.panel)",
            has_panel,
            severity="WARNING",
            details="OK" if has_panel else "Painéis não utilizam a classe corporativa .panel do Padrão Ouro."
        )

        has_foco_highlight = ".th-foco" in self.content or "td-foco" in self.content
        self.report(
            "Padrão Ouro: Destaque de Mês Foco (.th-foco / .td-foco)",
            has_foco_highlight,
            severity="WARNING",
            details="OK" if has_foco_highlight else "Tabelas sem destaque corporativo no Mês Foco."
        )

        has_hist_sep = "th-hist-start" in self.content or "td-hist-start" in self.content
        self.report(
            "Padrão Ouro: Divisória entre YoY e Histórico (.th-hist-start)",
            has_hist_sep,
            severity="WARNING",
            details="OK" if has_hist_sep else "Tabelas sem separador vertical de histórico temporal."
        )

    # ─────────────────────────────────────────────────────────────────
    # 16. TABELAS ANALÍTICAS: CLASSIFICAÇÃO / ORDENAÇÃO DE COLUNAS
    # ─────────────────────────────────────────────────────────────────
    def audit_table_sortable_columns(self):
        """Audita se tabelas analíticas possuem ordenação interativa de colunas (sortable / sortTable / etc.)"""
        is_analytical = "table" in self.content.lower() and any(
            k in self.content.lower() for k in ["churn", "fpd", "safra", "market share"]
        )
        if not is_analytical:
            return

        has_sorting = any(
            term in self.content for term in ["sortable", "sortTable", "initSortable", "sorted-asc", "sorted-desc", "sortCol"]
        )
        self.report(
            "Tabelas Analíticas: Ordenação/Classificação de Colunas (.sortable / sortTable)",
            has_sorting,
            severity="WARNING",
            details="OK" if has_sorting else "Tabelas analíticas sem ordenação/classificação interativa de colunas. Clique em th deve permitir ordenar."
        )

    # ─────────────────────────────────────────────────────────────────
    # 17. CABEÇALHO PADRÃO CORPORATIVO (Voltar ao Catálogo, Sair, .dot, .hd-right)
    # ─────────────────────────────────────────────────────────────────
    def audit_header_safra_standard(self):
        """Audita conformidade estrita do cabeçalho de relatórios:
        - Exatamente dois controles de ação no cabeçalho: 'Voltar ao Catálogo' e 'Sair'.
        - Proibido exportar HTML no cabeçalho (exclusivo da área de admin/gestão).
        - Proibido link textual redundante 'Portal Pephub' no canto superior esquerdo do .hd-sub.
        - Divisores pontuais .dot no .hd-sub e alinhamento à direita com .hd-right.
        """
        is_panel = any(k in self.content.lower() for k in ["churn", "fpd", "safra", "market share"])
        if not is_panel:
            return

        has_back_catalog = "Voltar ao Catálogo" in self.content or "btn-nav-catalog" in self.content
        self.report(
            "Cabeçalho Padrão: Botão 'Voltar ao Catálogo'",
            has_back_catalog,
            severity="WARNING",
            details="OK" if has_back_catalog else "Cabeçalho sem botão oficial 'Voltar ao Catálogo'."
        )

        has_logout = "Sair" in self.content or "btnLogout" in self.content or "UserWidget" in self.content
        self.report(
            "Cabeçalho Padrão: Controle de Sair / Logout Atômico",
            has_logout,
            severity="WARNING",
            details="OK" if has_logout else "Cabeçalho sem controle de 'Sair' com logout seguro."
        )

        # Proibição de exportar HTML no cabeçalho
        has_header_html_export = bool(re.search(r'<header[^>]*>.*?download=["\'][^"\']*\.html["\'].*?</header>', self.content, re.DOTALL))
        self.report(
            "Cabeçalho Padrão: Ausência de Exportação HTML (Exclusivo de Gestão)",
            not has_header_html_export,
            severity="ERROR",
            details="OK" if not has_header_html_export else "Cabeçalho contém botão de exportar HTML. Exportação de HTML deve ficar apenas na gestão/admin."
        )

        has_sub_elements = "dot" in self.content and "hd-right" in self.content
        self.report(
            "Cabeçalho Padrão: Divisores (.dot) e Alinhamento (.hd-right)",
            has_sub_elements,
            severity="WARNING",
            details="OK" if has_sub_elements else "Barra .hd-sub sem divisores .dot ou alinhamento .hd-right."
        )

    # ─────────────────────────────────────────────────────────────────
    # 18. BOTÕES E CONTROLES PADRÃO CHURN SAFRA (.primary, .drawer-btn, .tabs)
    # ─────────────────────────────────────────────────────────────────
    def audit_button_safra_standard(self):
        """Audita se botões e controles seguem o design system do Churn Safra:
        - Botões primários com classe .primary (fundo escuro corporativo --nav)
        - Botões de gaveta de filtro com .drawer-btn
        - Segmented controls de métricas/visões com .tabs e estado ativo .on
        """
        is_panel = any(k in self.content.lower() for k in ["churn", "fpd", "safra", "market share"])
        if not is_panel:
            return

        has_primary = "button.primary" in self.content or 'class="primary"' in self.content or "primary" in self.content
        self.report(
            "Botões Padrão Churn Safra: Ação Principal (.primary)",
            has_primary,
            severity="WARNING",
            details="OK" if has_primary else "Painel sem botões de ação principal padronizados com .primary."
        )

        has_tabs_active = ".tabs" in self.content and (".on" in self.content or "class=\"on\"" in self.content or "classList.add('on')" in self.content)
        self.report(
            "Botões Padrão Churn Safra: Segmented Controls (.tabs com .on)",
            has_tabs_active,
            severity="WARNING",
            details="OK" if has_tabs_active else "Controles de métricas/visões sem botões segmentados .tabs e estado ativo .on."
        )

    # ─────────────────────────────────────────────────────────────────
    # ORQUESTRADOR
    # ─────────────────────────────────────────────────────────────────
    def run_all(self) -> Tuple[int, int, float]:
        self.audit_css_variables()
        self.audit_header_branding()
        self.audit_typography()
        self.audit_no_emojis()
        self.audit_no_external_cdn()
        self.audit_help_dictionary()
        self.audit_svg_standards()
        self.audit_tooltips()
        self.audit_filter_drawer()
        self.audit_csv_export()
        self.audit_critical_views()
        self.audit_tabs()
        self.audit_active_filter_chips()
        self.audit_table_sortable_columns()
        self.audit_file_size()
        self.audit_churn_safra_golden_rules()
        self.audit_header_safra_standard()
        self.audit_button_safra_standard()

        self.score = max(0, min(100, self.score))
        pct = (self.checks_passed / self.checks_total * 100) if self.checks_total > 0 else 0
        return self.checks_passed, self.checks_total, pct

    def print_summary(self) -> bool:
        passed, total, pct = self.run_all()
        sev_order = {"CRITICAL": 0, "ERROR": 1, "WARNING": 2, "INFO": 3}
        sorted_issues = sorted(self.issues, key=lambda x: sev_order.get(x["severity"], 9))

        print("\n" + "=" * 72)
        print("  PEP HUB — AUDITOR DE LAYOUT & IDENTIDADE VISUAL  v2")
        print(f"  Arquivo : {self.rel_path}")
        print(f"  Linhas  : {self.line_count}")
        print("=" * 72)
        print(f"  Score de Conformidade : {self.score}/100")
        print(f"  Verificacoes Aprovadas: {passed}/{total} ({pct:.0f}%)")

        if self.score >= 95:
            grade = "A+ — Conformidade exemplar"
        elif self.score >= 85:
            grade = "A  — Alta conformidade"
        elif self.score >= 70:
            grade = "B  — Conformidade aceitavel com pontos a corrigir"
        elif self.score >= 55:
            grade = "C  — Desvios relevantes do Design System"
        else:
            grade = "D  — Reformulacao necessaria"
        print(f"  Grau                  : {grade}")
        print("-" * 72)

        if sorted_issues:
            print(f"  INCONFORMIDADES ({len(sorted_issues)}):")
            for idx, issue in enumerate(sorted_issues, 1):
                icons = {"CRITICAL": "[CRITICO]", "ERROR": "[ERRO]  ", "WARNING": "[AVISO] ", "INFO": "[INFO]  "}
                icon = icons.get(issue["severity"], "[?]")
                print(f"\n  {idx}. {icon} {issue['check']}")
                print(f"     => {issue['details']}")
        else:
            print("  100% CONFORME com o PADRAO_DESIGN_PAINEIS.md")

        print("\n" + "=" * 72 + "\n")
        return self.score >= 85


def run_all_panels():
    """Executa auditoria em todos os paineis analiticos e exibe sumario consolidado"""
    results = []
    for path in ANALYTICAL_PANELS:
        if not os.path.exists(path):
            continue
        try:
            agent = LayoutAuditorAgent(path)
            agent.print_summary()
            results.append((os.path.relpath(path, WORKSPACE_DIR), agent.score))
        except Exception as e:
            print(f"Erro ao auditar {path}: {e}")

    if len(results) > 1:
        print("\n" + "=" * 72)
        print("  SUMARIO CONSOLIDADO — TODOS OS PAINEIS")
        print("=" * 72)
        for rel, sc in sorted(results, key=lambda x: x[1]):
            grade = "A+" if sc >= 95 else "A" if sc >= 85 else "B" if sc >= 70 else "C" if sc >= 55 else "D"
            bar = "#" * (sc // 5) + "." * (20 - sc // 5)
            print(f"  [{grade}] {sc:3d}/100  [{bar}]  {rel}")
        avg = sum(s for _, s in results) / len(results)
        print(f"\n  Media Global: {avg:.1f}/100")
        print("=" * 72 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        agent = LayoutAuditorAgent(target)
        success = agent.print_summary()
        sys.exit(0 if success else 1)
    else:
        # Sem argumento: audita todos os paineis
        run_all_panels()
        sys.exit(0)
